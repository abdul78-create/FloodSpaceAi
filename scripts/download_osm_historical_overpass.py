import requests
from pathlib import Path

# ============================================================
# FloodSpaceAI — Historical OSM Bridge Downloader
# Snapshot: 27 July 2026 (pre-flood)
# ============================================================

OUT = Path("data/raw/osm")
OUT.mkdir(parents=True, exist_ok=True)

BBOX = "27.75,84.90,28.05,85.25"
DATE = "2026-07-27T00:00:00Z"

URL = "https://overpass.kumi.systems/api/interpreter"

OUTPUT_FILE = OUT / "bridges_pre_20260727.json"

QUERY = f'''
[out:json][timeout:300][date:"{DATE}"];
way["bridge"]({BBOX});
out tags geom;
'''

print("=" * 60)
print("FloodSpaceAI - Historical OSM Bridge Download")
print("=" * 60)
print()
print("Snapshot :", DATE)
print("AOI      :", BBOX)
print("Output   :", OUTPUT_FILE)
print()

headers = {
    "User-Agent": "FloodSpaceAI/1.0 (educational hackathon project)"
}

try:
    print("Sending request to Overpass...")
    
    response = requests.post(
        URL,
        data={"data": QUERY},
        headers=headers,
        timeout=360
    )

    print("HTTP:", response.status_code)

    if response.status_code != 200:
        print()
        print("ERROR RESPONSE:")
        print(response.text[:2000])
        raise RuntimeError(
            f"Overpass returned HTTP {response.status_code}"
        )

    # Validate that the response is JSON
    try:
        data = response.json()
    except ValueError:
        print("ERROR: Server did not return valid JSON.")
        print(response.text[:2000])
        raise

    # Basic validation
    if "elements" not in data:
        raise RuntimeError(
            "Response does not contain an 'elements' field."
        )

    elements = data["elements"]

    # Save
    OUTPUT_FILE.write_text(
        response.text,
        encoding="utf-8"
    )

    print()
    print("SUCCESS")
    print("-" * 60)
    print("Saved:", OUTPUT_FILE)
    print(
        "Size:",
        round(OUTPUT_FILE.stat().st_size / 1024 / 1024, 2),
        "MB"
    )
    print("Bridge features:", len(elements))
    print()
    print("Historical snapshot:", DATE)
    print("Attribution: © OpenStreetMap contributors")
    print("-" * 60)

except requests.exceptions.Timeout:
    print()
    print("ERROR: Overpass request timed out.")
    print("Do not delete the existing roads/buildings files.")

except requests.exceptions.RequestException as e:
    print()
    print("NETWORK ERROR:")
    print(e)
    print("Do not delete the existing roads/buildings files.")

except Exception as e:
    print()
    print("ERROR:")
    print(e)
    print("Do not delete the existing roads/buildings files.")