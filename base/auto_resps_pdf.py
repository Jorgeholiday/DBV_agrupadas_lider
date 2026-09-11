# base/auto_resps_pdf.py

import pyautogui
import webbrowser
import time
import pyperclip
import os

# --- CONFIGURAÇÕES ---
CLICK_X = 2764
CLICK_Y = 381
TEMPO_DE_ESPERA_PAGINA = 3

# CORREÇÃO: Apontando para a subpasta correta de PDFs das agrupadas
PASTA_PDFS = os.path.join("pdfs", "pdfs_agrupadas")

# --- FUNÇÕES DE LEITURA DOS ARQUIVOS ---

def carregar_respostas_pdf(nome_arquivo=os.path.join("tx", "resp_pdfs.txt")):
    """Lê o arquivo de respostas que inclui o nome do PDF."""
    respostas = {}
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read().split('titulo: ')
            for bloco in conteudo:
                if not bloco.strip():
                    continue
                
                linhas = bloco.strip().split('\n')
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
                
                if titulo_completo and dados['Data'] and dados['nome']:
                    respostas[titulo_completo] = dados
                    
    except FileNotFoundError:
        return None
    return respostas

def carregar_links_pdf(nome_arquivo=os.path.join("tx", "links-pdfs.txt")):
    """Lê o arquivo de links."""
    links = {}
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read().split('Titulo: ')
            for bloco in conteudo:
                if 'link: ' not in bloco:
                    continue
                
                partes = bloco.split('link: ')
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

    caminho_pdfs_completo = os.path.abspath(PASTA_PDFS)
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

            if not os.path.exists(caminho_arquivo_pdf):
                print(f"   - ERRO: Arquivo PDF não encontrado em '{caminho_arquivo_pdf}' - Pulando.")
                continue

            webbrowser.open(link, new=2)
            time.sleep(TEMPO_DE_ESPERA_PAGINA)

            pyautogui.click(CLICK_X, CLICK_Y)
            time.sleep(0.2)
            print(f"Link aberto: {link}")

            pyautogui.press('tab'); time.sleep(0.15)
            pyperclip.copy(data)
            pyautogui.hotkey('ctrl', 'v')
            print("   - Data colada.")

            pyautogui.press('tab'); time.sleep(0.15)
            pyperclip.copy(relatorio)
            pyautogui.hotkey('ctrl', 'v')
            print("   - Relatório colado.")

            pyautogui.press('tab'); time.sleep(0.2)
            pyautogui.press('enter')
            print("   - Abrindo seletor de arquivo...")
            time.sleep(1.5)

            pyperclip.copy(caminho_arquivo_pdf)
            pyautogui.hotkey('ctrl', 'v'); time.sleep(0.8)
            pyautogui.press('enter')
            print(f"   - PDF anexado: {nome_pdf}")
            time.sleep(1.5)

            pyautogui.press('tab')
            pyautogui.press('tab')
            print("   - Foco no botão de enviar.")
            
            pyautogui.press('enter')
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
