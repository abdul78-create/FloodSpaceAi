from pathlib import Path
import json

from osgeo import gdal, ogr, osr
import geopandas as gpd
from shapely.geometry import LineString, Polygon, shape
from shapely.ops import unary_union


# ============================================================
# FloodSpaceAI — Potentially Affected OSM Assets
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

OSM_DIR = ROOT / "data" / "raw" / "osm"
PROCESSED_DIR = ROOT / "data" / "processed"
OUTPUT_DIR = PROCESSED_DIR / "affected_assets"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FLOOD_RASTER = PROCESSED_DIR / "final_flood_candidate_v1.tif"

BUILDINGS = OSM_DIR / "buildings_pre_20260727.json"
ROADS = OSM_DIR / "roads_pre_20260727.json"
BRIDGES = OSM_DIR / "bridges_pre_20260727.json"

ROAD_BUFFER_M = 20
BRIDGE_BUFFER_M = 30


# ============================================================
# Load OSM ways
# ============================================================

def load_osm_ways(path):

    print(f"Loading: {path.name}")

    data = json.loads(
        path.read_text(encoding="utf-8")
    )

    features = []

    for element in data.get("elements", []):

        if element.get("type") != "way":
            continue

        geometry = element.get("geometry")

        if not geometry or len(geometry) < 2:
            continue

        coords = [
            (p["lon"], p["lat"])
            for p in geometry
            if "lon" in p and "lat" in p
        ]

        if len(coords) < 2:
            continue

        tags = element.get("tags", {})

        if (
            len(coords) >= 4
            and coords[0] == coords[-1]
            and "building" in tags
        ):
            geom = Polygon(coords)
        else:
            geom = LineString(coords)

        if geom.is_empty:
            continue

        features.append({
            "osm_id": element.get("id"),
            "tags": json.dumps(
                tags,
                ensure_ascii=False
            ),
            "geometry": geom,
        })

    if not features:
        return gpd.GeoDataFrame(
            columns=[
                "osm_id",
                "tags",
                "geometry",
            ],
            geometry="geometry",
            crs="EPSG:4326",
        )

    return gpd.GeoDataFrame(
        features,
        geometry="geometry",
        crs="EPSG:4326",
    )


# ============================================================
# Build flood polygon
# ============================================================

def build_flood_geometry(raster_path):

    print()
    print("Reading flood candidate:")
    print(raster_path)

    ds = gdal.Open(
        str(raster_path),
        gdal.GA_ReadOnly
    )

    if ds is None:
        raise RuntimeError(
            f"Could not open:\n{raster_path}"
        )

    band = ds.GetRasterBand(1)

    source = band.ReadAsArray()

    if source is None:
        raise RuntimeError(
            "Could not read flood raster."
        )

    mask = (
        source == 1
    ).astype("uint8")

    candidate_pixels = int(
        mask.sum()
    )

    print(
        "Candidate flood pixels:",
        candidate_pixels
    )

    if candidate_pixels == 0:
        raise RuntimeError(
            "No flood candidate pixels."
        )

    mem_driver = gdal.GetDriverByName(
        "MEM"
    )

    mask_ds = mem_driver.Create(
        "",
        ds.RasterXSize,
        ds.RasterYSize,
        1,
        gdal.GDT_Byte,
    )

    mask_ds.SetGeoTransform(
        ds.GetGeoTransform()
    )

    mask_ds.SetProjection(
        ds.GetProjection()
    )

    mask_band = mask_ds.GetRasterBand(1)
    mask_band.WriteArray(mask)
    mask_band.SetNoDataValue(0)

    vector_driver = ogr.GetDriverByName(
        "Memory"
    )

    vector_ds = vector_driver.CreateDataSource(
        "flood_memory"
    )

    spatial_ref = osr.SpatialReference()
    spatial_ref.ImportFromWkt(
        ds.GetProjection()
    )

    layer = vector_ds.CreateLayer(
        "flood",
        srs=spatial_ref,
        geom_type=ogr.wkbPolygon,
    )

    field_defn = ogr.FieldDefn(
        "value",
        ogr.OFTInteger
    )

    layer.CreateField(
        field_defn
    )

    print(
        "Polygonizing flood candidate..."
    )

    gdal.Polygonize(
        mask_band,
        None,
        layer,
        0,
        [],
        callback=None,
    )

    geometries = []

    layer.ResetReading()

    for feature in layer:

        if feature.GetField(
            "value"
        ) != 1:
            continue

        geom = feature.GetGeometryRef()

        if geom is None:
            continue

        try:

            geojson = json.loads(
                geom.ExportToJson()
            )

            shp = shape(
                geojson
            )

            if not shp.is_empty:
                geometries.append(shp)

        except Exception:
            continue

    if not geometries:
        raise RuntimeError(
            "No flood polygons created."
        )

    print(
        "Flood polygons created:",
        len(geometries)
    )

    print(
        "Merging flood polygons..."
    )

    flood_union = unary_union(
        geometries
    )

    print(
        "Flood geometry created."
    )

    return flood_union


# ============================================================
# Calculate affected buildings
# ============================================================

def calculate_buildings(
    flood_geom
):

    print()
    print("=" * 70)
    print("BUILDINGS")
    print("=" * 70)

    gdf = load_osm_ways(
        BUILDINGS
    )

    print(
        "Features loaded:",
        len(gdf)
    )

    if gdf.empty:
        return

    gdf = gdf[
        gdf.geometry.notna()
        & (~gdf.geometry.is_empty)
    ].copy()

    affected = gdf[
        gdf.geometry.intersects(
            flood_geom
        )
    ].copy()

    affected[
        "potentially_affected"
    ] = True

    affected[
        "analysis_type"
    ] = "flood_candidate_intersection"

    output = (
        OUTPUT_DIR /
        "potentially_affected_buildings.geojson"
    )

    affected.to_file(
        output,
        driver="GeoJSON"
    )

    print(
        "Potentially affected buildings:",
        len(affected)
    )

    print(
        "Saved:",
        output
    )


# ============================================================
# Calculate affected roads
# ============================================================

def calculate_roads(
    flood_geom
):

    print()
    print("=" * 70)
    print("ROADS")
    print("=" * 70)

    gdf = load_osm_ways(
        ROADS
    )

    print(
        "Features loaded:",
        len(gdf)
    )

    if gdf.empty:
        return

    gdf = gdf[
        gdf.geometry.notna()
        & (~gdf.geometry.is_empty)
    ].copy()

    # --------------------------------------------------------
    # Reproject to metric CRS
    # --------------------------------------------------------

    metric_crs = gdf.estimate_utm_crs()

    print(
        "Metric CRS:",
        metric_crs
    )

    roads_metric = gdf.to_crs(
        metric_crs
    )

    flood_gdf = gpd.GeoDataFrame(
        geometry=[flood_geom],
        crs="EPSG:4326"
    )

    flood_metric = flood_gdf.to_crs(
        metric_crs
    ).geometry.iloc[0]

    # --------------------------------------------------------
    # Buffer flood candidate by 20 m
    # --------------------------------------------------------

    flood_buffer = flood_metric.buffer(
        ROAD_BUFFER_M
    )

    affected = roads_metric[
        roads_metric.geometry.intersects(
            flood_buffer
        )
    ].copy()

    affected[
        "potentially_affected"
    ] = True

    affected[
        "buffer_distance_m"
    ] = ROAD_BUFFER_M

    affected[
        "analysis_type"
    ] = "flood_candidate_20m_buffer"

    affected = affected.to_crs(
        "EPSG:4326"
    )

    output = (
        OUTPUT_DIR /
        "potentially_affected_roads.geojson"
    )

    affected.to_file(
        output,
        driver="GeoJSON"
    )

    print(
        "Potentially affected roads:",
        len(affected)
    )

    print(
        "Saved:",
        output
    )


# ============================================================
# Calculate affected bridges
# ============================================================

def calculate_bridges(
    flood_geom
):

    print()
    print("=" * 70)
    print("BRIDGES")
    print("=" * 70)

    gdf = load_osm_ways(
        BRIDGES
    )

    print(
        "Features loaded:",
        len(gdf)
    )

    if gdf.empty:
        return

    gdf = gdf[
        gdf.geometry.notna()
        & (~gdf.geometry.is_empty)
    ].copy()

    # --------------------------------------------------------
    # Reproject to metric CRS
    # --------------------------------------------------------

    metric_crs = gdf.estimate_utm_crs()

    print(
        "Metric CRS:",
        metric_crs
    )

    bridges_metric = gdf.to_crs(
        metric_crs
    )

    flood_gdf = gpd.GeoDataFrame(
        geometry=[flood_geom],
        crs="EPSG:4326"
    )

    flood_metric = flood_gdf.to_crs(
        metric_crs
    ).geometry.iloc[0]

    # --------------------------------------------------------
    # Buffer flood candidate by 30 m
    # --------------------------------------------------------

    flood_buffer = flood_metric.buffer(
        BRIDGE_BUFFER_M
    )

    affected = bridges_metric[
        bridges_metric.geometry.intersects(
            flood_buffer
        )
    ].copy()

    affected[
        "potentially_affected"
    ] = True

    affected[
        "buffer_distance_m"
    ] = BRIDGE_BUFFER_M

    affected[
        "analysis_type"
    ] = "flood_candidate_30m_buffer"

    affected = affected.to_crs(
        "EPSG:4326"
    )

    output = (
        OUTPUT_DIR /
        "potentially_affected_bridges.geojson"
    )

    affected.to_file(
        output,
        driver="GeoJSON"
    )

    print(
        "Potentially affected bridges:",
        len(affected)
    )

    print(
        "Saved:",
        output
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print(
        "FloodSpaceAI — Affected Asset Analysis"
    )
    print("=" * 70)

    required = [
        FLOOD_RASTER,
        BUILDINGS,
        ROADS,
        BRIDGES,
    ]

    print()
    print(
        "Checking files..."
    )

    for path in required:

        if not path.exists():
            raise FileNotFoundError(
                f"Missing:\n{path}"
            )

        print(
            "OK:",
            path
        )

    # --------------------------------------------------------
    # Flood geometry
    # --------------------------------------------------------

    flood_geom = build_flood_geometry(
        FLOOD_RASTER
    )

    # --------------------------------------------------------
    # Assets
    # --------------------------------------------------------

    calculate_buildings(
        flood_geom
    )

    calculate_roads(
        flood_geom
    )

    calculate_bridges(
        flood_geom
    )

    # --------------------------------------------------------
    # Done
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)

    print()
    print(
        "Output directory:"
    )

    print(
        OUTPUT_DIR
    )

    print()
    print(
        "Road buffer:",
        ROAD_BUFFER_M,
        "meters"
    )

    print(
        "Bridge buffer:",
        BRIDGE_BUFFER_M,
        "meters"
    )

    print()
    print(
        "IMPORTANT:"
    )

    print(
        "Results represent POTENTIALLY AFFECTED assets."
    )

    print(
        "They are not confirmed destruction/damage."
    )


if __name__ == "__main__":
    main()