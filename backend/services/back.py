from services.extract import extract_text
from services.rules import apply_rules


def build_back(type, file_path):
    lines = extract_text(file_path)
    body = apply_rules(lines, section="back")

    content = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>Back Matter</title>
<link rel="stylesheet" type="text/css" href="../styles/stylesheet.css"/>
</head>
<body>
<section epub:type="backmatter">
{chr(10).join(body)}
</section>
</body>
</html>
"""

    return content, "back.xhtml"
