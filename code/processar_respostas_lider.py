import csv
import re
import os

def sanitizar_nome_arquivo(titulo):
    """Transforma um título em um nome de arquivo seguro."""
    # Remove os dois primeiros números e o ponto
    if re.match(r'^\d{2}\.', titulo):
        titulo = titulo[3:].strip()
    
    # Remove caracteres inválidos
    nome_arquivo = re.sub(r'[\\/*?:"<>|]', "", titulo)
    # Limita o tamanho para evitar nomes de arquivo muito longos
    nome_arquivo = nome_arquivo[:80].strip()
    # Substitui espaços por underscores
    nome_arquivo = nome_arquivo.replace(' ', '_')
    return f"{nome_arquivo}.pdf"

def extrair_respostas(caminho_txt):
    """
    Lê o arquivo de texto extraído do PDF e separa os dados
    em respostas de texto e respostas com PDF.
    """
    try:
        with open(caminho_txt, 'r', encoding='utf-8') as f:
            conteudo = f.read()
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{caminho_txt}' não encontrado. Verifique o caminho e o nome.")
        return [], []

    # Divide o documento inteiro em blocos de requisitos
    # A expressão regular `(?=\n\d{2}\.)` divide o texto antes de cada "01.", "02.", etc.
    blocos = re.split(r'(?=\n\d{2}\.)', conteudo)
    
    respostas_texto = []
    respostas_pdf = []

    for bloco in blocos:
        if not bloco.strip():
            continue

        linhas = [linha.strip() for linha in bloco.strip().split('\n') if linha.strip()]
        titulo_principal = linhas[0]

        # Verifica se é um requisito de múltiplas opções
        if any("Opção" in linha for linha in linhas):
            sub_blocos = re.split(r'(Opção \d{2})', bloco)
            for i in range(1, len(sub_blocos), 2):
                opcao_titulo = sub_blocos[i]
                opcao_corpo = sub_blocos[i+1]
                
                titulo_completo = f"{titulo_principal} ({opcao_titulo})"
                processar_dados_bloco(titulo_completo, opcao_corpo, respostas_texto, respostas_pdf)
        else:
            processar_dados_bloco(titulo_principal, bloco, respostas_texto, respostas_pdf)

    return respostas_texto, respostas_pdf

def processar_dados_bloco(titulo, corpo, lista_texto, lista_pdf):
    """Extrai data e relatório de um bloco de texto e o adiciona à lista correta."""
    data_match = re.search(r'Data:\s*(.*)', corpo)
    data = data_match.group(1).strip() if data_match else ""

    # Extrai o relatório, que pode ter múltiplas linhas
    relatorio_match = re.search(r'Relatório:\s*([\s\S]*?)(?=\nAtualizar|Se não está|Enviar|$)', corpo, re.MULTILINE)
    relatorio = " ".join(relatorio_match.group(1).strip().split()) if relatorio_match else ""

    # Decide o tipo de resposta
    is_pdf = any(keyword in corpo for keyword in ["Enviar arquivo", "Atualizar arquivo", "Se não está visualizando"])
    
    # Ignora itens que não têm nem data nem relatório e são para enviar arquivo (ainda não preenchidos)
    if is_pdf and not data and not relatorio:
        return

    if is_pdf:
        nome_arquivo = sanitizar_nome_arquivo(titulo)
        lista_pdf.append({'titulo': titulo, 'data': data, 'relatorio': relatorio, 'nome': nome_arquivo})
    else:
        # Só adiciona se houver dados preenchidos
        if data or relatorio:
            lista_texto.append({'titulo': titulo, 'data': data, 'relatorio': relatorio})

def salvar_csv(dados, caminho_csv, cabecalho):
    """Salva os dados extraídos em um arquivo CSV."""
    if not dados:
        print(f"Nenhum dado para salvar em '{caminho_csv}'.")
        return

    try:
        with open(caminho_csv, 'w', newline='', encoding='utf-8') as f:
            escritor = csv.DictWriter(f, fieldnames=cabecalho, quoting=csv.QUOTE_ALL)
            escritor.writeheader()
            escritor.writerows(dados)
        print(f"Sucesso! Arquivo '{caminho_csv}' criado com {len(dados)} itens.")
    except Exception as e:
        print(f"Erro ao salvar '{caminho_csv}': {e}")


# --- EXECUÇÃO PRINCIPAL ---
if __name__ == "__main__":
    PASTA_DADOS = "tx"
    ARQUIVO_ENTRADA = os.path.join(PASTA_DADOS, "respostas-lider.txt")
    
    ARQUIVO_SAIDA_TEXTO = "respostas-lider.csv"
    ARQUIVO_SAIDA_PDF = "respostas-lider-pdf.csv"
    
    respostas, pdfs = extrair_respostas(ARQUIVO_ENTRADA)

    print("\n--- SALVANDO ARQUIVOS DE RESPOSTA ---")
    
    salvar_csv(respostas, ARQUIVO_SAIDA_TEXTO, ['titulo', 'data', 'relatorio'])
    salvar_csv(pdfs, ARQUIVO_SAIDA_PDF, ['titulo', 'data', 'relatorio', 'nome'])