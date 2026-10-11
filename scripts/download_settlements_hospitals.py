import json
from pathlib import Path

import requests


# ============================================================
# FloodSpaceAI — Historical Settlements & Hospitals
# Snapshot: 27 July 2026
# ============================================================

OUT = Path("data/raw/osm")
OUT.mkdir(parents=True, exist_ok=True)

BBOX = "27.75,84.90,28.05,85.25"
DATE = "2026-07-27T00:00:00Z"

URL = "https://overpass.kumi.systems/api/interpreter"

HEADERS = {
    "User-Agent": "FloodSpaceAI/1.0 educational hackathon project"
}


QUERIES = {

    # Populated places: villages, towns, cities, etc.
    "settlements_pre_20260727.json": f'''
[out:json][timeout:300][date:"{DATE}"];
(
  node["place"]({BBOX});
  way["place"]({BBOX});
  relation["place"]({BBOX});
);
out center;
''',

    # Hospitals and healthcare facilities.
    "hospitals_pre_20260727.json": f'''
[out:json][timeout:300][date:"{DATE}"];
(
  node["amenity"="hospital"]({BBOX});
  way["amenity"="hospital"]({BBOX});
  relation["amenity"="hospital"]({BBOX});

  node["amenity"="clinic"]({BBOX});
  way["amenity"="clinic"]({BBOX});
  relation["amenity"="clinic"]({BBOX});
);
out center;
'''
}


def download(filename, query):

    output = OUT / filename

    print()
    print("=" * 60)
    print("Downloading:", filename)
    print("=" * 60)

    response = requests.post(
        URL,
        data={"data": query},
        headers=HEADERS,
        timeout=360,
    )

    print("HTTP:", response.status_code)

    if response.status_code != 200:
        print(response.text[:2000])
        raise RuntimeError(
            f"Overpass request failed: HTTP {response.status_code}"
        )

    data = response.json()

    elements = data.get("elements", [])

    output.write_text(
        response.text,
        encoding="utf-8"
    )

    print("Saved:", output)
    print(
        "Features:",
        len(elements)
    )
    print(
        "Size:",
        round(
            output.stat().st_size / 1024 / 1024,
            2
        ),
        "MB"
    )

    return elements


def main():

    print("=" * 60)
    print("FloodSpaceAI")
    print("Historical OSM Reference Locations")
    print("=" * 60)

    print()
    print("Snapshot:", DATE)
    print("AOI:", BBOX)

    results = {}

    for filename, query in QUERIES.items():

        results[filename] = download(
            filename,
            query
        )

    print()
    print("=" * 60)
    print("DOWNLOAD COMPLETE")
    print("=" * 60)

    print()
    print(
        "Settlements:",
        len(
            results[
                "settlements_pre_20260727.json"
            ]
        )
    )

    print(
        "Hospitals/clinics:",
        len(
            results[
                "hospitals_pre_20260727.json"
            ]
        )
    )

    print()
    print(
        "Attribution: © OpenStreetMap contributors"
    )


if __name__ == "__main__":
    main()