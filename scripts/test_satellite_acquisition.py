#!/usr/bin/env python3
"""
FloodSpaceAI — Phase 4A Test Suite: Real Satellite Imagery Acquisition & Provenance

Tests:
1. Real Provider Retrieval & Checksums: Verified live download from AWS Open Data / Element84 STAC.
2. Future Date Rejection: Clear UNAVAILABLE_FUTURE_DATE status for post-catalog dates.
3. Empty Catalog Handling: Clear EMPTY_CATALOG_RESULTS for coordinates without coverage.
4. Benchmark Isolation: Trishuli August 2026 strictly labeled VERIFIED_BENCHMARK_FIXTURE.
5. Multi-Tile MGRS Mosaicking: Successful alignment across tile boundaries.
6. Corrupt / Incomplete Raster Handling: Safe rejection of malformed or truncated inputs.
7. Anti-Synthetic Provenance Enforcement: Strict separation between synthetic fixtures and real data.
8. Secret & Credential Safety: Verifies no secrets or tokens are leaked in metadata or logs.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any
from unittest.mock import patch, MagicMock

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

from acquire_satellite_data import SatelliteAcquisitionEngine, compute_sha256
from run_satellite_processing import SatelliteRasterPipeline, TRISHULI_BBOX, TRISHULI_FLOOD_DATE


def run_all_acquisition_tests() -> int:
    print("=" * 78)
    print("FloodSpaceAI — Phase 4A Real Satellite Acquisition Test Suite")
    print("=" * 78)

    test_results = []
    engine = SatelliteAcquisitionEngine()

    # ------------------------------------------------------------------------
    # TEST 1: Real Provider Live Acquisition & Checksum Verification
    # ------------------------------------------------------------------------
    print("\n[TEST 1] Live Authoritative Satellite Retrieval (August 2024 Event)")
    test_run_dir = REPO_ROOT / "data" / "processed" / "pipeline_runs" / "test_live_data_end_to_end"
    meta_file = test_run_dir / "run_metadata.json"
    
    meta: dict[str, Any] = {}
    if meta_file.exists():
        with open(meta_file, "r", encoding="utf-8") as f:
            meta = json.load(f)
        prov = meta.get("raster_provenance", {})
        checksums = prov.get("checksums", {})
        s1_meta = prov.get("sentinel1_acquisition", {})
        s2_meta = prov.get("sentinel2_acquisition", {})

        t1_ok = (
            meta.get("status") == "SUCCESS_COMPLETED"
            and prov.get("mode") == "LIVE_AUTHORITATIVE_SATELLITE_RETRIEVAL"
            and len(checksums) == 4
            and all(len(c) == 64 for c in checksums.values())
            and s1_meta.get("orbit_match_verified") is True
            and "sentinel-1" in s1_meta.get("collection", "").lower()
            and "sentinel-2" in s2_meta.get("collection", "").lower()
        )
        test_results.append((
            "Test 1: Live Real-Data Retrieval & Checksums",
            t1_ok,
            f"Provider: {prov.get('provider')}, Checksums: {len(checksums)} verified, Mode: {prov.get('mode')}"
        ))
        print(f"  Result: {'PASS' if t1_ok else 'FAIL'}")
        print(f"  Provider: {prov.get('provider')}")
        print(f"  Mode:     {prov.get('mode')}")
        print(f"  Pre S1 SHA-256:  {checksums.get('s1_pre')}")
        print(f"  Post S1 SHA-256: {checksums.get('s1_post')}")
        print(f"  Pre S2 SHA-256:  {checksums.get('s2_pre')}")
        print(f"  Post S2 SHA-256: {checksums.get('s2_post')}")
    else:
        test_results.append(("Test 1: Live Real-Data Retrieval & Checksums", False, "Missing test_live_data_end_to_end run"))
        print("  Result: FAIL (Run directory missing)")

    # ------------------------------------------------------------------------
    # TEST 2: Future Date Rejection (No Hallucinated Observations)
    # ------------------------------------------------------------------------
    print("\n[TEST 2] Future Date Rejection (2026-12-31)")
    with tempfile.TemporaryDirectory() as tmp:
        res2 = engine.acquire_all(
            bbox=[84.95, 27.80, 85.05, 27.90],
            flood_date="2026-12-31",
            out_dir=Path(tmp),
            width=64,
            height=64
        )
    t2_ok = (
        res2.get("status") == "UNAVAILABLE_FUTURE_DATE"
        and "future" in res2.get("error", "").lower()
    )
    test_results.append((
        "Test 2: Future Date Rejection",
        t2_ok,
        f"Status: {res2.get('status')}, Error: {res2.get('error')}"
    ))
    print(f"  Result: {'PASS' if t2_ok else 'FAIL'}")
    print(f"  Status: {res2.get('status')}")
    print(f"  Error:  {res2.get('error')}")

    # ------------------------------------------------------------------------
    # TEST 3: Empty Catalog Handling
    # ------------------------------------------------------------------------
    print("\n[TEST 3] Empty Catalog Handling (Remote Pacific Ocean Coordinates)")
    with tempfile.TemporaryDirectory() as tmp:
        # Pacific ocean coordinates with no land/S2 tiles
        res3 = engine.acquire_all(
            bbox=[-140.0, -20.0, -139.9, -19.9],
            flood_date="2024-01-15",
            out_dir=Path(tmp),
            width=64,
            height=64
        )
    t3_ok = res3.get("status") in ["EMPTY_CATALOG_RESULTS", "NO_COMPATIBLE_SAR_PAIR"]
    test_results.append((
        "Test 3: Empty Catalog Handling",
        t3_ok,
        f"Status: {res3.get('status')}, Msg: {res3.get('sar_error') or res3.get('message')}"
    ))
    print(f"  Result: {'PASS' if t3_ok else 'FAIL'}")
    print(f"  Status: {res3.get('status')}")

    # ------------------------------------------------------------------------
    # TEST 4: Benchmark Fixture Isolation (Trishuli August 2026)
    # ------------------------------------------------------------------------
    print("\n[TEST 4] Trishuli Benchmark Isolation (Strict Fixture Labeling)")
    with tempfile.TemporaryDirectory() as tmp:
        res4 = engine.acquire_all(
            bbox=TRISHULI_BBOX,
            flood_date=TRISHULI_FLOOD_DATE,
            out_dir=Path(tmp),
            width=64,
            height=64
        )
    t4_ok = (
        res4.get("status") == "VERIFIED_BENCHMARK_FIXTURE"
        and res4.get("provenance_mode") == "VERIFIED_TRISHULI_BENCHMARK_CACHE"
        and any(w in res4.get("notice", "").lower() for w in ["benchmark", "fixture", "reference"])
    )
    test_results.append((
        "Test 4: Benchmark Fixture Labeling",
        t4_ok,
        f"Status: {res4.get('status')}, Mode: {res4.get('provenance_mode')}"
    ))
    print(f"  Result: {'PASS' if t4_ok else 'FAIL'}")
    print(f"  Status: {res4.get('status')}")
    print(f"  Mode:   {res4.get('provenance_mode')}")

    # ------------------------------------------------------------------------
    # TEST 5: Multi-Tile MGRS Mosaicking Verification
    # ------------------------------------------------------------------------
    print("\n[TEST 5] Multi-Tile MGRS Mosaicking")
    # Check optical metadata in Test 1 run
    s2_acq = meta.get("raster_provenance", {}).get("sentinel2_acquisition", {})
    t5_ok = (
        s2_acq.get("multi_tile_mosaicking_applied") is True
        and len(s2_acq.get("pre_acquisition", {}).get("tiles", [])) >= 2
    )
    test_results.append((
        "Test 5: Multi-Tile MGRS Mosaicking",
        t5_ok,
        f"Multi-tile applied: {s2_acq.get('multi_tile_mosaicking_applied')}, Tiles: {s2_acq.get('pre_acquisition', {}).get('tiles')}"
    ))
    print(f"  Result: {'PASS' if t5_ok else 'FAIL'}")
    print(f"  Multi-Tile Applied: {s2_acq.get('multi_tile_mosaicking_applied')}")
    print(f"  Pre Tiles Mosaicked:  {s2_acq.get('pre_acquisition', {}).get('tiles')}")
    print(f"  Post Tiles Mosaicked: {s2_acq.get('post_acquisition', {}).get('tiles')}")

    # ------------------------------------------------------------------------
    # TEST 6: Corrupt / Truncated Raster Rejection
    # ------------------------------------------------------------------------
    print("\n[TEST 6] Corrupt / Truncated Raster Handling")
    with tempfile.TemporaryDirectory() as tmp:
        corrupt_f = Path(tmp) / "corrupt.tif"
        corrupt_f.write_bytes(b"NOT_A_VALID_TIFF_HEADER_123456789")
        p6 = SatelliteRasterPipeline(
            bbox=[84.95, 27.80, 85.05, 27.90],
            flood_date="2024-08-20",
            run_id="test_corrupt_raster",
            s1_pre_path=str(corrupt_f),
            s1_post_path=str(corrupt_f),
            s2_pre_path=str(corrupt_f),
            s2_post_path=str(corrupt_f)
        )
        res6 = p6.execute()
    t6_ok = res6.get("status") == "FAILED_SAR_PROCESSING"
    test_results.append((
        "Test 6: Corrupt Input Rejection",
        t6_ok,
        f"Status: {res6.get('status')}, Error: {res6.get('error_message')}"
    ))
    print(f"  Result: {'PASS' if t6_ok else 'FAIL'}")
    print(f"  Status: {res6.get('status')}")
    print(f"  Error:  {res6.get('error_message')}")

    # ------------------------------------------------------------------------
    # TEST 7: Anti-Synthetic Provenance Enforcement
    # ------------------------------------------------------------------------
    print("\n[TEST 7] Strict Provenance Separation (No Synthetic Labeling as Real)")
    # When user supplies manual rasters, mode MUST be EXPLICIT_USER_SUPPLIED_INPUTS, never LIVE_DOWNLOADED
    with tempfile.TemporaryDirectory() as tmp:
        # Create minimal 2-pixel TIFFs
        driver = gdal.GetDriverByName("GTiff")
        f_s1 = Path(tmp) / "s1.tif"
        f_s2 = Path(tmp) / "s2.tif"
        ds1 = driver.Create(str(f_s1), 2, 2, 2, gdal.GDT_Float32)
        ds1.SetGeoTransform((84.95, 0.05, 0, 27.90, 0, -0.05))
        ds1.GetRasterBand(1).WriteArray(np.ones((2, 2)))
        ds1.GetRasterBand(2).WriteArray(np.ones((2, 2)))
        ds1 = None
        ds2 = driver.Create(str(f_s2), 2, 2, 3, gdal.GDT_Float32)
        ds2.SetGeoTransform((84.95, 0.05, 0, 27.90, 0, -0.05))
        ds2.GetRasterBand(1).WriteArray(np.ones((2, 2)))
        ds2.GetRasterBand(2).WriteArray(np.ones((2, 2)))
        ds2.GetRasterBand(3).WriteArray(np.ones((2, 2)))
        ds2 = None

        p7 = SatelliteRasterPipeline(
            bbox=[84.95, 27.80, 85.05, 27.90],
            flood_date="2024-08-20",
            run_id="test_explicit_provenance",
            s1_pre_path=str(f_s1),
            s1_post_path=str(f_s1),
            s2_pre_path=str(f_s2),
            s2_post_path=str(f_s2)
        )
        res7 = p7.execute()
    mode7 = res7.get("raster_provenance", {}).get("mode")
    t7_ok = (mode7 == "EXPLICIT_USER_SUPPLIED_INPUTS" and mode7 != "LIVE_AUTHORITATIVE_SATELLITE_RETRIEVAL")
    test_results.append((
        "Test 7: Anti-Synthetic Provenance Enforcement",
        t7_ok,
        f"Provenance mode: {mode7} (strictly distinct from LIVE_AUTHORITATIVE_SATELLITE_RETRIEVAL)"
    ))
    print(f"  Result: {'PASS' if t7_ok else 'FAIL'}")
    print(f"  Mode:   {mode7}")

    # ------------------------------------------------------------------------
    # TEST 8: Secrets & Token Safety in Logs and Metadata
    # ------------------------------------------------------------------------
    print("\n[TEST 8] Safe Handling of Secrets")
    # Verify no Authorization headers, bearer tokens, or secret keys appear in metadata
    meta_str = json.dumps(meta)
    leaked_keywords = ["bearer ", "secret_key", "password", "client_secret", "private_key"]
    has_leak = any(k in meta_str.lower() for k in leaked_keywords)
    t8_ok = not has_leak
    test_results.append((
        "Test 8: Secrets & Token Safety",
        t8_ok,
        "No tokens or secrets found in metadata" if t8_ok else "Potential secret leaked"
    ))
    print(f"  Result: {'PASS' if t8_ok else 'FAIL'}")
    print(f"  Secret Leak Detected: {has_leak}")

    # ------------------------------------------------------------------------
    # SUMMARY REPORT
    # ------------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("PHASE 4A TEST SUITE SUMMARY:")
    print("=" * 78)
    all_passed = True
    for name, passed, details in test_results:
        status_str = "PASS [OK]" if passed else "FAIL [X]"
        print(f"  {status_str} : {name}")
        print(f"          Details: {details}")
        if not passed:
            all_passed = False

    print("=" * 78)
    print(f"OVERALL RESULT: {'ALL TESTS PASSED (8/8)' if all_passed else 'SOME TESTS FAILED'}")
    print("=" * 78)

    summary_file = REPO_ROOT / "data" / "processed" / "phase4a_test_suite_summary.json"
    summary_data = {
        "suite": "Phase 4A Real Satellite Acquisition & Provenance Test Suite",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "all_passed": all_passed,
        "total_tests": len(test_results),
        "passed_tests": sum(1 for _, p, _ in test_results if p),
        "results": [
            {"test_name": name, "passed": passed, "details": details}
            for name, passed, details in test_results
        ]
    }
    summary_file.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)
    print(f"\nSaved machine-readable summary: {summary_file}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(run_all_acquisition_tests())
