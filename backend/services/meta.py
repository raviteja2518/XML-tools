from services.extract import extract_text
from services.rules import apply_rules


def build_meta(type, file_path):
    lines = extract_text(file_path)

    items = apply_rules(lines, section="meta")

    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:epub="http://www.idpf.org/2007/ops"
      xml:lang="de" lang="de">
<head>
<title>Navigational Table of Contents</title>
<link rel="stylesheet" type="text/css" href="styles/stylesheet.css"/>
</head>
<body>
<nav epub:type="toc" role="doc-toc">
<ol>
{chr(10).join(items)}
</ol>
</nav>
</body>
</html>
"""

    return content, "nav.xhtml"
