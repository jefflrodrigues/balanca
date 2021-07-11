from tkinter import*
import mysql.connector

def pesquisar():
    pass

def editar():
    pass

def gravar():
    con = mysql.connector.connect(
        host="localhost",
        user="root",
        password="240806",
        database="tcc"
    )
    cursor = con.cursor()
    codigo_brinco = entrada1.get()
    cor_brinco = str(entrada2.get())
    sexo_animal = str(entrad3.get())
    tipo_animal = str(entrada4.get())
    sql = "INSERT INTO balanca(codigo_brinco, cor_brinco, sexo_animal, tipo_animal) VALUES(?,?,?,?)"
    val = (codigo_brinco, cor_brinco, sexo_animal, tipo_animal)
    cursor.executemany(sql, val)
    con.commit()

def excluir():
    pass


app = Tk()
app.title('Interface Balança')
app.geometry('800x400')
app.resizable(width=False, height=False)

# label titulo
lb1 = Label(app, text="Cadastro de Bovinos")
lb1.configure(font=("Arial", 20))
lb1.place(x=260, y=20)

# label codigo do brinco
lb2 = Label(app, text="CÓDIGO BRINCO")
lb2.place(x=20, y=80)

# label cor do animal
lb3 = Label(app, text="COR DO BRINCO")
lb3.place(x=20, y=130)

# label Sexo do anima
lb4 = Label(app, text="SEXO DO ANIMAL")
lb4.place(x=20, y=180)

# label tipo do animal
lb5 = Label(app, text="TIPO DE ANIMAL")
lb5.place(x=20, y=230)

# label peso:
lb6 = Label(app, text="PESO")
lb6.place(x=20, y=280)

# botao pesquisar
bt1 = Button(app, text="PESQUISAR")
bt1.place(x=20, y=350)

# botão editar
bt2 = Button(app, text="EDITAR")
bt2.place(x=95, y=350)

# botão gravar
bt3 = Button(app, text="GRAVAR", command=gravar)
bt3.place(x=150, y=350)

# botão excluir
bt4 = Button(app, text="EXCLUIR")
bt4.place(x=210, y=350)

# botão sair
bt5 = Button(app, text="SAIR", bg="red", command=quit)
bt5.place(x=750, y=350)

# entrada de dados brinco
entrada1 = Entry(app).place(x=150, y=80, width=300, height=20)

# entrada de dados cor
entrada2 = Entry(app).place(x=150, y=130, width=300, height=20)

# entrada de dados sexo
entrad3 = Entry(app).place(x=150, y=180, width=300, height=20)

# entrada de dados tipo
entrada4 = Entry(app).place(x=150, y=230, width=300, height=20)

# entrada de dados peso
entrada5 = Entry(app).place(x=150, y=280, width=300, height=20)

app.mainloop()