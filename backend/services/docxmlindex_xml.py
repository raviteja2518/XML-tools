import re, html

PAGE_RE = re.compile(r"(\d+)\s*([ft]{1,2})?")

def make_links(text):
    found = PAGE_RE.findall(text)
    if not found: return ""
    links = []
    for p, f in found:
        l = f'<ulink url="#page{p}">{p}</ulink>'
        if f: l += f'<emphasis role="italic">{f}</emphasis>'
        links.append(l)
    return ", ".join(links)

def build_index_xml(text_blocks):
    header = '<?xml version="1.0" encoding="UTF-8"?>\n<index id="index">\n<title>Index</title>\n'
    body = ""
    current_div = ""

    for block in text_blocks:
        lines = block.splitlines()
        for line in lines:
            if not line.strip(): continue
            
            # Indent count chesi hierarchy decide chestunnam
            indent = len(line) - len(line.lstrip())
            term = PAGE_RE.sub("", line).strip(",. ")
            links = make_links(line)
            
            # Alphabet Division (A, B, C...)
            first_char = term[0].upper() if term else ""
            if first_char.isalpha() and first_char != current_div:
                if current_div: body += "</indexdiv>\n"
                current_div = first_char
                body += f"<indexdiv>\n<title>{current_div}</title>\n"

            # XML Tag Mapping
            escaped_term = html.escape(term)
            if indent == 0:
                body += f"<indexentry><primaryie>{escaped_term} {links}</primaryie></indexentry>\n"
            elif 1 <= indent <= 4:
                body += f"<secondaryie>{escaped_term} {links}</secondaryie>\n"
            else:
                body += f"<tertiaryie>{escaped_term} {links}</tertiaryie>\n"

    return header + body + "</indexdiv>\n</index>"