import re
import subprocess
from pathlib import Path

md_path = Path("docs/ONE_PAGE_SITUATION_REPORT.md")
html_path = Path("docs/ONE_PAGE_SITUATION_REPORT.html")
pdf_path = Path("docs/ONE_PAGE_SITUATION_REPORT.pdf")

content = md_path.read_text(encoding="utf-8")
lines = content.splitlines()

html_lines = []
in_table = False

for line in lines:
    if line.startswith("|") and line.endswith("|"):
        if not in_table:
            html_lines.append("<div class='table-wrapper'><table>")
            in_table = True
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(re.match(r"^:?-+:?$", c) for c in cells):
            continue
        tag = "th" if ("Analytical Metric" in line or "Settlement Name" in line) else "td"
        row_html = "".join(f"<{tag}>{c}</{tag}>" for c in cells)
        html_lines.append(f"<tr>{row_html}</tr>")
        continue
    else:
        if in_table:
            html_lines.append("</table></div>")
            in_table = False

    if line.startswith("# "):
        html_lines.append(f"<h1 class='title'>{line[2:]}</h1>")
    elif line.startswith("## "):
        html_lines.append(f"<h2 class='section-title'>{line[3:]}</h2>")
    elif line.startswith("### "):
        html_lines.append(f"<h3>{line[4:]}</h3>")
    elif line.startswith("---"):
        html_lines.append("<hr/>")
    elif line.startswith("> "):
        p_text = line[2:].strip()
        p_text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', p_text)
        html_lines.append(f"<blockquote class='callout'>{p_text}</blockquote>")
    elif re.match(r"^\d+\.\s+", line):
        item_text = re.sub(r"^\d+\.\s+", "", line)
        item_text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', item_text)
        item_text = re.sub(r'`(.+?)`', r'<code>\1</code>', item_text)
        html_lines.append(f"<div class='numbered-item'>{item_text}</div>")
    elif line.strip() == "":
        continue
    else:
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
  <title>FloodSpaceAI — Executive Disaster Situation Report</title>
  <style>
    @page {{
      size: A4 portrait;
      margin: 8mm 10mm;
    }}
    * {{
      box-sizing: border-box;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
      font-size: 7.2pt;
      line-height: 1.25;
      color: #111;
      margin: 0;
      padding: 0;
    }}
    .title {{
      font-size: 13pt;
      text-align: center;
      margin: 0 0 4px 0;
      color: #0b2538;
      font-weight: 700;
      letter-spacing: -0.3px;
    }}
    .section-title {{
      font-size: 8.5pt;
      font-weight: 700;
      color: #0e3854;
      border-bottom: 1px solid #0e3854;
      margin: 4px 0 2px 0;
      padding-bottom: 1px;
      text-transform: uppercase;
      letter-spacing: 0.3px;
    }}
    p {{
      margin: 1.5px 0;
    }}
    hr {{
      border: 0;
      border-top: 0.5px solid #ccc;
      margin: 3px 0;
    }}
    .table-wrapper {{
      margin: 2px 0;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 6.8pt;
      line-height: 1.15;
    }}
    th, td {{
      border: 0.5px solid #bccad6;
      padding: 1.5px 4px;
      text-align: left;
    }}
    th {{
      background-color: #e9f0f6;
      font-weight: 600;
      color: #0a2540;
    }}
    .callout {{
      background: #fdf5e6;
      border-left: 3px solid #d97706;
      margin: 2px 0;
      padding: 2px 6px;
      font-size: 6.8pt;
      color: #78350f;
    }}
    .numbered-item {{
      margin: 1px 0;
      font-size: 6.5pt;
      line-height: 1.2;
    }}
    code {{
      font-family: Consolas, monospace;
      background: #eef2f6;
      padding: 0 2px;
      font-size: 6.6pt;
    }}
    @media print {{
      body {{
        margin: 0;
        padding: 0;
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
print(f"Generated HTML at {html_path}")

# Run headless Edge to print to PDF
edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
cmd = [
    edge_path,
    "--headless",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={pdf_path.resolve()}",
    str(html_path.resolve())
]

res = subprocess.run(cmd, capture_output=True, text=True)
print(f"Edge conversion exit code: {res.returncode}")

# Verify page count
if pdf_path.exists():
    data = pdf_path.read_bytes()
    pages = re.findall(rb'/Type\s*/Page\b', data)
    print(f"Verified PDF page count: {len(pages)} pages ({len(data)} bytes)")
else:
    print("PDF was not created.")
