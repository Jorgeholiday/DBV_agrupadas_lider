import pyautogui
import webbrowser
import time
import pyperclip
import os
import subprocess
import sys
import csv

# --- CONFIGURAções GLOBAIS ---
CLICK_X = 2764
CLICK_Y = 381
TEMPO_DE_ESPERA_LOGIN = 5

# Nomes dos scripts de automação na ordem de execução
SCRIPTS_PARA_EXECUTAR = [
    "automatizar_respostas.py",
    "auto_resps_pdf.py"
]

# --- FUNÇÕES (As mesmas do script anterior para carregar e logar) ---

def carregar_usuarios(nome_arquivo=os.path.join("db", "grupo-1.csv")):
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

def trocar_usuario(usuario):
    """Executa a automação para preencher o formulário de troca de usuário."""
    url = "https://clubes.adventistas.org/br/personal-card/"
    
    print("\n" + "="*50)
    print(f"INICIANDO SESSÃO PARA O USUÁRIO: {usuario['nome'].upper()}")
    print("="*50)
    print("A automação do login começará em 5 segundos...")
    time.sleep(5)

    webbrowser.open(url, new=1)
    time.sleep(TEMPO_DE_ESPERA_LOGIN)

    pyautogui.click(CLICK_X, CLICK_Y)
    time.sleep(0.5)

    # Preenchimento dos dados
    pyautogui.press('tab'); time.sleep(0.2); pyperclip.copy(usuario['código']); pyautogui.hotkey('ctrl', 'v')
    print(f"- Código preenchido.")
    pyautogui.press('tab'); time.sleep(0.2); pyperclip.copy(usuario['e-mail']); pyautogui.hotkey('ctrl', 'v')
    print(f"- E-mail preenchido.")
    pyautogui.press('tab'); time.sleep(0.2); pyperclip.copy(usuario['ano']); pyautogui.hotkey('ctrl', 'v')
    print(f"- Ano preenchido.")
    
    pyautogui.press('tab')
    time.sleep(0.5)
    
    # IMPORTANTE: A ação de entrar deve estar ATIVADA para o fluxo funcionar
    pyautogui.press('enter') 
    print("- Botão 'Entrar' pressionado.")
    print("Login realizado! Aguardando 5 segundos para a página carregar...")
    time.sleep(5)

def executar_script(nome_script):
    """Chama e executa um script de automação."""
    print(f"\n--- EXECUTANDO SCRIPT: '{nome_script}' ---")
    try:
        subprocess.run([sys.executable, nome_script], check=True)
        print(f"--- SCRIPT '{nome_script}' CONCLUÍDO. ---")
    except FileNotFoundError:
        print(f"\nERRO FATAL: O script '{nome_script}' não foi encontrado na pasta 'main'.")
    except subprocess.CalledProcessError:
        print(f"\nERRO: O script '{nome_script}' foi encerrado com um erro.")

# --- FLUXO PRINCIPAL DE AUTOMAÇÃO TOTAL ---
if __name__ == "__main__":
    # <<< 1. MARQUE O TEMPO DE INÍCIO AQUI
    inicio = time.time()
    print(f"Início da automação total: {time.strftime('%H:%M:%S', time.localtime(inicio))}")

    lista_usuarios = carregar_usuarios()
    
    if not lista_usuarios:
        print("Nenhum usuário encontrado em 'grupo.csv'. Encerrando.")
    else:
        print(f"Automação total iniciada. {len(lista_usuarios)} usuário(s) serão processados.")
        
        # Loop principal que itera sobre cada usuário
        for i, usuario_atual in enumerate(lista_usuarios):
            # 1. Troca o usuário (faz o login)
            trocar_usuario(usuario_atual)
            
            # 2. Executa todos os scripts da lista para o usuário atual
            for nome_do_script in SCRIPTS_PARA_EXECUTAR:
                executar_script(nome_do_script)
            
            print(f"\nTAREFAS CONCLUÍDAS PARA {usuario_atual['nome'].upper()} ({i+1}/{len(lista_usuarios)})")

        # <<< 2. CALCULE E MOSTRE O TEMPO TOTAL AQUI
        fim = time.time()
        print("\n" + "="*50)
        print(f"Fim da automação total: {time.strftime('%H:%M:%S', time.localtime(fim))}")
        duracao = fim - inicio
        minutos = int(duracao // 60)
        segundos = int(duracao % 60)
        print(f"Duração total do processo: {minutos} min {segundos} s")
        print("="*50)

        print("\n\n>>> FIM DO PROCESSO DE AUTOMAÇÃO TOTAL. TODOS OS USUÁRIOS FORAM PROCESSADOS. <<<")