# base/agrupadas_orquestrador.py

import pyautogui
import webbrowser
import time
import pyperclip
import os
import subprocess
import sys

# --- CONFIGURAções GLOBAIS ---
CLICK_X = 2764
CLICK_Y = 381
TEMPO_DE_ESPERA_LOGIN = 5

# Nomes dos scripts de automação na ordem de execução
SCRIPTS_PARA_EXECUTAR = [
    "automatizar_respostas.py",
    "auto_resps_pdf.py"
]

# --- FUNÇÕES ---

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

    pyautogui.click(CLICK_X, CLICK_Y); time.sleep(0.5)

    pyautogui.press('tab'); time.sleep(0.2); pyperclip.copy(usuario['codigo']); pyautogui.hotkey('ctrl', 'v')
    print(f"- Código preenchido.")
    pyautogui.press('tab'); time.sleep(0.2); pyperclip.copy(usuario['email']); pyautogui.hotkey('ctrl', 'v')
    print(f"- E-mail preenchido.")
    pyautogui.press('tab'); time.sleep(0.2); pyperclip.copy(usuario['ano']); pyautogui.hotkey('ctrl', 'v')
    print(f"- Ano preenchido.")
    
    pyautogui.press('tab'); time.sleep(0.5)
    
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
        print(f"\nERRO FATAL: O script '{nome_script}' não foi encontrado.")
    except subprocess.CalledProcessError:
        print(f"\nERRO: O script '{nome_script}' foi encerrado com um erro.")

# --- FLUXO PRINCIPAL DE AUTOMAÇÃO ---
if __name__ == "__main__":
    # O script agora espera receber os dados do usuário como argumentos
    if len(sys.argv) != 5:
        print("ERRO: Este script deve ser chamado com os dados do usuário.")
        print("Uso: python agrupadas_orquestrador.py <nome> <codigo> <email> <ano>")
        sys.exit(1)

    # Monta o dicionário do usuário a partir dos argumentos
    usuario_atual = {
        "nome": sys.argv[1],
        "codigo": sys.argv[2],
        "email": sys.argv[3],
        "ano": sys.argv[4]
    }

    inicio = time.time()
    print(f"Início da automação para '{usuario_atual['nome']}': {time.strftime('%H:%M:%S', time.localtime(inicio))}")
    
    # 1. Troca o usuário (faz o login)
    trocar_usuario(usuario_atual)
    
    # 2. Executa todos os scripts da lista para o usuário atual
    for nome_do_script in SCRIPTS_PARA_EXECUTAR:
        executar_script(nome_do_script)
    
    print(f"\nTAREFAS CONCLUÍDAS PARA {usuario_atual['nome'].upper()}")

    fim = time.time()
    print("\n" + "="*50)
    duracao = fim - inicio
    minutos = int(duracao // 60)
    segundos = int(duracao % 60)
    print(f"Duração total do processo: {minutos} min {segundos} s")
    print("="*50)