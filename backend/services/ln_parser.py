from docx import Document
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom


def parse_word_to_ln_xml(docx_path: str) -> str:
    doc = Document(docx_path)

    root = Element("lnxml")
    body = SubElement(root, "body")

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        style = para.style.name.lower()

        # 🔹 Heading rules
        if "heading 1" in style:
            tag = SubElement(body, "h2")
            tag.text = text

        elif "heading 2" in style:
            tag = SubElement(body, "h3")
            tag.text = text

        else:
            tag = SubElement(body, "p")
            tag.text = text

    # Pretty XML
    rough = tostring(root, "utf-8")
    reparsed = minidom.parseString(rough)
    return reparsed.toprettyxml(indent="  ")
