<?php


$command = escapeshellcmd('python /home/pi/snitch-sniffer/hx711py/example.py');
$output = shell_exec($command);
echo $output;

var_dump($output);
 die();
?>
