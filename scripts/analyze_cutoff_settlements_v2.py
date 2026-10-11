import json
import math
from pathlib import Path
from collections import defaultdict, deque

from osgeo import ogr, osr


# ============================================================
# FloodSpaceAI
# Settlement Connectivity Analysis V2
#
# Uses OSM way.geometry directly.
# ============================================================

BASE = Path(".")

ROADS_FILE = BASE / "data/raw/osm/roads_pre_20260727.json"
SETTLEMENTS_FILE = BASE / "data/raw/osm/settlements_pre_20260727.json"

AFFECTED_ROADS_FILE = (
    BASE
    / "data/processed/affected_assets/"
    / "potentially_affected_roads.geojson"
)

OUTPUT_DIR = BASE / "data/processed/connectivity"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Vehicle-accessible road classes.
ALLOWED_HIGHWAYS = {
    "motorway",
    "motorway_link",
    "trunk",
    "trunk_link",
    "primary",
    "primary_link",
    "secondary",
    "secondary_link",
    "tertiary",
    "tertiary_link",
    "unclassified",
    "residential",
    "living_street",
    "service",
    "road",
    "track",
}


# ============================================================
# Helpers
# ============================================================

def haversine_m(lat1, lon1, lat2, lon2):

    R = 6371000.0

    p1 = math.radians(lat1)
    p2 = math.radians(lat2)

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(p1)
        * math.cos(p2)
        * math.sin(dlon / 2) ** 2
    )

    return 2 * R * math.asin(
        math.sqrt(a)
    )


def point_key(lon, lat):
    """
    Quantize coordinates so adjacent OSM way endpoints
    can be represented by the same graph node.
    """
    return (
        round(lon, 7),
        round(lat, 7),
    )


def load_json(path):

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


# ============================================================
# Load roads
# ============================================================

print("=" * 70)
print("FloodSpaceAI — Settlement Connectivity Analysis V2")
print("=" * 70)

print("\nLoading historical OSM roads...")

road_data = load_json(
    ROADS_FILE
)

all_ways = [
    e
    for e in road_data.get("elements", [])
    if e.get("type") == "way"
]

road_ways = []

for way in all_ways:

    tags = way.get(
        "tags",
        {}
    )

    highway = tags.get(
        "highway"
    )

    if highway not in ALLOWED_HIGHWAYS:
        continue

    geometry = way.get(
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
        if "lon" in p and "lat" in p
    ]

    if len(coords) < 2:
        continue

    road_ways.append(
        {
            "id": way["id"],
            "highway": highway,
            "coords": coords,
            "tags": tags,
        }
    )


print(
    "Total OSM ways:",
    len(all_ways)
)

print(
    "Vehicle-accessible ways:",
    len(road_ways)
)


# ============================================================
# Load potentially affected road geometries
# ============================================================

print("\nLoading potentially affected roads...")

affected_ds = ogr.Open(
    str(AFFECTED_ROADS_FILE)
)

if affected_ds is None:
    raise RuntimeError(
        "Could not open potentially affected roads."
    )

affected_layer = affected_ds.GetLayer()

affected_geometries = []

for feature in affected_layer:

    geom = feature.GetGeometryRef()

    if geom is None:
        continue

    affected_geometries.append(
        geom.Clone()
    )

print(
    "Potentially affected road features:",
    len(affected_geometries)
)


# ============================================================
# Transform affected geometries to UTM 45N
# ============================================================

src = osr.SpatialReference()
src.ImportFromEPSG(4326)

dst = osr.SpatialReference()
dst.ImportFromEPSG(32645)

transform = osr.CoordinateTransformation(
    src,
    dst
)

affected_metric = []

for geom in affected_geometries:

    g = geom.Clone()

    g.Transform(
        transform
    )

    affected_metric.append(
        g
    )


# ============================================================
# Convert OSM way to metric line
# ============================================================

def make_metric_line(coords):

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


# ============================================================
# Match OSM ways against affected roads
# ============================================================

print(
    "\nMatching affected road features..."
)

affected_way_ids = set()

for index, way in enumerate(
    road_ways
):

    line = make_metric_line(
        way["coords"]
    )

    # Small tolerance because the affected-road layer
    # itself was generated using a 20 m road proximity.
    test_geom = line.Buffer(5)

    for affected in affected_metric:

        if test_geom.Intersects(
            affected
        ):

            affected_way_ids.add(
                way["id"]
            )

            break


print(
    "Matched potentially affected vehicle-road ways:",
    len(affected_way_ids)
)


# ============================================================
# Build graph from OSM geometry
# ============================================================

print(
    "\nBuilding road network..."
)

graph = defaultdict(set)

way_nodes = {}

for way in road_ways:

    coords = way["coords"]

    nodes_for_way = [
        point_key(lon, lat)
        for lon, lat in coords
    ]

    way_nodes[
        way["id"]
    ] = nodes_for_way

    # Keep every segment between consecutive geometry points.
    for a, b in zip(
        nodes_for_way[:-1],
        nodes_for_way[1:]
    ):

        if a == b:
            continue

        graph[a].add(b)
        graph[b].add(a)


print(
    "Graph nodes:",
    len(graph)
)

print(
    "Graph edges:",
    sum(
        len(v)
        for v in graph.values()
    ) // 2
)


# ============================================================
# Build post-flood graph
# ============================================================

post_graph = defaultdict(set)

for way in road_ways:

    if way["id"] in affected_way_ids:
        continue

    nodes_for_way = way_nodes[
        way["id"]
    ]

    for a, b in zip(
        nodes_for_way[:-1],
        nodes_for_way[1:]
    ):

        if a == b:
            continue

        post_graph[a].add(b)
        post_graph[b].add(a)


print(
    "Post-event graph nodes:",
    len(post_graph)
)


# ============================================================
# Connected components
# ============================================================

def connected_components(graph):

    visited = set()
    components = []

    for start in graph:

        if start in visited:
            continue

        component = set()
        queue = deque([start])

        visited.add(start)

        while queue:

            current = queue.popleft()

            component.add(
                current
            )

            for neighbour in graph.get(
                current,
                ()
            ):

                if neighbour not in visited:

                    visited.add(
                        neighbour
                    )

                    queue.append(
                        neighbour
                    )

        components.append(
            component
        )

    return components


print(
    "\nCalculating network components..."
)

pre_components = connected_components(
    graph
)

post_components = connected_components(
    post_graph
)


def make_component_lookup(
    components
):

    lookup = {}

    for index, component in enumerate(
        components
    ):

        for node in component:
            lookup[node] = index

    return lookup


pre_lookup = make_component_lookup(
    pre_components
)

post_lookup = make_component_lookup(
    post_components
)


print(
    "Pre-event components:",
    len(pre_components)
)

print(
    "Post-event components:",
    len(post_components)
)


# ============================================================
# Load settlements
# ============================================================

print(
    "\nLoading historical settlements..."
)

settlement_data = load_json(
    SETTLEMENTS_FILE
)

settlements = []

for element in settlement_data.get(
    "elements",
    []
):

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
        "hamlet",
    }:
        continue

    if element.get(
        "type"
    ) == "node":

        lat = element.get(
            "lat"
        )

        lon = element.get(
            "lon"
        )

    else:

        center = element.get(
            "center"
        )

        if not center:
            continue

        lat = center.get(
            "lat"
        )

        lon = center.get(
            "lon"
        )

    if lat is None or lon is None:
        continue

    settlements.append(
        {
            "osm_id": element["id"],
            "name": tags.get(
                "name",
                f"OSM-{element['id']}"
            ),
            "place": place,
            "lat": lat,
            "lon": lon,
        }
    )


print(
    "Relevant settlements:",
    len(settlements)
)


# ============================================================
# Road graph coordinates
# ============================================================

graph_coords = list(
    graph.keys()
)


def nearest_graph_node(
    lon,
    lat
):

    best = None
    best_distance = float(
        "inf"
    )

    for node in graph_coords:

        node_lon, node_lat = node

        distance = haversine_m(
            lat,
            lon,
            node_lat,
            node_lon,
        )

        if distance < best_distance:

            best_distance = distance
            best = node

    return best, best_distance


# ============================================================
# Match settlements to road network
# ============================================================

print(
    "\nMatching settlements to road network..."
)

for settlement in settlements:

    node, distance = nearest_graph_node(
        settlement["lon"],
        settlement["lat"]
    )

    settlement[
        "road_node"
    ] = node

    settlement[
        "road_distance_m"
    ] = distance


# ============================================================
# Town/city hubs
# ============================================================

hubs = [
    s
    for s in settlements
    if s["place"]
    in {
        "city",
        "town",
    }
]


print(
    "Town/city hubs:",
    len(hubs)
)

for hub in hubs:

    print(
        f"  - {hub['name']} "
        f"({hub['place']})"
    )


# ============================================================
# Connectivity analysis
# ============================================================

results = []

for settlement in settlements:

    settlement_node = settlement[
        "road_node"
    ]

    if settlement_node is None:
        continue

    if not hubs:
        continue

    # Nearest town/city by straight-line distance.
    nearest_hub = min(
        hubs,
        key=lambda h:
        haversine_m(
            settlement["lat"],
            settlement["lon"],
            h["lat"],
            h["lon"],
        )
    )

    hub_node = nearest_hub[
        "road_node"
    ]

    if hub_node is None:
        continue

    pre_settlement_component = (
        pre_lookup.get(
            settlement_node
        )
    )

    pre_hub_component = (
        pre_lookup.get(
            hub_node
        )
    )

    post_settlement_component = (
        post_lookup.get(
            settlement_node
        )
    )

    post_hub_component = (
        post_lookup.get(
            hub_node
        )
    )

    connected_before = (
        pre_settlement_component is not None
        and pre_hub_component is not None
        and
        pre_settlement_component
        ==
        pre_hub_component
    )

    connected_after = (
        post_settlement_component is not None
        and post_hub_component is not None
        and
        post_settlement_component
        ==
        post_hub_component
    )

    potentially_cut_off = (
        connected_before
        and not connected_after
    )

    results.append(
        {
            "name": settlement["name"],
            "place": settlement["place"],
            "lat": settlement["lat"],
            "lon": settlement["lon"],
            "nearest_town_or_city":
                nearest_hub["name"],
            "nearest_hub_type":
                nearest_hub["place"],
            "distance_to_hub_m":
                round(
                    haversine_m(
                        settlement["lat"],
                        settlement["lon"],
                        nearest_hub["lat"],
                        nearest_hub["lon"],
                    ),
                    1
                ),
            "road_distance_m":
                round(
                    settlement[
                        "road_distance_m"
                    ],
                    1
                ),
            "connected_before":
                connected_before,
            "connected_after":
                connected_after,
            "potentially_cut_off":
                potentially_cut_off,
        }
    )


# ============================================================
# Save results
# ============================================================

all_results = (
    OUTPUT_DIR
    / "settlement_connectivity_results_v2.json"
)

all_results.write_text(
    json.dumps(
        results,
        indent=2,
        ensure_ascii=False
    ),
    encoding="utf-8"
)


cutoff_results = [
    r
    for r in results
    if r["potentially_cut_off"]
]


cutoff_json = (
    OUTPUT_DIR
    / "potentially_cut_off_settlements_v2.json"
)

cutoff_json.write_text(
    json.dumps(
        cutoff_results,
        indent=2,
        ensure_ascii=False
    ),
    encoding="utf-8"
)


# ============================================================
# GeoJSON
# ============================================================

features = []

for result in cutoff_results:

    properties = {
        k: v
        for k, v in result.items()
        if k not in {
            "lat",
            "lon",
        }
    }

    features.append(
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    result["lon"],
                    result["lat"],
                ],
            },
            "properties": properties,
        }
    )


geojson = {
    "type": "FeatureCollection",
    "features": features,
}


cutoff_geojson = (
    OUTPUT_DIR
    / "potentially_cut_off_settlements_v2.geojson"
)

cutoff_geojson.write_text(
    json.dumps(
        geojson,
        indent=2,
        ensure_ascii=False
    ),
    encoding="utf-8"
)


# ============================================================
# Final summary
# ============================================================

print()
print("=" * 70)
print("CONNECTIVITY ANALYSIS V2 COMPLETE")
print("=" * 70)

print(
    "Settlements analysed:",
    len(results)
)

print(
    "Potentially cut-off settlements:",
    len(cutoff_results)
)

print()
print(
    "All results:",
    all_results
)

print(
    "Cut-off JSON:",
    cutoff_json
)

print(
    "Cut-off GeoJSON:",
    cutoff_geojson
)

print()
print(
    "IMPORTANT:"
)

print(
    "Potentially cut-off = connected before,"
)

print(
    "but disconnected after removal of"
)

print(
    "potentially affected road ways."
)

print(
    "This is a modelled connectivity result,"
)

print(
    "not confirmed real-world isolation."
)

print("=" * 70)