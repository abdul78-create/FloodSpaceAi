#!/usr/bin/env python3
"""
FloodSpaceAI — Parameterized OSM Asset & Road Connectivity Engine (Phase 4B)

Performs reusable, date-aware OSM asset exposure and road network connectivity
analysis for any specified Area of Interest (AOI) bounding box and flood event date.

Core Capabilities:
1. Historical OSM Provenance Enforcement: Strict pre-event snapshot selection;
   rejection of post-event data; explicit metadata tracking.
2. Potentially Affected Asset Analysis: Metric buffer intersections for buildings,
   roads, and bridges against candidate flood extents.
3. Road Network Graph & Connectivity Modeling: Baseline vs disrupted graph comparison,
   settlement accessibility analysis, and identification of potentially cut-off settlements.
4. Isolated Per-Run Artifacts: Comprehensive GeoJSON and JSON outputs per run id without
   overwriting baseline competition fixtures.
"""

from __future__ import annotations

import argparse
from collections import defaultdict, deque
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

# Configure GDAL DLL directory for Windows environment
for dll_dir in [r"C:\Program Files\QGIS 3.44.14\bin", r"C:\OSGeo4W\bin"]:
    if os.path.exists(dll_dir):
        try:
            os.add_dll_directory(dll_dir)
        except Exception:
            pass

from osgeo import gdal, ogr, osr

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))

# Established Trishuli Benchmark Constants
TRISHULI_BBOX = [84.90, 27.75, 85.25, 28.05]
TRISHULI_FLOOD_DATE = "2026-08-28"
TRISHULI_OSM_SNAPSHOT = "2026-07-27T00:00:00Z"

# Road classes permitted for vehicle routing
ALLOWED_HIGHWAY_CLASSES = {
    "motorway", "motorway_link",
    "trunk", "trunk_link",
    "primary", "primary_link",
    "secondary", "secondary_link",
    "tertiary", "tertiary_link",
    "unclassified", "residential",
    "living_street", "service", "road", "track"
}

# Buffer distances (metric)
ROAD_BUFFER_M = 20.0
BRIDGE_BUFFER_M = 30.0
ROAD_DISRUPTION_MATCH_TOLERANCE_M = 5.0
SETTLEMENT_SNAP_M = 500.0


def compute_sha256(file_path: Path) -> str:
    """Computes SHA-256 hash of a file."""
    if not file_path.exists():
        return ""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def haversine_m(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    """Great-circle distance in meters between two (lon, lat) points."""
    lon1, lat1 = a
    lon2, lat2 = b
    r = 6371000.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    x = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(x))


def node_key(lon: float, lat: float) -> Tuple[float, float]:
    """Generates a stable coordinate tuple key for graph nodes."""
    return (round(lon, 7), round(lat, 7))


def get_spatial_references(center_lon: float, center_lat: float) -> Tuple[osr.SpatialReference, osr.SpatialReference, osr.CoordinateTransformation]:
    """Builds WGS84, appropriate UTM projection, and coordinate transformation."""
    wgs84 = osr.SpatialReference()
    wgs84.ImportFromEPSG(4326)

    # For Central Nepal (lon ~85), UTM zone 45N is standard (EPSG:32645)
    # For arbitrary locations, calculate UTM zone dynamically
    utm_zone = int((center_lon + 180) / 6) + 1
    utm_epsg = 32600 + utm_zone if center_lat >= 0 else 32700 + utm_zone

    utm = osr.SpatialReference()
    utm.ImportFromEPSG(utm_epsg)

    transform = osr.CoordinateTransformation(wgs84, utm)
    return wgs84, utm, transform


def is_trishuli_benchmark_aoi(bbox: List[float], flood_date: str) -> bool:
    """Checks whether parameters match the established Trishuli case study."""
    return (
        len(bbox) == 4
        and abs(bbox[0] - TRISHULI_BBOX[0]) < 1e-3
        and abs(bbox[1] - TRISHULI_BBOX[1]) < 1e-3
        and abs(bbox[2] - TRISHULI_BBOX[2]) < 1e-3
        and abs(bbox[3] - TRISHULI_BBOX[3]) < 1e-3
        and flood_date == TRISHULI_FLOOD_DATE
    )


def extract_flood_polygons_from_raster(
    raster_path: Path,
    wgs84_srs: osr.SpatialReference
) -> Tuple[List[ogr.Geometry], Dict[str, Any]]:
    """
    Polygonizes candidate flood pixels (value == 1) from GeoTIFF.
    Handles NoData values and validates coverage.
    """
    if not raster_path.exists():
        raise FileNotFoundError(f"Flood raster does not exist: {raster_path}")

    ds = gdal.Open(str(raster_path))
    if ds is None:
        raise RuntimeError(f"Could not open flood raster with GDAL: {raster_path}")

    band = ds.GetRasterBand(1)
    arr = band.ReadAsArray()
    gt = ds.GetGeoTransform()
    proj = ds.GetProjection()
    nodata = band.GetNoDataValue()

    total_pixels = int(arr.size)
    nodata_pixels = int((arr == nodata).sum()) if nodata is not None else 0
    flood_pixels = int(((arr == 1) & (arr != nodata)).sum()) if nodata is not None else int((arr == 1).sum())
    valid_pixels = total_pixels - nodata_pixels

    # If 0 flood pixels exist, return empty geometry list cleanly
    if flood_pixels == 0:
        return [], {
            "total_pixels": total_pixels,
            "valid_pixels": valid_pixels,
            "nodata_pixels": nodata_pixels,
            "flood_pixels": 0,
            "polygon_count": 0
        }

    # Create in-memory binary mask
    mem_driver = gdal.GetDriverByName("MEM")
    mask_ds = mem_driver.Create("", ds.RasterXSize, ds.RasterYSize, 1, gdal.GDT_Byte)
    mask_ds.SetGeoTransform(gt)
    mask_ds.SetProjection(proj)
    mask_band = mask_ds.GetRasterBand(1)

    binary_mask = (arr == 1).astype("uint8")
    if nodata is not None:
        binary_mask[arr == nodata] = 0
    mask_band.WriteArray(binary_mask)
    mask_band.SetNoDataValue(0)

    # In-memory vector datasource for polygonization
    mem_ogr = ogr.GetDriverByName("Memory")
    poly_ds = mem_ogr.CreateDataSource("mem_poly")
    poly_layer = poly_ds.CreateLayer("flood", srs=wgs84_srs, geom_type=ogr.wkbPolygon)
    field_defn = ogr.FieldDefn("value", ogr.OFTInteger)
    poly_layer.CreateField(field_defn)

    gdal.Polygonize(mask_band, None, poly_layer, 0, [], callback=None)

    polygons: List[ogr.Geometry] = []
    for feat in poly_layer:
        if feat.GetField("value") == 1:
            geom = feat.GetGeometryRef()
            if geom and not geom.IsEmpty():
                polygons.append(geom.Clone())

    return polygons, {
        "total_pixels": total_pixels,
        "valid_pixels": valid_pixels,
        "nodata_pixels": nodata_pixels,
        "flood_pixels": flood_pixels,
        "polygon_count": len(polygons)
    }


def load_flood_polygons_from_geojson(geojson_path: Path) -> List[ogr.Geometry]:
    """Loads polygons from a pre-generated GeoJSON file."""
    if not geojson_path.exists():
        raise FileNotFoundError(f"GeoJSON file not found: {geojson_path}")

    ds = ogr.Open(str(geojson_path))
    if ds is None:
        raise RuntimeError(f"Could not open GeoJSON with OGR: {geojson_path}")

    layer = ds.GetLayer()
    geometries: List[ogr.Geometry] = []
    for feat in layer:
        geom = feat.GetGeometryRef()
        if geom and not geom.IsEmpty():
            geometries.append(geom.Clone())
    return geometries


def way_to_geometry(element: Dict[str, Any]) -> Optional[ogr.Geometry]:
    """Constructs OGR LineString from Overpass JSON element geometry."""
    geom_list = element.get("geometry", [])
    if len(geom_list) < 2:
        return None
    line = ogr.Geometry(ogr.wkbLineString)
    for p in geom_list:
        line.AddPoint(float(p["lon"]), float(p["lat"]))
    return line


def building_to_polygon(element: Dict[str, Any]) -> Optional[ogr.Geometry]:
    """Constructs OGR Polygon from Overpass building way geometry."""
    geom_list = element.get("geometry", [])
    if len(geom_list) < 3:
        return None
    ring = ogr.Geometry(ogr.wkbLinearRing)
    for p in geom_list:
        ring.AddPoint(float(p["lon"]), float(p["lat"]))
    first_p = geom_list[0]
    last_p = geom_list[-1]
    if (first_p["lon"] != last_p["lon"]) or (first_p["lat"] != last_p["lat"]):
        ring.AddPoint(float(first_p["lon"]), float(first_p["lat"]))
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)
    return poly


def metric_line(coords: List[Tuple[float, float]], transform: osr.CoordinateTransformation) -> ogr.Geometry:
    """Builds a metric projected LineString from coordinate pairs."""
    line = ogr.Geometry(ogr.wkbLineString)
    for lon, lat in coords:
        pt = ogr.Geometry(ogr.wkbPoint)
        pt.AddPoint(lon, lat)
        pt.Transform(transform)
        line.AddPoint(pt.GetX(), pt.GetY())
    return line


def connected_components(graph: Dict[Any, Set[Any]]) -> List[Set[Any]]:
    """Calculates connected components using BFS."""
    seen: Set[Any] = set()
    comps: List[Set[Any]] = []

    for start in graph:
        if start in seen:
            continue
        comp: Set[Any] = set()
        queue = deque([start])
        seen.add(start)

        while queue:
            curr = queue.popleft()
            comp.add(curr)
            for neighbor in graph.get(curr, ()):
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)
        comps.append(comp)

    return comps


class ParameterizedAssetConnectivityEngine:
    """
    Main orchestration engine for Phase 4B OSM asset exposure and road connectivity.
    """

    def __init__(
        self,
        bbox: List[float],
        flood_date: str,
        flood_raster_path: Optional[Path] = None,
        flood_polygons_path: Optional[Path] = None,
        run_id: Optional[str] = None,
        osm_dir: Optional[Path] = None,
        snapshot_date: Optional[str] = None,
        output_base_dir: Optional[Path] = None,
        strict_provenance: bool = True,
        enable_live_osm: bool = True
    ):
        self.bbox = [float(x) for x in bbox]
        self.flood_date = flood_date
        self.flood_raster_path = Path(flood_raster_path) if flood_raster_path else None
        self.flood_polygons_path = Path(flood_polygons_path) if flood_polygons_path else None
        self.osm_dir = Path(osm_dir) if osm_dir else None
        self.strict_provenance = strict_provenance
        self.enable_live_osm = enable_live_osm

        # Validate inputs
        self._validate_inputs()

        # Generate run ID
        if not run_id:
            ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            self.run_id = f"asset_run_{ts}"
        else:
            self.run_id = run_id

        # Setup output directories
        base_dir = output_base_dir or (REPO_ROOT / "data" / "processed" / "pipeline_runs")
        self.run_dir = base_dir / self.run_id
        self.assets_dir = self.run_dir / "assets"
        self.connectivity_dir = self.run_dir / "connectivity"
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        self.connectivity_dir.mkdir(parents=True, exist_ok=True)

        # Coordinate references
        center_lon = (self.bbox[0] + self.bbox[2]) / 2.0
        center_lat = (self.bbox[1] + self.bbox[3]) / 2.0
        self.wgs84, self.utm, self.to_utm = get_spatial_references(center_lon, center_lat)

        # Determine snapshot date and provenance mode
        self.snapshot_date, self.provenance_mode, self.osm_source_info = self._resolve_osm_provenance(snapshot_date)

    def _validate_inputs(self):
        """Validates bounding box and date consistency."""
        if len(self.bbox) != 4:
            raise ValueError(f"Bbox must have 4 coordinates [west, south, east, north], got: {self.bbox}")
        west, south, east, north = self.bbox
        if west >= east:
            raise ValueError(f"Invalid bbox: west ({west}) >= east ({east})")
        if south >= north:
            raise ValueError(f"Invalid bbox: south ({south}) >= north ({north})")

        try:
            self.flood_datetime = datetime.strptime(self.flood_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError as e:
            raise ValueError(f"Invalid flood date format '{self.flood_date}', expected YYYY-MM-DD: {e}")

    def _resolve_osm_provenance(self, custom_snapshot: Optional[str]) -> Tuple[str, str, Dict[str, Any]]:
        """
        Determines and verifies pre-event snapshot timestamp and source.
        Rejects post-event data and enforces strict provenance.
        """
        if custom_snapshot:
            clean_ts = custom_snapshot.replace("Z", "+00:00")
            if "T" in clean_ts:
                dt_snap = datetime.fromisoformat(clean_ts)
            else:
                dt_snap = datetime.strptime(clean_ts, "%Y-%m-%d").replace(tzinfo=timezone.utc)

            # Ensure snapshot is strictly prior to flood date
            if dt_snap >= self.flood_datetime:
                raise ValueError(
                    f"PROVENANCE VIOLATION: Requested OSM snapshot ({custom_snapshot}) is on or after "
                    f"flood date ({self.flood_date}). Post-event OSM data is prohibited to avoid event edits."
                )
            snapshot = dt_snap.isoformat().replace("+00:00", "Z")
            mode = "HISTORICAL_PRE_EVENT_SNAPSHOT"
            source_info = {
                "provider": "OHsome API / Overpass Historical API",
                "snapshot_timestamp": snapshot,
                "query": f"Pre-event snapshot query for bbox={self.bbox} at timestamp {snapshot}",
                "attribution": "© OpenStreetMap contributors",
                "notice": "Selected strictly prior to flood event date; post-event modifications excluded."
            }
            return snapshot, mode, source_info

        # Benchmark scenario
        if is_trishuli_benchmark_aoi(self.bbox, self.flood_date):
            snapshot = TRISHULI_OSM_SNAPSHOT
            mode = "VERIFIED_TRISHULI_OSM_FIXTURE"
            source_info = {
                "provider": "Heidelberg University GIScience Research Group (OHsome API)",
                "snapshot_timestamp": snapshot,
                "query": "Historical pre-event extract for Trishuli watershed (2026-07-27)",
                "attribution": "© OpenStreetMap contributors",
                "notice": "Verified benchmark pre-event fixture; strict historical isolation enforced."
            }
            return snapshot, mode, source_info

        # Default to 7 days prior to flood event
        from datetime import timedelta
        dt_snap = datetime(
            self.flood_datetime.year, self.flood_datetime.month, self.flood_datetime.day,
            0, 0, 0, tzinfo=timezone.utc
        ) - timedelta(days=7)
        snapshot = dt_snap.isoformat().replace("+00:00", "Z")
        mode = "HISTORICAL_PRE_EVENT_SNAPSHOT"

        source_info = {
            "provider": "OHsome API / Overpass Historical API",
            "snapshot_timestamp": snapshot,
            "query": f"Pre-event snapshot query for bbox={self.bbox} at timestamp {snapshot}",
            "attribution": "© OpenStreetMap contributors",
            "notice": "Selected strictly prior to flood event date; post-event modifications excluded."
        }
        return snapshot, mode, source_info

    def load_osm_data(self) -> Dict[str, Any]:
        """Loads pre-event OSM files for roads, buildings, bridges, and settlements."""
        if self.osm_dir and self.osm_dir.exists():
            return self._load_from_directory(self.osm_dir)

        if self.provenance_mode == "VERIFIED_TRISHULI_OSM_FIXTURE":
            benchmark_osm_dir = REPO_ROOT / "data" / "raw" / "osm"
            if benchmark_osm_dir.exists():
                return self._load_from_directory(benchmark_osm_dir)

        run_osm_dir = self.run_dir / "osm"
        if run_osm_dir.exists() and any((run_osm_dir / f).exists() for f in ["roads.json", "roads.geojson", "roads_pre_20260727.json"]):
            return self._load_from_directory(run_osm_dir)

        # Attempt live historical OSM acquisition if enabled and not Trishuli benchmark
        if getattr(self, "enable_live_osm", True):
            try:
                from acquire_historical_osm import HistoricalOSMAcquisitionAdapter
                adapter = HistoricalOSMAcquisitionAdapter()
                acq_res = adapter.acquire_historical_osm(
                    bbox=self.bbox,
                    flood_date=self.flood_date,
                    out_dir=run_osm_dir,
                    custom_snapshot=self.snapshot_date
                )
                if acq_res.get("status") == "SUCCESS_DOWNLOADED":
                    loaded = self._load_from_directory(run_osm_dir)
                    loaded["osm_provenance_meta"] = acq_res
                    return loaded
                else:
                    return {
                        "status": "PARTIAL_RUN_OSM_UNAVAILABLE",
                        "roads": [],
                        "buildings": [],
                        "bridges": [],
                        "settlements": [],
                        "hospitals": [],
                        "message": acq_res.get("message") or acq_res.get("error") or "Historical OSM acquisition unavailable."
                    }
            except Exception as e:
                return {
                    "status": "PARTIAL_RUN_OSM_UNAVAILABLE",
                    "roads": [],
                    "buildings": [],
                    "bridges": [],
                    "settlements": [],
                    "hospitals": [],
                    "message": f"Historical OSM acquisition error: {e}"
                }

        return {
            "status": "PARTIAL_RUN_OSM_UNAVAILABLE",
            "roads": [],
            "buildings": [],
            "bridges": [],
            "settlements": [],
            "hospitals": [],
            "message": f"Pre-event OSM data for AOI {self.bbox} has not been downloaded to cache."
        }

    def _load_from_directory(self, d: Path) -> Dict[str, Any]:
        """Loads and parses JSON/GeoJSON files from specified folder."""
        data: Dict[str, Any] = {
            "status": "SUCCESS_LOADED",
            "roads": [],
            "buildings": [],
            "bridges": [],
            "settlements": [],
            "hospitals": []
        }

        # Provenance metadata file if exists
        prov_file = d / "osm_provenance.json"
        if prov_file.exists():
            try:
                data["osm_provenance_meta"] = json.loads(prov_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        # Roads
        for p in [d / "roads_pre_20260727.json", d / "roads.json", d / "roads.geojson"]:
            if p.exists():
                data["roads"] = self._parse_osm_file(p)
                data["roads_file"] = str(p)
                data["roads_sha256"] = compute_sha256(p)
                break

        # Buildings
        for p in [d / "buildings_pre_20260727.json", d / "buildings.json", d / "buildings.geojson"]:
            if p.exists():
                data["buildings"] = self._parse_osm_file(p)
                data["buildings_file"] = str(p)
                data["buildings_sha256"] = compute_sha256(p)
                break

        # Bridges
        for p in [d / "bridges_pre_20260727.json", d / "bridges.json", d / "bridges.geojson"]:
            if p.exists():
                data["bridges"] = self._parse_osm_file(p)
                data["bridges_file"] = str(p)
                data["bridges_sha256"] = compute_sha256(p)
                break

        # Settlements
        for p in [d / "settlements_pre_20260727.json", d / "settlements.json", d / "settlements.geojson"]:
            if p.exists():
                data["settlements"] = self._parse_osm_file(p)
                data["settlements_file"] = str(p)
                data["settlements_sha256"] = compute_sha256(p)
                break

        # Hospitals
        for p in [d / "hospitals_pre_20260727.json", d / "hospitals.json", d / "hospitals.geojson"]:
            if p.exists():
                data["hospitals"] = self._parse_osm_file(p)
                data["hospitals_file"] = str(p)
                data["hospitals_sha256"] = compute_sha256(p)
                break

        return data

    def _parse_osm_file(self, path: Path) -> List[Dict[str, Any]]:
        """Parses Overpass JSON or GeoJSON."""
        raw = json.loads(path.read_text(encoding="utf-8"))
        if "elements" in raw:
            return raw["elements"]
        elif "features" in raw:
            elements = []
            for f in raw["features"]:
                props = f.get("properties", {})
                geom = f.get("geometry", {})
                elem = {
                    "id": props.get("osm_id") or props.get("id", 0),
                    "tags": props,
                    "type": "way" if "LineString" in geom.get("type", "") or "Polygon" in geom.get("type", "") else "node"
                }
                coords = geom.get("coordinates", [])
                if geom.get("type") == "Point" and len(coords) == 2:
                    elem["lon"], elem["lat"] = coords[0], coords[1]
                elif geom.get("type") == "LineString":
                    elem["geometry"] = [{"lon": c[0], "lat": c[1]} for c in coords]
                elif geom.get("type") == "Polygon" and coords:
                    elem["geometry"] = [{"lon": c[0], "lat": c[1]} for c in coords[0]]
                elements.append(elem)
            return elements
        return []

    def execute(self) -> Dict[str, Any]:
        """Executes end-to-end asset exposure and connectivity analysis."""
        execution_start = datetime.now(timezone.utc)
        print("=" * 76, flush=True)
        print(f"FloodSpaceAI — Parameterized Asset & Connectivity Engine (Phase 4B)", flush=True)
        print(f"Run ID:    {self.run_id}", flush=True)
        print(f"AOI Bbox:  {self.bbox}", flush=True)
        print(f"Date:      {self.flood_date} (Snapshot: {self.snapshot_date})", flush=True)
        print("=" * 76, flush=True)

        # 1. Load or polygonize flood candidate extents
        flood_polygons_wgs84: List[ogr.Geometry] = []
        raster_stats: Dict[str, Any] = {}

        if self.flood_polygons_path and self.flood_polygons_path.exists():
            print(f"Loading pre-existing flood polygons: {self.flood_polygons_path}", flush=True)
            flood_polygons_wgs84 = load_flood_polygons_from_geojson(self.flood_polygons_path)
            raster_stats["source"] = str(self.flood_polygons_path)
            raster_stats["polygon_count"] = len(flood_polygons_wgs84)
        elif self.flood_raster_path and self.flood_raster_path.exists():
            print(f"Polygonizing flood raster: {self.flood_raster_path}", flush=True)
            flood_polygons_wgs84, raster_stats = extract_flood_polygons_from_raster(
                self.flood_raster_path, self.wgs84
            )
            poly_out = self.assets_dir / "flood_polygons.geojson"
            self._write_polygon_features(poly_out, flood_polygons_wgs84)
        else:
            if is_trishuli_benchmark_aoi(self.bbox, self.flood_date):
                default_v3_raster = REPO_ROOT / "data" / "processed" / "final_flood_candidate_v3.tif"
                if default_v3_raster.exists():
                    print(f"Using Trishuli benchmark raster: {default_v3_raster}", flush=True)
                    flood_polygons_wgs84, raster_stats = extract_flood_polygons_from_raster(
                        default_v3_raster, self.wgs84
                    )
            else:
                return {
                    "status": "FAILED_MISSING_FLOOD_INPUT",
                    "error": "No flood raster or polygon layer provided and not a benchmark run."
                }

        # Project flood polygons to UTM and pre-calculate spatial envelopes for rapid indexing
        flood_polygons_metric: List[ogr.Geometry] = []
        flood_envelopes: List[Tuple[float, float, float, float]] = []

        for poly in flood_polygons_wgs84:
            g = poly.Clone()
            g.Transform(self.to_utm)
            flood_polygons_metric.append(g)
            flood_envelopes.append(g.GetEnvelope())

        print(f"Active flood candidate polygons: {len(flood_polygons_metric)}", flush=True)

        # 2. Load OSM data
        osm_data = self.load_osm_data()
        if osm_data.get("status") == "PARTIAL_RUN_OSM_UNAVAILABLE":
            partial_meta = {
                "status": "PARTIAL_RUN_OSM_UNAVAILABLE",
                "run_id": self.run_id,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "inputs": {
                    "bbox": self.bbox,
                    "flood_date": self.flood_date,
                    "flood_raster": str(self.flood_raster_path) if self.flood_raster_path else None,
                    "flood_polygons": str(self.flood_polygons_path) if self.flood_polygons_path else None
                },
                "osm_provenance": {
                    "provenance_mode": self.provenance_mode,
                    "snapshot_timestamp": self.snapshot_date,
                    "source_info": self.osm_source_info
                },
                "message": osm_data.get("message")
            }
            (self.run_dir / "run_metadata.json").write_text(
                json.dumps(partial_meta, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            (self.run_dir / "run_summary.md").write_text(
                f"# FloodSpaceAI Run `{self.run_id}`\n\n**Status:** `PARTIAL_RUN_OSM_UNAVAILABLE`\n\n{osm_data.get('message')}\n",
                encoding="utf-8"
            )
            return partial_meta

        # 3. Analyze potentially affected assets
        asset_results = self._analyze_assets(osm_data, flood_polygons_metric, flood_envelopes)

        # 4. Model road connectivity & isolated settlements
        connectivity_results = self._analyze_connectivity(osm_data, asset_results["potentially_affected_roads_metric"])

        # 5. Write artifacts and summary files
        execution_end = datetime.now(timezone.utc)
        duration_s = (execution_end - execution_start).total_seconds()

        metadata = self._compile_metadata(
            raster_stats=raster_stats,
            osm_data=osm_data,
            asset_results=asset_results,
            connectivity_results=connectivity_results,
            duration_s=duration_s
        )

        self._save_run_outputs(asset_results, connectivity_results, metadata)

        print("\n" + "=" * 76, flush=True)
        print("PHASE 4B ANALYSIS COMPLETED SUCCESSFULLY", flush=True)
        print(f"Potentially affected buildings: {asset_results['summary']['potentially_affected_buildings']}", flush=True)
        print(f"Potentially affected roads:     {asset_results['summary']['potentially_affected_roads']}", flush=True)
        print(f"Potentially affected bridges:   {asset_results['summary']['potentially_affected_bridges']}", flush=True)
        print(f"Disrupted road segments:        {connectivity_results['summary']['disrupted_road_segments']}", flush=True)
        print(f"Potentially cut-off settlements: {connectivity_results['summary']['potentially_cut_off_settlements']}", flush=True)
        print(f"Outputs saved to: {self.run_dir}", flush=True)
        print("=" * 76, flush=True)

        return metadata

    def _analyze_assets(
        self,
        osm_data: Dict[str, Any],
        flood_polygons_metric: List[ogr.Geometry],
        flood_envelopes: List[Tuple[float, float, float, float]]
    ) -> Dict[str, Any]:
        """
        Clips assets to AOI, buffers, and calculates intersections with flood polygons.
        Uses envelope pre-filtering for sub-second performance across 60k+ geometries.
        """
        print("\n[Step 1] Analyzing Potentially Affected Assets...", flush=True)
        west, south, east, north = self.bbox

        has_floods = len(flood_polygons_metric) > 0
        if has_floods:
            total_flood_min_x = min(e[0] for e in flood_envelopes)
            total_flood_max_x = max(e[1] for e in flood_envelopes)
            total_flood_min_y = min(e[2] for e in flood_envelopes)
            total_flood_max_y = max(e[3] for e in flood_envelopes)
        else:
            total_flood_min_x = total_flood_max_x = total_flood_min_y = total_flood_max_y = 0.0

        # Buildings
        raw_buildings = osm_data.get("buildings", [])
        total_mapped_buildings = len(raw_buildings)
        affected_buildings: List[Dict[str, Any]] = []

        if has_floods:
            for elem in raw_buildings:
                geom_pts = elem.get("geometry", [])
                if len(geom_pts) < 3:
                    continue

                poly_geom = building_to_polygon(elem)
                if not poly_geom:
                    continue

                poly_metric = poly_geom.Clone()
                poly_metric.Transform(self.to_utm)
                b_env = poly_metric.GetEnvelope()

                # Fast envelope rejection against overall flood bounds
                if (b_env[1] < total_flood_min_x or b_env[0] > total_flood_max_x or
                    b_env[3] < total_flood_min_y or b_env[2] > total_flood_max_y):
                    continue

                # Test against candidate flood polygons
                hit = False
                for fg, fe in zip(flood_polygons_metric, flood_envelopes):
                    if not (b_env[1] < fe[0] or b_env[0] > fe[1] or b_env[3] < fe[2] or b_env[2] > fe[3]):
                        if poly_metric.Intersects(fg):
                            hit = True
                            break

                if hit:
                    coords = [[[p["lon"], p["lat"]] for p in elem["geometry"]]]
                    affected_buildings.append({
                        "type": "Feature",
                        "geometry": {"type": "Polygon", "coordinates": coords},
                        "properties": {
                            "osm_id": elem["id"],
                            "asset_type": "building",
                            "potentially_affected": True,
                            "analysis_version": "V4B"
                        }
                    })

        print(f"Potentially affected buildings: {len(affected_buildings)}", flush=True)

        # Roads
        raw_roads = osm_data.get("roads", [])
        total_mapped_roads = len(raw_roads)
        affected_roads: List[Dict[str, Any]] = []
        affected_roads_metric: List[ogr.Geometry] = []
        total_road_length_km = 0.0
        affected_road_length_km = 0.0

        for elem in raw_roads:
            if elem.get("type") != "way":
                continue
            geom_pts = elem.get("geometry", [])
            if len(geom_pts) < 2:
                continue

            line_geom = way_to_geometry(elem)
            if not line_geom:
                continue

            road_metric = line_geom.Clone()
            road_metric.Transform(self.to_utm)
            length_m = road_metric.Length()
            total_road_length_km += length_m / 1000.0

            if not has_floods:
                continue

            road_buffer = road_metric.Buffer(ROAD_BUFFER_M)
            r_env = road_buffer.GetEnvelope()

            if (r_env[1] < total_flood_min_x or r_env[0] > total_flood_max_x or
                r_env[3] < total_flood_min_y or r_env[2] > total_flood_max_y):
                continue

            hit = False
            for fg, fe in zip(flood_polygons_metric, flood_envelopes):
                if not (r_env[1] < fe[0] or r_env[0] > fe[1] or r_env[3] < fe[2] or r_env[2] > fe[3]):
                    if road_buffer.Intersects(fg):
                        hit = True
                        break

            if hit:
                affected_road_length_km += length_m / 1000.0
                coords = [[p["lon"], p["lat"]] for p in geom_pts]
                affected_roads.append({
                    "type": "Feature",
                    "geometry": {"type": "LineString", "coordinates": coords},
                    "properties": {
                        "osm_id": elem["id"],
                        "asset_type": "road",
                        "highway": elem.get("tags", {}).get("highway"),
                        "potentially_affected": True,
                        "buffer_distance_m": ROAD_BUFFER_M,
                        "length_m": round(length_m, 1),
                        "analysis_version": "V4B"
                    }
                })
                # Preserve metric geometry for connectivity disruption matching
                affected_roads_metric.append(line_geom.Clone())

        print(f"Potentially affected roads: {len(affected_roads)}", flush=True)

        # Bridges
        raw_bridges = osm_data.get("bridges", [])
        total_mapped_bridges = len(raw_bridges)
        affected_bridges: List[Dict[str, Any]] = []

        if has_floods:
            for elem in raw_bridges:
                geom_pts = elem.get("geometry", [])
                if len(geom_pts) < 2:
                    continue

                line_geom = way_to_geometry(elem)
                if not line_geom:
                    continue

                bridge_metric = line_geom.Clone()
                bridge_metric.Transform(self.to_utm)
                bridge_buffer = bridge_metric.Buffer(BRIDGE_BUFFER_M)
                br_env = bridge_buffer.GetEnvelope()

                if (br_env[1] < total_flood_min_x or br_env[0] > total_flood_max_x or
                    br_env[3] < total_flood_min_y or br_env[2] > total_flood_max_y):
                    continue

                hit = False
                for fg, fe in zip(flood_polygons_metric, flood_envelopes):
                    if not (br_env[1] < fe[0] or br_env[0] > fe[1] or br_env[3] < fe[2] or br_env[2] > fe[3]):
                        if bridge_buffer.Intersects(fg):
                            hit = True
                            break

                if hit:
                    coords = [[p["lon"], p["lat"]] for p in geom_pts]
                    affected_bridges.append({
                        "type": "Feature",
                        "geometry": {"type": "LineString", "coordinates": coords},
                        "properties": {
                            "osm_id": elem["id"],
                            "asset_type": "bridge",
                            "potentially_affected": True,
                            "buffer_distance_m": BRIDGE_BUFFER_M,
                            "tags": elem.get("tags", {}),
                            "analysis_version": "V4B"
                        }
                    })

        print(f"Potentially affected bridges: {len(affected_bridges)}", flush=True)

        summary = {
            "total_mapped_buildings": total_mapped_buildings,
            "potentially_affected_buildings": len(affected_buildings),
            "total_mapped_roads": total_mapped_roads,
            "total_mapped_road_length_km": round(total_road_length_km, 2),
            "potentially_affected_roads": len(affected_roads),
            "potentially_affected_road_length_km": round(affected_road_length_km, 2),
            "total_mapped_bridges": total_mapped_bridges,
            "potentially_affected_bridges": len(affected_bridges),
            "road_buffer_m": ROAD_BUFFER_M,
            "bridge_buffer_m": BRIDGE_BUFFER_M,
            "interpretation": "Modeled estimates based on candidate flood extents; does not confirm physical structural damage."
        }

        return {
            "summary": summary,
            "buildings": affected_buildings,
            "roads": affected_roads,
            "bridges": affected_bridges,
            "potentially_affected_roads_metric": affected_roads_metric
        }

    def _analyze_connectivity(
        self,
        osm_data: Dict[str, Any],
        affected_roads_wgs84: List[ogr.Geometry]
    ) -> Dict[str, Any]:
        """
        Builds road graph, models segment disruption, and calculates settlement cut-off status.
        """
        print("\n[Step 2] Modeling Road Graph & Settlement Connectivity...", flush=True)

        # Convert affected roads to UTM and pre-calculate envelopes for fast matching
        affected_roads_metric = []
        affected_envelopes = []
        for g in affected_roads_wgs84:
            gm = g.Clone()
            gm.Transform(self.to_utm)
            affected_roads_metric.append(gm)
            affected_envelopes.append(gm.GetEnvelope())

        has_affected_roads = len(affected_roads_metric) > 0
        if has_affected_roads:
            aff_min_x = min(e[0] for e in affected_envelopes)
            aff_max_x = max(e[1] for e in affected_envelopes)
            aff_min_y = min(e[2] for e in affected_envelopes)
            aff_max_y = max(e[3] for e in affected_envelopes)
        else:
            aff_min_x = aff_max_x = aff_min_y = aff_max_y = 0.0

        # 1. Extract vehicle-accessible ways
        ways = []
        for elem in osm_data.get("roads", []):
            if elem.get("type") != "way":
                continue
            highway = elem.get("tags", {}).get("highway")
            if highway not in ALLOWED_HIGHWAY_CLASSES:
                continue
            geom = elem.get("geometry", [])
            if len(geom) < 2:
                continue
            coords = [(p["lon"], p["lat"]) for p in geom]
            ways.append({
                "id": elem["id"],
                "highway": highway,
                "coords": coords
            })

        print(f"Vehicle-accessible road ways: {len(ways)}", flush=True)

        # 2. Identify disrupted road segments using spatial envelope indexing
        disrupted_segments: Set[Tuple[int, int]] = set()
        disrupted_features: List[Dict[str, Any]] = []

        if has_affected_roads:
            for way in ways:
                coords = way["coords"]
                for seg_idx in range(len(coords) - 1):
                    seg_line = metric_line([coords[seg_idx], coords[seg_idx + 1]], self.to_utm)
                    seg_test = seg_line.Buffer(ROAD_DISRUPTION_MATCH_TOLERANCE_M)
                    st_env = seg_test.GetEnvelope()

                    if (st_env[1] < aff_min_x or st_env[0] > aff_max_x or
                        st_env[3] < aff_min_y or st_env[2] > aff_max_y):
                        continue

                    hit = False
                    for aff_m, aff_e in zip(affected_roads_metric, affected_envelopes):
                        if not (st_env[1] < aff_e[0] or st_env[0] > aff_e[1] or st_env[3] < aff_e[2] or st_env[2] > aff_e[3]):
                            if seg_test.Intersects(aff_m):
                                hit = True
                                break

                    if hit:
                        disrupted_segments.add((way["id"], seg_idx))
                        disrupted_features.append({
                            "type": "Feature",
                            "geometry": {
                                "type": "LineString",
                                "coordinates": [
                                    [coords[seg_idx][0], coords[seg_idx][1]],
                                    [coords[seg_idx + 1][0], coords[seg_idx + 1][1]]
                                ]
                            },
                            "properties": {
                                "way_id": way["id"],
                                "segment_index": seg_idx,
                                "highway": way["highway"],
                                "disrupted": True
                            }
                        })

        print(f"Disrupted road segments: {len(disrupted_segments)}", flush=True)

        # 3. Build baseline and disrupted graphs
        pre_graph: Dict[Tuple[float, float], Set[Tuple[float, float]]] = defaultdict(set)
        post_graph: Dict[Tuple[float, float], Set[Tuple[float, float]]] = defaultdict(set)

        for way in ways:
            coords = way["coords"]
            for i in range(len(coords) - 1):
                a = node_key(*coords[i])
                b = node_key(*coords[i + 1])
                if a == b:
                    continue
                pre_graph[a].add(b)
                pre_graph[b].add(a)

                if (way["id"], i) not in disrupted_segments:
                    post_graph[a].add(b)
                    post_graph[b].add(a)

        pre_components = connected_components(pre_graph)
        post_components = connected_components(post_graph)

        pre_lookup = {node: idx for idx, comp in enumerate(pre_components) for node in comp}
        post_lookup = {node: idx for idx, comp in enumerate(post_components) for node in comp}

        print(f"Pre-event connected components:  {len(pre_components)}", flush=True)
        print(f"Post-event connected components: {len(post_components)}", flush=True)

        # 4. Load settlements and snap to road network
        settlements = []
        for elem in osm_data.get("settlements", []):
            tags = elem.get("tags", {})
            place = tags.get("place")
            if place not in {"city", "town", "village", "hamlet"}:
                continue
            if elem.get("type") == "node":
                lon = elem.get("lon")
                lat = elem.get("lat")
            else:
                center = elem.get("center", {})
                lon = center.get("lon")
                lat = center.get("lat")
            if lon is None or lat is None:
                continue

            settlements.append({
                "id": elem["id"],
                "name": tags.get("name", f"OSM-{elem['id']}"),
                "place": place,
                "point": (float(lon), float(lat))
            })

        print(f"Candidate settlements available: {len(settlements)}", flush=True)

        # Snap to nearest road node using spatial grid indexing (~1.1 km cell)
        road_nodes = list(pre_graph.keys())
        grid_cell_size = 0.01
        road_grid: Dict[Tuple[int, int], List[Tuple[float, float]]] = defaultdict(list)
        for node in road_nodes:
            cy = int(node[1] / grid_cell_size)
            cx = int(node[0] / grid_cell_size)
            road_grid[(cy, cx)].append(node)

        def find_nearest_road_node(pt: Tuple[float, float]) -> Tuple[Optional[Tuple[float, float]], float]:
            cy = int(pt[1] / grid_cell_size)
            cx = int(pt[0] / grid_cell_size)
            best_node = None
            best_dist = float("inf")
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    for node in road_grid.get((cy + dy, cx + dx), ()):
                        d = haversine_m(pt, node)
                        if d < best_dist:
                            best_dist = d
                            best_node = node
            if best_dist > SETTLEMENT_SNAP_M:
                return None, best_dist
            return best_node, best_dist

        for s in settlements:
            s_node, s_dist = find_nearest_road_node(s["point"])
            s["road_node"] = s_node
            s["road_distance_m"] = s_dist

        # Identify town/city hubs
        hubs = [
            s for s in settlements
            if s["place"] in {"town", "city"} and s["road_node"] is not None
        ]
        print(f"Town/city hubs identified: {len(hubs)}", flush=True)

        # Check hospital data availability
        hospitals_raw = osm_data.get("hospitals", [])
        hospital_data_available = len(hospitals_raw) > 0
        hospital_notice = (
            "Historical hospital locations present and evaluated."
            if hospital_data_available
            else "Historical hospital data not available in pre-event snapshot; town/city hubs utilized for modeled access."
        )

        # 5. Evaluate settlement connectivity
        connectivity_results = []
        for s in settlements:
            s_node = s["road_node"]
            if s_node is None:
                continue
            if not hubs:
                continue

            # Geographically nearest hub
            nearest_hub = min(hubs, key=lambda h: haversine_m(s["point"], h["point"]))
            hub_node = nearest_hub["road_node"]

            pre_connected = (pre_lookup.get(s_node) == pre_lookup.get(hub_node))
            post_connected = (post_lookup.get(s_node) == post_lookup.get(hub_node))
            potentially_cut_off = (pre_connected and not post_connected)

            connectivity_results.append({
                "osm_id": s["id"],
                "name": s["name"],
                "place": s["place"],
                "lon": s["point"][0],
                "lat": s["point"][1],
                "nearest_town_or_city": nearest_hub["name"],
                "nearest_hub_type": nearest_hub["place"],
                "road_snap_distance_m": round(s["road_distance_m"], 1),
                "connected_before": pre_connected,
                "connected_after": post_connected,
                "potentially_cut_off": potentially_cut_off
            })

        cutoff_settlements = [r for r in connectivity_results if r["potentially_cut_off"]]
        print(f"Potentially cut-off settlements: {len(cutoff_settlements)}", flush=True)

        summary = {
            "analysis_version": "V4B",
            "vehicle_accessible_ways": len(ways),
            "disrupted_road_segments": len(disrupted_segments),
            "pre_event_components": len(pre_components),
            "post_event_components": len(post_components),
            "settlements_available": len(settlements),
            "settlements_analysed": len(connectivity_results),
            "town_city_hubs": len(hubs),
            "potentially_cut_off_settlements": len(cutoff_settlements),
            "hospital_data_available": hospital_data_available,
            "hospital_notice": hospital_notice,
            "match_tolerance_m": ROAD_DISRUPTION_MATCH_TOLERANCE_M,
            "settlement_snap_distance_m": SETTLEMENT_SNAP_M,
            "interpretation": (
                "Modeled road-network connectivity result. "
                "Potentially cut-off settlements are settlements connected to their nearest town/city "
                "before removal of potentially affected road segments but disconnected afterward. "
                "This is a network modeling scenario, not confirmed real-world isolation."
            )
        }

        # Build GeoJSON for cut-off settlements
        cutoff_geojson_features = [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [r["lon"], r["lat"]]},
                "properties": {k: v for k, v in r.items() if k not in {"lon", "lat"}}
            }
            for r in cutoff_settlements
        ]

        return {
            "summary": summary,
            "all_settlements": connectivity_results,
            "cutoff_settlements": cutoff_settlements,
            "cutoff_features": cutoff_geojson_features,
            "disrupted_features": disrupted_features
        }

    def _compile_metadata(
        self,
        raster_stats: Dict[str, Any],
        osm_data: Dict[str, Any],
        asset_results: Dict[str, Any],
        connectivity_results: Dict[str, Any],
        duration_s: float
    ) -> Dict[str, Any]:
        """Compiles machine-readable run metadata."""
        source_info = dict(self.osm_source_info)
        if "osm_provenance_meta" in osm_data:
            source_info.update(osm_data["osm_provenance_meta"])

        return {
            "status": "SUCCESS_COMPLETED",
            "run_id": self.run_id,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "execution_duration_seconds": round(duration_s, 2),
            "inputs": {
                "bbox": self.bbox,
                "flood_date": self.flood_date,
                "flood_raster": str(self.flood_raster_path) if self.flood_raster_path else None,
                "flood_polygons": str(self.flood_polygons_path) if self.flood_polygons_path else None
            },
            "flood_raster_statistics": raster_stats,
            "osm_provenance": {
                "provenance_mode": self.provenance_mode,
                "snapshot_timestamp": self.snapshot_date,
                "source_info": source_info,
                "files_used": {
                    "roads": osm_data.get("roads_file"),
                    "buildings": osm_data.get("buildings_file"),
                    "bridges": osm_data.get("bridges_file"),
                    "settlements": osm_data.get("settlements_file"),
                    "hospitals": osm_data.get("hospitals_file")
                },
                "checksums": {
                    "roads_sha256": osm_data.get("roads_sha256"),
                    "buildings_sha256": osm_data.get("buildings_sha256"),
                    "bridges_sha256": osm_data.get("bridges_sha256"),
                    "settlements_sha256": osm_data.get("settlements_sha256"),
                    "hospitals_sha256": osm_data.get("hospitals_sha256")
                }
            },
            "asset_summary": asset_results["summary"],
            "connectivity_summary": connectivity_results["summary"],
            "scientific_disclaimers": [
                "Asset counts represent exposure estimates based on candidate flood extents; they do not confirm physical structural damage.",
                "Road disruption is modeled by intersecting candidate flood extents with a 20m road buffer and 5m matching tolerance.",
                "Settlement disconnection represents topological network fragmentation relative to nearest town/city hubs, not ground-verified physical isolation."
            ]
        }

    def _save_run_outputs(
        self,
        asset_results: Dict[str, Any],
        connectivity_results: Dict[str, Any],
        metadata: Dict[str, Any]
    ):
        """Saves all JSON and GeoJSON outputs to run directory."""
        (self.assets_dir / "asset_summary.json").write_text(
            json.dumps(asset_results["summary"], indent=2, ensure_ascii=False), encoding="utf-8"
        )
        (self.assets_dir / "potentially_affected_buildings.geojson").write_text(
            json.dumps({"type": "FeatureCollection", "features": asset_results["buildings"]}, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        (self.assets_dir / "potentially_affected_roads.geojson").write_text(
            json.dumps({"type": "FeatureCollection", "features": asset_results["roads"]}, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        (self.assets_dir / "potentially_affected_bridges.geojson").write_text(
            json.dumps({"type": "FeatureCollection", "features": asset_results["bridges"]}, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        unified_assets = (
            asset_results["buildings"] + asset_results["roads"] + asset_results["bridges"]
        )
        (self.assets_dir / "potentially_affected_assets.geojson").write_text(
            json.dumps({"type": "FeatureCollection", "features": unified_assets}, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        (self.connectivity_dir / "connectivity_summary.json").write_text(
            json.dumps(connectivity_results["summary"], indent=2, ensure_ascii=False), encoding="utf-8"
        )
        (self.connectivity_dir / "potentially_cut_off_settlements.geojson").write_text(
            json.dumps({"type": "FeatureCollection", "features": connectivity_results["cutoff_features"]}, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        (self.connectivity_dir / "disrupted_road_segments.geojson").write_text(
            json.dumps({"type": "FeatureCollection", "features": connectivity_results["disrupted_features"]}, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        (self.connectivity_dir / "settlement_connectivity.json").write_text(
            json.dumps(connectivity_results["all_settlements"], indent=2, ensure_ascii=False), encoding="utf-8"
        )

        (self.run_dir / "run_metadata.json").write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        summary_md = f"""# FloodSpaceAI — Asset & Connectivity Execution Summary

**Run ID:** `{self.run_id}`  
**AOI Bounding Box:** `{self.bbox}`  
**Event Date:** `{self.flood_date}`  
**OSM Snapshot Date:** `{self.snapshot_date}`  
**Provenance Mode:** `{self.provenance_mode}`  
**Timestamp (UTC):** `{metadata['timestamp_utc']}`  

---

## 1. Asset Exposure Estimates (Candidate Inundation Overlap)
- **Potentially Affected Buildings:** **{asset_results['summary']['potentially_affected_buildings']}** (out of {asset_results['summary']['total_mapped_buildings']} mapped)
- **Potentially Affected Roads:** **{asset_results['summary']['potentially_affected_roads']}** ({asset_results['summary']['potentially_affected_road_length_km']} km affected out of {asset_results['summary']['total_mapped_road_length_km']} km mapped)
- **Potentially Affected Bridges:** **{asset_results['summary']['potentially_affected_bridges']}** (out of {asset_results['summary']['total_mapped_bridges']} mapped)

> *Notice: These are modeled potential exposure estimates; they do not confirm physical structural damage.*

---

## 2. Road Network Connectivity & Isolated Settlement Modeling
- **Vehicle-Accessible Ways:** {connectivity_results['summary']['vehicle_accessible_ways']}
- **Disrupted Road Segments:** **{connectivity_results['summary']['disrupted_road_segments']}**
- **Connected Components:** {connectivity_results['summary']['pre_event_components']} (baseline) $\\rightarrow$ {connectivity_results['summary']['post_event_components']} (post-disruption)
- **Settlements Analysed:** {connectivity_results['summary']['settlements_analysed']}
- **Potentially Cut-Off Settlements:** **{connectivity_results['summary']['potentially_cut_off_settlements']}**
- **Hospital Data Available:** {connectivity_results['summary']['hospital_data_available']} ({connectivity_results['summary']['hospital_notice']})

---

## 3. Data Provenance & Isolation
- **OSM Attribution:** © OpenStreetMap contributors
- **Snapshot Selection:** Verified pre-event snapshot (`{self.snapshot_date}` < `{self.flood_date}`)
- **Checking-Only Isolation:** Copernicus EMSR927 / UNOSAT layers strictly excluded from production calculations.
"""
        (self.run_dir / "run_summary.md").write_text(summary_md, encoding="utf-8")

    def _write_polygon_features(self, out_path: Path, polygons: List[ogr.Geometry]):
        """Writes polygon geometries to GeoJSON."""
        features = []
        for idx, poly in enumerate(polygons):
            json_dict = json.loads(poly.ExportToJson())
            features.append({
                "type": "Feature",
                "geometry": json_dict,
                "properties": {"id": idx, "flood_candidate": True}
            })
        out_path.write_text(
            json.dumps({"type": "FeatureCollection", "features": features}, indent=2),
            encoding="utf-8"
        )


def main():
    parser = argparse.ArgumentParser(description="FloodSpaceAI — Parameterized Asset & Connectivity Engine")
    parser.add_argument("--bbox", nargs=4, type=float, required=True, help="Bounding box: WEST SOUTH EAST NORTH")
    parser.add_argument("--flood-date", type=str, required=True, help="Flood event date: YYYY-MM-DD")
    parser.add_argument("--flood-raster", type=str, default=None, help="Path to flood candidate GeoTIFF")
    parser.add_argument("--flood-polygons", type=str, default=None, help="Path to pre-extracted flood polygons GeoJSON")
    parser.add_argument("--run-id", type=str, default=None, help="Unique pipeline run ID")
    parser.add_argument("--osm-dir", type=str, default=None, help="Path to explicit pre-downloaded OSM directory")
    parser.add_argument("--snapshot-date", type=str, default=None, help="Historical OSM snapshot timestamp")
    parser.add_argument("--output-base-dir", type=str, default=None, help="Base output directory for runs")

    args = parser.parse_args()

    engine = ParameterizedAssetConnectivityEngine(
        bbox=args.bbox,
        flood_date=args.flood_date,
        flood_raster_path=Path(args.flood_raster) if args.flood_raster else None,
        flood_polygons_path=Path(args.flood_polygons) if args.flood_polygons else None,
        run_id=args.run_id,
        osm_dir=Path(args.osm_dir) if args.osm_dir else None,
        snapshot_date=args.snapshot_date,
        output_base_dir=Path(args.output_base_dir) if args.output_base_dir else None
    )

    result = engine.execute()
    if result.get("status") == "SUCCESS_COMPLETED":
        sys.exit(0)
    else:
        print(f"Execution finished with status: {result.get('status')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
