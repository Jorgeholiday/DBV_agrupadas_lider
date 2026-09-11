import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# Arquivo de texto central (dentro da pasta indivi)
BASE_DIR = "indivi"
TXT_FILE = os.path.join(BASE_DIR, "texto.txt")

def txt_to_pdf(txt_content, pdf_file):
    styles = getSampleStyleSheet()
    story = []

    for line in txt_content.splitlines():
        line = line.strip()
        if line:
            story.append(Paragraph(line, styles["Normal"]))
        else:
            story.append(Paragraph(" ", styles["Normal"]))  # quebra de linha

    doc = SimpleDocTemplate(pdf_file, pagesize=letter)
    doc.build(story)

def main():
    # Lê o txt central
    if not os.path.exists(TXT_FILE):
        print(f"⚠️ Arquivo não encontrado: {TXT_FILE}")
        return

    with open(TXT_FILE, "r", encoding="utf-8") as f:
        conteudo = f.read()

    # Extrai os blocos entre [[ ... ]]
    blocos = re.findall(r"\[\[(.*?)\]\]", conteudo, re.DOTALL)

    if not blocos:
        print("⚠️ Nenhum bloco [[...]] encontrado no arquivo.")
        return

    # Lista de subpastas dentro de indivi (ignora arquivos)
    pastas = [p for p in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, p))]

    if not pastas:
        print("⚠️ Nenhuma subpasta encontrada em 'indivi'.")
        return

    # Verifica se há blocos suficientes
    if len(blocos) < len(pastas):
        print(f"⚠️ Existem {len(pastas)} pastas mas só {len(blocos)} blocos no txt!")
        print("Algumas pastas ficarão sem PDF.")
    
    # Distribui blocos → pastas
    for pasta, bloco in zip(pastas, blocos):
        pasta_path = os.path.join(BASE_DIR, pasta)
        pdf_path = os.path.join(pasta_path, f"texto10-KAUA-{pasta}.pdf")

        print(f"📄 Gerando {pdf_path}")
        txt_to_pdf(bloco.strip(), pdf_path)

    print(f"\n✅ Finalizado! {min(len(blocos), len(pastas))} PDFs criados.")

if __name__ == "__main__":
    main()
