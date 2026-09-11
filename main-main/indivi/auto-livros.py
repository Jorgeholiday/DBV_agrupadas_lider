#!/usr/bin/env python3
# txt_to_pdfs_wrapped.py
import os
import re
import unicodedata
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

INPUT_TXT = "livros.txt"
OUTPUT_DIR = "pdfs_livros_wrapped"

# Layout
LEFT_MARGIN = 50
RIGHT_MARGIN = 50
TOP_MARGIN = 50
BOTTOM_MARGIN = 50
TITLE_SIZE = 16
BODY_SIZE = 12
LINE_SPACING = 14  # espaçamento entre linhas do corpo (em pontos)

os.makedirs(OUTPUT_DIR, exist_ok=True)


def register_fonts():
    """
    Tenta registrar DejaVu Sans (melhor suporte a acentuação).
    Se não encontrar os TTF no sistema, retorna False e usaremos fontes padrão.
    """
    possible_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "C:\\Windows\\Fonts\\DejaVuSans.ttf",
        "C:\\Windows\\Fonts\\DejaVuSans-Bold.ttf",
        "./DejaVuSans.ttf",
        "./DejaVuSans-Bold.ttf",
    ]

    registered = False
    try:
        # tenta registrar regular + bold se existirem
        if os.path.exists(possible_paths[0]) and os.path.exists(possible_paths[1]):
            pdfmetrics.registerFont(TTFont("DejaVuSans", possible_paths[0]))
            pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", possible_paths[1]))
            registered = True
        else:
            # tentativas mais simples: procura qualquer DejaVuSans ttf na lista
            for p in possible_paths:
                if p.lower().endswith(".ttf") and os.path.exists(p):
                    # registra com nome genérico dependendo do arquivo
                    base = os.path.basename(p).lower()
                    if "bold" in base:
                        pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", p))
                    else:
                        pdfmetrics.registerFont(TTFont("DejaVuSans", p))
                    registered = True
            # se só registrou um dos dois, tenta criar um alias Helvetica-Bold se faltar
            if registered:
                if "DejaVuSans" in pdfmetrics.getRegisteredFontNames() and "DejaVuSans-Bold" not in pdfmetrics.getRegisteredFontNames():
                    pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", possible_paths[0]))
    except Exception:
        registered = False

    return registered


def sanitize_filename(name: str) -> str:
    """Remove acentos e caracteres proibidos, substitui espaços por _"""
    name = name.strip()
    # Normaliza e remove acentos
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ASCII", "ignore").decode("ASCII")
    # Remove caracteres não alfanuméricos (mantém _ e -)
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"\s+", "_", name)
    return name


def save_book_to_pdf(title: str, content: str, use_dejavu: bool):
    filename = sanitize_filename(title) + ".pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    c = canvas.Canvas(filepath, pagesize=A4)
    page_width, page_height = A4
    max_width = page_width - LEFT_MARGIN - RIGHT_MARGIN

    # Fontes
    title_font = "DejaVuSans-Bold" if use_dejavu and "DejaVuSans-Bold" in pdfmetrics.getRegisteredFontNames() else "Helvetica-Bold"
    body_font = "DejaVuSans" if use_dejavu and "DejaVuSans" in pdfmetrics.getRegisteredFontNames() else "Helvetica"

    x = LEFT_MARGIN
    y = page_height - TOP_MARGIN

    # Escrever o título (pode quebrar se for longo)
    c.setFont(title_font, TITLE_SIZE)
    title_lines = simpleSplit(title, title_font, TITLE_SIZE, max_width)
    for line in title_lines:
        c.drawString(x, y, line)
        y -= TITLE_SIZE + 6
        if y < BOTTOM_MARGIN:
            c.showPage()
            c.setFont(title_font, TITLE_SIZE)
            y = page_height - TOP_MARGIN

    # Espaço após título
    y -= 6

    # Escrever o conteúdo com quebra automática por largura
    c.setFont(body_font, BODY_SIZE)
    for paragraph in content.splitlines():
        # Trata linhas vazias como parágrafo novo (pular linha)
        if not paragraph.strip():
            y -= LINE_SPACING
            if y < BOTTOM_MARGIN:
                c.showPage()
                c.setFont(body_font, BODY_SIZE)
                y = page_height - TOP_MARGIN
            continue

        wrapped = simpleSplit(paragraph, body_font, BODY_SIZE, max_width)
        for wline in wrapped:
            c.drawString(x, y, wline)
            y -= LINE_SPACING
            if y < BOTTOM_MARGIN:
                c.showPage()
                c.setFont(body_font, BODY_SIZE)
                y = page_height - TOP_MARGIN

    c.save()
    print(f"📖 PDF gerado: {filepath}")


def main():
    if not os.path.exists(INPUT_TXT):
        print(f"Arquivo não encontrado: {INPUT_TXT}")
        return

    use_dejavu = register_fonts()
    if use_dejavu:
        print("Fonte DejaVu registrada — suporte completo a acentos ativado.")
    else:
        print("DejaVu não encontrada. Usando fontes padrão (se tiver problema com acentuação, instale DejaVu e coloque o TTF na pasta).")

    with open(INPUT_TXT, "r", encoding="utf-8") as f:
        texto = f.read()

    # Divide pelos blocos que começam com "Livro N: ...". Mantemos o título capturado.
    partes = re.split(r"(Livro\s*\d+\s*:\s*[^\n\r]+)", texto, flags=re.IGNORECASE)

    # O resultado típico: ['', 'Livro 1: Título', 'conteúdo', 'Livro 2: ...', 'conteúdo', ...]
    for i in range(1, len(partes), 2):
        titulo = partes[i].strip()
        conteudo = partes[i + 1].strip() if i + 1 < len(partes) else ""
        save_book_to_pdf(titulo, conteudo, use_dejavu)

    print("Concluído.")

if __name__ == "__main__":
    main()
