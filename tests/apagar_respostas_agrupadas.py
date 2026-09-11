import pyautogui
import webbrowser
import time
import pyperclip
import os
import csv
import sys

# --- CONFIGURAÇÕES GLOBAIS ---
# Coordenadas para clicar e focar na janela do navegador
CLICK_X = 2764
CLICK_Y = 381

# Coordenadas para clicar em um espaço seguro DENTRO da página de resposta com PDF
CLICK_SEGURO_X = 2916
CLICK_SEGURO_Y = 311

# Coordenadas do botão de apagar em páginas com visualizador de PDF
CLICK_APAGAR_PDF_X = 3110
CLICK_APAGAR_PDF_Y = 667

TEMPO_DE_ESPERA_PAGINA = 3
PASTA_DB = "db"
PASTA_TX = "tx"

# --- FUNÇÕES DE CARREGAMENTO E MENUS ---

def carregar_usuarios(nome_arquivo=os.path.join(PASTA_DB, "grupo.csv")):
    """Lê o arquivo de usuários no formato CSV."""
    try:
        with open(nome_arquivo, mode='r', encoding='utf-8', newline='') as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        print(f"ERRO CRÍTICO: O arquivo de usuários '{nome_arquivo}' não foi encontrado!")
        sys.exit()

def carregar_links_txt(caminho_arquivo):
    """Lê os arquivos de links no formato TXT e retorna uma lista de tarefas."""
    tarefas = []
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read().split('Titulo: ')
            for bloco in conteudo:
                if 'link: ' not in bloco:
                    continue
                
                partes = bloco.split('link: ')
                # Limpa o título para garantir a correspondência
                titulo = " ".join(partes[0].strip().split())
                # Limpa o link para remover caracteres invisíveis
                link = partes[1].strip().split()[0]
                
                if titulo and link:
                    tarefas.append({'titulo': titulo, 'link': link})
        return tarefas
    except FileNotFoundError:
        print(f"ERRO CRÍTICO: O arquivo de links '{caminho_arquivo}' não foi encontrado!")
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

def selecionar_modo_apagar():
    """Menu para escolher qual tipo de resposta apagar."""
    print("\n--- QUAL TIPO DE RESPOSTA DESEJA APAGAR? ---")
    print("[1] - Requisitos SEM anexo de PDF (Classes Agrupadas)")
    print("[2] - Requisitos COM anexo de PDF (Classes Agrupadas)")
    while True:
        try:
            escolha = int(input("Digite o número do modo: "))
            if escolha in [1, 2]:
                return escolha
            else:
                print("Número inválido.")
        except ValueError:
            print("Entrada inválida. Digite um número.")

# --- FUNÇÕES DE AUTOMAÇÃO ---

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

def apagar_respostas_simples(tarefas):
    """Loop para apagar respostas de texto, com confirmação individual."""
    print("\n--- INICIANDO EXCLUSÃO DE RESPOSTAS DE TEXTO ---")
    total = len(tarefas)
    apagados = 0
    for i, tarefa in enumerate(tarefas):
        print("-" * 50)
        print(f"Item {i+1}/{total}: {tarefa['titulo']}")
        webbrowser.open(tarefa['link'], new=2); time.sleep(TEMPO_DE_ESPERA_PAGINA)
        
        # Lógica corrigida para evitar foco no visualizador de PDF
        pyautogui.click(CLICK_SEGURO_X, CLICK_SEGURO_Y); time.sleep(0.3)
        pyautogui.press('pgdn'); time.sleep(0.5)
        pyautogui.click(CLICK_APAGAR_PDF_X, CLICK_APAGAR_PDF_Y)
        print("   ...Ação de apagar enviada.")
        apagados += 1
        time.sleep(1)
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
        
        # Lógica corrigida para evitar foco no visualizador de PDF
        pyautogui.click(CLICK_SEGURO_X, CLICK_SEGURO_Y); time.sleep(0.3)
        pyautogui.press('pgdn'); time.sleep(0.5)
        pyautogui.click(CLICK_APAGAR_PDF_X, CLICK_APAGAR_PDF_Y)
        print("   ...Ação de apagar enviada.")
        apagados += 1
        time.sleep(1)
        pyautogui.hotkey('ctrl', 'w')
        time.sleep(1)
    return apagados

# --- FLUXO PRINCIPAL ---
if __name__ == "__main__":
    print("="*60)
    print("ATENÇÃO: ESTE SCRIPT REALIZA AÇÕES DE EXCLUSÃO PERMANENTE.")
    print("Use para as Classes Agrupadas (arquivos TXT).")
    print("="*60)
    
    confirmacao_geral = input("Digite 'SIM' para continuar com o processo de exclusão: ")
    
    if confirmacao_geral != 'SIM':
        print("Processo cancelado pelo usuário. Encerrando.")
        sys.exit()

    inicio = time.time()
    
    usuarios = carregar_usuarios()
    usuario_escolhido = selecionar_usuario(usuarios)
    trocar_usuario(usuario_escolhido)
    
    modo_escolhido = selecionar_modo_apagar()
    
    if modo_escolhido == 1:
        caminho_links = os.path.join(PASTA_TX, "links.txt")
        tarefas_para_apagar = carregar_links_txt(caminho_links)
        total_apagado = apagar_respostas_simples(tarefas_para_apagar)
    else: # modo_escolhido == 2
        caminho_links = os.path.join(PASTA_TX, "links-pdfs.txt")
        tarefas_para_apagar = carregar_links_txt(caminho_links)
        total_apagado = apagar_respostas_pdf(tarefas_para_apagar)

    fim = time.time()
    print("\n" + "="*50)
    print(f"Processo de exclusão finalizado. {total_apagado} itens foram apagados.")
    duracao = fim - inicio
    minutos = int(duracao // 60)
    segundos = int(duracao % 60)
    print(f"Duração total: {minutos} min {segundos} s")
    print("="*50)
