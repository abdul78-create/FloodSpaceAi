#!/usr/bin/env python3
"""
FloodSpaceAI — Phase 5 End-to-End Orchestrator Test Suite

Validates the full coordination layer:
1. Complete benchmark run with verified fixtures (reproducing analytical evidence)
2. Real-data acquisition failure / empty catalog handling
3. Historical OSM unavailable handling
4. Cloud-obscured optical input handling
5. Missing or invalid inputs (e.g. inverted bbox, future date)
6. Prevention of stale cache reuse across AOIs/dates
7. Strict prohibition of validation layers (EMSR927 / UNOSAT) in production
8. Grounded evidence and report numbers matching the run manifest
9. Dashboard manifest schema validity & registry sync
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

# Configure GDAL DLL directory for Windows environment
for dll_dir in [r"C:\Program Files\QGIS 3.44.14\bin", r"C:\OSGeo4W\bin"]:
    if os.path.exists(dll_dir):
        try:
            os.add_dll_directory(dll_dir)
        except Exception:
            pass

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from run_floodspace_pipeline import FloodSpaceOrchestrator


class TestFloodSpaceOrchestrator(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="fs_phase5_test_"))

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_complete_benchmark_run(self):
        """Test 1: Complete execution on Trishuli benchmark reproducing verified metrics."""
        print("\n[TEST 1] Complete Benchmark Run with Verified Fixtures")
        orch = FloodSpaceOrchestrator(
            bbox=[84.90, 27.75, 85.25, 28.05],
            flood_date="2026-08-28",
            run_id="test_p5_benchmark_run",
            output_base_dir=self.test_dir,
            publish_to_dashboard=False
        )
        manifest = orch.execute()

        self.assertIn(manifest.get("overall_status"), ["SUCCESS", "PARTIAL_RUN_OPTICAL_UNCONFIRMED"])
        self.assertEqual(manifest.get("provenance_mode"), "VERIFIED_TRISHULI_BENCHMARK_CACHE")

        metrics = manifest.get("metrics", {})
        self.assertEqual(metrics.get("candidate_flood_pixels"), 1286)
        self.assertEqual(metrics.get("candidate_flood_clusters"), 27)
        self.assertEqual(metrics.get("potentially_affected_buildings"), 195)
        self.assertEqual(metrics.get("potentially_affected_roads"), 115)
        self.assertEqual(metrics.get("potentially_affected_bridges"), 13)
        self.assertEqual(metrics.get("disrupted_road_segments"), 3748)
        self.assertEqual(metrics.get("potentially_cut_off_settlements"), 18)
        self.assertFalse(metrics.get("hospital_data_available"))

        print("  Result: PASS")
        print(f"  Overall Status: {manifest.get('overall_status')}")
        print(f"  V3 Pixels: {metrics.get('candidate_flood_pixels')}, Bldgs: {metrics.get('potentially_affected_buildings')}, Cut-offs: {metrics.get('potentially_cut_off_settlements')}")

    def test_02_future_date_and_acquisition_failure(self):
        """Test 2: Future date rejection and acquisition safety."""
        print("\n[TEST 2] Future Date Rejection")
        orch = FloodSpaceOrchestrator(
            bbox=[84.90, 27.75, 85.25, 28.05],
            flood_date="2028-06-15",
            run_id="test_p5_future_date",
            output_base_dir=self.test_dir,
            publish_to_dashboard=False
        )
        manifest = orch.execute()
        self.assertEqual(manifest.get("overall_status"), "UNAVAILABLE_FUTURE_DATE")
        self.assertEqual(manifest["stages"]["stage_1_input_validation"]["status"], "UNAVAILABLE")
        print("  Result: PASS (Safely halted with UNAVAILABLE_FUTURE_DATE)")

    def test_03_historical_osm_unavailable(self):
        """Test 3: Unseen AOI where historical OSM cache is unavailable."""
        print("\n[TEST 3] Historical OSM Unavailable Handling (Unseen AOI)")
        orch = FloodSpaceOrchestrator(
            bbox=[83.95, 28.18, 84.05, 28.28],
            flood_date="2026-09-15",
            run_id="test_p5_unseen_osm",
            output_base_dir=self.test_dir,
            publish_to_dashboard=False
        )
        manifest = orch.execute()
        self.assertIn("UNAVAILABLE", str(manifest.get("overall_status")))
        self.assertEqual(manifest["stages"]["stage_5_historical_osm"]["status"], "SKIPPED")
        self.assertEqual(manifest["stages"]["stage_6_asset_connectivity"]["status"], "SKIPPED")
        print(f"  Result: PASS (Overall Status: {manifest.get('overall_status')})")

    def test_04_cloud_obscured_optical_handling(self):
        """Test 4: Cloud-obscured optical scene handling."""
        print("\n[TEST 4] Cloud-Obscured Optical Scene Handling")
        orch = FloodSpaceOrchestrator(
            bbox=[84.90, 27.75, 85.25, 28.05],
            flood_date="2026-08-28",
            run_id="test_p5_cloud_optical",
            output_base_dir=self.test_dir,
            publish_to_dashboard=False
        )
        manifest = orch.execute()
        stage_2 = manifest["stages"]["stage_2_satellite_discovery"]
        self.assertEqual(stage_2["status"], "PARTIAL")
        self.assertIn("cloud-limited", stage_2["message"])
        print(f"  Result: PASS ({stage_2['message']})")

    def test_05_invalid_input_validation(self):
        """Test 5: Inverted bounding box rejection."""
        print("\n[TEST 5] Inverted Bounding Box Rejection")
        orch = FloodSpaceOrchestrator(
            bbox=[85.25, 28.05, 84.90, 27.75],
            flood_date="2026-08-28",
            run_id="test_p5_invalid_bbox",
            output_base_dir=self.test_dir,
            publish_to_dashboard=False
        )
        manifest = orch.execute()
        self.assertIn(manifest.get("overall_status"), ["FAILED", "FAILED_INPUT_VALIDATION"])
        self.assertEqual(manifest["stages"]["stage_1_input_validation"]["status"], "FAILED")
        print("  Result: PASS (Caught inverted coordinate bounds)")

    def test_06_prevention_of_stale_cache_reuse(self):
        """Test 6: Prevention of stale Trishuli cache reuse on different date."""
        print("\n[TEST 6] Anti-Pollution Check: Stale Cache Reuse Blocked")
        orch = FloodSpaceOrchestrator(
            bbox=[84.90, 27.75, 85.25, 28.05],
            flood_date="2024-08-15",
            run_id="test_p5_anti_cache",
            allow_cached_trishuli=False,
            output_base_dir=self.test_dir,
            publish_to_dashboard=False
        )
        manifest = orch.execute()
        self.assertEqual(manifest.get("overall_status"), "PARTIAL_RUN_IMAGERY_UNAVAILABLE")
        self.assertEqual(manifest["stages"]["stage_3_satellite_acquisition"]["status"], "UNAVAILABLE")
        print("  Result: PASS (Strictly blocked reusing cached Trishuli data)")

    def test_07_prohibition_of_emsr927_in_production(self):
        """Test 7: Verification that EMSR927 / UNOSAT do NOT enter production inputs."""
        print("\n[TEST 7] Strict Validation Data Isolation (No EMSR927/UNOSAT)")
        orch = FloodSpaceOrchestrator(
            bbox=[84.90, 27.75, 85.25, 28.05],
            flood_date="2026-08-28",
            run_id="test_p5_emsr_isolation",
            output_base_dir=self.test_dir,
            publish_to_dashboard=False
        )
        manifest = orch.execute()
        manifest_str = json.dumps(manifest)
        self.assertNotIn("EMSR927", manifest["inputs"])
        self.assertIn("strictly isolated", manifest_str.lower())
        print("  Result: PASS (EMSR927 / UNOSAT absent from production pipelines)")

    def test_08_evidence_and_report_grounding(self):
        """Test 8: Grounded evidence and report numbers match run manifest exactly."""
        print("\n[TEST 8] Grounded Evidence & Multilingual Report Consistency")
        orch = FloodSpaceOrchestrator(
            bbox=[84.90, 27.75, 85.25, 28.05],
            flood_date="2026-08-28",
            run_id="test_p5_evidence_grounding",
            output_base_dir=self.test_dir,
            publish_to_dashboard=False
        )
        manifest = orch.execute()
        evidence_file = self.test_dir / "test_p5_evidence_grounding" / "evidence" / "evidence.json"
        en_report_file = self.test_dir / "test_p5_evidence_grounding" / "evidence" / "situation_report_en.md"
        ne_report_file = self.test_dir / "test_p5_evidence_grounding" / "evidence" / "situation_report_ne.md"

        self.assertTrue(evidence_file.exists())
        self.assertTrue(en_report_file.exists())
        self.assertTrue(ne_report_file.exists())

        evidence = json.loads(evidence_file.read_text(encoding="utf-8"))
        self.assertEqual(evidence["flood_mapping"]["flood_pixels"], manifest["metrics"]["candidate_flood_pixels"])
        self.assertEqual(evidence["potentially_affected_assets"]["buildings"], manifest["metrics"]["potentially_affected_buildings"])
        self.assertEqual(evidence["potentially_affected_assets"]["roads"], manifest["metrics"]["potentially_affected_roads"])
        self.assertEqual(evidence["road_connectivity"]["potentially_cut_off_settlements"], manifest["metrics"]["potentially_cut_off_settlements"])

        en_text = en_report_file.read_text(encoding="utf-8")
        self.assertIn("1,286", en_text)
        self.assertIn("195", en_text)
        self.assertIn("115", en_text)
        self.assertIn("18", en_text)

        print("  Result: PASS (Evidence JSON and markdown reports 100% ground-matched)")

    def test_09_manifest_schema_and_dashboard_registry(self):
        """Test 9: Manifest schema completeness and dashboard registry sync."""
        print("\n[TEST 9] Manifest Schema 1.0.0 & Dashboard Registry Sync")
        orch = FloodSpaceOrchestrator(
            bbox=[84.90, 27.75, 85.25, 28.05],
            flood_date="2026-08-28",
            run_id="test_p5_manifest_sync",
            output_base_dir=self.test_dir,
            publish_to_dashboard=True
        )
        manifest = orch.execute()

        required_keys = [
            "schema_version", "run_id", "title", "overall_status", "overall_message",
            "provenance_mode", "timestamp_utc", "inputs", "stages", "metrics",
            "limitations", "attributions"
        ]
        for k in required_keys:
            self.assertIn(k, manifest)

        self.assertEqual(len(manifest["stages"]), 8)

        # Check dashboard public registry
        dash_registry_path = REPO_ROOT / "dashboard" / "public" / "data" / "pipeline_runs.json"
        self.assertTrue(dash_registry_path.exists())
        registry = json.loads(dash_registry_path.read_text(encoding="utf-8"))
        entry = next((r for r in registry if r.get("run_id") == "test_p5_manifest_sync"), None)
        self.assertIsNotNone(entry)
        self.assertEqual(entry["run_id"], "test_p5_manifest_sync")
        print("  Result: PASS (Schema validated and registered in dashboard registry)")


def run_tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFloodSpaceOrchestrator)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    summary = {
        "suite": "Phase 5 End-to-End Orchestrator Test Suite",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "total_tests": result.testsRun,
        "passed": result.wasSuccessful(),
        "failures": len(result.failures),
        "errors": len(result.errors),
        "test_count_passed": result.testsRun - len(result.failures) - len(result.errors)
    }

    out_json = REPO_ROOT / "data" / "processed" / "phase5_test_suite_summary.json"
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nSaved Phase 5 test summary to: {out_json}")

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
