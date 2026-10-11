from pathlib import Path
import re

pdf_path = Path("docs/FLOODSPACEAI_TECHNICAL_REPORT.pdf")
data = pdf_path.read_bytes()

# Search for /Count or /Type /Page
page_matches = re.findall(rb'/Type\s*/Page\b', data)
count_match = re.search(rb'/Count\s+(\d+)', data)

print(f"=== PDF REPORT INSPECTION ===")
print(f"Path: {pdf_path}")
print(f"Size: {len(data)} bytes ({len(data)/1024:.1f} KB)")
print(f"Page Count (Page Objects): {len(page_matches)}")
if count_match:
    print(f"Page Count (/Count field): {count_match.group(1).decode('ascii')}")
