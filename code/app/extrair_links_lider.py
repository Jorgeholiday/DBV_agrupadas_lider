import csv
from bs4 import BeautifulSoup
import re

def extrair_dados_do_html(caminho_html):
    """
    Lê um arquivo HTML, extrai títulos e links, e os separa em duas listas
    com base no texto do botão associado ('Responder' ou 'Enviar').
    """
    print(f"Lendo o arquivo HTML: {caminho_html}...")
    
    try:
        with open(caminho_html, 'r', encoding='utf-8') as f:
            conteudo = f.read()
    except FileNotFoundError:
        print(f"ERRO: O arquivo '{caminho_html}' não foi encontrado.")
        return [], []

    soup = BeautifulSoup(conteudo, 'html.parser')
    tags_de_titulo = soup.find_all('h4', style="color: #F90307; font-weight: bold")
    
    # AGORA TEMOS DUAS LISTAS PARA ARMAZENAR OS DADOS
    dados_respostas = []
    dados_pdfs = []
    
    print(f"Encontrados {len(tags_de_titulo)} requisitos para processar.")

    for i, h4_tag in enumerate(tags_de_titulo):
        titulo_principal = " ".join(h4_tag.get_text(strip=True).split())
        
        proximo_h4 = tags_de_titulo[i + 1] if i + 1 < len(tags_de_titulo) else None
        
        blocos_de_opcao = []
        for irmao in h4_tag.parent.find_next_siblings():
            if proximo_h4 and irmao == proximo_h4.parent:
                break
            if irmao.find('h5'):
                blocos_de_opcao.append(irmao)

        if blocos_de_opcao:
            # CASO 1: A pergunta tem múltiplas opções
            for bloco in blocos_de_opcao:
                processar_bloco(bloco, titulo_principal, dados_respostas, dados_pdfs)
        else:
            # CASO 2: A pergunta tem apenas um link (usa o pai do h4 como bloco)
            processar_bloco(h4_tag.parent, titulo_principal, dados_respostas, dados_pdfs)

    return dados_respostas, dados_pdfs

def processar_bloco(bloco, titulo_principal, lista_respostas, lista_pdfs):
    """
    Processa um bloco de HTML para extrair o título completo, o link e o tipo de botão.
    Depois, adiciona os dados à lista correta.
    """
    # CORREÇÃO: Usa .find_next() para procurar nos elementos SEGUINTES ao bloco
    button_tag = bloco.find_next('button')
    script_tag = bloco.find_next('script')

    if not (button_tag and script_tag and script_tag.string):
        return

    # A lógica daqui para baixo continua a mesma
    texto_botao = button_tag.get_text(strip=True)
    texto_opcao_tag = bloco.find('h5')
    titulo_completo = titulo_principal
    if texto_opcao_tag:
        titulo_completo = f"{titulo_principal} ({texto_opcao_tag.get_text(strip=True)})"
    
    link = None
    match = re.search(r'location\.href="([^"]+)"', script_tag.string)
    if match:
        link = match.group(1)

    if link:
        dado = {'titulo': titulo_completo, 'link': link}
        if "Responder requisito" in texto_botao:
            lista_respostas.append(dado)
        elif "Enviar arquivo" in texto_botao:
            lista_pdfs.append(dado)

def salvar_em_csv(dados, caminho_csv):
    """Salva os dados extraídos em um arquivo CSV, sempre usando aspas."""
    if not dados:
        print(f"Nenhum dado para salvar em '{caminho_csv}'. O arquivo não será criado.")
        return

    cabecalho = ['titulo', 'link']
    
    try:
        with open(caminho_csv, 'w', newline='', encoding='utf-8') as f:
            escritor = csv.DictWriter(f, fieldnames=cabecalho, quoting=csv.QUOTE_ALL)
            escritor.writeheader()
            escritor.writerows(dados)
            
        print(f"Sucesso! Os dados foram salvos em '{caminho_csv}'. Total de {len(dados)} itens.")
    except Exception as e:
        print(f"Ocorreu um erro ao salvar o arquivo '{caminho_csv}': {e}")

# --- EXECUÇÃO PRINCIPAL ---
if __name__ == "__main__":
    ARQUIVO_HTML_ENTRADA = 'Líder de Desbravadores - Paulo Vitor de Oliveira Santos.html'
    
    # Nomes dos dois arquivos de saída
    ARQUIVO_CSV_RESPOSTAS = 'links.csv'
    ARQUIVO_CSV_PDFS = 'links-pdf.csv'
    
    # A função agora retorna duas listas separadas
    respostas, pdfs = extrair_dados_do_html(ARQUIVO_HTML_ENTRADA)
    
    print("\n--- SALVANDO ARQUIVOS CSV ---")
    
    # Salva o primeiro arquivo CSV
    salvar_em_csv(respostas, ARQUIVO_CSV_RESPOSTAS)
    
    # Salva o segundo arquivo CSV
    salvar_em_csv(pdfs, ARQUIVO_CSV_PDFS)