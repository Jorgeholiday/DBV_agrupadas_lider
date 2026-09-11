import pyautogui
import webbrowser
import time
import pyperclip
import os
import csv
import sys

# --- CONFIGURAÇÕES GLOBAIS ---
CLICK_X = 2764 # Ajuste se necessário
CLICK_Y = 381  # Ajuste se necessário
TEMPO_DE_ESPERA_PAGINA = 3
PASTA_DADOS = "db"
PASTA_PDFS = "pdfs"

# --- FUNÇÕES DE CARREGAMENTO E MENUS ---

def carregar_csv(caminho_csv):
    """Função genérica para carregar qualquer um dos nossos arquivos CSV."""
    try:
        with open(caminho_csv, mode='r', encoding='utf-8', newline='') as f:
            leitor = csv.DictReader(f)
            return list(leitor)
    except FileNotFoundError:
        print(f"ERRO CRÍTICO: O arquivo '{caminho_csv}' não foi encontrado!")
        sys.exit() # Encerra o script se um arquivo essencial não for encontrado

def selecionar_usuario(usuarios):
    """Exibe um menu para o usuário escolher um perfil."""
    print("\n--- SELECIONE O USUÁRIO PARA A AUTOMAÇÃO ---")
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

def selecionar_modo():
    """Exibe um menu para escolher o tipo de automação."""
    print("\n--- QUAL TIPO DE REQUISITO DESEJA PREENCHER? ---")
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

# --- FUNÇÕES DE AUTOMAÇÃO ---

def trocar_usuario(usuario):
    """Executa a automação para preencher o formulário de troca de usuário."""
    url = "https://clubes.adventistas.org/br/personal-card/"
    print(f"\n--- TROCANDO PARA O USUÁRIO: {usuario['nome'].upper()} ---")
    print("A automação do login começará em 5 segundos...")
    time.sleep(5)

    webbrowser.open(url, new=1)
    time.sleep(TEMPO_DE_ESPERA_PAGINA + 1)

    pyautogui.click(CLICK_X, CLICK_Y); time.sleep(0.5)
    pyautogui.press('tab'); time.sleep(0.2); pyperclip.copy(usuario['codigo']); pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('tab'); time.sleep(0.2); pyperclip.copy(usuario['email']); pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('tab'); time.sleep(0.2); pyperclip.copy(usuario['ano']); pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('tab'); time.sleep(0.5)
    
    # IMPORTANTE: A linha abaixo clica em 'Entrar'. Mantenha-a ativa para o script funcionar.
    pyautogui.press('enter') 
    print("Login realizado com sucesso! Aguardando a página carregar...")
    time.sleep(5)

def preencher_formularios(tarefas, com_pdf=False):
    """Função principal que executa a automação de preenchimento."""
    if not tarefas:
        print("Nenhuma tarefa encontrada nos arquivos CSV para este modo.")
        return

    print("\n>>> ATENÇÃO: A automação dos requisitos começará em 5 segundos. <<<")
    print("NÃO MEXA NO MOUSE OU TECLADO APÓS O INÍCIO!")
    time.sleep(5)

    caminho_base_pdfs = os.path.abspath(PASTA_PDFS)
    total = len(tarefas)
    
    for i, tarefa in enumerate(tarefas):
        print(f"\n[Processando {i+1}/{total}] - {tarefa['titulo'][:60]}...")
        
        webbrowser.open(tarefa['link'], new=2); time.sleep(TEMPO_DE_ESPERA_PAGINA)
        pyautogui.click(CLICK_X, CLICK_Y); time.sleep(0.2)

        # Preenche Data
        pyautogui.press('tab'); time.sleep(0.15); pyperclip.copy(tarefa['data']); pyautogui.hotkey('ctrl', 'v')
        print("   - Data colada.")

        # Preenche Relatório
        pyautogui.press('tab'); time.sleep(0.15); pyperclip.copy(tarefa['relatorio']); pyautogui.hotkey('ctrl', 'v')
        print("   - Relatório colado.")
        
        if com_pdf:
            caminho_pdf = os.path.join(caminho_base_pdfs, tarefa['nome'])
            if not os.path.exists(caminho_pdf):
                print(f"   - ERRO: PDF não encontrado: {tarefa['nome']}. Pulando anexo.")
            else:
                pyautogui.press('tab'); time.sleep(0.4); pyautogui.press('enter'); time.sleep(1)
                pyperclip.copy(caminho_pdf); pyautogui.hotkey('ctrl', 'v'); time.sleep(0.5); pyautogui.press('enter')
                print(f"   - PDF anexado: {tarefa['nome']}")
                time.sleep(1)

        # Navega para o botão de Enviar/Salvar
        pyautogui.press('tab') # Foco em "Página anterior" (ou primeiro botão)
        pyautogui.press('tab') # Foco em "Enviar resposta/arquivo" (ou segundo botão)
        print("   - Foco no botão de enviar.")
        
        pyautogui.press('enter') # DESCOMENTE PARA ENVIAR O FORMULÁRIO
        #print("   - AÇÃO DE ENVIAR ESTÁ DESATIVADA.") 
        time.sleep(2)
        
        pyautogui.hotkey('ctrl', 'w')
        time.sleep(1)

# --- FLUXO PRINCIPAL ---
if __name__ == "__main__":
    inicio = time.time()
    print("--- INICIANDO AUTOMAÇÃO DA CLASSE DE LÍDER ---")

    # Carrega usuários
    caminho_grupos = os.path.join(PASTA_DADOS, "grupo-1.csv")
    usuarios = carregar_csv(caminho_grupos)
    
    # Menus de seleção
    usuario_escolhido = selecionar_usuario(usuarios)
    modo_escolhido = selecionar_modo()
    
    # Faz o login
    trocar_usuario(usuario_escolhido)
    
    tarefas_finais = []
    executar_com_pdf = False

    # Carrega os arquivos CSV corretos com base na escolha do usuário
    if modo_escolhido == 1:
        print("\nCarregando dados para requisitos SEM PDF...")
        links = {item['titulo']: item['link'] for item in carregar_csv(os.path.join(PASTA_DADOS, "links-lider.csv"))}
        respostas = carregar_csv(os.path.join(PASTA_DADOS, "respostas-lider.csv"))
    else: # modo_escolhido == 2
        print("\nCarregando dados para requisitos COM PDF...")
        executar_com_pdf = True
        links = {item['titulo']: item['link'] for item in carregar_csv(os.path.join(PASTA_DADOS, "links-lider-pdf.csv"))}
        respostas = carregar_csv(os.path.join(PASTA_DADOS, "respostas-lider-pdf.csv"))

    # Combina links e respostas em uma lista de tarefas
    for resp in respostas:
        if resp['titulo'] in links:
            tarefa_completa = resp.copy()
            tarefa_completa['link'] = links[resp['titulo']]
            tarefas_finais.append(tarefa_completa)
        else:
            print(f"AVISO: Título '{resp['titulo'][:50]}...' encontrado nas respostas, mas não nos links. Será ignorado.")

    # Executa a automação
    preencher_formularios(tarefas_finais, com_pdf=executar_com_pdf)

    # Mede o tempo total
    fim = time.time()
    print("\n" + "="*50)
    duracao = fim - inicio
    minutos = int(duracao // 60)
    segundos = int(duracao % 60)
    print(f"Duração total do processo: {minutos} min {segundos} s")
    print(">>> PROCESSO DE AUTOMAÇÃO FINALIZADO. <<<")