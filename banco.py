import os
import re
from time import sleep
import sqlite3
from datetime import datetime
from sys import exit
import bcrypt

# Conexão com o banco de dados
conn = sqlite3.connect("banco.db")
cursor = conn.cursor()

# Criação das tabelas
cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cpf TEXT UNIQUE NOT NULL,
        nome TEXT,
        saldo REAL DEFAULT 0,
        senha TEXT NOT NULL,
        investimentos REAL DEFAULT 0
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS investimentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cpf_investidor TEXT NOT NULL,
        tipo_investimento TEXT NOT NULL,
        valor_final REAL NOT NULL,
        valor_investido REAL NOT NULL,
        data_hora TEXT NOT NULL,
        FOREIGN KEY (cpf_investidor) REFERENCES usuarios(cpf)
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS transacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cpf_origem TEXT,
        cpf_destino TEXT,
        valor REAL,
        tipo TEXT,
        data_hora TEXT,
        FOREIGN KEY (cpf_origem) REFERENCES usuarios(cpf),
        FOREIGN KEY (cpf_destino) REFERENCES usuarios(cpf)
    );
""")

conn.commit()

def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")

def menu():
    while True:
        limpar_tela()
        print("1 - Entrar")
        print("2 - Criar conta")
        print("3 - Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            entrar()
        elif opcao == "2":
            criar_conta()
        elif opcao == "3":
            print("Encerrando o programa...")
            conn.close()
            exit()
        else:
            print("Opção inválida. Tente novamente.")
            sleep(2)

def criar_conta():
    limpar_tela()
    print("--- Criar Conta ---")

    cpf = input("Digite o CPF (somente números): ").strip()
    if not cpf.isdigit() or len(cpf) != 11:
        print("CPF inválido. Certifique-se de que possui 11 dígitos.")
        sleep(2)
        return

    cursor.execute("SELECT * FROM usuarios WHERE cpf = ?", (cpf,))

    if cursor.fetchone():
        print("CPF já cadastrado.")
        sleep(2)
        return

    nome = input("Digite seu nome: ").strip()
    senha = input("Crie uma senha (mínimo 8 caracteres, 1 número, 1 maiúscula): ").strip()

    if not re.fullmatch(r'^(?=.*[A-Z])(?=.*\d).{8,}$', senha):
        print("Senha inválida.")
        sleep(2)
        return

    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())

    cursor.execute("INSERT INTO usuarios (cpf, nome, senha) VALUES (?, ?, ?)", (cpf, nome, senha_hash))
    conn.commit()

    print("Conta criada com sucesso!")
    sleep(2)

def entrar():
    limpar_tela()
    print("--- Entrar ---")

    cpf = input("Digite seu CPF: ").strip()
    senha = input("Digite sua senha: ").strip()

    cursor.execute("SELECT * FROM usuarios WHERE cpf = ?", (cpf,))
    usuario = cursor.fetchone()

    if usuario and bcrypt.checkpw(senha.encode(), usuario[4].encode()):
        print(f"Bem-vindo(a), {usuario[2]}!")
        sleep(2)
        menu_usuario(cpf)
    else:
        print("CPF ou senha inválidos.")
        sleep(2)

def menu_usuario(cpf):
    while True:
        limpar_tela()
        print("1 - Consultar Saldo")
        print("2 - Adicionar Saldo")
        print("3 - Realizar Transferência")
        print("4 - Histórico de Transações")
        print("5 - Investimentos")
        print("6 - Resumo da Conta")
        print("7 - Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            consultar_saldo(cpf)
        elif opcao == "2":
            adicionar_saldo(cpf)
        elif opcao == "3":
            realizar_transferencia(cpf)
        elif opcao == "4":
            historico_transacoes(cpf)
        elif opcao == "5":
            investimentos(cpf)
        elif opcao == "6":
            resumo_conta(cpf)
        elif opcao == "7":
            break
        else:
            print("Opção inválida.")
            sleep(2)

def consultar_saldo(cpf):
    cursor.execute("SELECT saldo FROM usuarios WHERE cpf = ?", (cpf,))
    saldo = cursor.fetchone()[0]
    print(f"Seu saldo atual é: R${saldo:.2f}")
    input("Pressione Enter para voltar.")

def adicionar_saldo(cpf):
    try:
        valor = float(input("Digite o valor para adicionar: "))
        if valor <= 0:
            raise ValueError

        cursor.execute("UPDATE usuarios SET saldo = saldo + ? WHERE cpf = ?", (valor, cpf))
        conn.commit()
        print(f"R${valor:.2f} adicionados com sucesso.")
        sleep(2)
    except ValueError:
        print("Valor inválido.")
        sleep(2)

def realizar_transferencia(cpf_origem):
    try:
        cpf_destino = input("Digite o CPF do destinatário: ").strip()
        valor = float(input("Digite o valor a transferir: "))

        if valor <= 0:
            raise ValueError("O valor deve ser maior que zero.")

        cursor.execute("SELECT saldo FROM usuarios WHERE cpf = ?", (cpf_origem,))
        saldo_origem = cursor.fetchone()[0]

        if saldo_origem < valor:
            print("Saldo insuficiente.")
            sleep(2)
            return

        cursor.execute("SELECT * FROM usuarios WHERE cpf = ?", (cpf_destino,))
        if not cursor.fetchone():
            print("CPF do destinatário não encontrado.")
            sleep(2)
            return

        cursor.execute("UPDATE usuarios SET saldo = saldo - ? WHERE cpf = ?", (valor, cpf_origem))
        cursor.execute("UPDATE usuarios SET saldo = saldo + ? WHERE cpf = ?", (valor, cpf_destino))

        cursor.execute("INSERT INTO transacoes (cpf_origem, cpf_destino, valor, tipo, data_hora) VALUES (?, ?, ?, ?, ?)",
                       (cpf_origem, cpf_destino, valor, "Transferência", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()

        print("Transferência realizada com sucesso.")
        sleep(2)
    except ValueError as e:
        print(f"Erro: {e}")
        sleep(2)

def historico_transacoes(cpf):
    cursor.execute("SELECT * FROM transacoes WHERE cpf_origem = ? OR cpf_destino = ?", (cpf, cpf))
    transacoes = cursor.fetchall()

    if not transacoes:
        print("Nenhuma transação encontrada.")
    else:
        for transacao in transacoes:
            tipo = "Enviado" if transacao[1] == cpf else "Recebido"
            print(f"{tipo}: R${transacao[3]:.2f} | {transacao[5]} | Destino: {transacao[2]}")

    input("Pressione Enter para voltar.")

def resumo_conta(cpf_usuario):
    cursor.execute("SELECT * FROM usuarios WHERE cpf = ?", (cpf_usuario,))
    usuario = cursor.fetchone()

    if not usuario:
        print("Usuário não encontrado.")
        return

    print(f"CPF: {usuario[1]}")
    print(f"Nome: {usuario[2]}")
    print(f"Saldo: R${usuario[3]:.2f}")

def investimentos(cpf):
    while True:
        limpar_tela()
        print("--- Menu de Investimentos ---")
        print("1 - Realizar Investimento")
        print("2 - Histórico de Investimentos")
        print("3 - Voltar")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            realizar_investimento(cpf)
        elif opcao == "2":
            historico_investimentos(cpf)
        elif opcao == "3":
            break
        else:
            print("Opção inválida.")
            sleep(2)

def realizar_investimento(cpf):
    try:
        tipo = input("Digite o tipo de investimento: ").strip()
        valor = float(input("Digite o valor a investir: "))


        if valor <= 0 and saldo_atual < valor:
            raise ValueError("Saldo insuficiente.")

        cursor.execute("SELECT saldo FROM usuarios WHERE cpf = ?", (cpf,))
        saldo_atual = cursor.fetchone()[0]

        valor_final = valor * 1.1 

        cursor.execute("UPDATE usuSarios SET saldo = saldo - ? WHERE cpf = ?", (valor, cpf))
        cursor.execute("INSERT INTO investimentos (cpf_investidor, tipo_investimento, valor_final, valor_investido, data_hora) VALUES (?, ?, ?, ?, ?)",
                       (cpf, tipo, valor_final, valor, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()

        print(f"Investimento de R${valor:.2f} realizado com sucesso. Valor final estimado: R${valor_final:.2f}")
        sleep(2)
    except ValueError as e:
        print(f"Erro: {e}")
        sleep(2)

def historico_investimentos(cpf):
    cursor.execute("SELECT tipo_investimento, valor_investido, valor_final, data_hora FROM investimentos WHERE cpf_investidor = ?", (cpf,))
    investimentos = cursor.fetchall()

    if not investimentos:
        print("Nenhum investimento encontrado.")
    else:
        for investimento in investimentos:
            print(f"Tipo: {investimento[0]} | Valor Investido: R${investimento[1]:.2f} | Valor Final: R${investimento[2]:.2f} | Data: {investimento[3]}")

    input("Pressione Enter para voltar.")

menu()
