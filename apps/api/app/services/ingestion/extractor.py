import io
import chardet
from pypdf import PdfReader
from docx import Document as DocxDocument


def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF bytes."""
    reader = PdfReader(io.BytesIO(file_content))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text.strip())
    return "\n\n".join(pages)


def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX bytes."""
    doc = DocxDocument(io.BytesIO(file_content))
    paragraphs = []
    for para in doc.paragraphs:
        if para.text.strip():
            paragraphs.append(para.text.strip())
    return "\n\n".join(paragraphs)


def extract_text_from_txt(file_content: bytes) -> str:
    """Extract text from TXT bytes with encoding detection."""
    detected = chardet.detect(file_content)
    encoding = detected.get("encoding", "utf-8") or "utf-8"
    return file_content.decode(encoding)


def extract_text(file_content: bytes, file_type: str) -> str:
    """Extract text based on file type."""
    extractors = {
        "pdf": extract_text_from_pdf,
        "docx": extract_text_from_docx,
        "txt": extract_text_from_txt,
    }
    extractor = extractors.get(file_type.lower())
    if not extractor:
        raise ValueError(f"Unsupported file type: {file_type}")

    text = extractor(file_content)
    # Clean: strip excessive whitespace
    lines = [line.strip() for line in text.splitlines()]
    text = "\n".join(line for line in lines if line)
    return text
