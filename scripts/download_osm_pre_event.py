from pathlib import Path
import requests
import time

BASE_URL = "https://api.ohsome.org/v1/elements/geometry"

AOI = "84.90,27.75,85.25,28.05"
SNAPSHOT = "2026-07-27T00:00:00Z"

OUT_DIR = Path("data/raw/osm")
OUT_DIR.mkdir(parents=True, exist_ok=True)

DATASETS = {
    "buildings_pre_20260727.geojson": "building=* and type:way",
    "roads_pre_20260727.geojson": "highway=* and type:way",
    "bridges_pre_20260727.geojson": "bridge=* and type:way",
}

session = requests.Session()
session.headers.update({
    "User-Agent": "FloodSpaceAI/1.0 educational hackathon project"
})

for filename, osm_filter in DATASETS.items():
    output = OUT_DIR / filename

    print(f"\nDownloading: {filename}")
    print(f"Filter: {osm_filter}")

    params = {
        "bboxes": AOI,
        "time": SNAPSHOT,
        "filter": osm_filter,
        "properties": "tags,metadata",
        "clipGeometry": "true",
    }

    for attempt in range(1, 4):
        try:
            response = session.get(
                BASE_URL,
                params=params,
                timeout=180
            )

            print("HTTP:", response.status_code)

            response.raise_for_status()

            output.write_text(response.text, encoding="utf-8")

            print(f"Saved: {output}")
            print(f"Size: {output.stat().st_size / 1024 / 1024:.2f} MB")
            break

        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")

            if attempt == 3:
                raise

            time.sleep(5)

print("\nOSM PRE-EVENT DOWNLOAD COMPLETE")
print(f"Snapshot: {SNAPSHOT}")
print(f"AOI: {AOI}")
print(f"Output: {OUT_DIR}")
print("\nAttribution: © OpenStreetMap contributors")