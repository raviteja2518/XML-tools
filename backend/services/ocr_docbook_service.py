from docx import Document
import re

SPECIAL_CHAR_MAP = {
    "’": "&#x2019;",
    "“": "&#x201C;",
    "”": "&#x201D;",
    "–": "&#x2013;",
    "—": "&#x2014;",
}

def replace_special_chars(text: str) -> str:
    for k, v in SPECIAL_CHAR_MAP.items():
        text = text.replace(k, v)
    return text


def process_word_doc(input_path: str, output_path: str):
    doc = Document(input_path)
    page_counter = 1

    for para in doc.paragraphs:
        new_text = ""

        for run in para.runs:
            text = run.text

            if not text:
                continue

            text = replace_special_chars(text)

            if run.font.superscript:
                text = f"<sup>{text}</sup>"

            if run.italic:
                text = f"<italic>{text}</italic>"

            if run.bold:
                text = f"<bold>{text}</bold>"

            new_text += text

        if para.text.strip().isdigit():
            para.text = f'<?page value="{str(page_counter).zfill(2)}"?>\n{new_text}'
            page_counter += 1
        else:
            para.text = new_text

    doc.save(output_path)
