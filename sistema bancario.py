import os
import re
from time import sleep

# Variáveis globais
nome_ADM = "AdMiN"
senha_ADM = "AdminPython123"

cpf_loggin = []
senha_loggin = []
saldos = [] 
investimentos = []
historico_transacoes = []


def limpar_tela():
    try:
        if os.name == "nt":
            os.system("cls")
    except Exception:
        print("\n" * 100)


def menu():
    limpar_tela()
    print("\n" * 100)
    print("1 - Entrar")
    print("2 - Criar conta")
    print("3 - Entrar como ADM")
    print("4 - Resumo da conta")
    print("5 - Sair")
    
    try:
        perguntadeentrada = int(input("Escolha uma opção: "))
        if perguntadeentrada == 1:
            entrar()
        elif perguntadeentrada == 2:
            criarconta()
        elif perguntadeentrada == 3:
            entrar_ADM()
        elif perguntadeentrada == 4:
            resumo_conta()
        elif perguntadeentrada == 5:
            print("Encerrando o programa...")
            exit()
        else:
            print("Opção inválida. Tente novamente.")
            menu()
    except ValueError:
        print("Por favor, insira um número válido.")
        menu()


def criarconta():
    while True:
        print("Digite 'Z' para sair")
        cpf = input("Digite o seu CPF: ").lower().strip()
        
        if cpf == "z":
            print("Encerrando o programa...")
            exit()
        
        if cpf in cpf_loggin:
            print("Esse CPF já está cadastrado. Tente novamente.")
        else:
            cpf_loggin.append(cpf)
            print("Digite a sua nova senha:")
            senha = input()
            
            if re.fullmatch(r'^(?=.*[A-Z])(?=.*\d).{8,}$', senha):
                senha_loggin.append(senha)
                saldos.append(0.0)
                investimentos.append([])
                print("Conta criada com sucesso!")
                sleep(2)
                menu()
            else:
                print("Senha inválida. Deve ter ao menos 8 caracteres, 1 número e 1 letra maiúscula.")


def entrar():
    print("Digite 'Z' para sair")
    cpf = input("Digite seu CPF: ").lower().strip()
    
    if cpf == "z":
        print("Encerrando o programa...")
        exit()
    
    if cpf in cpf_loggin:
        index = cpf_loggin.index(cpf)
        senha = input("Digite sua senha: ")
        
        if senha == senha_loggin[index]:
            print("Login bem-sucedido!")
            sleep(2)
            menu_usuario(index)
        else:
            print("Senha incorreta. Tente novamente.")
            entrar()
    else:
        print("CPF não encontrado. Tente novamente.")
        entrar()


def entrar_ADM():
    cpf = input("Digite o CPF de ADM: ")
    senha = input("Digite a senha de ADM: ")
    
    if cpf == nome_ADM and senha == senha_ADM:
        print("Bem-vindo, Administrador!")
        sleep(2)
        print("Entrando como ADM...")
    else:
        print("Credenciais de ADM inválidas.")
        entrar_ADM()


def menu_usuario(index):
    while True:
        print("\nMenu do Usuário:")
        print("1 - Consultar Saldo")
        print("2 - Adicionar Saldo")
        print("3 - Transferir Dinheiro")
        print("4 - Investir")
        print("5 - Resumo da Conta")
        print("6 - Sair")
        
        try:
            opcao = int(input("Escolha uma opção: "))
            if opcao == 1:
                consultar_saldo(index)
            elif opcao == 2:
                adicionar_saldo(index)
            elif opcao == 3:
                realizar_transferencia(index)
            elif opcao == 4:
                investimento(index)
            elif opcao == 5:
                resumo_conta(index)
            elif opcao == 6:
                print("Saindo...")
                sleep(2)
                menu()
            else:
                print("Opção inválida. Tente novamente.")
        except ValueError:
            print("Por favor, insira um número válido.")


def consultar_saldo(index):
    print(f"Seu saldo atual é: R${saldos[index]:.2f}")


def adicionar_saldo(index):
    try:
        valor = float(input("Digite o valor para adicionar: R$"))
        if valor > 0:
            saldos[index] += valor
            print(f"R${valor:.2f} adicionado com sucesso!")
        else:
            print("O valor deve ser positivo.")
    except ValueError:
        print("Por favor, insira um valor numérico.")


def realizar_transferencia(index):
    cpf_destino = input("Digite o CPF do destinatário: ").strip()
    
    if cpf_destino not in cpf_loggin:
        print("CPF não encontrado. Tente novamente.")
        return

    destino_index = cpf_loggin.index(cpf_destino)
    valor = float(input("Digite o valor que deseja transferir: R$"))
    
    if valor <= 0 or valor > saldos[index]:
        print("Saldo insuficiente ou valor inválido.")
        return

    print(f"Você está prestes a transferir R${valor:.2f} para o CPF {cpf_destino}.")
    confirmar = input("Deseja continuar? (S/N): ").strip().lower()
    
    if confirmar == "s":
        senha = input("Digite sua senha para confirmar a transferência: ").strip()
        if senha == senha_loggin[index]:
            saldos[index] -= valor
            saldos[destino_index] += valor
            print(f"Transferência de R${valor:.2f} realizada com sucesso!")
        else:
            print("Senha incorreta. Transferência cancelada.")
    else:
        print("Transferência cancelada.")


def investimento(index):
    print("1 - Realizar investimento")
    print("2 - Cancelar investimento")
    pergunta_investimento = input()
    
    if pergunta_investimento == "1":
        print("Digite o valor do investimento:")
        valor_investimento = float(input())
        
        if valor_investimento > saldos[index]:
            print("Saldo insuficiente.")
            return

        print("Escolha uma opção de investimento:")
        print("1 - Curto Prazo\n2 - Médio Prazo\n3 - Longo Prazo")
        opcao_inv = int(input())
        
        if opcao_inv == 1:
            print("Escolha o prazo:\n1 - 30 Dias\n2 - 60 Dias\n3 - 180 Dias")
            prazo = int(input())
            dias, taxa_cdi = (30, 0.9) if prazo == 1 else (60, 0.95) if prazo == 2 else (180, 1.0)
        elif opcao_inv == 2:
            print("Escolha o prazo:\n1 - 1 Ano\n2 - 2 Anos")
            prazo = int(input())
            dias, taxa_cdi = (365, 1.1) if prazo == 1 else (730, 1.2)
        elif opcao_inv == 3:
            print("Escolha o prazo:\n1 - 3 Anos\n2 - 5 Anos")
            prazo = int(input())
            dias, taxa_cdi = (1095, 1.25) if prazo == 1 else (1825, 1.3)
        else:
            print("Opção inválida.")
            return

        cdi_anual = 13.65 / 100
        rendimento = valor_investimento * ((1 + (cdi_anual * taxa_cdi)) ** (dias / 365) - 1)
        valor_final = valor_investimento + rendimento
        saldos[index] -= valor_investimento
        investimentos[index].append((valor_investimento, dias, taxa_cdi, valor_final))
        print(f"Investimento de R${valor_investimento:.2f} realizado com sucesso. Valor ao final do prazo: R${valor_final:.2f}.")

    elif pergunta_investimento == "2":
        print("Digite o valor para retirada:")
        valor_retirada = float(input())
        print("Digite a sua senha para realizar a operação:")
        senha_cancelarinv = input()

        if senha_cancelarinv == senha_loggin[index]:
            if valor_retirada <= sum(inv[3] for inv in investimentos[index]):
                saldos[index] += valor_retirada
                print(f"R${valor_retirada:.2f} retirados do investimento com sucesso.")
            else:
                print("Saldo insuficiente no investimento para realizar a retirada.")
        else:
            print("Senha incorreta.")


from datetime import datetime


def registrar_transacao(tipo, valor):
   
    transacao = {
        "tipo": tipo,
        "valor": valor,
        "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }
    historico_transacoes.append(transacao)


def exibir_historico():
    
    if not historico_transacoes:
        print("Nenhuma transação registrada ainda.")
        return
    
    print("Histórico de Transações:")
    print("-" * 40)
    for transacao in historico_transacoes:
        print(f"Tipo: {transacao['tipo']}")
        print(f"Valor: R$ {transacao['valor']:.2f}")
        print(f"Data/Hora: {transacao['data_hora']}")
        print("-" * 40)

def resumo_conta(index):
    limpar_tela()
    print(f"--- Resumo da Conta ---")
    print(f"CPF do usuário: {cpf_loggin[index]}")
    print(f"Saldo atual: R${saldos[index]:.2f}\n")
    
    
    print("Histórico de Transações:")
    if historico_transacoes:
        for transacao in historico_transacoes:
            if transacao["cpf"] == cpf_loggin[index]:  
                print(f"- Tipo: {transacao['tipo']}, Valor: R${transacao['valor']:.2f}, Data/Hora: {transacao['data_hora']}")
    else:
        print("Nenhuma transação registrada.\n")

    print("\nInvestimentos realizados:")
    if investimentos[index]:
        for i, inv in enumerate(investimentos[index], start=1):
            print(f"{i} - Valor: R${inv[0]:.2f}, Prazo: {inv[1]} dias, CDI: {inv[2]*100:.0f}%, Valor Final: R${inv[3]:.2f}")
    else:
        print("Nenhum investimento realizado.\n")
    
    print("\nPressione Enter para voltar ao menu do usuário...")
    input()

def registrar_transacao(tipo, valor, cpf):
    transacao = {
        "tipo": tipo,
        "valor": valor,
        "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "cpf": cpf
    }
    historico_transacoes.append(transacao)


menu()