import sys
from pathlib import Path

from markdown_it import MarkdownIt

md_path = Path(sys.argv[1])
html_path = md_path.with_suffix(".html")

md = MarkdownIt().enable("table")

html_content = md.render(md_path.read_text(encoding="utf-8"))

full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Community Analysis Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; line-height: 1.6; max-width: 900px; margin: 40px auto; padding: 0 20px; color: #333; }}
        h1, h2, h3 {{ border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
        table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
        th, td {{ border: 1px solid #dfe2e5; padding: 6px 13px; }}
        th {{ background-color: #f6f8fa; }}
        code {{ background-color: rgba(27,31,35,0.05); padding: 0.2em 0.4em; border-radius: 3px; font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace; font-size: 85%; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""

html_path.write_text(full_html, encoding="utf-8")
print("HTML generated successfully with tables")
