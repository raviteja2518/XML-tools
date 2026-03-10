def build_book_xml(pages: list[str]) -> str:
    xml = []
    xml.append("<book>")

    # ---- META ----
    xml.append("<book-meta>")
    xml.append("<book-title-group>")
    xml.append("<book-title>Auto Generated Book</book-title>")
    xml.append("</book-title-group>")
    xml.append("</book-meta>")

    # ---- BODY ----
    xml.append("<book-body>")

    for page in pages:
        xml.append("<book-part>")
        xml.append("<body>")

        for line in page.split("\n"):
            line = line.strip()
            if not line:
                continue

            # ---- HEADING ----
            if line.isupper() and len(line) < 80:
                xml.append("<sec>")
                xml.append(f"<title>{line}</title>")
                xml.append("</sec>")
            else:
                xml.append(f"<p>{line}</p>")

        xml.append("</body>")
        xml.append("</book-part>")

    xml.append("</book-body>")
    xml.append("</book>")

    return "\n".join(xml)
