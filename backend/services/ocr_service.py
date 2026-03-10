from pdf2image import convert_from_path, pdfinfo_from_path
import pytesseract

def ocr_pdf(pdf_path: str):
    info = pdfinfo_from_path(pdf_path)
    pages = info["Pages"]

    all_text = []

    for p in range(1, pages + 1):
        images = convert_from_path(
            pdf_path, dpi=300, first_page=p, last_page=p
        )
        text = pytesseract.image_to_string(images[0])
        all_text.append(text)

    return all_text
