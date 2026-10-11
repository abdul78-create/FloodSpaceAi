import json
import math
from pathlib import Path
from collections import defaultdict, deque

from osgeo import ogr, osr


BASE = Path(".")

ROADS = BASE / "data/raw/osm/roads_pre_20260727.json"
SETTLEMENTS = BASE / "data/raw/osm/settlements_pre_20260727.json"

AFFECTED_ROADS = (
    BASE
    / "data/processed/affected_assets_v3/"
    / "potentially_affected_roads_v3.geojson"
)

OUT = BASE / "data/processed/connectivity_v4"
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


MATCH_TOLERANCE_M = 5
SETTLEMENT_SNAP_M = 500


def haversine(a, b):

    lon1, lat1 = a
    lon2, lat2 = b

    R = 6371000.0

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

    return 2 * R * math.asin(
        math.sqrt(x)
    )


def node_key(lon, lat):

    return (
        round(lon, 7),
        round(lat, 7)
    )


def components(graph):

    seen = set()
    result = []

    for start in graph:

        if start in seen:
            continue

        component = set()

        queue = deque([start])
        seen.add(start)

        while queue:

            current = queue.popleft()

            component.add(current)

            for nxt in graph.get(
                current,
                ()
            ):

                if nxt not in seen:

                    seen.add(nxt)
                    queue.append(nxt)

        result.append(component)

    return result


def metric_line(coords, transform):

    line = ogr.Geometry(
        ogr.wkbLineString
    )

    for lon, lat in coords:

        point = ogr.Geometry(
            ogr.wkbPoint
        )

        point.AddPoint(
            lon,
            lat
        )

        point.Transform(
            transform
        )

        line.AddPoint(
            point.GetX(),
            point.GetY()
        )

    return line


print("=" * 70)
print("FloodSpaceAI — Conservative Settlement Connectivity V4")
print("=" * 70)


# ============================================================
# LOAD ROADS
# ============================================================

print("\nLoading historical OSM roads...")

road_data = json.loads(
    ROADS.read_text(
        encoding="utf-8"
    )
)

ways = []

for element in road_data["elements"]:

    if element.get("type") != "way":
        continue

    highway = element.get(
        "tags",
        {}
    ).get(
        "highway"
    )

    if highway not in ALLOWED:
        continue

    geometry = element.get(
        "geometry",
        []
    )

    if len(geometry) < 2:
        continue

    coords = [
        (
            p["lon"],
            p["lat"]
        )
        for p in geometry
    ]

    ways.append({
        "id": element["id"],
        "highway": highway,
        "coords": coords
    })


print(
    "Vehicle-accessible ways:",
    len(ways)
)


# ============================================================
# LOAD V3 AFFECTED ROADS
# ============================================================

print(
    "\nLoading V3 potentially affected roads..."
)

affected_ds = ogr.Open(
    str(AFFECTED_ROADS)
)

if affected_ds is None:
    raise RuntimeError(
        "Could not open V3 affected-road layer."
    )

affected_layer = (
    affected_ds.GetLayer()
)

affected_geometries = []

for feature in affected_layer:

    geometry = feature.GetGeometryRef()

    if geometry:
        affected_geometries.append(
            geometry.Clone()
        )


print(
    "V3 affected road features:",
    len(affected_geometries)
)


# ============================================================
# COORDINATE TRANSFORM
# ============================================================

wgs84 = osr.SpatialReference()
wgs84.ImportFromEPSG(4326)

utm45 = osr.SpatialReference()
utm45.ImportFromEPSG(32645)

to_utm = osr.CoordinateTransformation(
    wgs84,
    utm45
)


affected_metric = []

for geometry in affected_geometries:

    g = geometry.Clone()

    g.Transform(
        to_utm
    )

    affected_metric.append(
        g
    )


# ============================================================
# IDENTIFY DISRUPTED ROAD SEGMENTS
# ============================================================

print(
    "\nFinding disrupted road segments..."
)

disrupted_segments = set()

for index, way in enumerate(ways):

    coords = way["coords"]

    for segment_index in range(
        len(coords) - 1
    ):

        segment = metric_line(
            [
                coords[segment_index],
                coords[segment_index + 1]
            ],
            to_utm
        )

        # Small tolerance to account for
        # geometry/resampling differences.
        test = segment.Buffer(
            MATCH_TOLERANCE_M
        )

        for affected in affected_metric:

            if test.Intersects(
                affected
            ):

                disrupted_segments.add(
                    (
                        way["id"],
                        segment_index
                    )
                )

                break


print(
    "Disrupted road segments:",
    len(disrupted_segments)
)


# ============================================================
# BUILD ROAD GRAPHS
# ============================================================

print(
    "\nBuilding road networks..."
)

pre_graph = defaultdict(set)
post_graph = defaultdict(set)

for way in ways:

    coords = way["coords"]

    for i in range(
        len(coords) - 1
    ):

        a = node_key(
            *coords[i]
        )

        b = node_key(
            *coords[i + 1]
        )

        if a == b:
            continue

        pre_graph[a].add(b)
        pre_graph[b].add(a)

        if (
            way["id"],
            i
        ) not in disrupted_segments:

            post_graph[a].add(b)
            post_graph[b].add(a)


print(
    "Pre-event graph nodes:",
    len(pre_graph)
)

print(
    "Post-event graph nodes:",
    len(post_graph)
)


# ============================================================
# COMPONENTS
# ============================================================

print(
    "\nCalculating connected components..."
)

pre_components = components(
    pre_graph
)

post_components = components(
    post_graph
)

pre_lookup = {}

for index, component in enumerate(
    pre_components
):

    for node in component:
        pre_lookup[node] = index


post_lookup = {}

for index, component in enumerate(
    post_components
):

    for node in component:
        post_lookup[node] = index


print(
    "Pre-event components:",
    len(pre_components)
)

print(
    "Post-event components:",
    len(post_components)
)


# ============================================================
# LOAD SETTLEMENTS
# ============================================================

print(
    "\nLoading historical settlements..."
)

settlement_data = json.loads(
    SETTLEMENTS.read_text(
        encoding="utf-8"
    )
)

settlements = []

for element in settlement_data["elements"]:

    tags = element.get(
        "tags",
        {}
    )

    place = tags.get(
        "place"
    )

    if place not in {
        "city",
        "town",
        "village",
        "hamlet"
    }:
        continue

    if element.get("type") == "node":

        lon = element.get(
            "lon"
        )

        lat = element.get(
            "lat"
        )

    else:

        center = element.get(
            "center"
        )

        if not center:
            continue

        lon = center["lon"]
        lat = center["lat"]

    if lon is None or lat is None:
        continue

    settlements.append({
        "id": element["id"],
        "name": tags.get(
            "name",
            f"OSM-{element['id']}"
        ),
        "place": place,
        "point": (
            lon,
            lat
        )
    })


print(
    "Relevant settlements:",
    len(settlements)
)


# ============================================================
# ROAD NODE LIST
# ============================================================

road_nodes = list(
    pre_graph.keys()
)


def nearest_road_node(point):

    best_node = None
    best_distance = float("inf")

    for node in road_nodes:

        distance = haversine(
            point,
            node
        )

        if distance < best_distance:

            best_distance = distance
            best_node = node

    if best_distance > SETTLEMENT_SNAP_M:

        return None, best_distance

    return best_node, best_distance


# ============================================================
# SNAP SETTLEMENTS
# ============================================================

for settlement in settlements:

    node, distance = nearest_road_node(
        settlement["point"]
    )

    settlement["road_node"] = node

    settlement["road_distance_m"] = (
        distance
    )


# ============================================================
# HUBS
# ============================================================

hubs = [
    settlement
    for settlement in settlements
    if settlement["place"] in {
        "town",
        "city"
    }
    and settlement["road_node"] is not None
]


print(
    "Town/city hubs:",
    len(hubs)
)

for hub in hubs:

    print(
        "  -",
        hub["name"],
        "(" + hub["place"] + ")"
    )


# ============================================================
# CONNECTIVITY ANALYSIS
# ============================================================

print(
    "\nAnalysing settlement connectivity..."
)

results = []

for settlement in settlements:

    settlement_node = (
        settlement["road_node"]
    )

    if settlement_node is None:
        continue

    # --------------------------------------------------------
    # Find geographically nearest town/city.
    # Connectivity is then evaluated through the road graph.
    # --------------------------------------------------------

    nearest_hub = min(
        hubs,
        key=lambda hub:
        haversine(
            settlement["point"],
            hub["point"]
        )
    )

    hub_node = nearest_hub[
        "road_node"
    ]

    pre_connected = (
        pre_lookup.get(
            settlement_node
        )
        ==
        pre_lookup.get(
            hub_node
        )
    )

    post_connected = (
        post_lookup.get(
            settlement_node
        )
        ==
        post_lookup.get(
            hub_node
        )
    )

    potentially_cut_off = (
        pre_connected
        and not post_connected
    )

    results.append({
        "osm_id": settlement["id"],
        "name": settlement["name"],
        "place": settlement["place"],
        "lon": settlement["point"][0],
        "lat": settlement["point"][1],
        "nearest_town_or_city": nearest_hub["name"],
        "nearest_hub_type": nearest_hub["place"],
        "road_snap_distance_m": round(
            settlement["road_distance_m"],
            1
        ),
        "connected_before": pre_connected,
        "connected_after": post_connected,
        "potentially_cut_off": potentially_cut_off
    })


cutoff = [
    result
    for result in results
    if result["potentially_cut_off"]
]


# ============================================================
# SAVE JSON
# ============================================================

results_path = (
    OUT
    / "settlement_connectivity_v4.json"
)

cutoff_path = (
    OUT
    / "potentially_cut_off_settlements_v4.json"
)

results_path.write_text(
    json.dumps(
        results,
        indent=2,
        ensure_ascii=False
    ),
    encoding="utf-8"
)

cutoff_path.write_text(
    json.dumps(
        cutoff,
        indent=2,
        ensure_ascii=False
    ),
    encoding="utf-8"
)


# ============================================================
# SAVE GEOJSON
# ============================================================

features = []

for result in cutoff:

    properties = {
        key: value
        for key, value in result.items()
        if key not in {
            "lon",
            "lat"
        }
    }

    features.append({
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [
                result["lon"],
                result["lat"]
            ]
        },
        "properties": properties
    })


geojson = {
    "type": "FeatureCollection",
    "features": features
}


geojson_path = (
    OUT
    / "potentially_cut_off_settlements_v4.geojson"
)

geojson_path.write_text(
    json.dumps(
        geojson,
        indent=2,
        ensure_ascii=False
    ),
    encoding="utf-8"
)


# ============================================================
# SUMMARY
# ============================================================

summary = {
    "analysis_version": "V4",
    "vehicle_accessible_ways": len(ways),
    "v3_affected_road_features": len(
        affected_geometries
    ),
    "disrupted_road_segments": len(
        disrupted_segments
    ),
    "pre_event_components": len(
        pre_components
    ),
    "post_event_components": len(
        post_components
    ),
    "settlements_available": len(
        settlements
    ),
    "settlements_analysed": len(
        results
    ),
    "town_city_hubs": len(
        hubs
    ),
    "potentially_cut_off_settlements": len(
        cutoff
    ),
    "match_tolerance_m": MATCH_TOLERANCE_M,
    "settlement_snap_distance_m": SETTLEMENT_SNAP_M,
    "interpretation": (
        "Modelled road-network connectivity result. "
        "Potentially cut-off settlements are settlements "
        "connected to their nearest town/city before removal "
        "of V3 potentially affected road segments but "
        "disconnected afterward. This does not confirm "
        "real-world isolation."
    )
}


summary_path = (
    OUT
    / "connectivity_v4_summary.json"
)

summary_path.write_text(
    json.dumps(
        summary,
        indent=2,
        ensure_ascii=False
    ),
    encoding="utf-8"
)


print()
print("=" * 70)
print("V4 CONNECTIVITY ANALYSIS COMPLETE")
print("=" * 70)

print(
    "Settlements analysed:",
    len(results)
)

print(
    "Potentially cut-off:",
    len(cutoff)
)

print()
print(
    "V3 affected roads:",
    len(affected_geometries)
)

print(
    "Disrupted segments:",
    len(disrupted_segments)
)

print()
print(
    "Output:",
    geojson_path
)

print()
print(
    "IMPORTANT:"
)

print(
    "These are MODELLED potentially cut-off settlements,"
)

print(
    "not confirmed real-world isolation."
)

print("=" * 70)