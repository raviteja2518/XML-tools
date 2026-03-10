import os
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ENTITY_FILE = os.path.join(BASE_DIR, "data", "entities.html")

def load_entity_map():
    with open(ENTITY_FILE, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    table = soup.find("table")
    mapping = {}

    for row in table.find_all("tr")[1:]:
        cols = row.find_all("td")
        if len(cols) >= 3:
            char = cols[-1].text.strip()
            hexv = cols[-2].text.strip()
            mapping[char] = hexv

    return mapping

ENTITY_MAP = load_entity_map()

def replace_entities(text: str):
    return "".join(ENTITY_MAP.get(c, c) for c in text)
