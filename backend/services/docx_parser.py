from docx import Document

def extract_references(path: str):
    doc = Document(path)

    refs = []
    start = False

    for p in doc.paragraphs:
        text = p.text.strip()

        if not text:
            continue

        if text.lower() in ["references", "reference", "bibliography"]:
            start = True
            continue

        if start and len(text) > 10:
            refs.append(text)

    return refs
