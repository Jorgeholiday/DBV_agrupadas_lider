import pyautogui
import webbrowser
import time
import pyperclip
import os  # Importa a biblioteca para manipulação de caminhos de arquivo

# --- CONFIGURAÇÕES ---
# Coloque aqui as coordenadas (X, Y) para focar na janela do navegador.
CLICK_X = 2764
CLICK_Y = 381

# Tempo em segundos para a página carregar após abrir o link.
TEMPO_DE_ESPERA_PAGINA = 3

# Nome da pasta onde os arquivos PDF estão armazenados.
PASTA_PDFS = "pdfs"

# --- NOVAS FUNÇÕES DE LEITURA DOS ARQUIVOS ---

def carregar_respostas_pdf(nome_arquivo=os.path.join("tx", "resp_pdfs.txt")):
    """
    Lê o arquivo de respostas que inclui o nome do PDF.
    """
    respostas = {}
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as f:
            # Usa 'titulo: ' (minúsculo) para dividir os blocos, conforme seu arquivo
            conteudo = f.read().split('titulo: ')
            for bloco in conteudo:
                if not bloco.strip():
                    continue
                
                linhas = bloco.strip().split('\n')
                # O título agora é a primeira linha do bloco
                titulo_completo = " ".join(linhas[0].strip().split())
                
                dados = {'Data': '', 'Relatorios': '', 'nome': ''}
                relatorio_linhas = []
                is_relatorio = False

                for linha in linhas[1:]:
                    if linha.startswith('Data: '):
                        dados['Data'] = linha.replace('Data: ', '').strip()
                        is_relatorio = False
                    elif linha.startswith('Relatorios: '):
                        relatorio_linhas.append(linha.replace('Relatorios: ', '').strip())
                        is_relatorio = True
                    elif linha.startswith('nome: '):
                        dados['nome'] = linha.replace('nome: ', '').strip()
                        is_relatorio = False
                    elif is_relatorio:
                        relatorio_linhas.append(linha.strip())
                
                dados['Relatorios'] = "\n".join(relatorio_linhas).strip()
                
                # Garante que temos as informações essenciais
                if titulo_completo and dados['Data'] and dados['nome']:
                    respostas[titulo_completo] = dados
                    
    except FileNotFoundError:
        return None
    return respostas

def carregar_links_pdf(nome_arquivo=os.path.join("tx", "links-pdfs.txt")):
    """
    Lê o arquivo de links. Esta função foi ajustada para lidar com títulos
    que podem ter múltiplas linhas, padronizando-os para uma única linha.
    """
    links = {}
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as f:
            # Usa 'Titulo: ' (maiúsculo) para dividir os blocos
            conteudo = f.read().split('Titulo: ')
            for bloco in conteudo:
                if 'link: ' not in bloco:
                    continue
                
                partes = bloco.split('link: ')
                # Junta todas as linhas do título em uma só, separadas por espaço
                titulo = " ".join(partes[0].strip().split())
                link = partes[1].strip().split()[0]
                links[titulo] = link
    except FileNotFoundError:
        return None
    return links

# --- FUNÇÃO PRINCIPAL DE AUTOMAÇÃO COM UPLOAD ---

def preencher_formularios_pdf(respostas, links):
    if not respostas or not links:
        print("Erro: Arquivos 'resp_pdfs.txt' ou 'links-pdfs.txt' não encontrados ou vazios.")
        return

    print(">>> ATENÇÃO: A automação com UPLOAD DE PDF começará em 5 segundos. <<<")
    print("Prepare-se: abra seu navegador e deixe-o visível.")
    print("NÃO MEXA NO MOUSE OU TECLADO APÓS O INÍCIO!")
    time.sleep(5)

    # Constrói o caminho absoluto para a pasta de PDFs
    # Isso garante que o script encontre a pasta, não importa de onde ele seja executado.
    diretorio_do_script = os.path.dirname(os.path.abspath(__file__))
    caminho_base = os.path.dirname(diretorio_do_script)
    caminho_pdfs_completo = os.path.join(caminho_base, PASTA_PDFS)

    print(f"Pasta de PDFs configurada em: {caminho_pdfs_completo}")

    total_respostas = len(respostas)
    contador = 0

    for titulo, dados in respostas.items():
        contador += 1
        print(f"\n[Processando {contador}/{total_respostas}] - {titulo[:60]}...")
        
        if titulo in links:
            link = links[titulo]
            data = dados['Data']
            relatorio = dados['Relatorios']
            nome_pdf = dados['nome']
            caminho_arquivo_pdf = os.path.join(caminho_pdfs_completo, nome_pdf)

            # Verifica se o arquivo PDF realmente existe antes de prosseguir
            if not os.path.exists(caminho_arquivo_pdf):
                print(f"   - ERRO: Arquivo PDF não encontrado: {nome_pdf} - Pulando.")
                continue

            print(f"DEBUG: Link entre colchetes: [{link}]")
            print(f"DEBUG: Comprimento do link: {len(link)}")

            webbrowser.open(link, new=2)
            time.sleep(TEMPO_DE_ESPERA_PAGINA)

            pyautogui.click(CLICK_X, CLICK_Y)
            time.sleep(0.2)
            print(f"Link aberto: {link}")

            # 1. Preenche a Data
            pyautogui.press('tab')
            time.sleep(0.15)
            pyperclip.copy(data)
            pyautogui.hotkey('ctrl', 'v')
            print("   - Data colada.")

            # 2. Preenche o Relatório
            pyautogui.press('tab')
            time.sleep(0.15)
            pyperclip.copy(relatorio)
            pyautogui.hotkey('ctrl', 'v')
            print("   - Relatório colado.")

            # 3. Anexa o arquivo PDF
            pyautogui.press('tab') # Move o foco para o botão "Choose File"
            time.sleep(0.2)
            pyautogui.press('enter') # Abre a janela de seleção de arquivo
            print("   - Abrindo seletor de arquivo...")
            time.sleep(1.5) # Espera a janela de diálogo abrir completamente

            # Cola o caminho completo do arquivo e pressiona Enter
            pyperclip.copy(caminho_arquivo_pdf)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.8)
            pyautogui.press('enter')
            print(f"   - PDF anexado: {nome_pdf}")
            time.sleep(1.5)

            # 4. Envia o formulário
            pyautogui.press('tab') # Foco em "Página anterior"
            pyautogui.press('tab') # Foco em "Enviar resposta/arquivo"
            print("   - Foco no botão de enviar.")
            
            pyautogui.press('enter') # DESCOMENTE ESTA LINHA PARA ENVIAR O FORMULÁRIO
            time.sleep(2)
            
            pyautogui.hotkey('ctrl', 'w')
            time.sleep(1)

        else:
            print(f"   - AVISO: Título não encontrado no arquivo de links. Pulando.")
            
    print("\n--- AUTOMAÇÃO CONCLUÍDA! ---")


# --- EXECUÇÃO DO SCRIPT ---
if __name__ == "__main__":
    respostas_dict = carregar_respostas_pdf()
    links_dict = carregar_links_pdf()
    preencher_formularios_pdf(respostas_dict, links_dict)
