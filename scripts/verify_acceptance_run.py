import os
import sys
from pathlib import Path

if sys.platform == "win32":
    os.environ["PATH"] = r"C:\Program Files\QGIS 3.44.14\bin;" + os.environ.get("PATH", "")
    if hasattr(os, "add_dll_directory"):
        try:
            os.add_dll_directory(r"C:\Program Files\QGIS 3.44.14\bin")
        except Exception:
            pass

from osgeo import gdal, osr
import numpy as np
import json
import hashlib

def get_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    repo_root = Path(__file__).resolve().parent.parent
    run_dir = repo_root / "data" / "processed" / "pipeline_runs" / "narayani_2024_live"
    
    print("=" * 80)
    print("VERIFYING ACCEPTANCE RUN: narayani_2024_live")
    print("=" * 80)
    
    # Check Manifest
    manifest_path = run_dir / "run_manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    print(f"Overall Status:   {manifest.get('overall_status')}")
    print(f"Provenance Mode:  {manifest.get('provenance_mode')}")
    print(f"Target Bbox:      {manifest.get('inputs', {}).get('bbox')}")
    print(f"Flood Date:       {manifest.get('inputs', {}).get('flood_date')}")
    print(f"Snapshot Date:    {manifest.get('inputs', {}).get('snapshot_date')}")

    print("\n[1] ACQUIRED RAW SATELLITE RASTERS")
    acquired_dir = run_dir / "acquired_raw"
    for p in sorted(acquired_dir.rglob("*.tif")):
        ds = gdal.Open(str(p), gdal.GA_ReadOnly)
        gt = ds.GetGeoTransform()
        proj = ds.GetProjection()
        srs = osr.SpatialReference(wkt=proj)
        epsg = srs.GetAttrValue("AUTHORITY", 1) or "EPSG:4326"
        bands = ds.RasterCount
        w, h = ds.RasterXSize, ds.RasterYSize
        arr = ds.ReadAsArray()
        valid = int(np.count_nonzero(np.isfinite(arr) & (arr != 0)))
        sha = get_sha256(p)
        print(f"  - {p.name}:")
        print(f"      Size: {w}x{h}, Bands: {bands}, CRS: {epsg}")
        print(f"      GeoTransform: {gt}")
        print(f"      Valid pixel elements: {valid:,}")
        print(f"      SHA-256: {sha}")

    print("\n[2] PROCESSED PIPELINE RASTERS")
    rasters_dir = run_dir / "rasters"
    for p in sorted(rasters_dir.glob("*.tif")):
        ds = gdal.Open(str(p), gdal.GA_ReadOnly)
        gt = ds.GetGeoTransform()
        w, h = ds.RasterXSize, ds.RasterYSize
        bands = ds.RasterCount
        arr = ds.ReadAsArray()
        valid = int(np.count_nonzero(np.isfinite(arr)))
        sha = get_sha256(p)
        print(f"  - {p.name}: {w}x{h}, Bands: {bands}, Valid values: {valid:,}, SHA-256: {sha[:16]}...")

    print("\n[3] HISTORICAL OSM INFRASTRUCTURE")
    osm_dir = run_dir / "osm"
    for p in sorted(osm_dir.glob("*.json")):
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "features" in data:
            count = len(data["features"])
        elif isinstance(data, list):
            count = len(data)
        elif isinstance(data, dict) and "elements" in data:
            count = len(data["elements"])
        else:
            count = len(data) if isinstance(data, (dict, list)) else 1
        sha = get_sha256(p)
        print(f"  - {p.name}: {count:,} records, SHA-256: {sha}")

    print("\n[4] ASSET & CONNECTIVITY DISRUPTION")
    assets_dir = run_dir / "assets"
    conn_dir = run_dir / "connectivity"
    for p in sorted(assets_dir.glob("*.geojson")):
        with open(p, "r", encoding="utf-8") as f:
            fc = json.load(f)
        print(f"  - {p.name}: {len(fc.get('features', []))} affected features")
    for p in sorted(conn_dir.glob("*.geojson")):
        with open(p, "r", encoding="utf-8") as f:
            fc = json.load(f)
        print(f"  - {p.name}: {len(fc.get('features', []))} features")

    print("\n[5] DASHBOARD REGISTRY SYNC")
    reg_path = repo_root / "dashboard" / "public" / "data" / "pipeline_runs.json"
    with open(reg_path, "r", encoding="utf-8") as f:
        reg = json.load(f)
    print(f"  Registered runs count: {len(reg)}")
    print(f"  First registered run: {reg[0].get('run_id')} ({reg[0].get('status')})")

if __name__ == "__main__":
    main()
