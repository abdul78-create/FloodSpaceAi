import re
from pathlib import Path

report_path = Path("docs/FLOODSPACEAI_TECHNICAL_REPORT.md")
text = report_path.read_text(encoding="utf-8")
words = len(re.findall(r'\b\w+\b', text))
lines = len(text.splitlines())
chars = len(text)

print(f"=== TECHNICAL REPORT METRICS ===")
print(f"File: {report_path}")
print(f"Total Lines: {lines}")
print(f"Total Characters: {chars}")
print(f"Total Word Count: {words}")
print(f"Estimated Standard 2-Column Academic Pages (~500 words/page): {words / 500:.2f} pages")
print(f"Estimated Standard Single-Column 1.5-spaced Pages (~350 words/page): {words / 350:.2f} pages")

# Check required sections:
required_headers = [
    "Abstract",
    "Introduction & Operational Motivation",
    "Multi-Sensor Remote Sensing & Flood Extraction",
    "Historical Infrastructure & Network Graph Topology",
    "Evidence-Grounded AI Architecture & Adversarial Defenses",
    "Independent Validation: Copernicus EMSR927",
    "Software Engineering & Empirical Verification",
    "Authoritative Attributions, Licensing & Ethics",
    "Conclusion"
]

print("\n=== SECTION COMPLETENESS CHECK ===")
for h in required_headers:
    present = h.lower() in text.lower()
    print(f"  [{'OK' if present else 'MISSING'}] {h}")

print("\n=== ATTRIBUTION CHECK ===")
attributions = ["Copernicus Sentinel", "Copernicus DEM", "OpenStreetMap", "Copernicus Emergency Management Service", "EMSR927"]
for a in attributions:
    present = a.lower() in text.lower()
    print(f"  [{'OK' if present else 'MISSING'}] {a}")
