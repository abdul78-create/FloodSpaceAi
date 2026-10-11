#!/usr/bin/env python3
"""
Quick utility to ensure existing runs (like narayani_2024_live) have their
evidence.json, situation_report_en.md, and situation_report_ne.md refreshed
with the new Phase 6 grounded_claims schema without re-downloading satellite imagery.
"""

import json
from pathlib import Path
import shutil
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from run_floodspace_pipeline import FloodSpaceOrchestrator

def refresh_run(run_id: str, bbox: list, flood_date: str, mode: str):
    print(f"Refreshing Phase 6 Grounded Claims for run: {run_id}")
    orch = FloodSpaceOrchestrator(
        bbox=bbox,
        flood_date=flood_date,
        run_id=run_id,
        publish_to_dashboard=True
    )
    orch.provenance_mode = mode
    
    # Load existing manifest if present to preserve metrics and stage messages
    manifest_file = orch.run_dir / "run_manifest.json"
    if not manifest_file.exists():
        manifest_file = REPO_ROOT / "dashboard" / "public" / "data" / "pipeline_runs" / run_id / "run_manifest.json"
    
    if manifest_file.exists():
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        orch.metrics = manifest.get("metrics", {})
        orch.stages = manifest.get("stages", {})
        orch.overall_status = manifest.get("overall_status", "PARTIAL_RUN_OPTICAL_UNCONFIRMED")
        orch.overall_message = manifest.get("overall_message", "")
        orch.limitations = manifest.get("limitations", [])

    # Run stage 7 and stage 8
    orch.run_stage_7_situation_evidence()
    orch.run_stage_8_publish_manifest()
    print(f"Successfully refreshed {run_id}")

if __name__ == "__main__":
    # Refresh Narayani live run
    refresh_run(
        run_id="narayani_2024_live",
        bbox=[84.30, 27.55, 84.50, 27.72],
        flood_date="2024-08-20",
        mode="LIVE_AUTHORITATIVE_SATELLITE_RETRIEVAL"
    )

    # Also update default dashboard evidence.json with trishuli benchmark evidence
    trishuli_ev = REPO_ROOT / "dashboard" / "public" / "data" / "pipeline_runs" / "trishuli_benchmark_verified" / "evidence.json"
    default_ev = REPO_ROOT / "dashboard" / "public" / "data" / "evidence.json"
    if trishuli_ev.exists():
        shutil.copy2(trishuli_ev, default_ev)
        print("Copied trishuli evidence to dashboard default evidence.json")
