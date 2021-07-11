
import RPi.GPIO as GPIO
import time
import threading

class HX711:

    def __init__(self, dout, pd_sck, gain=128):
        self.PD_SCK = pd_sck

        self.DOUT = dout

        self.readLock = threading.Lock()

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.PD_SCK, GPIO.OUT)
        GPIO.setup(self.DOUT, GPIO.IN)

        self.GAIN = 0


        self.REFERENCE_UNIT = 1
        self.REFERENCE_UNIT_B = 1

        self.OFFSET = 1
        self.OFFSET_B = 1
        self.lastVal = int(0)

        self.DEBUG_PRINTING = False

        self.byte_format = 'MSB'
        self.bit_format = 'MSB'

        self.set_gain(gain)

        # Think about whether this is necessary.
        time.sleep(1)

    def convertFromTwosComplement24bit(self, inputValue):
        return -(inputValue & 0x800000) + (inputValue & 0x7fffff)


    def is_ready(self):
        return GPIO.input(self.DOUT) == 0

    def set_gain(self, gain):
        if gain is 128:
            self.GAIN = 1
        elif gain is 64:
            self.GAIN = 3
        elif gain is 32:
            self.GAIN = 2

        GPIO.output(self.PD_SCK, False)


        self.readRawBytes()


    def get_gain(self):
        if self.GAIN == 1:
            return 128
        if self.GAIN == 3:
            return 64
        if self.GAIN == 2:
            return 32


        return 0


    def readNextBit(self):



       GPIO.output(self.PD_SCK, True)
       GPIO.output(self.PD_SCK, False)
       value = GPIO.input(self.DOUT)


       return int(value)


    def readNextByte(self):
       byteValue = 0

       for x in range(8):
          if self.bit_format == 'MSB':
             byteValue <<= 1
             byteValue |= self.readNextBit()
          else:
             byteValue >>= 1              
             byteValue |= self.readNextBit() * 0x80


       return byteValue


    def readRawBytes(self):

        self.readLock.acquire()


        while not self.is_ready():
           pass


        firstByte  = self.readNextByte()
        secondByte = self.readNextByte()
        thirdByte  = self.readNextByte()



        for i in range(self.GAIN):

           self.readNextBit()


        self.readLock.release()


        if self.byte_format == 'LSB':
           return [thirdByte, secondByte, firstByte]
        else:
           return [firstByte, secondByte, thirdByte]


    def read_long(self):

        dataBytes = self.readRawBytes()


        if self.DEBUG_PRINTING:
            print(dataBytes,)


        twosComplementValue = ((dataBytes[0] << 16) |
                               (dataBytes[1] << 8)  |
                               dataBytes[2])

        if self.DEBUG_PRINTING:
            print("Twos: 0x%06x" % twosComplementValue)


        signedIntValue = self.convertFromTwosComplement24bit(twosComplementValue)

        self.lastVal = signedIntValue


        return int(signedIntValue)

    def read_average(self, times=3):

        if times <= 0:
            raise ValueError("HX711()::read_average(): times must >= 1!!")


        if times == 1:
            return self.read_long()



        if times < 5:
            return self.read_median(times)


        valueList = []

        for x in range(times):
            valueList += [self.read_long()]

        valueList.sort()


        trimAmount = int(len(valueList) * 0.2)


        valueList = valueList[trimAmount:-trimAmount]


        return sum(valueList) / len(valueList)


    def read_median(self, times=3):
       if times <= 0:
          raise ValueError("HX711::read_median(): times must be greater than zero!")

       if times == 1:
          return self.read_long()

       valueList = []

       for x in range(times):
          valueList += [self.read_long()]

       valueList.sort()

       if (times & 0x1) == 0x1:
          return valueList[len(valueList) // 2]
       else:

          midpoint = len(valueList) / 2
          return sum(valueList[midpoint:midpoint+2]) / 2.0



    def get_value(self, times=3):
        return self.get_value_A(times)


    def get_value_A(self, times=3):
        return self.read_median(times) - self.get_offset_A()


    def get_value_B(self, times=3):

        g = self.get_gain()
        self.set_gain(32)
        value = self.read_median(times) - self.get_offset_B()
        self.set_gain(g)
        return value


    def get_weight(self, times=3):
        return self.get_weight_A(times)


    def get_weight_A(self, times=3):
        value = self.get_value_A(times)
        value = value / self.REFERENCE_UNIT
        return value

    def get_weight_B(self, times=3):
        value = self.get_value_B(times)
        value = value / self.REFERENCE_UNIT_B
        return value


    def tare(self, times=15):
        return self.tare_A(times)

    def tare_A(self, times=15):

        backupReferenceUnit = self.get_reference_unit_A()
        self.set_reference_unit_A(1)

        value = self.read_average(times)

        if self.DEBUG_PRINTING:
            print("Tare A value:", value)

        self.set_offset_A(value)


        self.set_reference_unit_A(backupReferenceUnit)

        return value


    def tare_B(self, times=15):
        backupReferenceUnit = self.get_reference_unit_B()
        self.set_reference_unit_B(1)


        backupGain = self.get_gain()
        self.set_gain(32)

        value = self.read_average(times)

        if self.DEBUG_PRINTING:
            print("Tare B value:", value)

        self.set_offset_B(value)


        self.set_gain(backupGain)
        self.set_reference_unit_B(backupReferenceUnit)

        return value



    def set_reading_format(self, byte_format="LSB", bit_format="MSB"):
        if byte_format == "LSB":
            self.byte_format = byte_format
        elif byte_format == "MSB":
            self.byte_format = byte_format
        else:
            raise ValueError("Unrecognised byte_format: \"%s\"" % byte_format)

        if bit_format == "LSB":
            self.bit_format = bit_format
        elif bit_format == "MSB":
            self.bit_format = bit_format
        else:
            raise ValueError("Unrecognised bitformat: \"%s\"" % bit_format)


    def set_offset(self, offset):
        self.set_offset_A(offset)

    def set_offset_A(self, offset):
        self.OFFSET = offset

    def set_offset_B(self, offset):
        self.OFFSET_B = offset

    def get_offset(self):
        return self.get_offset_A()

    def get_offset_A(self):
        return self.OFFSET

    def get_offset_B(self):
        return self.OFFSET_B



    def set_reference_unit(self, reference_unit):
        self.set_reference_unit_A(reference_unit)


    def set_reference_unit_A(self, reference_unit):

        if reference_unit == 0:
            raise ValueError("HX711::set_reference_unit_A() can't accept 0 as a reference unit!")
            return

        self.REFERENCE_UNIT = reference_unit


    def set_reference_unit_B(self, reference_unit):
        if reference_unit == 0:
            raise ValueError("HX711::set_reference_unit_A() can't accept 0 as a reference unit!")
            return

        self.REFERENCE_UNIT_B = reference_unit


    def get_reference_unit(self):
        return get_reference_unit_A()


    def get_reference_unit_A(self):
        return self.REFERENCE_UNIT


    def get_reference_unit_B(self):
        return self.REFERENCE_UNIT_B

    def power_down(self):

        self.readLock.acquire()

        GPIO.output(self.PD_SCK, False)
        GPIO.output(self.PD_SCK, True)

        time.sleep(0.0001)


        self.readLock.release()

    def power_up(self):

        self.readLock.acquire()

        GPIO.output(self.PD_SCK, False)

        time.sleep(0.0001)

        self.readLock.release()

        if self.get_gain() != 128:
            self.readRawBytes()


    def reset(self):
        self.power_down()
        self.power_up()


