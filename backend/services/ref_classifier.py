import re

def parse_reference(ref: str):
    data = {
        "type": "book",
        "year": None,
        "collab": None,
        "source": ref,
        "url": None,
    }

    if "http" in ref:
        data["type"] = "web"

    if "journal" in ref.lower():
        data["type"] = "journal"

    year = re.search(r"\((19|20)\d{2}\)", ref)
    if year:
        data["year"] = year.group(0)[1:-1]

    url = re.search(r"https?://\S+", ref)
    if url:
        data["url"] = url.group(0)

    return data
