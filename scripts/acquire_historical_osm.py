#!/usr/bin/env python3
"""
FloodSpaceAI — Historical OpenStreetMap Acquisition Adapter (Phase 5.1)

Retrieves verified pre-event OpenStreetMap infrastructure snapshots using
the Overpass Historical API ([date:"..."]) with multi-mirror resilience.

Scientific & Integrity Safeguards:
1. Strict Temporal Precedence: Snapshot timestamp must be strictly earlier than flood date (T_osm < T_flood).
2. Anti-Pollution Policy: Never fall back to current OSM or post-event edits; never label current data as historical.
3. Multi-Mirror Resilience: Retries across multiple public Overpass endpoints with bounded backoff.
4. Cryptographic Provenance: Records snapshot timestamp, actual retrieval time, mirror used, query bounding box,
   element counts, and SHA-256 hashes.
5. Graceful Failure: If historical OSM is unreachable, reports UNAVAILABLE_HISTORICAL_OSM with an actionable reason.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent

# Public Overpass API mirrors with historical attics support
OVERPASS_MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter"
]

USER_AGENT = "FloodSpaceAI-Research/1.0 (Multimodal AI Hackathon 2026; contact: research@floodspace.ai)"


def compute_sha256(file_path: Path) -> str:
    """Computes SHA-256 hash of a file."""
    if not file_path.exists():
        return ""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class HistoricalOSMAcquisitionAdapter:
    """Adapter for acquiring genuine pre-event OpenStreetMap snapshots."""

    def __init__(self, timeout: int = 40, max_retries_per_mirror: int = 2):
        self.timeout = timeout
        self.max_retries = max_retries_per_mirror

    def determine_snapshot_date(self, flood_date: str, custom_snapshot: Optional[str] = None) -> str:
        """
        Determine and validate pre-event snapshot timestamp.
        Enforces strict precedence: T_snapshot < T_flood.
        """
        flood_dt = datetime.strptime(flood_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)

        if custom_snapshot:
            clean_ts = custom_snapshot.replace("Z", "+00:00")
            if "T" in clean_ts:
                snap_dt = datetime.fromisoformat(clean_ts)
            else:
                snap_dt = datetime.strptime(clean_ts, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            if snap_dt >= flood_dt:
                raise ValueError(
                    f"PROVENANCE VIOLATION: Requested snapshot timestamp ({custom_snapshot}) is on or after "
                    f"flood date ({flood_date}). Post-event OSM data is prohibited to avoid event edits."
                )
            return snap_dt.strftime("%Y-%m-%dT00:00:00Z")

        # Default to 7 days prior to flood event
        snap_dt = flood_dt - timedelta(days=7)
        return snap_dt.strftime("%Y-%m-%dT00:00:00Z")

    def _execute_overpass_query(self, query: str) -> Tuple[Optional[Dict[str, Any]], str, Optional[str]]:
        """
        Executes Overpass query with mirror rotation and bounded retries.
        """
        headers = {"User-Agent": USER_AGENT}
        last_error = ""

        for mirror in OVERPASS_MIRRORS:
            for attempt in range(1, self.max_retries + 1):
                try:
                    resp = requests.post(
                        mirror,
                        data={"data": query},
                        headers=headers,
                        timeout=self.timeout
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        if "elements" in data:
                            return data, mirror, None
                        else:
                            last_error = f"Missing elements in response from {mirror}"
                    elif resp.status_code in [429, 504]:
                        # Provider rate limit or timeout: backoff
                        time.sleep(1.5 * attempt)
                        last_error = f"HTTP {resp.status_code} from {mirror}"
                    else:
                        last_error = f"HTTP {resp.status_code} from {mirror}: {resp.text[:200]}"
                except requests.exceptions.Timeout:
                    last_error = f"Timeout ({self.timeout}s) from {mirror}"
                except Exception as e:
                    last_error = f"Error from {mirror}: {e}"

                time.sleep(1.0)

        return None, "", last_error

    def acquire_historical_osm(
        self,
        bbox: List[float],
        flood_date: str,
        out_dir: Path,
        custom_snapshot: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Acquire pre-event roads, buildings, bridges, and settlements for AOI bounding box.
        Bbox order: [west, south, east, north].
        """
        out_dir.mkdir(parents=True, exist_ok=True)
        west, south, east, north = bbox

        # 1. Validate snapshot date
        try:
            snapshot_iso = self.determine_snapshot_date(flood_date, custom_snapshot)
        except Exception as e:
            return {
                "status": "FAILED_INVALID_SNAPSHOT_DATE",
                "error": str(e)
            }

        retrieval_start = datetime.now(timezone.utc).isoformat()

        # 2. Build targeted Overpass query for infrastructure
        # Overpass bbox format: south, west, north, east
        op_bbox = f"{south:.4f},{west:.4f},{north:.4f},{east:.4f}"

        # We execute a structured query retrieving ways with geometries
        infra_query = f"""[out:json][timeout:{self.timeout}][date:"{snapshot_iso}"];
(
  way["highway"~"motorway|trunk|primary|secondary|tertiary|unclassified|residential|living_street|service|road|track"]({op_bbox});
  way["building"]({op_bbox});
  way["bridge"]({op_bbox});
  node["place"~"city|town|village|hamlet"]({op_bbox});
  node["amenity"="hospital"]({op_bbox});
  way["amenity"="hospital"]({op_bbox});
);
out tags geom;
"""

        data, mirror_used, err = self._execute_overpass_query(infra_query)

        if not data:
            return {
                "status": "UNAVAILABLE_HISTORICAL_OSM",
                "requested_snapshot": snapshot_iso,
                "error": f"Overpass historical API query failed across all mirrors: {err}",
                "message": (
                    f"Could not retrieve historical OSM snapshot for {snapshot_iso} over bbox {bbox}. "
                    f"Preserving UNAVAILABLE status without substituting current OSM."
                )
            }

        elements = data.get("elements", [])
        if not elements:
            return {
                "status": "UNAVAILABLE_HISTORICAL_OSM",
                "requested_snapshot": snapshot_iso,
                "error": "Overpass returned zero infrastructure elements for target bounding box.",
                "message": f"Zero historical OSM elements found for {snapshot_iso} in AOI."
            }

        # 3. Categorize elements into separate datasets
        roads = []
        buildings = []
        bridges = []
        settlements = []
        hospitals = []

        for el in elements:
            tags = el.get("tags", {})
            if "highway" in tags:
                roads.append(el)
            if "building" in tags:
                buildings.append(el)
            if "bridge" in tags:
                bridges.append(el)
            if tags.get("place") in ["city", "town", "village", "hamlet"]:
                settlements.append(el)
            if tags.get("amenity") == "hospital":
                hospitals.append(el)

        # 4. Save discrete json files
        roads_file = out_dir / "roads.json"
        buildings_file = out_dir / "buildings.json"
        bridges_file = out_dir / "bridges.json"
        settlements_file = out_dir / "settlements.json"
        hospitals_file = out_dir / "hospitals.json"

        roads_file.write_text(json.dumps({"elements": roads}, indent=2), encoding="utf-8")
        buildings_file.write_text(json.dumps({"elements": buildings}, indent=2), encoding="utf-8")
        bridges_file.write_text(json.dumps({"elements": bridges}, indent=2), encoding="utf-8")
        settlements_file.write_text(json.dumps({"elements": settlements}, indent=2), encoding="utf-8")
        hospitals_file.write_text(json.dumps({"elements": hospitals}, indent=2), encoding="utf-8")

        # 5. Build provenance summary
        checksums = {
            "roads": compute_sha256(roads_file),
            "buildings": compute_sha256(buildings_file),
            "bridges": compute_sha256(bridges_file),
            "settlements": compute_sha256(settlements_file),
            "hospitals": compute_sha256(hospitals_file)
        }

        provenance = {
            "status": "SUCCESS_DOWNLOADED",
            "provider": "Overpass Historical API ([date])",
            "mirror_endpoint": mirror_used,
            "requested_snapshot_utc": snapshot_iso,
            "retrieval_timestamp_utc": retrieval_start,
            "bbox_wsen": bbox,
            "query_bounding_box": op_bbox,
            "counts": {
                "total_elements": len(elements),
                "roads": len(roads),
                "buildings": len(buildings),
                "bridges": len(bridges),
                "settlements": len(settlements),
                "hospitals": len(hospitals)
            },
            "files": {
                "roads": str(roads_file),
                "buildings": str(buildings_file),
                "bridges": str(bridges_file),
                "settlements": str(settlements_file),
                "hospitals": str(hospitals_file)
            },
            "checksums": checksums,
            "attribution": "© OpenStreetMap contributors, ODbL 1.0",
            "scientific_notice": (
                f"Historical snapshot strictly precedes flood date {flood_date} (T_osm={snapshot_iso} < T_flood={flood_date}). "
                "Post-event edits and disaster-response tags are strictly excluded."
            )
        }

        prov_file = out_dir / "osm_provenance.json"
        prov_file.write_text(json.dumps(provenance, indent=2), encoding="utf-8")

        return provenance


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Acquire historical pre-event OpenStreetMap snapshot.")
    parser.add_argument("--bbox", nargs=4, type=float, required=True, help="Bounding box [west, south, east, north]")
    parser.add_argument("--flood-date", type=str, required=True, help="Flood event date (YYYY-MM-DD)")
    parser.add_argument("--snapshot-date", type=str, default=None, help="Custom snapshot date (YYYY-MM-DD or ISO)")
    parser.add_argument("--out-dir", type=str, default="data/raw/osm_live", help="Output directory")
    args = parser.parse_args()

    adapter = HistoricalOSMAcquisitionAdapter()
    res = adapter.acquire_historical_osm(args.bbox, args.flood_date, Path(args.out_dir), args.snapshot_date)
    print(json.dumps(res, indent=2))
