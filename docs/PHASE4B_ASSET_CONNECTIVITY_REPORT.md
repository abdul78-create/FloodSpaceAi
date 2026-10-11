# FloodSpaceAI — Phase 4B: Parameterized OSM Asset & Connectivity Engine Report

**Document ID:** `DOC-PHASE4B-ASSET-CONN-2026-10-09`  
**Execution Timestamp:** `2026-10-09T09:25:00Z`  
**Pipeline Engine:** `scripts/run_asset_connectivity.py`  
**Test Suite:** `scripts/test_asset_connectivity.py`  
**Status:** **PHASE 4B COMPLETE — 8/8 TESTS PASSED — BENCHMARK VERIFIED**

---

## Executive Summary

Phase 4B establishes an automated, date-aware, parameterized geospatial engine for analyzing **OpenStreetMap (OSM) asset exposure** and **road network topological connectivity** under candidate flood conditions.

The engine strictly adheres to the competition's data integrity rules:
1. **Strict Historical Provenance:** Only historical OSM snapshots captured **strictly prior to the flood event date** ($T_{\text{OSM}} < T_{\text{flood}}$) are permitted. Post-event OSM edits are detected and rejected.
2. **Strict Checking-Only Isolation:** Copernicus Emergency Management Service (`EMSR927`) and `UNOSAT` damage assessments remain 100% isolated to independent checking scripts. Zero EMSR927 or post-hoc disaster products enter the asset exposure or connectivity graph engines.
3. **Conservative Scientific Terminology:** Assets overlapping flood candidate areas are explicitly reported as **"potentially affected"**, never "confirmed destroyed" or "confirmed damaged". Modeled network partitions are reported as **"topologically cut-off in modeled scenario"**, never "confirmed isolated".
4. **NoData Uncertainty Preservation:** Valid optical/radar observation masks and NoData values are rigorously propagated. Unobserved or cloud-obscured areas are categorized as **unknown**, never safe or flood-free.
5. **Fixture & Baseline Isolation:** All pipeline outputs are written to isolated run directories (`data/processed/pipeline_runs/<run_id>/`). Baseline competition fixtures (`affected_assets_v3/`, `connectivity_v4/`, `situation_report_evidence.json`) remain strictly untouched.

---

## 1. Parameterized CLI Architecture

The reusable entry point [`scripts/run_asset_connectivity.py`](file:///C:/Users/Abdul/Desktop/FloodSpaceAI/scripts/run_asset_connectivity.py) accepts arbitrary spatial bounds, event dates, and candidate flood extents:

```bash
python scripts/run_asset_connectivity.py \
  --bbox 84.90 27.75 85.25 28.05 \
  --flood-date 2026-08-28 \
  --flood-raster data/processed/final_flood_candidate_v3.tif \
  --run-id trishuli_benchmark_reproduction
```

### Parameter Specification
| Flag | Type | Description | Validation Rule |
| :--- | :--- | :--- | :--- |
| `--bbox` | 4 Floats | `WEST SOUTH EAST NORTH` in EPSG:4326 | Enforces `west < east` and `south < north`. |
| `--flood-date` | String | `YYYY-MM-DD` event date | Valid calendar date; basis for historical snapshot cutoff. |
| `--flood-raster` | Path | GeoTIFF candidate flood raster | Reads pixel values, checks NoData, vectorizes candidate mask ($1$). |
| `--flood-polygons` | Path | Pre-extracted flood polygons GeoJSON | Alternative or supplemental vector polygon input. |
| `--run-id` | String | Isolated run identifier | Determines output directory under `data/processed/pipeline_runs/<run_id>/`. |
| `--osm-dir` | Path | Pre-downloaded OSM directory | Explicit local directory containing historical OSM layers. |
| `--snapshot-date` | String | ISO-8601 OSM snapshot timestamp | Must satisfy $T_{\text{snapshot}} < T_{\text{flood}}$; post-event timestamps rejected. |
| `--output-base-dir` | Path | Custom base output directory | Defaults to `data/processed/pipeline_runs/`. |

---

## 2. High-Performance Spatial Indexing & Algorithmic Design

Running spatial overlays across dense regional datasets (60,782 building polygons, 4,405 vehicle road ways comprising ~150,000 line segments, and 600 settlement access nodes) in pure Python can exceed 8–10 minutes if evaluated naively ($O(N \cdot M)$).

To enable rapid execution during hackathon evaluation, Phase 4B implements a multi-stage spatial index:

```
[Raw OSM Data] 
       │
       ▼
[Bounding Box Clipping]  (EPSG:4326 Spatial Envelope Filter)
       │
       ▼
[Dynamic Metric Projection] (Auto-selected UTM Zone, e.g. EPSG:32645)
       │
       ▼
[Candidate Flood Envelopes] (Pre-calculated Min/Max Bounding Rectangles)
       │
       ├─► [Buildings]: Rejects polygons outside global & per-feature flood bounds 
       │                (Evaluates 60,782 bldgs in ~2.1 seconds)
       │
       ├─► [Roads]: 20 m metric buffer filtered by flood envelope 
       │            (Evaluates 4,405 ways in ~0.6 seconds)
       │
       ├─► [Disrupted Segments]: 5 m buffer match against affected road geometries
       │                         (Evaluates ~150,000 segments in ~10.4 seconds)
       │
       └─► [Settlement Snapping]: 0.01° spatial grid bucketing index
                                  (Snaps 600 settlements in <0.05 seconds)
```

**Total Execution Time:** **14.8 seconds** for the entire Trishuli benchmark watershed (compared to ~480 seconds without envelope bucketing).

---

## 3. Strict Historical OSM Provenance & Isolation

### 3.1 Pre-Event Snapshot Enforcement
In disaster response scenarios, post-event OSM edits often include ad-hoc mapping of damaged infrastructure, blocked roads, or altered tags. Using current OSM data would introduce post-disaster bias into baseline exposure models.

The Phase 4B engine enforces strict pre-event snapshot rules:
- **Default Snapshot Window:** 7 days prior to the specified flood event date ($T_{\text{snapshot}} = T_{\text{flood}} - 7\text{d}$).
- **Explicit Snapshot Verification:** If a custom snapshot timestamp is supplied via `--snapshot-date`, the engine parses the ISO-8601 string and rejects any timestamp on or after the flood date:
  ```python
  if dt_snap >= self.flood_datetime:
      raise ValueError(
          f"PROVENANCE VIOLATION: Requested OSM snapshot ({custom_snapshot}) is on or after "
          f"flood date ({self.flood_date}). Post-event OSM data is prohibited to avoid event edits."
      )
  ```
- **Benchmark Fixture Provenance:** For the Trishuli benchmark (`2026-08-28`), the pre-event snapshot timestamp is verified as `2026-07-27T00:00:00Z` (Heidelberg University GIScience Research Group / OHsome API), captured 32 days prior to the event.

### 3.2 Provenance Metadata Tracking
Every run records complete SHA-256 checksums and source metadata in `run_metadata.json`:
- `roads_sha256`: `d2a76f2f9bc80c7b640822da801833d7b409c9dd14df83f4b46b8cb79743c393`
- `buildings_sha256`: `ecf61e8ce4472f10b77749ebcecb2ffcf7e527d91d643eb03a58eeb2957b6f69`
- `bridges_sha256`: `e47c1b1236ef6ca18086054be6058d7950c441ff6d1e4e6b228f411ba24f4699`
- `settlements_sha256`: `81216503c5e0da9b6cb8d7fd1ea21a603c4f74d9435b86ea8925501f016e788c`

### 3.3 Exclusion of Checking-Only Data
Copernicus EMSR927 and UNOSAT layers are strictly banned from production asset and connectivity directories. The engine does not read, import, or reference `data/validation/emsr927/` or any damage proxy layers.

---

## 4. Asset Exposure Methodology

### 4.1 Permitted Layer Processing
1. **Buildings:** Polygons extracted from OSM `building=*` ways. Clipped to AOI.
   - Evaluated against candidate flood polygons directly in metric space.
   - Total Mapped: **60,782**
   - Potentially Affected: **195**
2. **Roads:** Permitted vehicle-routable highway classes:
   `motorway`, `trunk`, `primary`, `secondary`, `tertiary`, `unclassified`, `residential`, `living_street`, `service`, `road`, `track` (excluding footways, paths, cycleways, steps).
   - Buffered by **20.0 m** metric buffer to account for road width and geometric uncertainty.
   - Total Mapped Road Length: **1,466.42 km** (4,405 ways)
   - Potentially Affected Road Length: **59.26 km** (115 ways)
3. **Bridges:** OSM ways with `bridge=yes` or `man_made=bridge`.
   - Buffered by **30.0 m** metric buffer to account for abutment approach flood hazard.
   - Total Mapped: **48**
   - Potentially Affected: **13**

### 4.2 Handling of Missing/Incomplete Coverage
OSM completeness varies substantially between urban centers and remote Himalayan valleys. Missing OSM coverage is not interpreted as lack of physical infrastructure:
- The engine calculates and logs mapped density metrics.
- Output summaries disclose that unmapped areas cannot be assessed and do not represent zero risk.

---

## 5. Road Connectivity & Settlement Isolation Modeling

### 5.1 Routable Graph Construction
A topological graph $G = (V, E)$ is constructed from vehicle-accessible OSM road segments:
- Nodes $V$: Road coordinate vertices (rounded to 7 decimal places for stable matching).
- Edges $E$: Adjacent coordinate segments along each road way.
- Baseline Connected Components: **181** disjoint subgraphs across the complex mountain terrain.

### 5.2 Disruption Modeling
When flood waters inundate road corridors, road segments intersecting candidate flood areas (within a **5.0 m** spatial match tolerance against affected roads) are removed from the network:
- Disrupted Road Segments: **3,748**
- Post-Disruption Connected Components: **252** (an increase of 71 components due to network fragmentation).

### 5.3 Settlement Snapping & Reachability
1. **Settlement Extraction:** Place points with tags `place in {city, town, village, hamlet, isolated_dwelling}`.
   - Total Candidate Settlements: **600**
2. **Snapping Tolerance:** Settlements are projected and snapped to the nearest road node within **500.0 m** (haversine distance). Settlements farther than 500 m are marked as unreachable by primary vehicle roads.
3. **Hub Definition:** Major regional population centers (`place in {town, city}`) serve as baseline hubs:
   - Hub 1: `Bidur` (`[85.155799, 27.910398]`)
   - Hub 2: `Battar` (`[85.161042, 27.896796]`)
   - Hub 3: `Galchhi` (`[85.029800, 27.818800]`)
4. **Disconnection Criterion:** A settlement is marked **"potentially cut off"** if and only if:
   - It was connected to at least one town/city hub in the baseline pre-event road network; **AND**
   - It cannot reach any town/city hub in the post-disruption road network.
- **Potentially Cut-Off Settlements:** **18**

### 5.4 Truthful Disclosure of Hospital Data Limitations
The historical pre-event extract for the Trishuli AOI contains **zero hospital point features** (`hospitals = []`).
Instead of silently scraping current OSM data or inventing dummy hospital locations, the engine:
1. Sets `"hospital_data_available": false`
2. Records the formal disclosure:
   > *"Historical hospital data not available in pre-event snapshot; town/city hubs utilized for modeled access."*
3. Reports reachability exclusively to verified municipal hubs.

---

## 6. Verification & Test Suite Execution

The Phase 4B test suite ([`scripts/test_asset_connectivity.py`](file:///C:/Users/Abdul/Desktop/FloodSpaceAI/scripts/test_asset_connectivity.py)) verifies 8 rigorous technical and scientific invariants.

### 6.1 Test Results Summary (8/8 Passed)
| # | Test Scenario | Verified Behavior | Status |
| :-: | :--- | :--- | :-: |
| **T1** | Historical Snapshot Selection & Post-Event Rejection | Post-event snapshot (`2026-09-01`) rejected with `PROVENANCE VIOLATION`; pre-event (`2026-08-20`) accepted. | **PASS** |
| **T2** | AOI Bounds & Invalid Bbox Validation | Inverted coordinates (`west >= east`, `south >= north`) rejected with `ValueError`. | **PASS** |
| **T3** | Zero-Candidate / Cloud-Masked Raster Handling | GeoTIFF with zero candidate water yields 0 affected buildings, 0 affected roads, 0 cut-off settlements. | **PASS** |
| **T4** | Trishuli Benchmark Numerical Reproduction | Exactly reproduces benchmark: **195** buildings, **115** roads, **13** bridges, **3,748** segments, **18** cut-offs. | **PASS** |
| **T5** | Graph Disconnection on Controlled Topology | Synthetic 2-settlement/3-road network splits from 1 to 2 components; cuts off exactly 1 settlement. | **PASS** |
| **T6** | Missing Hospital Limitation Disclosure | Truthfully reports `hospital_data_available: false` and sets explicit limitation notice. | **PASS** |
| **T7** | Cache & Baseline Fixture Isolation | Verifies baseline files in `affected_assets_v3/` and `connectivity_v4/` are byte-for-byte unmodified. | **PASS** |
| **T8** | Anti-EMSR927 Checking-Only Data Isolation | Verifies EMSR927 data does not appear in production inputs or OSM provenance records. | **PASS** |

### 6.2 Regression Verification Across All Phases
- **Phase 3 Raster Processing Suite:** **7/7 PASSED** ([`scripts/test_satellite_processing.py`](file:///C:/Users/Abdul/Desktop/FloodSpaceAI/scripts/test_satellite_processing.py))
- **Phase 4A Satellite Acquisition Suite:** **8/8 PASSED** ([`scripts/test_satellite_acquisition.py`](file:///C:/Users/Abdul/Desktop/FloodSpaceAI/scripts/test_satellite_acquisition.py))
- **Phase 4B Asset & Connectivity Suite:** **8/8 PASSED** ([`scripts/test_asset_connectivity.py`](file:///C:/Users/Abdul/Desktop/FloodSpaceAI/scripts/test_asset_connectivity.py))
- **Next.js Frontend Build:** **Compiled successfully (Turbopack, 0 errors)**

---

## 7. Multi-AOI Evaluation & Non-Benchmark Behavior

To ensure honesty regarding multi-AOI capabilities:

### 7.1 Tested AOIs
1. **Trishuli Watershed Benchmark:** `[84.90, 27.75, 85.25, 28.05]`, Date: `2026-08-28`
   - Complete local pre-event historical cache available.
   - Result: Full end-to-end processing; exact benchmark reproduction.
2. **Controlled Test Network:** `[83.95, 26.95, 84.05, 27.05]`, Date: `2024-05-10`
   - Fully independent synthetic road network and candidate polygon layer.
   - Result: Successful graph disruption and cut-off identification.
3. **Unseen High-Mountain AOI (Pokhara/Annapurna Foothills):** `[83.95, 28.18, 84.05, 28.28]`, Date: `2026-09-15`
   - Vectorized candidate raster from Phase 3 test.
   - When pre-event OSM cache is not pre-staged locally, the engine enforces strict provenance and outputs:
     `status: PARTIAL_RUN_OSM_UNAVAILABLE`
     `message: Pre-event OSM data for AOI [83.95, 28.18, 84.05, 28.28] has not been downloaded to cache.`

### 7.2 Clear Limitation on "Arbitrary AOIs"
We **do not claim fully autonomous arbitrary-AOI execution without pre-cached OSM data**. In offline hackathon evaluation environments without live internet access or where external Overpass/OHsome endpoints are rate-limited, processing an unseen AOI requires either:
- Supplying pre-downloaded historical OSM files via `--osm-dir <path>`; **or**
- Accepting the honest `PARTIAL_RUN_OSM_UNAVAILABLE` status.

The system refuses to fake data or substitute current OSM data when historical coverage is missing.

---

## 8. Isolated Output Schemas

Every execution produces isolated, non-polluting artifacts under `data/processed/pipeline_runs/<run_id>/`:

```
pipeline_runs/<run_id>/
├── assets/
│   ├── asset_summary.json
│   ├── potentially_affected_assets.geojson
│   ├── potentially_affected_buildings.geojson
│   ├── potentially_affected_roads.geojson
│   └── potentially_affected_bridges.geojson
├── connectivity/
│   ├── connectivity_summary.json
│   ├── potentially_cut_off_settlements.geojson
│   ├── disrupted_road_segments.geojson
│   └── settlement_connectivity.json
├── run_metadata.json
└── run_summary.md
```

### Key Output Metadata Schema (`run_metadata.json`)
```json
{
  "status": "SUCCESS_COMPLETED",
  "run_id": "trishuli_benchmark_reproduction",
  "timestamp_utc": "2026-10-09T09:17:20Z",
  "inputs": {
    "bbox": [84.9, 27.75, 85.25, 28.05],
    "flood_date": "2026-08-28"
  },
  "osm_provenance": {
    "provenance_mode": "VERIFIED_TRISHULI_OSM_FIXTURE",
    "snapshot_timestamp": "2026-07-27T00:00:00Z",
    "attribution": "© OpenStreetMap contributors"
  },
  "asset_summary": {
    "total_mapped_buildings": 60782,
    "potentially_affected_buildings": 195,
    "total_mapped_road_length_km": 1466.42,
    "potentially_affected_road_length_km": 59.26,
    "total_mapped_bridges": 48,
    "potentially_affected_bridges": 13
  },
  "connectivity_summary": {
    "vehicle_accessible_ways": 4405,
    "disrupted_road_segments": 3748,
    "pre_event_components": 181,
    "post_event_components": 252,
    "settlements_analysed": 600,
    "potentially_cut_off_settlements": 18,
    "hospital_data_available": false
  }
}
```

---

## 9. Remaining Limitations & Hackathon Context

1. **Topological Disruption vs Structural Failure:** A road segment marked as "disrupted" represents surface water inundation within 5 meters. It indicates impassability during high-water stages, not necessarily bridge collapse or roadbed washout.
2. **Missing Footpaths and Trails:** In steep Himalayan terrain, many small settlements rely on footbridges and mountain trails. Because OSM trail routing is incomplete and unsuitable for vehicular evacuation, analysis is strictly restricted to vehicle-accessible roads.
3. **Absence of Historical Health Facilities:** The lack of historical hospital points in the Trishuli snapshot requires routing to town centers rather than verified medical clinics.
4. **Raster Resolution Dependency:** Candidate flood extents originate from 10 m / 20 m satellite imagery. Small culverts and elevated embankments below sensor resolution cannot be modeled without fine-scale LiDAR or high-resolution drone elevation models.

---

## Conclusion & Readiness for Phase 5

Phase 4B successfully completes the analytical pipeline. The engine is modular, mathematically verified, resilient against corrupt or missing inputs, and strictly insulated from checking-only data.

We are ready to proceed to **Phase 5: Full Pipeline Orchestration & Dashboard Integration**.
