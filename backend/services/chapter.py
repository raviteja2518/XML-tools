from services.extract import extract_text
from services.rules import apply_rules


def build_chapter(type, file_path):
    lines = extract_text(file_path)
    body = apply_rules(lines, section="chapter")

    content = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>Chapter</title>
<link rel="stylesheet" type="text/css" href="../styles/stylesheet.css"/>
</head>
<body>
<section epub:type="chapter">
{chr(10).join(body)}
</section>
</body>
</html>
"""

    return content, "chapter.xhtml"
