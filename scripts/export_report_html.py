import re
from pathlib import Path

md_path = Path("docs/FLOODSPACEAI_TECHNICAL_REPORT.md")
html_path = Path("docs/FLOODSPACEAI_TECHNICAL_REPORT.html")

content = md_path.read_text(encoding="utf-8")

# Basic markdown parser for clean technical styling
# Convert headers
lines = content.splitlines()
html_lines = []
in_code = False
in_table = False

for line in lines:
    if line.startswith("```"):
        if in_code:
            html_lines.append("</pre>")
            in_code = False
        else:
            lang = line[3:].strip()
            html_lines.append(f"<pre class='code-block {lang}'>")
            in_code = True
        continue
    if in_code:
        html_lines.append(line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
        continue

    if line.startswith("|") and line.endswith("|"):
        if not in_table:
            html_lines.append("<div class='table-wrapper'><table>")
            in_table = True
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(re.match(r"^:?-+:?$", c) for c in cells):
            continue # separator
        tag = "th" if "Claim ID" in line or "Evaluation Metric" in line or "Tier" in line or "Analytical Metric" in line else "td"
        row_html = "".join(f"<{tag}>{c}</{tag}>" for c in cells)
        html_lines.append(f"<tr>{row_html}</tr>")
        continue
    else:
        if in_table:
            html_lines.append("</table></div>")
            in_table = False

    if line.startswith("# "):
        html_lines.append(f"<h1>{line[2:]}</h1>")
    elif line.startswith("## "):
        html_lines.append(f"<h2>{line[3:]}</h2>")
    elif line.startswith("### "):
        html_lines.append(f"<h3>{line[4:]}</h3>")
    elif line.startswith("#### "):
        html_lines.append(f"<h4>{line[5:]}</h4>")
    elif line.startswith("---"):
        html_lines.append("<hr/>")
    elif line.startswith("- "):
        html_lines.append(f"<li>{line[2:]}</li>")
    elif line.strip() == "":
        html_lines.append("<p></p>")
    else:
        # Bold and italic formatting
        p_text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
        p_text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', p_text)
        p_text = re.sub(r'`(.+?)`', r'<code>\1</code>', p_text)
        html_lines.append(f"<p>{p_text}</p>")

if in_table:
    html_lines.append("</table></div>")

body_html = "\n".join(html_lines)

full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>FloodSpaceAI Technical Report — Multimodal AI Hackathon 2026</title>
  <style>
    @page {{
      size: A4;
      margin: 12mm 15mm;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 9pt;
      line-height: 1.35;
      color: #111;
      max-width: 100%;
      margin: 0;
      padding: 0;
    }}
    h1 {{
      font-size: 16pt;
      text-align: center;
      margin-top: 0;
      margin-bottom: 4px;
      color: #0b1a24;
    }}
    h2 {{
      font-size: 11pt;
      border-bottom: 1px solid #ccc;
      padding-bottom: 2px;
      margin-top: 12px;
      margin-bottom: 4px;
      color: #1a364a;
    }}
    h3 {{
      font-size: 9.5pt;
      margin-top: 8px;
      margin-bottom: 2px;
      color: #2c4c62;
    }}
    h4 {{
      font-size: 9pt;
      margin-top: 6px;
      margin-bottom: 2px;
    }}
    p {{
      margin: 3px 0;
      text-align: justify;
    }}
    .table-wrapper {{
      overflow-x: auto;
      margin: 6px 0;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 8pt;
      line-height: 1.2;
    }}
    th, td {{
      border: 1px solid #bbb;
      padding: 3px 6px;
      text-align: left;
    }}
    th {{
      background-color: #f0f4f7;
      font-weight: 600;
    }}
    pre.code-block {{
      background: #f7f9fa;
      border: 1px solid #ddd;
      padding: 5px;
      font-family: 'Consolas', 'Courier New', monospace;
      font-size: 7pt;
      line-height: 1.15;
      overflow-x: auto;
      margin: 4px 0;
    }}
    code {{
      font-family: 'Consolas', 'Courier New', monospace;
      background: #f0f2f4;
      padding: 1px 3px;
      font-size: 8pt;
      border-radius: 2px;
    }}
    hr {{
      border: 0;
      border-top: 1px solid #ddd;
      margin: 8px 0;
    }}
    li {{
      margin: 2px 0 2px 16px;
    }}
    @media print {{
      body {{
        padding: 0;
        max-width: 100%;
      }}
    }}
  </style>
</head>
<body>
{body_html}
</body>
</html>
"""

html_path.write_text(full_html, encoding="utf-8")
print(f"Exported printable HTML technical report to {html_path}")
