import pyautogui
import webbrowser
import time
import pyperclip
import os
import csv
import sys

# --- CONFIGURAÇÕES GLOBAIS ---
CLICK_X = 2504 # Ajuste se necessário
CLICK_Y = 603  # Ajuste se necessário
TEMPO_DE_ESPERA_PAGINA = 3
PASTA_DADOS = "db"
PASTA_PDFS = "pdfs"

# --- FUNÇÕES DE CARREGAMENTO E AUTOMAÇÃO ---

def carregar_csv(caminho_csv):
    """Função genérica para carregar arquivos CSV."""
    try:
        with open(caminho_csv, mode='r', encoding='utf-8', newline='') as f:
            leitor = csv.DictReader(f)
            return list(leitor)
    except FileNotFoundError:
        print(f"ERRO CRÍTICO: O arquivo '{caminho_csv}' não foi encontrado! O script será encerrado.")
        sys.exit()

def trocar_usuario(usuario):
    """Executa a automação para preencher o formulário de troca de usuário."""
    url = "https://clubes.adventistas.org/br/personal-card/"
    print("\n" + "="*60)
    print(f"INICIANDO SESSÃO PARA O USUÁRIO: {usuario['nome'].upper()}")
    print("="*60)
    print("A automação do login começará em 5 segundos...")
    time.sleep(5)

    webbrowser.open(url, new=1)
    time.sleep(TEMPO_DE_ESPERA_PAGINA + 2) # Tempo extra para a página de login

    pyautogui.click(CLICK_X, CLICK_Y); time.sleep(0.5)
    pyautogui.press('tab'); time.sleep(0.2); pyperclip.copy(usuario['codigo']); pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('tab'); time.sleep(0.2); pyperclip.copy(usuario['email']); pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('tab'); time.sleep(0.2); pyperclip.copy(usuario['ano']); pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('tab'); time.sleep(0.5)
    
    pyautogui.press('enter') 
    print("Login realizado com sucesso! Aguardando a página carregar...")
    time.sleep(5)

def preencher_formularios(tarefas, com_pdf=False):
    """Função principal que executa a automação de preenchimento."""
    if not tarefas:
        print("Nenhuma tarefa encontrada nos arquivos CSV para este modo. Pulando...")
        return

    modo = "COM PDF" if com_pdf else "SEM PDF"
    print(f"\n>>> INICIANDO automação dos requisitos {modo}. <<<")
    print("Atenção em 5 segundos. NÃO MEXA NO MOUSE OU TECLADO!")
    time.sleep(5)

    caminho_base_pdfs = os.path.abspath(PASTA_PDFS)
    total = len(tarefas)
    
    for i, tarefa in enumerate(tarefas):
        print(f"\n[Processando {i+1}/{total} - {modo}] - {tarefa['titulo'][:60]}...")
        
        webbrowser.open(tarefa['link'], new=2); time.sleep(TEMPO_DE_ESPERA_PAGINA)
        pyautogui.click(CLICK_X, CLICK_Y); time.sleep(0.2)

        pyautogui.press('tab'); time.sleep(0.15); pyperclip.copy(tarefa['data']); pyautogui.hotkey('ctrl', 'v')
        print("   - Data colada.")

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

        pyautogui.press('tab')
        pyautogui.press('tab')
        print("   - Foco no botão de enviar.")
        
        # AÇÃO DE ENVIAR ATIVADA
        pyautogui.press('enter')
        time.sleep(2) # Tempo para o formulário processar
        
        pyautogui.hotkey('ctrl', 'w')
        time.sleep(1)

def combinar_tarefas(links_csv, respostas_csv):
    """Combina os dados dos arquivos de links e respostas."""
    links = {item['titulo']: item['link'] for item in carregar_csv(os.path.join(PASTA_DADOS, links_csv))}
    respostas = carregar_csv(os.path.join(PASTA_DADOS, respostas_csv))
    
    tarefas_finais = []
    for resp in respostas:
        if resp['titulo'] in links:
            tarefa_completa = resp.copy()
            tarefa_completa['link'] = links[resp['titulo']]
            tarefas_finais.append(tarefa_completa)
        else:
            print(f"AVISO: Título '{resp['titulo'][:50]}...' das respostas não encontrado nos links. Será ignorado.")
    return tarefas_finais

# --- FLUXO PRINCIPAL ---
if __name__ == "__main__":
    inicio = time.time()
    print("--- INICIANDO AUTOMAÇÃO TOTAL DA CLASSE DE LÍDER ---")

    caminho_grupos = os.path.join(PASTA_DADOS, "grupo-1.csv")
    usuarios = carregar_csv(caminho_grupos)
    
    if not usuarios:
        print("Nenhum usuário encontrado para processar. Encerrando.")
    else:
        print(f"Encontrados {len(usuarios)} usuários. Iniciando o processo completo...")

        # Loop principal que itera sobre cada usuário
        for i, usuario_atual in enumerate(usuarios):
            # 1. FAZ O LOGIN PARA O USUÁRIO ATUAL
            trocar_usuario(usuario_atual)
            
            # 2. EXECUTA A TAREFA SEM PDF
            print("\nCarregando dados para requisitos SEM PDF...")
            tarefas_sem_pdf = combinar_tarefas("links-lider.csv", "respostas-lider.csv")
            preencher_formularios(tarefas_sem_pdf, com_pdf=False)

            # 3. EXECUTA A TAREFA COM PDF
            print("\nCarregando dados para requisitos COM PDF...")
            tarefas_com_pdf = combinar_tarefas("links-lider-pdf.csv", "respostas-lider-pdf.csv")
            preencher_formularios(tarefas_com_pdf, com_pdf=True)
            
            print(f"\n--- TAREFAS CONCLUÍDAS PARA {usuario_atual['nome'].upper()} ({i+1}/{len(usuarios)}) ---")

    # Mede o tempo total
    fim = time.time()
    print("\n" + "="*60)
    duracao = fim - inicio
    minutos = int(duracao // 60)
    segundos = int(duracao % 60)
    print(f"DURAÇÃO TOTAL DO PROCESSO: {minutos} min {segundos} s")
    print(">>> PROCESSO DE AUTOMAÇÃO TOTAL FINALIZADO. <<<")
    print("="*60)