import os

# Optional imports (only used if files exist)
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    from docx import Document
except ImportError:
    Document = None


# =====================================================
# MAIN EXTRACT FUNCTION (USED EVERYWHERE)
# =====================================================

def extract_text(file_path: str):
    """
    Extracts RAW TEXT lines from PDF or DOCX.
    Returns: list[str]
    """

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_from_pdf(file_path)

    if ext == ".docx":
        return extract_from_docx(file_path)

    return []


# =====================================================
# PDF TEXT EXTRACTION (NO FORMATTING)
# =====================================================

def extract_from_pdf(file_path: str):
    lines = []

    if not fitz:
        raise RuntimeError("PyMuPDF (fitz) not installed")

    doc = fitz.open(file_path)

    for page in doc:
        text = page.get_text("text")
        for line in text.split("\n"):
            line = line.strip()
            if line:
                lines.append(line)

    return lines


# =====================================================
# DOCX TEXT EXTRACTION (NO STYLES)
# =====================================================

def extract_from_docx(file_path: str):
    lines = []

    if not Document:
        raise RuntimeError("python-docx not installed")

    doc = Document(file_path)

    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            lines.append(text)

    return lines
