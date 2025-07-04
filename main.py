# Como o código completo foi fornecido anteriormente em partes, vamos reorganizá-lo com melhorias visuais em todas as janelas.

import sqlite3
import csv
from tkinter import *
from tkinter import ttk, messagebox, simpledialog
from PIL import ImageTk, Image
from datetime import datetime

# Banco de dados
conexao = sqlite3.connect('presenca.db')
cursor = conexao.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS pessoas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    matricula TEXT UNIQUE NOT NULL,
    sessao TEXT
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS registros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pessoa_id INTEGER,
    tipo TEXT,
    data TEXT,
    hora TEXT,
    FOREIGN KEY(pessoa_id) REFERENCES pessoas(id)
)
''')
conexao.commit()

# Variáveis globais
senha_admin = "admin123"

def registrar_presenca(tipo):
    matricula = entry_matricula.get()
    if not matricula:
        messagebox.showwarning("Atenção", "Digite sua matrícula.")
        return

    cursor.execute("SELECT id FROM pessoas WHERE matricula=?", (matricula,))
    resultado = cursor.fetchone()
    if resultado:
        pessoa_id = resultado[0]
        agora = datetime.now()
        data = agora.strftime("%Y-%m-%d")
        hora = agora.strftime("%H:%M:%S")
        cursor.execute("INSERT INTO registros (pessoa_id, tipo, data, hora) VALUES (?, ?, ?, ?)",
                       (pessoa_id, tipo, data, hora))
        conexao.commit()
        messagebox.showinfo("Sucesso", f"{tipo} registrada com sucesso!")
    else:
        messagebox.showerror("Erro", "Matrícula não encontrada.")

def acesso_admin():
    senha = simpledialog.askstring("Autenticação", "Digite a senha do administrador:", show="*")
    if senha == senha_admin:
        janela_admin()
    else:
        messagebox.showerror("Erro", "Senha incorreta.")

def janela_admin():
    admin = Toplevel()
    admin.title("Área do Administrador")
    admin.geometry("450x350")
    admin.configure(bg="#f9f9f9")

    frame = Frame(admin, bg="#f9f9f9")
    frame.pack(pady=20)

    ttk.Label(frame, text="Área do Administrador", font=("Segoe UI", 14, "bold")).pack(pady=10)

    ttk.Button(frame, text="Cadastrar Pessoa", width=25, command=cadastrar_pessoa).pack(pady=5)
    ttk.Button(frame, text="Gerenciar Pessoas", width=25, command=gerenciar_pessoas).pack(pady=5)
    ttk.Button(frame, text="Ver Registros", width=25, command=ver_registros).pack(pady=5)
    ttk.Button(frame, text="Exportar CSV", width=25, command=exportar_csv).pack(pady=5)
    ttk.Button(frame, text="Status em Tempo Real", width=25, command=status_tempo_real).pack(pady=5)

def cadastrar_pessoa():
    def salvar():
        nome = entry_nome.get()
        matricula = entry_matricula_cadastro.get()
        sessao = entry_sessao.get()
        if nome and matricula:
            try:
                cursor.execute("INSERT INTO pessoas (nome, matricula, sessao) VALUES (?, ?, ?)",
                               (nome, matricula, sessao))
                conexao.commit()
                messagebox.showinfo("Sucesso", "Pessoa cadastrada!")
                janela.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("Erro", "Matrícula já cadastrada.")
        else:
            messagebox.showwarning("Atenção", "Preencha todos os campos.")

    janela = Toplevel()
    janela.title("Cadastrar Pessoa")
    janela.geometry("400x300")
    janela.configure(bg="#f9f9f9")

    frame = Frame(janela, bg="#f9f9f9")
    frame.pack(pady=20)

    ttk.Label(frame, text="Nome:").pack(pady=5)
    entry_nome = ttk.Entry(frame, width=30)
    entry_nome.pack()

    ttk.Label(frame, text="Matrícula:").pack(pady=5)
    entry_matricula_cadastro = ttk.Entry(frame, width=30)
    entry_matricula_cadastro.pack()

    ttk.Label(frame, text="Sessão (opcional):").pack(pady=5)
    entry_sessao = ttk.Entry(frame, width=30)
    entry_sessao.pack()

    ttk.Button(frame, text="Salvar", command=salvar).pack(pady=10)

def gerenciar_pessoas():
    janela = Toplevel()
    janela.title("Gerenciar Pessoas")
    janela.geometry("500x400")
    janela.configure(bg="#f9f9f9")

    def atualizar_lista():
        listbox.delete(0, END)
        cursor.execute("SELECT id, nome, matricula FROM pessoas")
        for id_, nome, matricula in cursor.fetchall():
            listbox.insert(END, f"{id_} - {nome} ({matricula})")

    def excluir():
        selecionado = listbox.get(ACTIVE)
        if not selecionado:
            return
        id_ = selecionado.split(" - ")[0]
        cursor.execute("DELETE FROM pessoas WHERE id=?", (id_,))
        conexao.commit()
        atualizar_lista()

    def editar():
        selecionado = listbox.get(ACTIVE)
        if not selecionado:
            return
        id_ = selecionado.split(" - ")[0]

        def salvar_edicao():
            novo_nome = entry_nome.get()
            nova_matricula = entry_matricula.get()
            nova_sessao = entry_sessao.get()
            cursor.execute("UPDATE pessoas SET nome=?, matricula=?, sessao=? WHERE id=?",
                           (novo_nome, nova_matricula, nova_sessao, id_))
            conexao.commit()
            atualizar_lista()
            editar_janela.destroy()

        cursor.execute("SELECT nome, matricula, sessao FROM pessoas WHERE id=?", (id_,))
        nome, matricula, sessao = cursor.fetchone()

        editar_janela = Toplevel()
        editar_janela.title("Editar Pessoa")
        editar_janela.geometry("400x250")
        editar_janela.configure(bg="#f9f9f9")

        ttk.Label(editar_janela, text="Nome:").pack(pady=5)
        entry_nome = ttk.Entry(editar_janela, width=30)
        entry_nome.insert(0, nome)
        entry_nome.pack()

        ttk.Label(editar_janela, text="Matrícula:").pack(pady=5)
        entry_matricula = ttk.Entry(editar_janela, width=30)
        entry_matricula.insert(0, matricula)
        entry_matricula.pack()

        ttk.Label(editar_janela, text="Sessão:").pack(pady=5)
        entry_sessao = ttk.Entry(editar_janela, width=30)
        entry_sessao.insert(0, sessao)
        entry_sessao.pack()

        ttk.Button(editar_janela, text="Salvar", command=salvar_edicao).pack(pady=10)

    listbox = Listbox(janela, width=60, height=15)
    listbox.pack(pady=10)

    btn_frame = Frame(janela, bg="#f9f9f9")
    btn_frame.pack()

    ttk.Button(btn_frame, text="Editar", command=editar).grid(row=0, column=0, padx=5)
    ttk.Button(btn_frame, text="Excluir", command=excluir).grid(row=0, column=1, padx=5)

    atualizar_lista()

def ver_registros():
    janela = Toplevel()
    janela.title("Registros de Presença")
    janela.geometry("600x400")

    tree = ttk.Treeview(janela, columns=("nome", "tipo", "data", "hora"), show="headings")
    tree.heading("nome", text="Nome")
    tree.heading("tipo", text="Tipo")
    tree.heading("data", text="Data")
    tree.heading("hora", text="Hora")
    tree.pack(fill=BOTH, expand=True)

    cursor.execute('''
    SELECT pessoas.nome, registros.tipo, registros.data, registros.hora
    FROM registros
    JOIN pessoas ON registros.pessoa_id = pessoas.id
    ORDER BY registros.data DESC, registros.hora DESC
    ''')
    for row in cursor.fetchall():
        tree.insert("", END, values=row)

def exportar_csv():
    with open("registros.csv", "w", newline="", encoding="utf-8") as arquivo:
        writer = csv.writer(arquivo)
        writer.writerow(["Nome", "Tipo", "Data", "Hora"])
        cursor.execute('''
        SELECT pessoas.nome, registros.tipo, registros.data, registros.hora
        FROM registros
        JOIN pessoas ON registros.pessoa_id = pessoas.id
        ''')
        for row in cursor.fetchall():
            writer.writerow(row)
    messagebox.showinfo("Exportação", "Registros exportados para registros.csv!")

def status_tempo_real():
    janela = Toplevel()
    janela.title("Status de Presença")
    janela.geometry("500x400")

    tree = ttk.Treeview(janela, columns=("nome", "status", "hora"), show="headings")
    tree.heading("nome", text="Nome")
    tree.heading("status", text="Status")
    tree.heading("hora", text="Hora")
    tree.pack(fill=BOTH, expand=True)

    cursor.execute("SELECT id, nome FROM pessoas")
    pessoas = cursor.fetchall()

    for pessoa_id, nome in pessoas:
        cursor.execute('''
        SELECT tipo, hora FROM registros
        WHERE pessoa_id=? AND data=?
        ORDER BY hora DESC LIMIT 1
        ''', (pessoa_id, datetime.now().strftime("%Y-%m-%d")))
        resultado = cursor.fetchone()
        if resultado:
            tipo, hora = resultado
            status = "Presente" if tipo == "Entrada" else "Ausente"
        else:
            status = "Sem registro"
            hora = "-"
        tree.insert("", END, values=(nome, status, hora))

# Janela Inicial
janela = Tk()
janela.title("Bem-vindo ao Sistema de Presença")
janela.geometry("400x500")
janela.configure(bg="#f0f0f0")

style = ttk.Style()
style.configure("TButton", font=("Segoe UI", 10), padding=6)
style.configure("TLabel", font=("Segoe UI", 11))
style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"))

frame = Frame(janela, bg="#f0f0f0")
frame.pack(pady=20)

try:
    imagem = Image.open("logo.png")
    imagem = imagem.resize((180, 180))
    img_logo = ImageTk.PhotoImage(imagem)
    Label(frame, image=img_logo, bg="#f0f0f0").pack(pady=10)
except:
    Label(frame, text="(Logo não carregado)", fg="red", bg="#f0f0f0", font=("Segoe UI", 10)).pack()

ttk.Label(frame, text="Bem-vindo!", style="Header.TLabel").pack(pady=(10, 5))
ttk.Label(frame, text="Este sistema permite registrar sua entrada e saída.\nClique para começar.", justify="center").pack(pady=5)

def abrir_registro():
    janela.destroy()
    global entry_matricula
    janela_registro = Tk()
    janela_registro.geometry("450x300")
    janela_registro.title("Registro de Presença")
    janela_registro.configure(bg="#f9f9f9")

    frame = Frame(janela_registro, bg="#f9f9f9")
    frame.pack(pady=20)

    ttk.Label(frame, text="Digite sua matrícula:", font=("Segoe UI", 11)).pack(pady=(10, 5))
    entry_matricula = ttk.Entry(frame)
    entry_matricula.pack(pady=5, ipady=3, ipadx=30)

    ttk.Button(frame, text="Registrar Entrada", command=lambda: registrar_presenca("Entrada")).pack(pady=5, fill=X)
    ttk.Button(frame, text="Registrar Saída", command=lambda: registrar_presenca("Saída")).pack(pady=5, fill=X)
    ttk.Button(frame, text="Área do Administrador", command=acesso_admin).pack(pady=5, fill=X)

    janela_registro.mainloop()

ttk.Button(frame, text="Entrar", command=abrir_registro).pack(pady=15)

janela.mainloop()
