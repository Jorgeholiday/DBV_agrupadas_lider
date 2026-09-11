import pyautogui
import webbrowser
import time
import pyperclip # Importa a nova biblioteca
import os

# --- CONFIGURAÇÕES ---
# Coloque aqui as coordenadas (X, Y) que você descobriu.
# Este é o ponto onde o script vai clicar para focar na janela do navegador.
CLICK_X = 2764
CLICK_Y = 381

# Tempo em segundos para a página carregar após abrir o link.
TEMPO_DE_ESPERA_PAGINA = 2

# --- FUNÇÕES DE LEITURA DOS ARQUIVOS (As mesmas de antes) ---

def carregar_respostas(nome_arquivo=os.path.join("tx", "respostas.txt")):
    respostas = {}
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read().split('Titulo: ')
            for bloco in conteudo:
                if not bloco.strip(): continue
                linhas = bloco.strip().split('\n')
                titulo = linhas[0].strip()
                data, relatorio_completo = "", ""
                relatorio_linhas = []
                is_relatorio = False
                for linha in linhas[1:]:
                    if linha.startswith('Data: '):
                        data = linha.replace('Data: ', '').strip()
                    elif linha.startswith('Relatorios: '):
                        relatorio_linhas.append(linha.replace('Relatorios: ', '').strip())
                        is_relatorio = True
                    elif is_relatorio:
                        relatorio_linhas.append(linha)
                relatorio_completo = "\n".join(relatorio_linhas).strip()
                if titulo and data:
                    respostas[titulo] = {'Data': data, 'Relatorios': relatorio_completo}
    except FileNotFoundError:
        return None
    return respostas

def carregar_links(nome_arquivo=os.path.join("tx", "links.txt")):
    links = {}
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read().split('Titulo: ')
            for bloco in conteudo:
                if not bloco.strip(): continue
                partes = bloco.strip().split('link: ')
                if len(partes) == 2:
                    titulo = partes[0].strip()
                    link = partes[1].strip().split()[0]
                    links[titulo] = link
    except FileNotFoundError:
        return None
    return links

# --- FUNÇÃO PRINCIPAL DE AUTOMAÇÃO ---

def preencher_formularios(respostas, links):
    if not respostas or not links:
        print("Erro: Arquivos 'respostas.txt' ou 'links.txt' não encontrados ou vazios.")
        return

    print(">>> ATENÇÃO: A automação começará em 10 segundos. <<<")
    print("Prepare-se: abra seu navegador e deixe-o visível.")
    print("NÃO MEXA NO MOUSE OU TECLADO APÓS O INÍCIO!")
    print("Para parar a automação em caso de emergência, mova o mouse para o canto superior esquerdo da tela.")
    
    for i in range(5, 0, -1):
        print(f"{i}...")
        time.sleep(1)

    inicio = time.time()
    print(f"\nInício: {time.strftime('%H:%M:%S', time.localtime(inicio))}")
    
    print("\n--- INICIANDO AUTOMAÇÃO ---")

    total_respostas = len(respostas)
    contador = 0

    for titulo, dados in respostas.items():
        contador += 1
        print(f"\n[Processando {contador}/{total_respostas}] - {titulo[:60]}...")
        
        if titulo in links:
            link = links[titulo]
            data = dados['Data']
            relatorio = dados['Relatorios']

            webbrowser.open(link, new=2)
            time.sleep(TEMPO_DE_ESPERA_PAGINA)

            pyautogui.click(CLICK_X, CLICK_Y)
            time.sleep(0.15)

            # --- MUDANÇA AQUI ---
            # 3. Preenche a Data usando Copiar e Colar
            pyautogui.press('tab')
            time.sleep(0.15)
            pyperclip.copy(data)
            pyautogui.hotkey('ctrl', 'v')
            print("  - Data colada.")

            # 4. Preenche o Relatório usando Copiar e Colar
            pyautogui.press('tab')
            time.sleep(0.15)
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.15)
            pyperclip.copy(relatorio)
            pyautogui.hotkey('ctrl', 'v')
            print("  - Relatório colado.")
            # --- FIM DA MUDANÇA ---

            pyautogui.press('tab')
            time.sleep(0.15)
            pyautogui.press('tab')
            time.sleep(0.15)
            print("  - Foco no botão de salvar.")

            pyautogui.press('enter') # Descomente para salvar
            print("  - AÇÃO DE SALVAR ESTÁ DESATIVADA.")
            time.sleep(1)
            
            pyautogui.hotkey('ctrl', 'w')
            time.sleep(1)

        else:
            print(f"  - AVISO: Título não encontrado no arquivo de links. Pulando.")
            
    print("\n--- AUTOMAÇÃO CONCLUÍDA! ---")

    fim = time.time()
    print(f"Fim: {time.strftime('%H:%M:%S', time.localtime(fim))}")
    duracao = fim - inicio
    minutos = int(duracao // 60)
    segundos = int(duracao % 60)
    print(f"Duração total: {minutos} min {segundos} s")


# --- EXECUÇÃO DO SCRIPT ---
if __name__ == "__main__":
    respostas_dict = carregar_respostas()
    links_dict = carregar_links()
    preencher_formularios(respostas_dict, links_dict)