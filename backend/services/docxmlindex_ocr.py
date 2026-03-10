import pytesseract
from PIL import Image

def ocr_crop(image_path: str, sel: dict) -> str:
    img = Image.open(image_path)
    box = (sel["x"], sel["y"], sel["x"] + sel["width"], sel["y"] + sel["height"])
    cropped = img.crop(box)
    # PSM 4 is optimized for column-wise reading
    return pytesseract.image_to_string(cropped, config='--oem 3 --psm 4')