import re

# =====================================================
# 1. BASIC TEXT CLEANING
# =====================================================

def clean_text(line: str) -> str:
    line = line.replace("\u00a0", " ")
    line = re.sub(r"\s+", " ", line)
    return line.strip()


# =====================================================
# 2. LINE CLASSIFICATION (HARD-CODED LOGIC)
# =====================================================

def classify_line(line: str) -> str:
    """
    Returns one of:
    toc | heading | title | paragraph | empty
    """

    if not line or len(line.strip()) == 0:
        return "empty"

    # -------------------------------
    # REAL-WORLD TOC LINES
    # 1. Title .......... 23
    # -------------------------------
    if re.match(r"^\d+\.\s+.+?\s*\.{2,}\s*\d+$", line):
        return "toc"

    # Fallback TOC:
    # 1. Title 23
    if re.match(r"^\d+\.\s+.+\s+\d+$", line):
        return "toc"

    # Chapter headings
    if re.match(r"^(chapter|kapitel)\s+\d+", line.lower()):
        return "heading"

    # ALL CAPS short headings
    if line.isupper() and len(line) < 80:
        return "heading"

    # Short line → title
    if len(line) < 60:
        return "title"

    return "paragraph"


# =====================================================
# 3. CLIENT TAG MAP (LOCKED)
# =====================================================

CLIENT_TAGS = {
    "front": {
        "title": '<h1 class="TitlePage">{text}</h1>',
        "heading": '<h2 class="Front-Heading">{text}</h2>',
        "paragraph": '<p class="Front-Para">{text}</p>',
    },

    "chapter": {
        "heading": '<h1 class="Chapter-Title">{text}</h1>',
        "paragraph": '<p class="Para-Indent">{text}</p>',
    },

    "back": {
        "heading": '<h2 class="Back-Heading">{text}</h2>',
        "paragraph": '<p class="Back-Para">{text}</p>',
    },

    "meta": {
        "toc": '<li><a href="{href}">{text}</a></li>',
    }
}


# =====================================================
# 4. APPLY RULES (MAIN ENGINE)
# =====================================================

def apply_rules(lines, section: str):
    """
    Input:
      lines   → list[str] (plain extracted text)
      section → front | chapter | back | meta

    Output:
      list of XHTML strings (CLIENT TAGS ONLY)
    """

    output = []
    index = 1

    for raw in lines:
        line = clean_text(raw)
        kind = classify_line(line)

        if kind == "empty":
            continue

        # -------------------------------
        # META → nav.xhtml
        # -------------------------------
        if section == "meta" and kind == "toc":
            # remove dots + page numbers
            clean = re.sub(r"\.{2,}\s*\d+$", "", line).strip()
            clean = re.sub(r"\s+\d+$", "", clean).strip()

            tag = CLIENT_TAGS["meta"]["toc"]
            href = f"xhtml/{index:02d}.xhtml"

            output.append(tag.format(text=clean, href=href))
            index += 1
            continue

        # -------------------------------
        # OTHER SECTIONS
        # -------------------------------
        section_map = CLIENT_TAGS.get(section, {})
        tag_tpl = section_map.get(kind)

        if tag_tpl:
            output.append(tag_tpl.format(text=line))

    return output
