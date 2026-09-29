import fitz  # PyMuPDF
from docx import Document
import os


def parse_pdf(file_path: str) -> str:
    text = ""

    pdf = fitz.open(file_path)

    for page in pdf:
        text += page.get_text()

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