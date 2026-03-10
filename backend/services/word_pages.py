from docx import Document

def extract_word_pages(path: str):
    doc = Document(path)
    pages = []
    current = []

    for para in doc.paragraphs:
        if para.text.strip():
            current.append(para.text)

        # Detect page break
        for run in para.runs:
            if run._element.xpath('.//w:br[@w:type="page"]'):
                pages.append("\n".join(current))
                current = []

    if current:
        pages.append("\n".join(current))

    return pages
