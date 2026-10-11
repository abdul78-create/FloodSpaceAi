import json
from pathlib import Path
import requests

OUT = Path("data/raw/osm")
OUT.mkdir(parents=True, exist_ok=True)

BBOX = "27.75,84.90,28.05,85.25"
DATE = "2026-07-27T00:00:00Z"

URL = "https://overpass.kumi.systems/api/interpreter"

query = f'''
[out:json][timeout:180][date:"{DATE}"];
node["amenity"="hospital"]({BBOX});
out;
'''

print("Downloading historical hospitals...")
print("Snapshot:", DATE)

r = requests.post(
    URL,
    data={"data": query},
    headers={"User-Agent": "FloodSpaceAI/1.0"},
    timeout=240
)

print("HTTP:", r.status_code)

if r.status_code != 200:
    print(r.text[:2000])
    raise SystemExit("Hospital query failed.")

data = r.json()

path = OUT / "hospitals_pre_20260727.json"

path.write_text(
    json.dumps(data, indent=2),
    encoding="utf-8"
)

print("Saved:", path)
print("Hospitals:", len(data.get("elements", [])))