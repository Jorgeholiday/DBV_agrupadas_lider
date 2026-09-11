import pyautogui
import webbrowser
import time
import os
import csv
import sys

import pyperclip

# --- CONFIGURAÇÕES GLOBAIS ---
CLICK_X = 2764  # Posição segura para focar na janela
CLICK_Y = 381
TEMPO_DE_ESPERA_PAGINA = 3
PASTA_DADOS = "db"

# Coordenadas específicas para o botão de apagar em páginas com PDF
CLICK_APAGAR_PDF_X = 3013
CLICK_APAGAR_PDF_Y = 676

# NOVAS COORDENADAS PARA O CLIQUE SEGURO DENTRO DA PÁGINA
CLICK_SEGURO_X = 2916
CLICK_SEGURO_Y = 311

# --- FUNÇÕES REUTILIZADAS ---

def carregar_csv(caminho_csv):
    """Função genérica para carregar arquivos CSV."""
    try:
        with open(caminho_csv, mode='r', encoding='utf-8', newline='') as f:
            leitor = csv.DictReader(f)
            return list(leitor)
    except FileNotFoundError:
        print(f"ERRO CRÍTICO: O arquivo '{caminho_csv}' não foi encontrado!")
        sys.exit()

def selecionar_usuario(usuarios):
    """Exibe um menu para o usuário escolher um perfil."""
    print("\n--- SELECIONE O USUÁRIO ---")
    for i, usuario in enumerate(usuarios):
        print(f"[{i + 1}] - {usuario['nome']}")
    while True:
        try:
            escolha = int(input("Digite o número do usuário: "))
            if 1 <= escolha <= len(usuarios):
                return usuarios[escolha - 1]
            else:
                print("Número inválido.")
        except ValueError:
            print("Entrada inválida. Digite um número.")

def trocar_usuario(usuario):
    """Executa a automação de login."""
    url = "https://clubes.adventistas.org/br/personal-card/"
    print(f"\n--- FAZENDO LOGIN COMO: {usuario['nome'].upper()} ---")
    time.sleep(2)
    webbrowser.open(url, new=1)
    time.sleep(TEMPO_DE_ESPERA_PAGINA + 2)
    pyautogui.click(CLICK_X, CLICK_Y); time.sleep(0.5)
    pyautogui.press('tab'); time.sleep(0.2); pyperclip.copy(usuario['codigo']); pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('tab'); time.sleep(0.2); pyperclip.copy(usuario['email']); pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('tab'); time.sleep(0.2); pyperclip.copy(usuario['ano']); pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('tab'); time.sleep(0.5)
    pyautogui.press('enter')
    print("Login realizado com sucesso! Aguardando...")
    time.sleep(5)

# --- NOVAS FUNÇÕES DE EXCLUSÃO ---

def selecionar_modo_apagar():
    """Menu para escolher qual tipo de resposta apagar."""
    print("\n--- QUAL TIPO DE RESPOSTA DESEJA APAGAR? ---")
    print("[1] - Requisitos SEM anexo de PDF (Respostas de texto)")
    print("[2] - Requisitos COM anexo de PDF (Upload de arquivo)")
    while True:
        try:
            escolha = int(input("Digite o número do modo: "))
            if escolha in [1, 2]:
                return escolha
            else:
                print("Número inválido.")
        except ValueError:
            print("Entrada inválida. Digite um número.")

def apagar_respostas_simples(tarefas):
    """Loop para apagar respostas de texto, com confirmação individual."""
    print("\n--- INICIANDO EXCLUSÃO DE RESPOSTAS DE TEXTO ---")
    total = len(tarefas)
    apagados = 0
    for i, tarefa in enumerate(tarefas):
        print("-" * 50)
        print(f"Item {i+1}/{total}: {tarefa['titulo']}")
        webbrowser.open(tarefa['link'], new=2); time.sleep(TEMPO_DE_ESPERA_PAGINA)
        pyautogui.click(CLICK_X, CLICK_Y); time.sleep(0.2)
            
            # Lógica de 5 TABS
        pyautogui.press('tab', presses=5, interval=0.2)
        pyautogui.press('enter')
        print("   ...Ação de apagar enviada.")
        apagados += 1
        time.sleep(1.5) # Espera solicitada
        pyautogui.hotkey('ctrl', 'w')
        time.sleep(1)
    return apagados

def apagar_respostas_pdf(tarefas):
    """Loop para apagar respostas com PDF, com confirmação individual."""
    print("\n--- INICIANDO EXCLUSÃO DE RESPOSTAS COM PDF ---")
    total = len(tarefas)
    apagados = 0
    for i, tarefa in enumerate(tarefas):
        print("-" * 50)
        print(f"Item {i+1}/{total}: {tarefa['titulo']}")
        
        webbrowser.open(tarefa['link'], new=2); time.sleep(TEMPO_DE_ESPERA_PAGINA)
        
        # --- LÓGICA CORRIGIDA ---
        # 1. Clica em um local seguro para focar na página principal
        pyautogui.click(CLICK_SEGURO_X, CLICK_SEGURO_Y)
        time.sleep(0.3)
        
        # 2. Usa Page Down para rolar a página
        pyautogui.press('pgdn')
        time.sleep(0.5)
        
        # 3. Clica no botão de apagar por coordenada
        pyautogui.click(CLICK_APAGAR_PDF_X, CLICK_APAGAR_PDF_Y)
        # --- FIM DA CORREÇÃO ---
        print("   ...Ação de apagar enviada.")
        apagados += 1
        time.sleep(1) # Pequena pausa antes de fechar
        pyautogui.hotkey('ctrl', 'w')
        time.sleep(1)
    return apagados

# --- FLUXO PRINCIPAL ---
if __name__ == "__main__":
    print("="*60)
    print("ATENÇÃO: ESTE SCRIPT REALIZA AÇÕES DE EXCLUSÃO PERMANENTE.")
    print("Certifique-se de que o navegador está visível e na tela correta.")
    print("="*60)
    
    confirmacao_geral = input("Digite 'SIM' para continuar com o processo de exclusão: ")
    
    if confirmacao_geral != 'SIM':
        print("Processo cancelado pelo usuário. Encerrando.")
        sys.exit()

    inicio = time.time()
    
    caminho_grupos = os.path.join(PASTA_DADOS, "grupo.csv")
    usuarios = carregar_csv(caminho_grupos)
    
    usuario_escolhido = selecionar_usuario(usuarios)
    trocar_usuario(usuario_escolhido)
    
    modo_escolhido = selecionar_modo_apagar()
    
    if modo_escolhido == 1:
        tarefas_para_apagar = carregar_csv(os.path.join(PASTA_DADOS, "links-lider.csv"))
        total_apagado = apagar_respostas_simples(tarefas_para_apagar)
    else: # modo_escolhido == 2
        tarefas_para_apagar = carregar_csv(os.path.join(PASTA_DADOS, "links-lider-pdf.csv"))
        total_apagado = apagar_respostas_pdf(tarefas_para_apagar)

    fim = time.time()
    print("\n" + "="*50)
    print(f"Processo de exclusão finalizado. {total_apagado} itens foram apagados.")
    duracao = fim - inicio
    minutos = int(duracao // 60)
    segundos = int(duracao % 60)
    print(f"Duração total: {minutos} min {segundos} s")
    print("="*50)
