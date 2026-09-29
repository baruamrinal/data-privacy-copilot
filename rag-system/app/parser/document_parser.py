import fitz  # PyMuPDF
from docx import Document
from collections import Counter
import os
import re


# Top/bottom fraction of each page where running headers and footers live
HEADER_FOOTER_MARGIN = 0.08


def _normalize_block(text: str) -> str:
    # Ignore page numbers so "Page 3 of 6" matches "Page 4 of 6"
    return re.sub(r"\d+", "#", " ".join(text.split()))


def parse_pdf(file_path: str) -> str:

    pdf = fitz.open(file_path)

    # Collect text blocks per page, flagging those in the header/footer margins
    pages = []

    for page in pdf:
        height = page.rect.height
        blocks = []

        for x0, y0, x1, y1, block_text, block_no, block_type in page.get_text("blocks"):
            if block_type != 0:
                continue

            in_margin = (
                y1 <= height * HEADER_FOOTER_MARGIN
                or y0 >= height * (1 - HEADER_FOOTER_MARGIN)
            )
            blocks.append((block_text, in_margin))

        pages.append(blocks)

    # A margin block repeated on at least half the pages is a running header/footer
    counts = Counter(
        normalized
        for blocks in pages
        for normalized in {_normalize_block(t) for t, in_margin in blocks if in_margin}
    )
    min_pages = max(2, len(pages) // 2)
    repeated = {n for n, count in counts.items() if count >= min_pages}

    text = ""

    for blocks in pages:
        for block_text, in_margin in blocks:
            if in_margin and _normalize_block(block_text) in repeated:
                continue
            text += block_text if block_text.endswith("\n") else block_text + "\n"

    return text


def parse_docx(file_path: str) -> str:
    doc = Document(file_path)

    text = "\n".join([para.text for para in doc.paragraphs])

    return text


def parse_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def parse_document(file_path: str) -> dict:

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":
        text = parse_pdf(file_path)

    elif extension == ".docx":
        text = parse_docx(file_path)

    elif extension == ".txt":
        text = parse_txt(file_path)

    else:
        raise ValueError(f"Unsupported file type: {extension}")

    return {
        "text": text,
        "metadata": {
            "source": file_path,
            "file_type": extension
        }
    }