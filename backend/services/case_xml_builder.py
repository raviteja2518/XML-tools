from xml.etree.ElementTree import Element, SubElement, ElementTree
import os

def build_ref_list_xml(parsed_data: dict, job_id: str):
    """
    Builds LN COURTCASE XML skeleton using ONLY approved tags
    """

    root = Element("COURTCASE")

    # ================= DOC META =================
    docinfo = SubElement(root, "lndocmeta:docinfo")

    SubElement(docinfo, "lndocmeta:lnlni", {"lnlni": ""})
    SubElement(docinfo, "lndocmeta:lnminrev", {"lnminrev": "00000"})
    SubElement(docinfo, "lndocmeta:smi", {"lnsmi": "0000"})
    SubElement(docinfo, "lndocmeta:dpsi", {"lndpsi": "0000"})
    SubElement(docinfo, "lndocmeta:lnsourcedocid", {"lnsourcedocid": ""})

    SubElement(
        docinfo,
        "lndocmeta:lndoctype",
        {"lndoctypename": "COURTCASE"}
    )

    SubElement(
        docinfo,
        "lndocmeta:lndoctypeversion",
        {
            "lndoctypeversionmajor": "06",
            "lndoctypeversionminor": "000"
        }
    )

    SubElement(
        docinfo,
        "lndocmeta:lndoctypelang",
        {"lndoctypelang": "EN"}
    )

    SubElement(
        docinfo,
        "lndocmeta:lnfilenum",
        {"lnfilenum": "001"}
    )

    fab = SubElement(docinfo, "lndocmeta:fabinfo")
    SubElement(
        fab,
        "lndocmeta:fabinfoitem",
        {"name": "B4DBNO", "value": "0000"}
    )

    # ================= CASE DETAILS =================
    SubElement(root, "lnv:FULL-NAME").text = parsed_data.get("full_name", "")
    SubElement(root, "lnv:SHORT-NAME").text = parsed_data.get("short_name", "")
    SubElement(root, "lnv:NUMBER").text = parsed_data.get("docket_number", "")
    SubElement(root, "lnv:COURT").text = parsed_data.get("court", "")
    SubElement(root, "lnv:CITE").text = parsed_data.get("citation", "")

    # ================= DATES =================
    if parsed_data.get("argued_date"):
        ad = SubElement(root, "lnv:ARGUEDDATE")
        SubElement(ad, "lnvxe:date").text = parsed_data["argued_date"]

    if parsed_data.get("decided_date"):
        dd = SubElement(root, "lnv:DECIDEDDATE")
        SubElement(dd, "lnvxe:date").text = parsed_data["decided_date"]

    if parsed_data.get("filed_date"):
        fd = SubElement(root, "lnv:FILEDDATE")
        SubElement(fd, "lnvxe:date").text = parsed_data["filed_date"]

    # ================= OPINION =================
    opinion = SubElement(root, "lnv:OPINION")
    p = SubElement(opinion, "p", {"i": "3"})
    SubElement(p, "lnvxe:text").text = parsed_data.get("opinion_text", "")

    # ================= OUTPUT =================
    os.makedirs("outputs", exist_ok=True)
    out_path = f"outputs/{job_id}.xml"

    ElementTree(root).write(
        out_path,
        encoding="utf-8",
        xml_declaration=True
    )

    return out_path
