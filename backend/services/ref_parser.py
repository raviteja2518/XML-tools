import re
import html

def split_authors(author_text: str):
    """
    Converts:
    Ball, D. L., Thames, M. H., & Phelps, G.
    → list of {surname, given-names}
    """
    authors = []

    author_text = author_text.replace("&", ",")
    parts = [a.strip() for a in author_text.split(",") if a.strip()]

    i = 0
    while i < len(parts) - 1:
        surname = parts[i]
        given = parts[i + 1]
        authors.append({
            "surname": html.escape(surname),
            "given-names": html.escape(given)
        })
        i += 2

    return authors


def parse_reference(text: str):
    text = html.unescape(text)

    data = {
        "type": "book",
        "collab": None,
        "authors": [],
        "year": None,
        "article_title": None,
        "source": None,
        "publisher": None,
        "volume": None,
        "issue": None,
        "fpage": None,
        "lpage": None,
        "comment": None,
        "url": None,
    }

    # URL
    url = re.search(r"https?://\S+", text)
    if url:
        data["url"] = url.group()
        data["type"] = "web"

    # Year
    y = re.search(r"\((19|20)\d{2}\)", text)
    if y:
        data["year"] = y.group()[1:-1]

    # Detect journal
    if "journal" in text.lower() or "register" in text.lower():
        data["type"] = "journal"

    # Split before year → authors / collab
    before_year = text.split("(")[0].strip(" .")

    # Organization (collab) vs authors
    if "," not in before_year:
        data["collab"] = before_year
    else:
        data["authors"] = split_authors(before_year)

    # Article title
    at = re.search(r"\)\.\s*(.*?)\.\s*", text)
    if at:
        data["article_title"] = at.group(1)

    # Volume / Issue
    v = re.search(r",\s*(\d+)\s*\(", text)
    if v:
        data["volume"] = v.group(1)

    iss = re.search(r"\((\d+)\)", text)
    if iss:
        data["issue"] = iss.group(1)

    # Pages
    pages = re.search(r"(\d+)[–-](\d+)", text)
    if pages:
        data["fpage"] = pages.group(1)
        data["lpage"] = pages.group(2)

    # Publisher
    pub = re.search(r"\.\s*([^\.]+)\.$", text)
    if pub:
        data["publisher"] = pub.group(1)

    data["source"] = data["article_title"] or text
    return data
