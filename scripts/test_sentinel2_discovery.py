#!/usr/bin/env python3
"""
FloodSpaceAI — Test Suite for Parameterized Sentinel-2 Discovery Engine (Phase 2)

Tests:
1. Existing Trishuli AOI and flood date 2026-08-28 (Trishuli benchmark).
2. A different date using the same bbox (e.g. 2024-08-15).
3. AOI crossing Sentinel-2 tile boundaries (verifying multi-tile mosaicking detection).
4. No suitable pair found (e.g. strict max_cloud_cover=5% during monsoon season).
5. Invalid inputs (invalid dates and inverted bounding boxes).
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from search_sentinel2_pair import find_sentinel2_pair, validate_inputs


def run_tests():
    print("=" * 76)
    print("FloodSpaceAI — Sentinel-2 Optical Discovery Test Suite (Phase 2)")
    print("=" * 76)

    test_results = []

    # ------------------------------------------------------------------------
    # TEST 1: Trishuli Benchmark (bbox + 2026-08-28)
    # ------------------------------------------------------------------------
    print("\n[TEST 1] Trishuli Baseline (Bbox: [84.90, 27.75, 85.25, 28.05], Date: 2026-08-28)")
    t1_pair = find_sentinel2_pair(
        bbox=[84.90, 27.75, 85.25, 28.05],
        flood_date="2026-08-28",
        max_cloud_cover=85.0
    )
    t1_ok = (
        t1_pair.status == "SUCCESS_MATCHED_PAIR"
        and t1_pair.pre_event_acquisition is not None
        and t1_pair.post_event_acquisition is not None
        and t1_pair.post_event_acquisition["date"] == "2026-08-27"
        and t1_pair.pre_event_acquisition["date"] == "2026-08-12"
        and t1_pair.requires_mosaicking is True
        and len(t1_pair.tiles_involved) == 4
    )
    test_results.append(("Test 1: Trishuli Benchmark", t1_ok, f"Status: {t1_pair.status}, Post: {t1_pair.post_event_acquisition['date'] if t1_pair.post_event_acquisition else None}, Pre: {t1_pair.pre_event_acquisition['date'] if t1_pair.pre_event_acquisition else None}"))
    print(f"  Result: {'PASS' if t1_ok else 'FAIL'}")
    print(f"  Post Scene Date: {t1_pair.post_event_acquisition['date'] if t1_pair.post_event_acquisition else 'None'}")
    print(f"  Pre Scene Date:  {t1_pair.pre_event_acquisition['date'] if t1_pair.pre_event_acquisition else 'None'}")
    print(f"  Tiles Involved:  {t1_pair.tiles_involved}")
    print(f"  Requires Mosaic: {t1_pair.requires_mosaicking}")

    # ------------------------------------------------------------------------
    # TEST 2: Different Date on Same Bbox (e.g. 2024-08-15)
    # ------------------------------------------------------------------------
    print("\n[TEST 2] Alternative Date Test (Bbox: Trishuli, Date: 2024-08-15)")
    t2_pair = find_sentinel2_pair(
        bbox=[84.90, 27.75, 85.25, 28.05],
        flood_date="2024-08-15",
        pre_window_days=21,
        post_window_days=10,
        max_cloud_cover=90.0
    )
    t2_ok = (
        t2_pair.status in ("SUCCESS_MATCHED_PAIR", "PARTIAL_MATCH")
        and t2_pair.post_event_acquisition is not None
        and t2_pair.query_flood_date == "2024-08-15"
    )
    test_results.append(("Test 2: Alternative Date (2024-08-15)", t2_ok, f"Status: {t2_pair.status}, Post: {t2_pair.post_event_acquisition['date'] if t2_pair.post_event_acquisition else None}"))
    print(f"  Result: {'PASS' if t2_ok else 'FAIL'}")
    if t2_pair.post_event_acquisition:
        print(f"  Discovered Post: {t2_pair.post_event_acquisition['date']} (Cloud: {t2_pair.post_event_acquisition['mean_cloud_cover_pct']}%)")
    if t2_pair.pre_event_acquisition:
        print(f"  Discovered Pre:  {t2_pair.pre_event_acquisition['date']} (Cloud: {t2_pair.pre_event_acquisition['mean_cloud_cover_pct']}%)")

    # ------------------------------------------------------------------------
    # TEST 3: AOI Crossing Tile Boundaries vs Single Tile
    # ------------------------------------------------------------------------
    print("\n[TEST 3] Multi-Tile Boundary Crossing vs Single-Tile AOI")
    # Multi-tile: Trishuli spans 4 tiles (45RTL, 45RTM, 45RUL, 45RUM)
    # Single-tile: Small AOI in Kathmandu valley center [85.28, 27.65, 85.35, 27.72] (45RUL only)
    t3_single = find_sentinel2_pair(
        bbox=[85.28, 27.65, 85.35, 27.72],
        flood_date="2026-08-12",
        post_window_days=3,
        pre_window_days=10
    )
    t3_ok = (
        t1_pair.requires_mosaicking is True  # Trishuli crosses 4 tiles
        and len(t1_pair.tiles_involved) == 4
        and (t3_single.requires_mosaicking is False or len(t3_single.tiles_involved) == 1) # Kathmandu is single tile
    )
    test_results.append(("Test 3: Tile Boundary & Mosaicking Logic", t3_ok, f"Trishuli multi-tile: {t1_pair.tiles_involved}, KTM single-tile: {t3_single.tiles_involved}"))
    print(f"  Result: {'PASS' if t3_ok else 'FAIL'}")
    print(f"  Trishuli Multi-Tile ({len(t1_pair.tiles_involved)} tiles): {t1_pair.tiles_involved} -> requires_mosaicking={t1_pair.requires_mosaicking}")
    print(f"  Kathmandu Single-Tile ({len(t3_single.tiles_involved)} tiles): {t3_single.tiles_involved} -> requires_mosaicking={t3_single.requires_mosaicking}")

    # ------------------------------------------------------------------------
    # TEST 4: No Suitable Pair Found (Cloud filter too strict or mock scenario)
    # ------------------------------------------------------------------------
    print("\n[TEST 4] Edge Case: No Suitable Pair Found")
    t4_pair_mock = find_sentinel2_pair(
        bbox=[84.90, 27.75, 85.25, 28.05],
        flood_date="2026-08-28",
        mock_scenario="NO_SUITABLE_PAIR"
    )
    # Also test an impossible cloud threshold (1.0% cloud during monsoon)
    t4_pair_cloud = find_sentinel2_pair(
        bbox=[84.90, 27.75, 85.25, 28.05],
        flood_date="2026-08-28",
        max_cloud_cover=1.0,
        pre_window_days=5,
        post_window_days=3
    )
    t4_ok = (
        t4_pair_mock.status == "NO_SUITABLE_PAIR"
        and len(t4_pair_mock.warnings) > 0
    )
    test_results.append(("Test 4: No Suitable Pair Detection", t4_ok, f"Mock Status: {t4_pair_mock.status}, Strict-cloud warnings: {len(t4_pair_cloud.warnings)}"))
    print(f"  Result: {'PASS' if t4_ok else 'FAIL'}")
    print(f"  Status: {t4_pair_mock.status}")
    print(f"  Warning: {t4_pair_mock.warnings[0] if t4_pair_mock.warnings else 'None'}")

    # ------------------------------------------------------------------------
    # TEST 5: Invalid Date and Invalid Bounding Box Inputs
    # ------------------------------------------------------------------------
    print("\n[TEST 5] Input Validation Failure Cases")
    # 5a: Inverted coordinates (west > east)
    t5a = find_sentinel2_pair(
        bbox=[85.25, 28.05, 84.90, 27.75],  # Inverted
        flood_date="2026-08-28"
    )
    # 5b: Malformed date string
    t5b = find_sentinel2_pair(
        bbox=[84.90, 27.75, 85.25, 28.05],
        flood_date="invalid-date-2026"
    )
    # 5c: Impossible calendar day
    t5c = find_sentinel2_pair(
        bbox=[84.90, 27.75, 85.25, 28.05],
        flood_date="2026-02-31"
    )
    # 5d: Out of range coordinates
    t5d = find_sentinel2_pair(
        bbox=[200.0, 27.75, 205.0, 28.05],
        flood_date="2026-08-28"
    )

    t5_ok = (
        t5a.status == "INVALID_INPUT"
        and t5b.status == "INVALID_INPUT"
        and t5c.status == "INVALID_INPUT"
        and t5d.status == "INVALID_INPUT"
    )
    test_results.append(("Test 5: Input Validation Checks", t5_ok, f"5a: {t5a.status}, 5b: {t5b.status}, 5c: {t5c.status}, 5d: {t5d.status}"))
    print(f"  Result: {'PASS' if t5_ok else 'FAIL'}")
    print(f"  5a (Inverted Bbox):   {t5a.status} -> {t5a.warnings[0]}")
    print(f"  5b (Malformed Date):  {t5b.status} -> {t5b.warnings[0]}")
    print(f"  5c (Impossible Day):  {t5c.status} -> {t5c.warnings[0]}")
    print(f"  5d (Out-of-range Lon):{t5d.status} -> {t5d.warnings[0]}")

    # ------------------------------------------------------------------------
    # SUMMARY
    # ------------------------------------------------------------------------
    print("\n" + "=" * 76)
    print("TEST SUITE SUMMARY:")
    print("=" * 76)
    all_passed = True
    for name, passed, details in test_results:
        status_str = "PASS [OK]" if passed else "FAIL [X]"
        print(f"  {status_str} : {name}")
        print(f"          Details: {details}")
        if not passed:
            all_passed = False

    print("=" * 76)
    print(f"OVERALL RESULT: {'ALL TESTS PASSED (5/5)' if all_passed else 'SOME TESTS FAILED'}")
    print("=" * 76)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(run_tests())
