from xml.etree.ElementTree import Element, SubElement, ElementTree

XLINK = "http://www.w3.org/1999/xlink"

def build_ref_list_xml(refs, uid):
    root = Element("ref-list", {"id": f"book-{uid}-refs1"})
    title = SubElement(root, "title")
    title.text = "References"

    for i, r in enumerate(refs, start=1):
        ref = SubElement(root, "ref", {
            "id": f"book-{uid}-ref{str(i).zfill(3)}"
        })

        mixed = SubElement(ref, "mixed-citation", {
            "publication-type": r["type"]
        })

        # Authors
        if r["authors"]:
            pg = SubElement(mixed, "person-group", {
                "person-group-type": "author"
            })
            for idx, a in enumerate(r["authors"]):
                sn = SubElement(pg, "string-name")
                s = SubElement(sn, "surname")
                s.text = a["surname"]
                g = SubElement(sn, "given-names")
                g.text = a["given-names"]
                if idx < len(r["authors"]) - 1:
                    sn.tail = ", "

        # Collab
        if r["collab"]:
            c = SubElement(mixed, "collab")
            c.text = r["collab"]

        # Year
        if r["year"]:
            y = SubElement(mixed, "year")
            y.text = r["year"]

        # Article title
        if r["article_title"]:
            at = SubElement(mixed, "article-title")
            at.text = r["article_title"]

        # Source
        src = SubElement(mixed, "source")
        it = SubElement(src, "italic")
        it.text = r["source"]

        # Volume / Issue / Pages
        if r["volume"]:
            SubElement(mixed, "volume").text = r["volume"]
        if r["issue"]:
            SubElement(mixed, "issue").text = r["issue"]
        if r["fpage"]:
            SubElement(mixed, "fpage").text = r["fpage"]
        if r["lpage"]:
            SubElement(mixed, "lpage").text = r["lpage"]

        # Publisher
        if r["publisher"]:
            SubElement(mixed, "publisher-name").text = r["publisher"]

        # URL
        if r["url"]:
            ext = SubElement(
                mixed,
                "ext-link",
                {
                    "ext-link-type": "uri",
                    f"{{{XLINK}}}href": r["url"]
                }
            )
            ext.text = r["url"]

    out = f"outputs/{uid}_refs.xml"
    ElementTree(root).write(out, encoding="utf-8", xml_declaration=True)
    return out
