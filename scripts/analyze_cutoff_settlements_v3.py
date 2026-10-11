import json
import math
from pathlib import Path
from collections import defaultdict, deque

from osgeo import ogr, osr


BASE = Path(".")

ROADS = BASE / "data/raw/osm/roads_pre_20260727.json"
SETTLEMENTS = BASE / "data/raw/osm/settlements_pre_20260727.json"
AFFECTED = BASE / "data/processed/affected_assets/potentially_affected_roads.geojson"

OUT = BASE / "data/processed/connectivity"
OUT.mkdir(parents=True, exist_ok=True)

ALLOWED = {
    "motorway", "motorway_link",
    "trunk", "trunk_link",
    "primary", "primary_link",
    "secondary", "secondary_link",
    "tertiary", "tertiary_link",
    "unclassified", "residential",
    "living_street", "service", "road", "track"
}


def haversine(a, b):
    lon1, lat1 = a
    lon2, lat2 = b

    R = 6371000

    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)

    x = (
        math.sin(dp / 2) ** 2
        + math.cos(p1)
        * math.cos(p2)
        * math.sin(dl / 2) ** 2
    )

    return 2 * R * math.asin(math.sqrt(x))


def key(lon, lat):
    return (round(lon, 7), round(lat, 7))


def components(graph):
    seen = set()
    result = []

    for start in graph:

        if start in seen:
            continue

        comp = set()
        q = deque([start])
        seen.add(start)

        while q:
            u = q.popleft()
            comp.add(u)

            for v in graph.get(u, ()):

                if v not in seen:
                    seen.add(v)
                    q.append(v)

        result.append(comp)

    return result


print("=" * 70)
print("FloodSpaceAI — Conservative Connectivity Analysis V3")
print("=" * 70)


# ------------------------------------------------------------
# Load roads
# ------------------------------------------------------------

data = json.loads(
    ROADS.read_text(encoding="utf-8")
)

ways = []

for e in data["elements"]:

    if e.get("type") != "way":
        continue

    highway = e.get("tags", {}).get("highway")

    if highway not in ALLOWED:
        continue

    geom = e.get("geometry", [])

    if len(geom) < 2:
        continue

    coords = [
        (p["lon"], p["lat"])
        for p in geom
    ]

    ways.append({
        "id": e["id"],
        "coords": coords,
        "highway": highway
    })


print("Vehicle-accessible ways:", len(ways))


# ------------------------------------------------------------
# Load affected roads
# ------------------------------------------------------------

ds = ogr.Open(str(AFFECTED))
layer = ds.GetLayer()

affected = []

for f in layer:

    g = f.GetGeometryRef()

    if g:
        affected.append(g.Clone())


print("Potentially affected road features:", len(affected))


# ------------------------------------------------------------
# Coordinate transform
# ------------------------------------------------------------

src = osr.SpatialReference()
src.ImportFromEPSG(4326)

dst = osr.SpatialReference()
dst.ImportFromEPSG(32645)

transform = osr.CoordinateTransformation(
    src, dst
)


def metric_line(coords):

    line = ogr.Geometry(ogr.wkbLineString)

    for lon, lat in coords:

        p = ogr.Geometry(ogr.wkbPoint)
        p.AddPoint(lon, lat)
        p.Transform(transform)

        line.AddPoint(
            p.GetX(),
            p.GetY()
        )

    return line


affected_metric = []

for g in affected:

    x = g.Clone()
    x.Transform(transform)
    affected_metric.append(x)


# ------------------------------------------------------------
# Determine disrupted ROAD SEGMENTS
# ------------------------------------------------------------

print("\nFinding disrupted road segments...")

disrupted_segments = set()

for way in ways:

    coords = way["coords"]

    for i in range(len(coords) - 1):

        segment = metric_line([
            coords[i],
            coords[i + 1]
        ])

        # 20 m disruption tolerance.
        test = segment.Buffer(20)

        hit = False

        for flood_road in affected_metric:

            if test.Intersects(flood_road):
                hit = True
                break

        if hit:
            disrupted_segments.add(
                (
                    way["id"],
                    i
                )
            )


print(
    "Disrupted road segments:",
    len(disrupted_segments)
)


# ------------------------------------------------------------
# Build PRE and POST graphs
# ------------------------------------------------------------

pre = defaultdict(set)
post = defaultdict(set)

for way in ways:

    coords = way["coords"]

    for i in range(len(coords) - 1):

        a = key(*coords[i])
        b = key(*coords[i + 1])

        if a == b:
            continue

        pre[a].add(b)
        pre[b].add(a)

        if (way["id"], i) not in disrupted_segments:

            post[a].add(b)
            post[b].add(a)


print("Pre-event graph nodes:", len(pre))
print("Post-event graph nodes:", len(post))

pre_components = components(pre)
post_components = components(post)

pre_lookup = {}

for i, c in enumerate(pre_components):
    for n in c:
        pre_lookup[n] = i

post_lookup = {}

for i, c in enumerate(post_components):
    for n in c:
        post_lookup[n] = i


print("Pre-event components:", len(pre_components))
print("Post-event components:", len(post_components))


# ------------------------------------------------------------
# Settlements
# ------------------------------------------------------------

settlement_data = json.loads(
    SETTLEMENTS.read_text(
        encoding="utf-8"
    )
)

settlements = []

for e in settlement_data["elements"]:

    tags = e.get("tags", {})
    place = tags.get("place")

    if place not in {
        "city",
        "town",
        "village",
        "hamlet"
    }:
        continue

    if e["type"] == "node":

        lat = e.get("lat")
        lon = e.get("lon")

    else:

        center = e.get("center")

        if not center:
            continue

        lat = center["lat"]
        lon = center["lon"]

    if lat is None or lon is None:
        continue

    settlements.append({
        "id": e["id"],
        "name": tags.get(
            "name",
            f"OSM-{e['id']}"
        ),
        "place": place,
        "point": (lon, lat)
    })


print("Settlements:", len(settlements))


# ------------------------------------------------------------
# Nearest graph node
# ------------------------------------------------------------

graph_nodes = list(pre.keys())


def nearest_node(point, max_distance=500):

    best = None
    best_d = float("inf")

    for n in graph_nodes:

        d = haversine(
            point,
            n
        )

        if d < best_d:
            best_d = d
            best = n

    if best_d > max_distance:
        return None, best_d

    return best, best_d


for s in settlements:

    n, d = nearest_node(
        s["point"]
    )

    s["road_node"] = n
    s["road_distance_m"] = d


# ------------------------------------------------------------
# Town/city hubs
# ------------------------------------------------------------

hubs = [
    s for s in settlements
    if s["place"] in {"town", "city"}
    and s["road_node"] is not None
]

print("Town/city hubs:", len(hubs))

for h in hubs:
    print(
        "  -",
        h["name"],
        "(" + h["place"] + ")"
    )


# ------------------------------------------------------------
# Connectivity
# ------------------------------------------------------------

results = []

for s in settlements:

    sn = s["road_node"]

    if sn is None:
        continue

    # Ignore settlements more than 500 m from
    # the mapped road network.
    if s["road_distance_m"] > 500:
        continue

    # Choose geographically nearest town/city.
    hub = min(
        hubs,
        key=lambda h:
        haversine(
            s["point"],
            h["point"]
        )
    )

    hn = hub["road_node"]

    pre_connected = (
        pre_lookup.get(sn)
        == pre_lookup.get(hn)
    )

    post_connected = (
        post_lookup.get(sn)
        == post_lookup.get(hn)
    )

    cutoff = (
        pre_connected
        and not post_connected
    )

    results.append({
        "name": s["name"],
        "place": s["place"],
        "lat": s["point"][1],
        "lon": s["point"][0],
        "nearest_town_or_city": hub["name"],
        "nearest_hub_type": hub["place"],
        "road_distance_m": round(
            s["road_distance_m"], 1
        ),
        "connected_before": pre_connected,
        "connected_after": post_connected,
        "potentially_cut_off": cutoff
    })


cutoff = [
    r for r in results
    if r["potentially_cut_off"]
]


# ------------------------------------------------------------
# Save
# ------------------------------------------------------------

(OUT / "settlement_connectivity_v3.json").write_text(
    json.dumps(
        results,
        indent=2,
        ensure_ascii=False
    ),
    encoding="utf-8"
)

(OUT / "potentially_cut_off_settlements_v3.json").write_text(
    json.dumps(
        cutoff,
        indent=2,
        ensure_ascii=False
    ),
    encoding="utf-8"
)

features = []

for r in cutoff:

    features.append({
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [
                r["lon"],
                r["lat"]
            ]
        },
        "properties": {
            k: v
            for k, v in r.items()
            if k not in {"lon", "lat"}
        }
    })


geojson = {
    "type": "FeatureCollection",
    "features": features
}


(OUT / "potentially_cut_off_settlements_v3.geojson").write_text(
    json.dumps(
        geojson,
        indent=2,
        ensure_ascii=False
    ),
    encoding="utf-8"
)


print()
print("=" * 70)
print("V3 COMPLETE")
print("=" * 70)
print("Settlements analysed:", len(results))
print("Potentially cut-off:", len(cutoff))
print()
print("Output:")
print(OUT / "potentially_cut_off_settlements_v3.geojson")
print()
print("IMPORTANT: modelled connectivity, not confirmed isolation.")
print("=" * 70)