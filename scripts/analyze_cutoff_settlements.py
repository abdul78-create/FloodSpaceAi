import json
import math
from pathlib import Path
from collections import defaultdict, deque

from osgeo import ogr, osr


# ============================================================
# FloodSpaceAI — Settlement Road Connectivity Analysis
#
# Goal:
# Identify settlements whose road connectivity to their
# nearest town/city is broken after potentially affected
# road segments are removed.
#
# IMPORTANT:
# Results are connectivity estimates, NOT confirmed isolation.
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


# ------------------------------------------------------------
# Road classes used for vehicle-access network
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# Geographic helpers
# ------------------------------------------------------------

def haversine_m(lat1, lon1, lat2, lon2):
    """
    Approximate geographic distance in meters.
    Used only for nearest-node matching.
    """
    R = 6371000.0

    p1 = math.radians(lat1)
    p2 = math.radians(lat2)

    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)

    a = (
        math.sin(dp / 2) ** 2
        + math.cos(p1)
        * math.cos(p2)
        * math.sin(dl / 2) ** 2
    )

    return 2 * R * math.asin(math.sqrt(a))


def way_is_allowed(element):
    tags = element.get("tags", {})
    highway = tags.get("highway")

    return highway in ALLOWED_HIGHWAYS


def extract_way_coordinates(element, node_lookup):
    """
    Return [(lon, lat), ...] for an OSM way.
    """
    coords = []

    for node_id in element.get("nodes", []):
        node = node_lookup.get(node_id)

        if node is None:
            continue

        lat = node.get("lat")
        lon = node.get("lon")

        if lat is None or lon is None:
            continue

        coords.append((lon, lat))

    return coords


def point_to_segment_distance_m(
    px,
    py,
    ax,
    ay,
    bx,
    by,
):
    """
    Approximate distance in meters using local equirectangular
    projection.
    """

    lat_ref = math.radians((py + ay + by) / 3.0)

    meters_per_degree_lat = 111320.0
    meters_per_degree_lon = (
        111320.0 * math.cos(lat_ref)
    )

    px_m = px * meters_per_degree_lon
    py_m = py * meters_per_degree_lat

    ax_m = ax * meters_per_degree_lon
    ay_m = ay * meters_per_degree_lat

    bx_m = bx * meters_per_degree_lon
    by_m = by * meters_per_degree_lat

    vx = bx_m - ax_m
    vy = by_m - ay_m

    wx = px_m - ax_m
    wy = py_m - ay_m

    length_sq = vx * vx + vy * vy

    if length_sq == 0:
        return math.hypot(
            px_m - ax_m,
            py_m - ay_m,
        )

    t = (
        wx * vx + wy * vy
    ) / length_sq

    t = max(0.0, min(1.0, t))

    closest_x = ax_m + t * vx
    closest_y = ay_m + t * vy

    return math.hypot(
        px_m - closest_x,
        py_m - closest_y,
    )


def point_to_polyline_distance_m(
    lon,
    lat,
    coords,
):
    if len(coords) < 2:
        return float("inf")

    best = float("inf")

    for i in range(len(coords) - 1):

        ax, ay = coords[i]
        bx, by = coords[i + 1]

        d = point_to_segment_distance_m(
            lon,
            lat,
            ax,
            ay,
            bx,
            by,
        )

        if d < best:
            best = d

    return best


# ------------------------------------------------------------
# Load OSM
# ------------------------------------------------------------

print("=" * 70)
print("FloodSpaceAI — Settlement Connectivity Analysis")
print("=" * 70)

print("\nLoading historical roads...")

roads_data = json.loads(
    ROADS_FILE.read_text(
        encoding="utf-8"
    )
)

elements = roads_data.get("elements", [])

nodes = {
    e["id"]: e
    for e in elements
    if e.get("type") == "node"
}

ways = [
    e
    for e in elements
    if e.get("type") == "way"
    and way_is_allowed(e)
]

print("Total OSM elements:", len(elements))
print("Road nodes:", len(nodes))
print("Allowed road ways:", len(ways))


# ------------------------------------------------------------
# Build graph
# ------------------------------------------------------------

print("\nBuilding road graph...")

graph = defaultdict(set)

way_records = []

for way in ways:

    coords = extract_way_coordinates(
        way,
        nodes
    )

    node_ids = [
        n
        for n in way.get("nodes", [])
        if n in nodes
    ]

    if len(node_ids) < 2:
        continue

    for a, b in zip(
        node_ids[:-1],
        node_ids[1:]
    ):

        graph[a].add(b)
        graph[b].add(a)

    way_records.append(
        {
            "id": way["id"],
            "node_ids": node_ids,
            "coords": coords,
            "tags": way.get("tags", {}),
        }
    )


print("Graph nodes:", len(graph))
print("Graph edges:", sum(len(v) for v in graph.values()) // 2)


# ------------------------------------------------------------
# Load potentially affected roads
# ------------------------------------------------------------

print("\nLoading potentially affected roads...")

affected_ds = ogr.Open(
    str(AFFECTED_ROADS_FILE)
)

if affected_ds is None:
    raise RuntimeError(
        "Could not open affected roads GeoJSON."
    )

affected_layer = affected_ds.GetLayer()

affected_features = []

for feature in affected_layer:

    geom = feature.GetGeometryRef()

    if geom is None:
        continue

    affected_features.append(
        geom.Clone()
    )


print(
    "Potentially affected road features:",
    len(affected_features)
)


# ------------------------------------------------------------
# Match affected road geometry to historical OSM ways
# ------------------------------------------------------------

print("\nMatching affected roads to OSM road ways...")

# Transform OSM geographic coordinates to UTM 45N.
src = osr.SpatialReference()
src.ImportFromEPSG(4326)

dst = osr.SpatialReference()
dst.ImportFromEPSG(32645)

transform = osr.CoordinateTransformation(
    src,
    dst
)


def coords_to_geometry(coords):

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

        point.Transform(transform)

        line.AddPoint(
            point.GetX(),
            point.GetY()
        )

    return line


affected_geometries_metric = []

for geom in affected_features:

    g = geom.Clone()

    g.Transform(transform)

    affected_geometries_metric.append(g)


affected_way_ids = set()

for index, way in enumerate(way_records):

    coords = way["coords"]

    if len(coords) < 2:
        continue

    line = coords_to_geometry(coords)

    # Affected road dataset was generated with a 20 m
    # proximity criterion, so use a conservative 25 m
    # matching tolerance here.
    buffer = line.Buffer(25)

    matched = False

    for affected_geom in affected_geometries_metric:

        if buffer.Intersects(affected_geom):

            matched = True
            break

    if matched:
        affected_way_ids.add(
            way["id"]
        )


print(
    "Matched potentially affected OSM ways:",
    len(affected_way_ids)
)


# ------------------------------------------------------------
# Remove affected ways from graph
# ------------------------------------------------------------

print("\nCreating post-flood connectivity graph...")

post_graph = defaultdict(set)

for way in way_records:

    if way["id"] in affected_way_ids:
        continue

    node_ids = way["node_ids"]

    for a, b in zip(
        node_ids[:-1],
        node_ids[1:]
    ):

        post_graph[a].add(b)
        post_graph[b].add(a)


# ------------------------------------------------------------
# Connected components
# ------------------------------------------------------------

print("Calculating connected components...")


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

            component.add(current)

            for neighbour in graph.get(
                current,
                ()
            ):

                if neighbour not in visited:

                    visited.add(neighbour)
                    queue.append(neighbour)

        components.append(component)

    return components


pre_components = connected_components(graph)
post_components = connected_components(post_graph)

print(
    "Pre-event connected components:",
    len(pre_components)
)

print(
    "Post-event connected components:",
    len(post_components)
)


pre_component_id = {}

for cid, component in enumerate(
    pre_components
):

    for node_id in component:
        pre_component_id[node_id] = cid


post_component_id = {}

for cid, component in enumerate(
    post_components
):

    for node_id in component:
        post_component_id[node_id] = cid


# ------------------------------------------------------------
# Load settlements
# ------------------------------------------------------------

print("\nLoading settlements...")

settlement_data = json.loads(
    SETTLEMENTS_FILE.read_text(
        encoding="utf-8"
    )
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

    if element["type"] == "node":

        lat = element.get("lat")
        lon = element.get("lon")

    else:

        center = element.get(
            "center"
        )

        if not center:
            continue

        lat = center.get("lat")
        lon = center.get("lon")

    if lat is None or lon is None:
        continue

    name = tags.get(
        "name",
        f"OSM-{element['id']}"
    )

    settlements.append(
        {
            "osm_id": element["id"],
            "type": element["type"],
            "name": name,
            "place": place,
            "lat": lat,
            "lon": lon,
        }
    )


print(
    "Relevant settlements:",
    len(settlements)
)


# ------------------------------------------------------------
# Match each settlement to nearest road node
# ------------------------------------------------------------

print("\nMatching settlements to road network...")

road_node_coords = {}

for node_id, node in nodes.items():

    if (
        node.get("lat") is None
        or node.get("lon") is None
    ):
        continue

    road_node_coords[node_id] = (
        node["lat"],
        node["lon"]
    )


def nearest_road_node(
    lat,
    lon,
):

    best_node = None
    best_distance = float("inf")

    for node_id, (
        node_lat,
        node_lon
    ) in road_node_coords.items():

        d = haversine_m(
            lat,
            lon,
            node_lat,
            node_lon,
        )

        if d < best_distance:

            best_distance = d
            best_node = node_id

    return (
        best_node,
        best_distance
    )


for settlement in settlements:

    node_id, distance = nearest_road_node(
        settlement["lat"],
        settlement["lon"],
    )

    settlement["road_node"] = node_id
    settlement["road_distance_m"] = distance


# ------------------------------------------------------------
# Town / city hubs
# ------------------------------------------------------------

hubs = [
    s
    for s in settlements
    if s["place"] in {
        "city",
        "town",
    }
]

print(
    "Town/city hubs:",
    len(hubs)
)


# ------------------------------------------------------------
# Determine nearest hub using geographic distance.
#
# Then test whether the settlement and that hub remain in
# the same road-network component after affected roads are
# removed.
# ------------------------------------------------------------

results = []

for settlement in settlements:

    settlement_node = settlement[
        "road_node"
    ]

    if settlement_node is None:
        continue

    if not hubs:
        continue

    nearest_hub = min(
        hubs,
        key=lambda hub:
        haversine_m(
            settlement["lat"],
            settlement["lon"],
            hub["lat"],
            hub["lon"],
        )
    )

    hub_node = nearest_hub[
        "road_node"
    ]

    if hub_node is None:
        continue

    pre_component = (
        pre_component_id.get(
            settlement_node
        )
    )

    pre_hub_component = (
        pre_component_id.get(
            hub_node
        )
    )

    post_component = (
        post_component_id.get(
            settlement_node
        )
    )

    post_hub_component = (
        post_component_id.get(
            hub_node
        )
    )

    was_connected = (
        pre_component is not None
        and pre_component
        == pre_hub_component
    )

    remains_connected = (
        post_component is not None
        and post_component
        == post_hub_component
    )

    cutoff = (
        was_connected
        and not remains_connected
    )

    results.append(
        {
            "name": settlement["name"],
            "place": settlement["place"],
            "lat": settlement["lat"],
            "lon": settlement["lon"],
            "nearest_town_or_city": nearest_hub[
                "name"
            ],
            "nearest_hub_type": nearest_hub[
                "place"
            ],
            "distance_to_hub_m": round(
                haversine_m(
                    settlement["lat"],
                    settlement["lon"],
                    nearest_hub["lat"],
                    nearest_hub["lon"],
                ),
                1,
            ),
            "road_node_distance_m": round(
                settlement[
                    "road_distance_m"
                ],
                1,
            ),
            "connected_before": was_connected,
            "connected_after": remains_connected,
            "potentially_cut_off": cutoff,
        }
    )


# ------------------------------------------------------------
# Save JSON
# ------------------------------------------------------------

all_results_file = (
    OUTPUT_DIR
    / "settlement_connectivity_results.json"
)

all_results_file.write_text(
    json.dumps(
        results,
        indent=2,
        ensure_ascii=False,
    ),
    encoding="utf-8"
)


cutoff_results = [
    r
    for r in results
    if r["potentially_cut_off"]
]

cutoff_file = (
    OUTPUT_DIR
    / "potentially_cut_off_settlements.json"
)

cutoff_file.write_text(
    json.dumps(
        cutoff_results,
        indent=2,
        ensure_ascii=False,
    ),
    encoding="utf-8"
)


# ------------------------------------------------------------
# GeoJSON output
# ------------------------------------------------------------

geojson_features = []

for result in cutoff_results:

    geojson_features.append(
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    result["lon"],
                    result["lat"],
                ],
            },
            "properties": {
                k: v
                for k, v in result.items()
                if k not in {
                    "lon",
                    "lat",
                }
            },
        }
    )


geojson = {
    "type": "FeatureCollection",
    "features": geojson_features,
}


geojson_file = (
    OUTPUT_DIR
    / "potentially_cut_off_settlements.geojson"
)

geojson_file.write_text(
    json.dumps(
        geojson,
        indent=2,
        ensure_ascii=False,
    ),
    encoding="utf-8"
)


# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------

print()
print("=" * 70)
print("CONNECTIVITY ANALYSIS COMPLETE")
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
    all_results_file
)

print(
    "Cut-off JSON:",
    cutoff_file
)

print(
    "Cut-off GeoJSON:",
    geojson_file
)

print()
print(
    "IMPORTANT:"
)

print(
    "These are POTENTIALLY CUT-OFF settlements."
)

print(
    "They are not confirmed real-world isolation."
)

print("=" * 70)