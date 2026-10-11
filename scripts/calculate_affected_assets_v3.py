import json
from pathlib import Path

from osgeo import gdal, ogr, osr


BASE = Path(".")

FLOOD_RASTER = (
    BASE / "data/processed/final_flood_candidate_v3.tif"
)

OSM_DIR = BASE / "data/raw/osm"

ROADS_FILE = OSM_DIR / "roads_pre_20260727.json"
BUILDINGS_FILE = OSM_DIR / "buildings_pre_20260727.json"
BRIDGES_FILE = OSM_DIR / "bridges_pre_20260727.json"

OUT = (
    BASE
    / "data/processed/affected_assets_v3"
)

OUT.mkdir(
    parents=True,
    exist_ok=True
)


# ------------------------------------------------------------
# CRS
# ------------------------------------------------------------

WGS84 = osr.SpatialReference()
WGS84.ImportFromEPSG(4326)

UTM45N = osr.SpatialReference()
UTM45N.ImportFromEPSG(32645)

to_utm = osr.CoordinateTransformation(
    WGS84,
    UTM45N
)


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def json_load(path):
    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def make_point(lon, lat):
    p = ogr.Geometry(
        ogr.wkbPoint
    )
    p.AddPoint(
        lon,
        lat
    )
    return p


def way_geometry(element):

    geometry = element.get(
        "geometry",
        []
    )

    if len(geometry) < 2:
        return None

    line = ogr.Geometry(
        ogr.wkbLineString
    )

    for point in geometry:

        line.AddPoint(
            point["lon"],
            point["lat"]
        )

    return line


def transform_geom(geom):

    g = geom.Clone()

    g.Transform(
        to_utm
    )

    return g


def write_geojson(
    path,
    features
):

    collection = {
        "type": "FeatureCollection",
        "features": features
    }

    path.write_text(
        json.dumps(
            collection,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


# ------------------------------------------------------------
# Start
# ------------------------------------------------------------

print("=" * 70)
print("FloodSpaceAI — Affected Assets V3")
print("=" * 70)

print(
    "\nFlood raster:",
    FLOOD_RASTER
)


# ------------------------------------------------------------
# Open flood raster
# ------------------------------------------------------------

raster = gdal.Open(
    str(FLOOD_RASTER)
)

if raster is None:
    raise RuntimeError(
        "Could not open V3 flood raster."
    )

band = raster.GetRasterBand(1)

flood = band.ReadAsArray()

gt = raster.GetGeoTransform()

projection = raster.GetProjection()

nodata = band.GetNoDataValue()

print(
    "Raster:",
    raster.RasterXSize,
    "x",
    raster.RasterYSize
)

print(
    "Flood pixels:",
    int(
        ((flood == 1) & (flood != nodata)).sum()
    )
)


# ------------------------------------------------------------
# Polygonize flood mask
# ------------------------------------------------------------

print(
    "\nPolygonizing V3 flood candidate..."
)

mem_driver = gdal.GetDriverByName(
    "MEM"
)

mask_ds = mem_driver.Create(
    "",
    raster.RasterXSize,
    raster.RasterYSize,
    1,
    gdal.GDT_Byte
)

mask_ds.SetGeoTransform(
    gt
)

mask_ds.SetProjection(
    projection
)

mask_band = mask_ds.GetRasterBand(1)

mask_band.WriteArray(
    (
        flood == 1
    ).astype("uint8")
)

mask_band.SetNoDataValue(
    0
)

vector_driver = ogr.GetDriverByName(
    "GeoJSON"
)

flood_vector_path = (
    OUT / "v3_flood_polygons.geojson"
)

if flood_vector_path.exists():
    flood_vector_path.unlink()

flood_ds = vector_driver.CreateDataSource(
    str(flood_vector_path)
)

flood_layer = flood_ds.CreateLayer(
    "flood",
    srs=WGS84,
    geom_type=ogr.wkbPolygon
)

field = ogr.FieldDefn(
    "value",
    ogr.OFTInteger
)

flood_layer.CreateField(
    field
)

gdal.Polygonize(
    mask_band,
    None,
    flood_layer,
    0,
    [],
    callback=None
)

flood_ds.FlushCache()

# Reload through OGR so geometries are easy to use.
flood_ds = ogr.Open(
    str(flood_vector_path)
)

flood_layer = flood_ds.GetLayer()

flood_geometries = []

for feature in flood_layer:

    value = feature.GetField(
        "value"
    )

    if value != 1:
        continue

    geom = feature.GetGeometryRef()

    if geom:
        flood_geometries.append(
            transform_geom(geom)
        )


print(
    "Flood polygons:",
    len(flood_geometries)
)


# ------------------------------------------------------------
# Load historical OSM
# ------------------------------------------------------------

print(
    "\nLoading historical OSM assets..."
)

roads = json_load(
    ROADS_FILE
)

buildings = json_load(
    BUILDINGS_FILE
)

bridges = json_load(
    BRIDGES_FILE
)


# ------------------------------------------------------------
# BUILDINGS
# ------------------------------------------------------------

print(
    "\nAnalysing buildings..."
)

affected_buildings = []

for element in buildings.get(
    "elements",
    []
):

    geometry = element.get(
        "geometry"
    )

    if not geometry:
        continue

    ring = ogr.Geometry(
        ogr.wkbLinearRing
    )

    for p in geometry:

        ring.AddPoint(
            p["lon"],
            p["lat"]
        )

    polygon = ogr.Geometry(
        ogr.wkbPolygon
    )

    polygon.AddGeometry(
        ring
    )

    polygon_metric = transform_geom(
        polygon
    )

    hit = False

    for flood_geom in flood_geometries:

        if polygon_metric.Intersects(
            flood_geom
        ):

            hit = True
            break

    if not hit:
        continue

    tags = element.get(
        "tags",
        {}
    )

    affected_buildings.append(
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [
                        p["lon"],
                        p["lat"]
                    ]
                    for p in geometry
                ]]
            },
            "properties": {
                "osm_id": element["id"],
                "potentially_affected": True,
                "analysis_version": "V3"
            }
        }
    )


print(
    "Potentially affected buildings:",
    len(affected_buildings)
)


# ------------------------------------------------------------
# ROAD ANALYSIS
# ------------------------------------------------------------

print(
    "\nAnalysing roads..."
)

affected_roads = []

for element in roads.get(
    "elements",
    []
):

    geometry = way_geometry(
        element
    )

    if geometry is None:
        continue

    road_metric = transform_geom(
        geometry
    )

    # Same 20 m proximity approach used in the
    # previous asset analysis.
    road_buffer = road_metric.Buffer(
        20
    )

    hit = False

    for flood_geom in flood_geometries:

        if road_buffer.Intersects(
            flood_geom
        ):

            hit = True
            break

    if not hit:
        continue

    coords = [
        [
            p["lon"],
            p["lat"]
        ]
        for p in element["geometry"]
    ]

    affected_roads.append(
        {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": coords
            },
            "properties": {
                "osm_id": element["id"],
                "tags": element.get(
                    "tags",
                    {}
                ),
                "potentially_affected": True,
                "buffer_distance_m": 20,
                "analysis_version": "V3"
            }
        }
    )


print(
    "Potentially affected roads:",
    len(affected_roads)
)


# ------------------------------------------------------------
# BRIDGES
# ------------------------------------------------------------

print(
    "\nAnalysing bridges..."
)

affected_bridges = []

for element in bridges.get(
    "elements",
    []
):

    geometry = way_geometry(
        element
    )

    if geometry is None:
        continue

    bridge_metric = transform_geom(
        geometry
    )

    bridge_buffer = bridge_metric.Buffer(
        30
    )

    hit = False

    for flood_geom in flood_geometries:

        if bridge_buffer.Intersects(
            flood_geom
        ):

            hit = True
            break

    if not hit:
        continue

    coords = [
        [
            p["lon"],
            p["lat"]
        ]
        for p in element["geometry"]
    ]

    affected_bridges.append(
        {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": coords
            },
            "properties": {
                "osm_id": element["id"],
                "tags": element.get(
                    "tags",
                    {}
                ),
                "potentially_affected": True,
                "buffer_distance_m": 30,
                "analysis_version": "V3"
            }
        }
    )


print(
    "Potentially affected bridges:",
    len(affected_bridges)
)


# ------------------------------------------------------------
# Save outputs
# ------------------------------------------------------------

buildings_out = (
    OUT
    / "potentially_affected_buildings_v3.geojson"
)

roads_out = (
    OUT
    / "potentially_affected_roads_v3.geojson"
)

bridges_out = (
    OUT
    / "potentially_affected_bridges_v3.geojson"
)


write_geojson(
    buildings_out,
    affected_buildings
)

write_geojson(
    roads_out,
    affected_roads
)

write_geojson(
    bridges_out,
    affected_bridges
)


# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------

summary = {
    "analysis_version": "V3",
    "flood_raster": str(
        FLOOD_RASTER
    ),
    "flood_polygons": len(
        flood_geometries
    ),
    "potentially_affected_buildings": len(
        affected_buildings
    ),
    "potentially_affected_roads": len(
        affected_roads
    ),
    "potentially_affected_bridges": len(
        affected_bridges
    ),
    "road_buffer_m": 20,
    "bridge_buffer_m": 30,
    "interpretation": (
        "Potentially affected assets; "
        "not confirmed physical damage."
    )
}


summary_path = (
    OUT
    / "affected_assets_v3_summary.json"
)

summary_path.write_text(
    json.dumps(
        summary,
        indent=2
    ),
    encoding="utf-8"
)


print()
print("=" * 70)
print("V3 AFFECTED-ASSET ANALYSIS COMPLETE")
print("=" * 70)

print(
    "Buildings:",
    len(affected_buildings)
)

print(
    "Roads:",
    len(affected_roads)
)

print(
    "Bridges:",
    len(affected_bridges)
)

print()
print(
    "Output directory:",
    OUT
)

print()
print(
    "IMPORTANT:"
)

print(
    "These are POTENTIALLY AFFECTED assets,"
)

print(
    "not confirmed damage/destruction."
)

print("=" * 70)