import json
from pathlib import Path

from osgeo import ogr, osr


BASE = Path(".")

AFFECTED_FILE = (
    BASE
    / "data/processed/affected_assets/"
    / "potentially_affected_roads.geojson"
)

CONNECTIVITY_FILE = (
    BASE
    / "data/processed/connectivity/"
    / "potentially_cut_off_settlements_v3.json"
)

OUT = BASE / "data/processed/road_impact"
OUT.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# WGS84 -> UTM 45N
# ------------------------------------------------------------

src = osr.SpatialReference()
src.ImportFromEPSG(4326)

dst = osr.SpatialReference()
dst.ImportFromEPSG(32645)

transform = osr.CoordinateTransformation(
    src,
    dst
)


def length_km(geom):

    g = geom.Clone()
    g.Transform(transform)

    return g.Length() / 1000.0


# ------------------------------------------------------------
# Open affected roads
# ------------------------------------------------------------

print("=" * 65)
print("FloodSpaceAI — Road Impact Summary")
print("=" * 65)

ds = ogr.Open(
    str(AFFECTED_FILE)
)

if ds is None:
    raise RuntimeError(
        "Could not open affected-road GeoJSON."
    )

layer = ds.GetLayer()

print(
    "Available fields:",
    [
        layer.GetLayerDefn()
        .GetFieldDefn(i)
        .GetName()
        for i in range(
            layer.GetLayerDefn()
            .GetFieldCount()
        )
    ]
)


total_km = 0.0
count = 0

for feature in layer:

    geom = feature.GetGeometryRef()

    if geom is None:
        continue

    total_km += length_km(
        geom
    )

    count += 1


# ------------------------------------------------------------
# Load V3 cutoff results
# ------------------------------------------------------------

cutoff_count = 0

if CONNECTIVITY_FILE.exists():

    cutoff_data = json.loads(
        CONNECTIVITY_FILE.read_text(
            encoding="utf-8"
        )
    )

    cutoff_count = len(
        cutoff_data
    )


# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------

summary = {
    "potentially_affected_road_features": count,
    "potentially_affected_road_length_km": round(
        total_km,
        3
    ),
    "potentially_cut_off_settlements_v3": cutoff_count,
    "road_class_breakdown": None,
    "note": (
        "Road-class breakdown unavailable because "
        "the affected-road GeoJSON does not contain "
        "road-class attributes."
    )
}


output = (
    OUT
    / "road_impact_summary.json"
)

output.write_text(
    json.dumps(
        summary,
        indent=2
    ),
    encoding="utf-8"
)


print()
print(
    "Potentially affected road features:",
    count
)

print(
    "Potentially affected road length:",
    round(
        total_km,
        3
    ),
    "km"
)

print(
    "Potentially cut-off settlements:",
    cutoff_count
)

print()
print(
    "Road-class breakdown: unavailable "
    "(source GeoJSON has no road-class field)"
)

print()
print("Saved:")
print(output)

print()
print(
    "IMPORTANT: these are modelled/potential impacts."
)

print("=" * 65)