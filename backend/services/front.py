from services.extract import extract_text
from services.rules import apply_rules


def build_front(type, file_path):
    # 1. Extract RAW TEXT ONLY
    lines = extract_text(file_path)

    # 2. Apply HARD-CODED RULES + CLIENT TAGS
    body = apply_rules(lines, section="front")

    # 3. Wrap in client XHTML structure
    content = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>Front Matter</title>
<link rel="stylesheet" type="text/css" href="../styles/stylesheet.css"/>
</head>
<body>
<section epub:type="frontmatter">
{chr(10).join(body)}
</section>
</body>
</html>
"""

    return content, "front.xhtml"
