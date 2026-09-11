import pyautogui
import webbrowser
import time
import pyperclip
import os
import subprocess # Para executar outros scripts
import sys # Para encontrar o executável do Python
import csv

# --- CONFIGURAÇÕES ---
# Coordenadas para clicar em um espaço seguro e focar na janela
CLICK_X = 2764
CLICK_Y = 381
TEMPO_DE_ESPERA_PAGINA = 4 # Aumentei um pouco para garantir o carregamento

# Nomes dos scripts de automação
SCRIPT_RESPOSTAS = "automatizar_respostas.py"
SCRIPT_PDFS = "auto_resps_pdf.py"

# --- FUNÇÕES ---

def carregar_usuarios(nome_arquivo=os.path.join("db", "grupo.csv")):
    """Lê e processa o arquivo de usuários no formato CSV."""
    usuarios = []
    try:
        # Abre o arquivo CSV com encoding utf-8 para lidar com acentos
        with open(nome_arquivo, mode='r', encoding='utf-8', newline='') as f:
            # DictReader lê cada linha como um dicionário
            leitor_csv = csv.DictReader(f)
            for linha in leitor_csv:
                # Renomeia as chaves para corresponder ao que o resto do script espera
                usuario_formatado = {
                    'nome': linha['nome'],
                    'código': linha['codigo'],
                    'e-mail': linha['email'],
                    'ano': linha['ano']
                }
                usuarios.append(usuario_formatado)
        return usuarios
    except FileNotFoundError:
        print(f"ERRO: O arquivo '{nome_arquivo}' não foi encontrado!")
        return None

def selecionar_usuario(usuarios):
    """Exibe um menu para o usuário escolher um perfil."""
    print("\n--- SELECIONE O USUÁRIO PARA A AUTOMAÇÃO ---")
    for i, usuario in enumerate(usuarios):
        print(f"[{i + 1}] - {usuario['nome']}")
    
    while True:
        try:
            escolha = int(input("Digite o número do usuário desejado: "))
            if 1 <= escolha <= len(usuarios):
                return usuarios[escolha - 1]
            else:
                print("Número inválido. Tente novamente.")
        except ValueError:
            print("Entrada inválida. Por favor, digite um número.")

def selecionar_script():
    """Exibe um menu para escolher qual script de automação rodar."""
    print("\n--- QUAL AUTOMAÇÃO VOCÊ DESEJA EXECUTAR? ---")
    print(f"[1] - Apenas Respostas (Script: {SCRIPT_RESPOSTAS})")
    print(f"[2] - Respostas com PDF (Script: {SCRIPT_PDFS})")

    while True:
        try:
            escolha = int(input("Digite o número da automação desejada: "))
            if escolha == 1:
                return SCRIPT_RESPOSTAS
            elif escolha == 2:
                return SCRIPT_PDFS
            else:
                print("Número inválido. Tente novamente.")
        except ValueError:
            print("Entrada inválida. Por favor, digite um número.")

def trocar_usuario(usuario):
    """Executa a automação para preencher o formulário de troca de usuário."""
    url = "https://clubes.adventistas.org/br/personal-card/"
    
    print(f"\n--- TROCANDO PARA O USUÁRIO: {usuario['nome'].upper()} ---")
    print("A automação do login começará em 5 segundos...")
    time.sleep(5)

    webbrowser.open(url, new=1)
    time.sleep(TEMPO_DE_ESPERA_PAGINA)

    # Preenchimento
    pyautogui.click(CLICK_X, CLICK_Y)
    time.sleep(0.5)

    # Usar pyperclip (copiar e colar) é mais confiável que pyautogui.write
    # 1. Código
    pyautogui.press('tab')
    time.sleep(0.2)
    pyperclip.copy(usuario['código'])
    pyautogui.hotkey('ctrl', 'v')
    print(f"- Código preenchido.")

    # 2. E-mail
    pyautogui.press('tab')
    time.sleep(0.2)
    pyperclip.copy(usuario['e-mail'])
    pyautogui.hotkey('ctrl', 'v')
    print(f"- E-mail preenchido.")

    # 3. Ano
    pyautogui.press('tab')
    time.sleep(0.2)
    pyperclip.copy(usuario['ano'])
    pyautogui.hotkey('ctrl', 'v')
    print(f"- Ano preenchido.")

    # 4. Botão Entrar
    pyautogui.press('tab')
    time.sleep(0.5)
    
    pyautogui.press('enter') # DESCOMENTE PARA CLICAR EM "ENTRAR"
    #print("- AÇÃO DE ENTRAR ESTÁ DESATIVADA PARA TESTES.")
    print("Login realizado com sucesso! Aguardando 5 segundos para a página carregar...")
    time.sleep(5)

def executar_script(nome_script):
    """Chama e executa o script de automação escolhido."""
    print(f"\n--- INICIANDO O SCRIPT '{nome_script}' ---")
    try:
        # sys.executable garante que estamos usando o mesmo interpretador Python
        # check=True faz o script parar se o processo chamado der erro
        subprocess.run([sys.executable, nome_script], check=True)
        print(f"\n--- SCRIPT '{nome_script}' CONCLUÍDO COM SUCESSO! ---")
    except FileNotFoundError:
        print(f"\nERRO FATAL: O script '{nome_script}' não foi encontrado na pasta 'main'.")
    except subprocess.CalledProcessError:
        print(f"\nERRO: O script '{nome_script}' foi encerrado com um erro.")

# --- FLUXO PRINCIPAL ---
if __name__ == "__main__":
    # 1. Registra o tempo de início
    inicio = time.time()
    print(f"Início da automação: {time.strftime('%H:%M:%S', time.localtime(inicio))}")

    lista_usuarios = carregar_usuarios()
    
    if lista_usuarios:
        usuario_escolhido = selecionar_usuario(lista_usuarios)
        script_escolhido = selecionar_script()
        
        trocar_usuario(usuario_escolhido)
        executar_script(script_escolhido)
        
        # 2. Calcula e exibe a duração total ao final do processo
        fim = time.time()
        print("\n" + "="*50)
        print(f"Fim da automação: {time.strftime('%H:%M:%S', time.localtime(fim))}")
        duracao = fim - inicio
        minutos = int(duracao // 60)
        segundos = int(duracao % 60)
        print(f"Duração total do processo: {minutos} min {segundos} s")
        print("="*50)
        
        print("\n\n>>> TODO O PROCESSO DE AUTOMAÇÃO FOI FINALIZADO. <<<")