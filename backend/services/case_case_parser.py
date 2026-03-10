import re

def parse_case(text: str):
    """
    Extracts basic case structure from raw text
    """
    return {
        "full_name": extract_full_case_name(text),
        "short_name": extract_short_name(text),
        "court": find_court(text),
        "docket_number": extract_docket(text),
        "argued_date": extract_date(text, "Argued"),
        "decided_date": extract_date(text, "Decided"),
        "filed_date": extract_date(text, "Filed"),
        "opinion_text": extract_opinion(text)
    }


# ================= HELPERS =================

def extract_full_case_name(text):
    m = re.search(r"(.*? v\. .*?)\n", text)
    return m.group(1).strip() if m else ""

def extract_short_name(text):
    m = re.search(r"(.*? v\. .*?)", text)
    return m.group(1).split(" v. ")[0] if m else ""

def extract_docket(text):
    m = re.search(r"No\.\s*([\w\-]+)", text)
    return m.group(1) if m else ""

def find_court(text):
    for line in text.split("\n"):
        if "COURT" in line.upper():
            return line.strip()
    return ""

def extract_date(text, label):
    m = re.search(label + r".*?(\w+\s+\d{1,2},\s+\d{4})", text)
    return m.group(1) if m else None

def extract_opinion(text):
    blocks = []
    for p in text.split("\n\n"):
        if len(p.strip()) > 40:
            blocks.append(p.strip())
    return "\n\n".join(blocks[:5])
