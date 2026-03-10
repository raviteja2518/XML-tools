def build_ln_xml_from_pages(pages):
    xml = ['<lnxml>']

    for idx, page in enumerate(pages, start=1):
        xml.append(f'<page number="{idx}">')

        for line in page.split("\n"):
            if line.isupper():
                xml.append(f'<h2>{line}</h2>')
            else:
                xml.append(f'<p>{line}</p>')

        xml.append('</page>')

    xml.append('</lnxml>')
    return "\n".join(xml)
