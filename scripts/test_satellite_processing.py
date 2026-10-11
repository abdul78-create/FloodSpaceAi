#!/usr/bin/env python3
"""
FloodSpaceAI — Test Suite for Parameterized Satellite Raster Processing Engine (Phase 3)

Tests:
1. Trishuli Benchmark: Verified cached inputs produce exact V3 candidate pixels (1,286 px).
2. Anti-Pollution Check: Unseen date/AOI without downloaded rasters fails cleanly (no accidental Trishuli reuse).
3. Missing Input Handling: Graceful descriptive failure when explicit input rasters are missing.
4. Cloudy / Invalid Optical Pixel Handling: SCL cloud/shadow masking and nodata verification.
5. Grid Alignment & NoData Propagation: Pixel-for-pixel alignment across SAR & optical layers.
6. Input Validation: Inverted bbox and invalid calendar dates.
7. Unseen AOI End-to-End Processing: Proves that new custom/downloaded rasters process through V3.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
import sys
import tempfile

import numpy as np

# Configure GDAL DLL directory for Windows environment
for dll_dir in [r"C:\Program Files\QGIS 3.44.14\bin", r"C:\OSGeo4W\bin"]:
    if os.path.exists(dll_dir):
        try:
            os.add_dll_directory(dll_dir)
        except Exception:
            pass

from osgeo import gdal

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from run_satellite_processing import (
    SatelliteRasterPipeline,
    is_trishuli_benchmark,
    TRISHULI_BBOX,
    TRISHULI_FLOOD_DATE,
    NODATA_FLOAT,
    NODATA_BYTE,
    write_single_band_raster
)


def run_all_tests():
    print("=" * 76)
    print("FloodSpaceAI — Phase 3 Raster Processing Test Suite")
    print("=" * 76)

    test_results = []

    # ------------------------------------------------------------------------
    # TEST 1: Trishuli Benchmark Run (Cached Raw Inputs)
    # ------------------------------------------------------------------------
    print("\n[TEST 1] Trishuli Benchmark Run (Cached Verified Inputs)")
    p1 = SatelliteRasterPipeline(
        bbox=TRISHULI_BBOX,
        flood_date=TRISHULI_FLOOD_DATE,
        run_id="test_trishuli_benchmark"
    )
    res1 = p1.execute()
    v3_m = res1.get("v3_flood_metrics", {})
    t1_ok = (
        res1["status"] == "SUCCESS_COMPLETED"
        and v3_m.get("final_v3_pixels") == 1286
        and v3_m.get("raw_candidate_pixels") == 3040
        and (p1.rasters_dir / "final_flood_candidate_v3.tif").exists()
        and (p1.rasters_dir / "filtered_vv_change_db.tif").exists()
        and (p1.rasters_dir / "pre_ndwi_cloudmasked.tif").exists()
    )
    test_results.append((
        "Test 1: Trishuli Benchmark (1,286 V3 pixels)",
        t1_ok,
        f"Status: {res1['status']}, V3 Pixels: {v3_m.get('final_v3_pixels')}, Clusters: {v3_m.get('final_flood_clusters')}"
    ))
    print(f"  Result: {'PASS' if t1_ok else 'FAIL'}")
    print(f"  V3 Candidate Pixels: {v3_m.get('final_v3_pixels')} (expected 1,286)")
    print(f"  Raw Pixels:          {v3_m.get('raw_candidate_pixels')} (expected 3,040)")
    print(f"  Patch Reduction:     {v3_m.get('patch_reduction_pct')}% (expected 57.7%)")

    # ------------------------------------------------------------------------
    # TEST 2: Anti-Pollution Check on Different Date (No Accidental Reuse)
    # ------------------------------------------------------------------------
    print("\n[TEST 2] Anti-Pollution Check: Unseen Date Must NOT Reuse Trishuli Cache")
    p2 = SatelliteRasterPipeline(
        bbox=TRISHULI_BBOX,
        flood_date="2024-08-15",
        run_id="test_anti_pollution_date"
    )
    res2 = p2.execute()
    t2_ok = (
        res2["status"] == "PARTIAL_RUN_IMAGERY_UNAVAILABLE"
        and "Strict provenance isolation" in res2.get("error_message", "")
        and len(list(p2.rasters_dir.glob("*.tif"))) == 0
    )
    test_results.append((
        "Test 2: Anti-Pollution Isolation (Unseen Date)",
        t2_ok,
        f"Status: {res2['status']}, Message: {res2.get('error_message', '')[:65]}..."
    ))
    print(f"  Result: {'PASS' if t2_ok else 'FAIL'}")
    print(f"  Status:  {res2['status']}")
    print(f"  Message: {res2.get('error_message')}")

    # ------------------------------------------------------------------------
    # TEST 3: Missing Input Handling
    # ------------------------------------------------------------------------
    print("\n[TEST 3] Missing Explicit Input Files Handling")
    p3 = SatelliteRasterPipeline(
        bbox=[85.0, 27.8, 85.1, 27.9],
        flood_date="2026-09-01",
        run_id="test_missing_inputs",
        s1_pre_path="non_existent_s1_pre.tif",
        s1_post_path="non_existent_s1_post.tif",
        s2_pre_path="non_existent_s2_pre.tif",
        s2_post_path="non_existent_s2_post.tif"
    )
    res3 = p3.execute()
    t3_ok = (
        res3["status"] == "FAILED_MISSING_OVERRIDE"
        and "not found" in res3.get("error_message", "")
    )
    test_results.append((
        "Test 3: Missing Input Error Handling",
        t3_ok,
        f"Status: {res3['status']}, Error: {res3.get('error_message')}"
    ))
    print(f"  Result: {'PASS' if t3_ok else 'FAIL'}")
    print(f"  Status: {res3['status']}")

    # ------------------------------------------------------------------------
    # TEST 4: Cloudy & Invalid Optical Pixels Masking
    # ------------------------------------------------------------------------
    print("\n[TEST 4] SCL Cloud/Shadow Masking & Nodata Propagation")
    # Inspect generated post_ndwi_cloudmasked.tif in test 1
    post_ndwi_ds = gdal.Open(str(p1.rasters_dir / "post_ndwi_cloudmasked.tif"))
    band = post_ndwi_ds.GetRasterBand(1)
    arr = band.ReadAsArray()
    nodata = band.GetNoDataValue()
    valid_opt = (arr != nodata) & np.isfinite(arr)
    valid_opt_count = int(valid_opt.sum())
    # Raw file has 2,208,564 valid pixels out of 4,194,304 (52.66% coverage, 47.34% cloudy)
    t4_ok = (
        valid_opt_count == 2208564
        and nodata == NODATA_FLOAT
    )
    test_results.append((
        "Test 4: SCL Cloud/Shadow Masking Policy",
        t4_ok,
        f"Valid Optical Pixels: {valid_opt_count} / {arr.size} (52.66%), Nodata: {nodata}"
    ))
    print(f"  Result: {'PASS' if t4_ok else 'FAIL'}")
    print(f"  Valid Unmasked Pixels: {valid_opt_count:,} ({valid_opt_count / arr.size * 100:.2f}%)")
    print(f"  Cloud-Masked Pixels:   {arr.size - valid_opt_count:,} ({(1 - valid_opt_count / arr.size) * 100:.2f}%)")
    print(f"  Nodata Value:          {nodata}")

    # ------------------------------------------------------------------------
    # TEST 5: Grid Alignment & Nodata Propagation to Flood Candidate
    # ------------------------------------------------------------------------
    print("\n[TEST 5] Grid Alignment & NoData Propagation")
    vv_ds = gdal.Open(str(p1.rasters_dir / "filtered_vv_change_db.tif"))
    flood_ds = gdal.Open(str(p1.rasters_dir / "final_flood_candidate_v3.tif"))
    
    gt_vv = vv_ds.GetGeoTransform()
    gt_flood = flood_ds.GetGeoTransform()
    dims_vv = (vv_ds.RasterXSize, vv_ds.RasterYSize)
    dims_flood = (flood_ds.RasterXSize, flood_ds.RasterYSize)
    
    flood_arr = flood_ds.GetRasterBand(1).ReadAsArray()
    flood_nodata = flood_ds.GetRasterBand(1).GetNoDataValue()

    # Where post NDWI is cloudy (invalid), flood candidate MUST be 0 (or nodata), NEVER 1
    cloud_pixels = ~valid_opt
    false_positives_in_cloud = int((flood_arr[cloud_pixels] == 1).sum())

    t5_ok = (
        gt_vv == gt_flood
        and dims_vv == dims_flood
        and flood_nodata == NODATA_BYTE
        and false_positives_in_cloud == 0
    )
    test_results.append((
        "Test 5: Grid Alignment & Zero Cloud False Positives",
        t5_ok,
        f"Alignment: {dims_vv} vs {dims_flood}, False water in cloudy pixels: {false_positives_in_cloud}"
    ))
    print(f"  Result: {'PASS' if t5_ok else 'FAIL'}")
    print(f"  GeoTransform Match: {gt_vv == gt_flood}")
    print(f"  Dimensions Match:   {dims_vv == dims_flood} ({dims_vv[0]}x{dims_vv[1]})")
    print(f"  False Water in Cloudy Pixels: {false_positives_in_cloud} (strictly 0)")

    # ------------------------------------------------------------------------
    # TEST 6: Input Validation Errors
    # ------------------------------------------------------------------------
    print("\n[TEST 6] Input Validation Failure Cases")
    p6a = SatelliteRasterPipeline(bbox=[85.25, 28.05, 84.90, 27.75], flood_date="2026-08-28")  # Inverted bbox
    res6a = p6a.execute()
    p6b = SatelliteRasterPipeline(bbox=TRISHULI_BBOX, flood_date="2026-02-31")  # Invalid date
    res6b = p6b.execute()

    t6_ok = (
        res6a["status"] == "FAILED_INVALID_INPUT"
        and res6b["status"] == "FAILED_INVALID_INPUT"
    )
    test_results.append((
        "Test 6: Input Validation Error Rejection",
        t6_ok,
        f"6a (Inverted Bbox): {res6a['status']}, 6b (Invalid Day): {res6b['status']}"
    ))
    print(f"  Result: {'PASS' if t6_ok else 'FAIL'}")
    print(f"  6a: {res6a['status']} -> {res6a.get('error_message')}")
    print(f"  6b: {res6b['status']} -> {res6b.get('error_message')}")

    # ------------------------------------------------------------------------
    # TEST 7: End-to-End Processing on Unseen AOI (New Custom Synthetic Rasters)
    # ------------------------------------------------------------------------
    print("\n[TEST 7] Genuinely Unseen AOI End-to-End Raster Processing Run")
    # Create distinct 100x100 test rasters for Pokhara valley sub-box [83.95, 28.18, 84.05, 28.28]
    test_aoi_bbox = [83.95, 28.18, 84.05, 28.28]
    test_flood_date = "2026-09-15"
    test_rows, test_cols = 100, 100
    test_gt = (83.95, 0.001, 0.0, 28.28, 0.0, -0.001)
    
    # We create a temporary directory for the new raw test rasters
    temp_raw_dir = Path(tempfile.mkdtemp(prefix="floodspace_test_raw_"))
    s1_pre_f = temp_raw_dir / "s1_pre_vv_vh.tif"
    s1_post_f = temp_raw_dir / "s1_post_vv_vh.tif"
    s2_pre_f = temp_raw_dir / "s2_pre_b03_b08_scl.tif"
    s2_post_f = temp_raw_dir / "s2_post_b03_b08_scl.tif"

    driver = gdal.GetDriverByName("GTiff")
    srs = "EPSG:4326"

    # S1 pre: baseline amplitude 0.20
    # S1 post: flood patch (rows 40..60, cols 40..60) drops to 0.05 (drop of -6.0 dB < -1.5 dB)
    ds_s1_pre = driver.Create(str(s1_pre_f), test_cols, test_rows, 2, gdal.GDT_Float32)
    ds_s1_pre.SetGeoTransform(test_gt)
    ds_s1_pre.GetRasterBand(1).WriteArray(np.full((test_rows, test_cols), 0.20, dtype=np.float32))
    ds_s1_pre.GetRasterBand(2).WriteArray(np.full((test_rows, test_cols), 0.10, dtype=np.float32))
    ds_s1_pre = None

    s1_post_vv = np.full((test_rows, test_cols), 0.20, dtype=np.float32)
    s1_post_vh = np.full((test_rows, test_cols), 0.10, dtype=np.float32)
    s1_post_vv[40:60, 40:60] = 0.05  # -6.02 dB drop
    s1_post_vh[40:60, 40:60] = 0.025 # -6.02 dB drop
    ds_s1_post = driver.Create(str(s1_post_f), test_cols, test_rows, 2, gdal.GDT_Float32)
    ds_s1_post.SetGeoTransform(test_gt)
    ds_s1_post.GetRasterBand(1).WriteArray(s1_post_vv)
    ds_s1_post.GetRasterBand(2).WriteArray(s1_post_vh)
    ds_s1_post = None

    # S2 pre: vegetation (B03=0.10, B08=0.30 -> NDWI = (0.1-0.3)/0.4 = -0.50 < 0.20)
    ds_s2_pre = driver.Create(str(s2_pre_f), test_cols, test_rows, 3, gdal.GDT_Float32)
    ds_s2_pre.SetGeoTransform(test_gt)
    ds_s2_pre.GetRasterBand(1).WriteArray(np.full((test_rows, test_cols), 0.10, dtype=np.float32))
    ds_s2_pre.GetRasterBand(2).WriteArray(np.full((test_rows, test_cols), 0.30, dtype=np.float32))
    ds_s2_pre.GetRasterBand(3).WriteArray(np.full((test_rows, test_cols), 4.0, dtype=np.float32)) # SCL=4 vegetation
    ds_s2_pre = None

    # S2 post: flood patch becomes water (B03=0.25, B08=0.10 -> NDWI = (0.25-0.10)/0.35 = +0.43 > 0.05)
    # Change is +0.43 - (-0.50) = +0.93 > 0.15
    s2_post_b3 = np.full((test_rows, test_cols), 0.10, dtype=np.float32)
    s2_post_b8 = np.full((test_rows, test_cols), 0.30, dtype=np.float32)
    s2_post_scl = np.full((test_rows, test_cols), 4.0, dtype=np.float32)

    s2_post_b3[40:60, 40:60] = 0.25
    s2_post_b8[40:60, 40:60] = 0.10
    s2_post_scl[40:60, 40:60] = 6.0 # SCL=6 water

    ds_s2_post = driver.Create(str(s2_post_f), test_cols, test_rows, 3, gdal.GDT_Float32)
    ds_s2_post.SetGeoTransform(test_gt)
    ds_s2_post.GetRasterBand(1).WriteArray(s2_post_b3)
    ds_s2_post.GetRasterBand(2).WriteArray(s2_post_b8)
    ds_s2_post.GetRasterBand(3).WriteArray(s2_post_scl)
    ds_s2_post = None

    # Execute pipeline with explicit new inputs
    p7 = SatelliteRasterPipeline(
        bbox=test_aoi_bbox,
        flood_date=test_flood_date,
        run_id="test_unseen_aoi_end_to_end",
        s1_pre_path=str(s1_pre_f),
        s1_post_path=str(s1_post_f),
        s2_pre_path=str(s2_pre_f),
        s2_post_path=str(s2_post_f)
    )
    res7 = p7.execute()
    v3_m7 = res7.get("v3_flood_metrics", {})
    t7_ok = (
        res7["status"] == "SUCCESS_COMPLETED"
        and v3_m7.get("final_v3_pixels") == 396 # 20x20 patch with 4 corner pixels rounded by 3x3 median filter = 396 pixels
        and (p7.rasters_dir / "final_flood_candidate_v3.tif").exists()
        and (p7.rasters_dir / "filtered_vv_change_db.tif").exists()
    )
    test_results.append((
        "Test 7: Unseen AOI End-to-End Processing (396 new V3 px)",
        t7_ok,
        f"Status: {res7['status']}, New V3 Pixels: {v3_m7.get('final_v3_pixels')}, Area: {v3_m7.get('estimated_candidate_area_ha')} ha"
    ))
    print(f"  Result: {'PASS' if t7_ok else 'FAIL'}")
    print(f"  Status:             {res7['status']}")
    print(f"  New V3 Pixels:      {v3_m7.get('final_v3_pixels')} (expected 396)")
    print(f"  New Candidate Area: {v3_m7.get('estimated_candidate_area_ha')} ha")
    print(f"  Run Directory:      {p7.run_dir}")

    # Cleanup temp raw files
    for f in [s1_pre_f, s1_post_f, s2_pre_f, s2_post_f]:
        if f.exists():
            f.unlink()
    if temp_raw_dir.exists():
        temp_raw_dir.rmdir()

    # ------------------------------------------------------------------------
    # SUMMARY REPORT
    # ------------------------------------------------------------------------
    print("\n" + "=" * 76)
    print("PHASE 3 TEST SUITE SUMMARY:")
    print("=" * 76)
    all_passed = True
    for name, passed, details in test_results:
        status_str = "PASS [OK]" if passed else "FAIL [X]"
        print(f"  {status_str} : {name}")
        print(f"          Details: {details}")
        if not passed:
            all_passed = False

    print("=" * 76)
    print(f"OVERALL RESULT: {'ALL TESTS PASSED (7/7)' if all_passed else 'SOME TESTS FAILED'}")
    print("=" * 76)

    # Save machine-readable test summary
    summary_path = REPO_ROOT / "data" / "processed" / "phase3_test_suite_summary.json"
    summary_data = {
        "suite": "Phase 3 Parameterized Satellite Raster Processing",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "all_passed": all_passed,
        "total_tests": len(test_results),
        "passed_tests": sum(1 for _, p, _ in test_results if p),
        "results": [
            {"test_name": name, "passed": passed, "details": details}
            for name, passed, details in test_results
        ]
    }
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)
    print(f"\nSaved machine-readable summary: {summary_path}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
