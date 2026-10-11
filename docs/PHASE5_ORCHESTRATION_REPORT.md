# FloodSpaceAI — Phase 5: End-to-End Orchestration & Dashboard Integration Report

**Date:** October 9, 2026  
**Track:** Multimodal AI Hackathon 2026 — Track B: Mapping Flood Damage from Space  
**Status:** **PHASE 5 COMPLETE & VERIFIED**  
**Run Manifest Schema:** Version 1.0.0  

---

## 1. Executive Summary

Phase 5 delivers the complete end-to-end orchestration and dashboard integration layer for FloodSpaceAI. It coordinates:
1. Parameterized satellite catalog discovery (Sentinel-1 SAR orbit pairing and Sentinel-2 optical scene discovery).
2. Live and cached satellite raster acquisition with cryptographic SHA-256 provenance verification.
3. Aligned SAR backscatter difference and optical NDWI change detection with cloud-masking and valid-pixel tracking.
4. Historical OpenStreetMap baseline ingestion with strict pre-event temporal validation ($T_{\text{OSM}} < T_{\text{flood}}$).
5. Geospatial asset exposure and road network graph connectivity modeling.
6. Run-level multilingual situation reporting strictly grounded to verified evidence.
7. Machine-readable versioned run-manifest publishing (`run_manifest.json`).
8. Interactive dashboard integration with dynamic run selection, provenance mode indicators, 8-stage execution tracing, and honest uncertainty disclosures.

```
                              [USER / CLI REQUEST]
                       --bbox W S E N  --flood-date YYYY-MM-DD
                                        │
                                        ▼
             ┌─────────────────────────────────────────────────────────┐
             │         Stage 1: AOI & Calendar Date Validation         │
             └──────────────────────────┬──────────────────────────────┘
                                        │
                                        ▼
             ┌─────────────────────────────────────────────────────────┐
             │    Stage 2: Sentinel-1 & Sentinel-2 Discovery (STAC)    │
             └──────────────────────────┬──────────────────────────────┘
                                        │
                                        ▼
             ┌─────────────────────────────────────────────────────────┐
             │       Stage 3: Satellite Data Acquisition & Verification │
             └──────────────────────────┬──────────────────────────────┘
                                        │
                                        ▼
             ┌─────────────────────────────────────────────────────────┐
             │     Stage 4: Aligned SAR/Optical Raster Processing      │
             └──────────────────────────┬──────────────────────────────┘
                                        │
                                        ▼
             ┌─────────────────────────────────────────────────────────┐
             │    Stage 5: Historical OSM Snapshot Ingestion (Pre-Event)│
             └──────────────────────────┬──────────────────────────────┘
                                        │
                                        ▼
             ┌─────────────────────────────────────────────────────────┐
             │   Stage 6: Asset Exposure & Road Connectivity Modeling  │
             └──────────────────────────┬──────────────────────────────┘
                                        │
                                        ▼
             ┌─────────────────────────────────────────────────────────┐
             │   Stage 7: Grounded Situation Reports (English/Nepali)  │
             └──────────────────────────┬──────────────────────────────┘
                                        │
                                        ▼
             ┌─────────────────────────────────────────────────────────┐
             │ Stage 8: Run Manifest Publishing & Dashboard Registry   │
             └──────────────────────────┬──────────────────────────────┘
                                        │
                                        ▼
                         [NEXT.JS INTERACTIVE DASHBOARD]
               Run Selector · Status Badges · 8-Stage Execution Trace
```

---

## 2. Key Deliverables Produced

| Deliverable | Path | Description |
|---|---|---|
| **Single Orchestrator CLI** | [`scripts/run_floodspace_pipeline.py`](file:///c:/Users/Abdul/Desktop/FloodSpaceAI/scripts/run_floodspace_pipeline.py) | Full 8-stage coordinator supporting `--bbox`, `--flood-date`, `--run-id`, explicit rasters, and OSM snapshot controls |
| **Run-Manifest Schema** | Schema `1.0.0` | Standardized, versioned JSON metadata structure recording stage timings, provenance, metrics, warnings, limitations, and attributions |
| **Phase 5 Test Suite** | [`scripts/test_orchestrator.py`](file:///c:/Users/Abdul/Desktop/FloodSpaceAI/scripts/test_orchestrator.py) | 9 automated tests verifying benchmark reproduction, failure modes, cache isolation, anti-EMSR927 protection, and registry sync |
| **Machine-Readable Results** | [`data/processed/phase5_test_suite_summary.json`](file:///c:/Users/Abdul/Desktop/FloodSpaceAI/data/processed/phase5_test_suite_summary.json) | Complete JSON test execution summary (9/9 passed) |
| **Global Run Context** | [`dashboard/src/data/RunContext.tsx`](file:///c:/Users/Abdul/Desktop/FloodSpaceAI/dashboard/src/data/RunContext.tsx) | React Context managing active run selection, manifest hydration, and evidence binding |
| **Interactive Run Selector** | [`dashboard/src/components/common/Header.tsx`](file:///c:/Users/Abdul/Desktop/FloodSpaceAI/dashboard/src/components/common/Header.tsx) | Header dropdown switching runs with live status pills, provenance badges, and dynamic AOI bounds |
| **8-Stage Execution Trace** | [`dashboard/src/components/pipeline/PipelineDiagram.tsx`](file:///c:/Users/Abdul/Desktop/FloodSpaceAI/dashboard/src/components/pipeline/PipelineDiagram.tsx) | Live inspection board rendering stage statuses, durations, and details for the selected run |
| **Manifest Viewer & Grounding** | [`dashboard/src/components/copilot/SituationReportCopilot.tsx`](file:///c:/Users/Abdul/Desktop/FloodSpaceAI/dashboard/src/components/copilot/SituationReportCopilot.tsx) | Dual-view panel toggling between official situation reports and raw verified `run_manifest.json` |
| **Safeguard Disclosures** | `AssetAnalysis.tsx`, `ConnectivityAnalysis.tsx`, `MapHero.tsx`, `ProvenanceModal.tsx` | Honest alerts explaining when and why stages were halted on unavailable inputs |

---

## 3. Explicit Stage Statuses & Provenance Modes

Every pipeline execution records structured statuses across all 8 stages:

| Status Code | Meaning | Example Scenario |
|---|---|---|
| `SUCCESS` | Stage completed with all expected analytical outputs verified. | Valid input bounds; S1 orbit match; successful graph disconnection. |
| `PARTIAL` | Stage completed with known scientific limitations that are honestly disclosed. | SAR analysis successful but optical confirmation cloud-limited; S2 scene has 75.9% cloud cover. |
| `UNAVAILABLE` | Required input data could not be acquired or is not present in live/cached catalogs. | Unseen AOI where live multiband rasters have not been fetched; future date requested. |
| `FAILED` | Input validation failed or an unrecoverable processing exception occurred. | Inverted bounding box coordinates ($W > E$); post-event OSM snapshot supplied. |
| `SKIPPED` | Stage was intentionally bypassed because preceding dependencies were unavailable. | Asset and connectivity modeling skipped when candidate flood raster was not generated. |

### Provenance Modes
- `VERIFIED_TRISHULI_BENCHMARK_CACHE`: Pre-verified calibration run utilizing benchmark satellite rasters and historical OSM snapshots.
- `LIVE_AUTHORITATIVE_API`: Authenticated retrieval from live catalog endpoints (Element84 AWS Open Data / CDSE STAC).
- `EXPLICIT_USER_SUPPLIED_INPUTS`: User provided explicit local GeoTIFF / GeoJSON overrides.
- `UNKNOWN`: Unseen AOI where live catalog discovery found candidate metadata but raw pixel ingestion has not yet been performed.

---

## 4. Scientific and Provenance Safeguards Enforced

FloodSpaceAI implements strict safeguards designed to maintain institutional credibility:

1. **Anti-Pollution & Stale Cache Prevention:**
   The orchestrator strictly prevents reusing cached Trishuli rasters or geometries for an unseen AOI or alternative flood date. If genuine imagery is unavailable for a requested query, the run halts honestly with `PARTIAL_RUN_IMAGERY_UNAVAILABLE`.
2. **Strict Validation Layer Isolation:**
   Copernicus Emergency Management Service (EMSR927) and UNOSAT products are classified strictly as post-hoc checking references. They are never ingested as inputs into the V3 flood candidate pipeline, asset overlay, or connectivity graph.
3. **Temporal OpenStreetMap Baseline Integrity:**
   The historical OSM ingestion stage mandates that the infrastructure snapshot date strictly precedes the flood event ($T_{\text{OSM}} < T_{\text{flood}}$). Attempting to pass a post-event snapshot immediately triggers a pipeline rejection (`FAILED`).
4. **Cloud and NoData Integrity:**
   NoData and cloud-masked pixels are never treated as confirmed dry ground or confirmed water. The pipeline computes valid pixel percentages and discloses when optical confirmation is inconclusive, falling back explicitly to SAR-only evidence.
5. **Conservative Impact Terminology:**
   All outputs and dashboard displays use precise, defensible language:
   - "Potentially affected buildings/roads/bridges" (never "confirmed destroyed").
   - "Modelled potential road disconnection" (never "confirmed real-world physical isolation").
6. **Mandatory Legal Attributions:**
   The run manifest and dashboard enforce exact attributions:
   - *Copernicus Sentinel:* Contains modified Copernicus Sentinel data (2024/2026), processed under ESA Copernicus Open Access.
   - *Copernicus DEM:* Produced using Copernicus WorldDEM-30 © DLR e.V. 2010–2014 and © Airbus Defence and Space GmbH 2014–2018.
   - *OpenStreetMap:* © OpenStreetMap contributors, ODbL 1.0 license.

---

## 5. End-to-End Orchestrator Execution Results

### Run 1: Verified Trishuli Benchmark (`trishuli_benchmark_verified`)
Executed via:
```bash
python scripts/run_floodspace_pipeline.py \
  --bbox 84.90 27.75 85.25 28.05 \
  --flood-date 2026-08-28 \
  --run-id trishuli_benchmark_verified \
  --publish-to-dashboard
```

**Results:**
- **Overall Status:** `PARTIAL_RUN_OPTICAL_UNCONFIRMED`
- **Overall Message:** SAR analysis completed; optical verification limited by cloud cover.
- **Provenance Mode:** `VERIFIED_TRISHULI_BENCHMARK_CACHE`
- **Stage 1 (Input Validation):** `SUCCESS` (Valid AOI `[84.9, 27.75, 85.25, 28.05]`, Date `2026-08-28`)
- **Stage 2 (Satellite Discovery):** `PARTIAL` (S1 Orbit 85 matched, 12-day baseline; S2 post-event scene 75.9% cloud-covered)
- **Stage 3 (Satellite Acquisition):** `SUCCESS` (Pre/Post S1 and S2 inputs verified)
- **Stage 4 (Raster Processing):** `SUCCESS` (1,286 V3 candidate pixels across 27 clusters; 35.03 ha extent)
- **Stage 5 (Historical OSM):** `SUCCESS` (Snapshot `2026-07-27T00:00:00Z`; 132,765 buildings, 4,405 roads, 187 bridges mapped)
- **Stage 6 (Asset & Connectivity):** `SUCCESS`
  - Potentially affected buildings: **195**
  - Potentially affected roads: **115** (59.26 km)
  - Potentially affected bridges: **13**
  - Disrupted road segments: **3,748**
  - Pre-event connected components: **181**
  - Post-event connected components: **252** (+71 partitions)
  - Settlements analysed: **589**
  - Potentially cut-off settlements: **18**
  - Hospital data availability: `false` (Town/city hubs Bidur, Galchhi, Belkotgadhi utilized)
- **Stage 7 (Situation Evidence):** `SUCCESS` (Grounded English and Nepali situation reports generated)
- **Stage 8 (Manifest Publishing):** `SUCCESS` (Published to `dashboard/public/data/pipeline_runs/trishuli_benchmark_verified/run_manifest.json` and registered in `pipeline_runs.json`)

---

### Run 2: Unseen AOI Demonstration (`unseen_aoi_pokhara`)
Executed via:
```bash
python scripts/run_floodspace_pipeline.py \
  --bbox 83.95 28.18 84.05 28.28 \
  --flood-date 2026-09-15 \
  --run-id unseen_aoi_pokhara \
  --publish-to-dashboard
```

**Results:**
- **Overall Status:** `PARTIAL_RUN_IMAGERY_UNAVAILABLE`
- **Overall Message:** Satellite imagery not yet acquired/cached for requested AOI/date.
- **Provenance Mode:** `UNKNOWN`
- **Stage 1 (Input Validation):** `SUCCESS` (Valid AOI `[83.95, 28.18, 84.05, 28.28]`, Date `2026-09-15`)
- **Stage 2 (Satellite Discovery):** `SUCCESS` (Discovered S1 Orbit 19 pair and S2 optical scenes)
- **Stage 3 (Satellite Acquisition):** `UNAVAILABLE` (Raw multiband satellite rasters not yet ingested for this AOI/date)
- **Stage 4 (Raster Processing):** `UNAVAILABLE` (Strict provenance isolation halts processing; cached Trishuli rasters not reused)
- **Stage 5 (Historical OSM):** `SKIPPED` (Bypassed because flood raster was not generated)
- **Stage 6 (Asset & Connectivity):** `SKIPPED` (Bypassed to prevent fabricating ungrounded statistics)
- **Stage 7 (Situation Evidence):** `SUCCESS` (Generated truthful report acknowledging that imagery acquisition is pending)
- **Stage 8 (Manifest Publishing):** `SUCCESS` (Published and registered as `PARTIAL_RUN_IMAGERY_UNAVAILABLE`)

---

## 6. Comprehensive Test Suite Results

Every phase test suite was executed against the active repository:

| Test Suite | Script | Total Tests | Result | Summary File |
|---|---|---|---|---|
| **Phase 3: Raster Processing** | [`scripts/test_satellite_processing.py`](file:///c:/Users/Abdul/Desktop/FloodSpaceAI/scripts/test_satellite_processing.py) | 7 | **7/7 PASS** | [`phase3_test_suite_summary.json`](file:///c:/Users/Abdul/Desktop/FloodSpaceAI/data/processed/phase3_test_suite_summary.json) |
| **Phase 4A: Real Satellite Acquisition** | [`scripts/test_satellite_acquisition.py`](file:///c:/Users/Abdul/Desktop/FloodSpaceAI/scripts/test_satellite_acquisition.py) | 8 | **8/8 PASS** | [`phase4a_test_suite_summary.json`](file:///c:/Users/Abdul/Desktop/FloodSpaceAI/data/processed/phase4a_test_suite_summary.json) |
| **Phase 4B: Asset & Connectivity Engine** | [`scripts/test_asset_connectivity.py`](file:///c:/Users/Abdul/Desktop/FloodSpaceAI/scripts/test_asset_connectivity.py) | 8 | **8/8 PASS** | [`phase4b_test_suite_summary.json`](file:///c:/Users/Abdul/Desktop/FloodSpaceAI/data/processed/phase4b_test_suite_summary.json) |
| **Phase 5: End-to-End Orchestrator** | [`scripts/test_orchestrator.py`](file:///c:/Users/Abdul/Desktop/FloodSpaceAI/scripts/test_orchestrator.py) | 9 | **9/9 PASS** | [`phase5_test_suite_summary.json`](file:///c:/Users/Abdul/Desktop/FloodSpaceAI/data/processed/phase5_test_suite_summary.json) |
| **Dashboard Production Build** | `cd dashboard && npm run build` | — | **SUCCESS** | Next.js 16 (Turbopack) 0 errors, 4/4 pages static |

### Phase 5 Automated Test Matrix

```
[TEST 1] Complete Benchmark Run with Verified Fixtures ...................... PASS
[TEST 2] Future Date Rejection (2028-06-15) ................................. PASS
[TEST 3] Historical OSM Unavailable Handling (Unseen AOI) .................. PASS
[TEST 4] Cloud-Obscured Optical Scene Handling ............................. PASS
[TEST 5] Inverted Bounding Box Rejection (W > E) ........................... PASS
[TEST 6] Anti-Pollution Check: Stale Cache Reuse Blocked ................... PASS
[TEST 7] Strict Validation Data Isolation (No EMSR927/UNOSAT) .............. PASS
[TEST 8] Grounded Evidence & Multilingual Report Consistency ............... PASS
[TEST 9] Manifest Schema 1.0.0 & Dashboard Registry Sync ................... PASS
-----------------------------------------------------------------------------
OVERALL RESULT: ALL 9 TESTS PASSED (Ran in 244.5s)
```

---

## 7. Versioned Run Manifest Schema (v1.0.0)

Every pipeline execution produces a standardized `run_manifest.json`:

```json
{
  "schema_version": "1.0.0",
  "run_id": "trishuli_benchmark_verified",
  "title": "Run trishuli_benchmark_verified (2026-08-28)",
  "overall_status": "PARTIAL_RUN_OPTICAL_UNCONFIRMED",
  "overall_message": "SAR analysis completed; optical verification limited by cloud cover.",
  "provenance_mode": "VERIFIED_TRISHULI_BENCHMARK_CACHE",
  "timestamp_utc": "2026-10-09T09:42:58.580692+00:00",
  "inputs": {
    "bbox": [84.9, 27.75, 85.25, 28.05],
    "flood_date": "2026-08-28",
    "snapshot_date": "2026-07-27T00:00:00Z"
  },
  "stages": {
    "stage_1_input_validation": { "stage": "Input Validation", "status": "SUCCESS", "duration_s": 0.001 },
    "stage_2_satellite_discovery": { "stage": "Satellite Discovery", "status": "PARTIAL", "duration_s": 2.339 },
    "stage_3_satellite_acquisition": { "stage": "Satellite Data Acquisition", "status": "SUCCESS", "duration_s": 11.449 },
    "stage_4_raster_processing": { "stage": "SAR & Optical Raster Processing", "status": "SUCCESS", "duration_s": 11.449 },
    "stage_5_historical_osm": { "stage": "Historical OSM Snapshot Ingestion", "status": "SUCCESS", "duration_s": 25.203 },
    "stage_6_asset_connectivity": { "stage": "Asset Exposure & Road Connectivity Modeling", "status": "SUCCESS", "duration_s": 25.203 },
    "stage_7_situation_evidence": { "stage": "Situation Report & Evidence Grounding", "status": "SUCCESS", "duration_s": 0.005 },
    "stage_8_publish_manifest": { "stage": "Run Manifest Publishing & Dashboard Registry", "status": "SUCCESS", "duration_s": 0.004 }
  },
  "metrics": {
    "candidate_flood_pixels": 1286,
    "candidate_flood_clusters": 27,
    "candidate_flood_area_ha": 35.03,
    "potentially_affected_buildings": 195,
    "total_mapped_buildings": 132765,
    "potentially_affected_roads": 115,
    "potentially_affected_road_length_km": 59.26,
    "potentially_affected_bridges": 13,
    "total_mapped_bridges": 187,
    "disrupted_road_segments": 3748,
    "pre_event_components": 181,
    "post_event_components": 252,
    "settlements_analysed": 589,
    "potentially_cut_off_settlements": 18,
    "hospital_data_available": false
  },
  "limitations": [
    "Modelled candidate only: The flood output is a modelled potential inundation candidate...",
    "No confirmed physical damage: Potentially affected assets are identified solely through 2D spatial overlap...",
    "Optical cloud contamination: Post-event Sentinel-2 optical imagery is cloud-contaminated...",
    "Road disconnection vs real-world isolation: The 18 potentially cut-off settlements represent modelled graph disconnections...",
    "Hospital coverage limitation: Historical hospital data not available; regional administrative hubs used."
  ],
  "attributions": {
    "copernicus_sentinel": "Contains modified Copernicus Sentinel data (2024/2026), processed under ESA Copernicus Open Access.",
    "copernicus_dem": "Copernicus WorldDEM-30 © DLR e.V. 2010–2014 and © Airbus Defence and Space GmbH 2014–2018.",
    "openstreetmap": "© OpenStreetMap contributors, ODbL 1.0 license.",
    "validation_isolation": "Copernicus EMSR927 / UNOSAT products strictly isolated from analytical pipeline inputs."
  }
}
```

---

## 8. Dashboard Integration Highlights

1. **Unified Pipeline Run Selector (`Header.tsx`):**
   Top-level dropdown selector allows judges to switch between pipeline runs (`trishuli_benchmark_verified`, `unseen_aoi_pokhara`, test error runs). Displays active run bounding box, date, provenance badge, and dynamic status pill (`SUCCESS`, `PARTIAL`, `UNAVAILABLE`, `FAILED`).
2. **8-Stage Live Execution Trace (`PipelineDiagram.tsx`):**
   Displays an interactive matrix of the 8 execution stages for the chosen run. Clicking any stage card reveals execution duration, status badge, message, and files used.
3. **Dual Situation Report & Raw Manifest View (`SituationReportCopilot.tsx`):**
   Toggle switch enables viewing the multilingual grounded situation report (English or Nepali) or the raw verified `run_manifest.json`.
4. **Honest Safeguard Alerts Across Panels:**
   When an unseen AOI or failed run is selected (e.g. `unseen_aoi_pokhara`), the map, asset analysis, and connectivity analysis panels immediately display clear safeguard notices explaining that exposure calculations were safely halted to prevent fabricating ungrounded statistics.

---

## 9. Current Limitations & Blockers

1. **Arbitrary-AOI Live Satellite Ingestion Bandwidth:**
   While the pipeline discovers matching Sentinel-1 SAR and Sentinel-2 optical scenes via STAC for arbitrary bounding boxes across Nepal, automated downloading of raw multi-gigabyte SAFE/COG rasters in real-time requires live Copernicus Data Space Ecosystem (CDSE) / AWS Open Data session credentials and bandwidth. When credentials or rasters are not present locally, the system halts with `PARTIAL_RUN_IMAGERY_UNAVAILABLE`.
2. **Arbitrary-AOI Historical OSM Extraction:**
   Overpass API historical snapshot queries (`[date:"YYYY-MM-DDTHH:MM:SSZ"]`) are subject to upstream public server rate limits and timeouts for large regional bounding boxes. Pre-event OSM snapshots are cached for the primary evaluation areas.
3. **Optical Cloud Obscuration in Mountain Terrain:**
   Monsoon convective cloud cover frequently obstructs post-flood Sentinel-2 optical imagery. The system prioritizes all-weather Sentinel-1 C-band SAR change detection and discloses optical confirmation as inconclusive whenever cloud cover exceeds analytical thresholds.

---

## 10. Summary of Changed Files in Phase 5

- [`scripts/run_floodspace_pipeline.py`](file:///c:/Users/Abdul/Desktop/FloodSpaceAI/scripts/run_floodspace_pipeline.py) *(New orchestrator script coordinating all 8 stages)*
- [`scripts/test_orchestrator.py`](file:///c:/Users/Abdul/Desktop/FloodSpaceAI/scripts/test_orchestrator.py) *(New Phase 5 test suite with 9 automated tests)*
- [`data/processed/phase5_test_suite_summary.json`](file:///c:/Users/Abdul/Desktop/FloodSpaceAI/data/processed/phase5_test_suite_summary.json) *(Machine-readable Phase 5 test summary)*
- [`dashboard/src/data/types.ts`](file:///c:/Users/Abdul/Desktop/FloodSpaceAI/dashboard/src/data/types.ts) *(Added RunManifest, PipelineStageInfo, and RunRegistryEntry types)*
- [`dashboard/src/data/dataLoader.ts`](file:///c:/Users/Abdul/Desktop/FloodSpaceAI/dashboard/src/data/dataLoader.ts) *(Added getPipelineRuns, getRunManifest, getRunEvidence, getRunReport)*
- [`dashboard/src/data/RunContext.tsx`](file:///c:/Users/Abdul/Desktop/FloodSpaceAI/dashboard/src/data/RunContext.tsx) *(New React context managing global run selection and manifest state)*
- [`dashboard/src/app/page.tsx`](file:///c:/Users/Abdul/Desktop/FloodSpaceAI/dashboard/src/app/page.tsx) *(Wrapped application with RunProvider)*
- [`dashboard/src/components/common/Header.tsx`](file:///c:/Users/Abdul/Desktop/FloodSpaceAI/dashboard/src/components/common/Header.tsx) *(Integrated Run Selector, status pills, provenance badges, dynamic tabs)*
- [`dashboard/src/components/pipeline/PipelineDiagram.tsx`](file:///c:/Users/Abdul/Desktop/FloodSpaceAI/dashboard/src/components/pipeline/PipelineDiagram.tsx) *(Integrated 8-stage orchestrator execution trace grid)*
- [`dashboard/src/components/assets/AssetAnalysis.tsx`](file:///c:/Users/Abdul/Desktop/FloodSpaceAI/dashboard/src/components/assets/AssetAnalysis.tsx) *(Dynamic run metrics, unavailable run safeguard disclosures)*
- [`dashboard/src/components/connectivity/ConnectivityAnalysis.tsx`](file:///c:/Users/Abdul/Desktop/FloodSpaceAI/dashboard/src/components/connectivity/ConnectivityAnalysis.tsx) *(Dynamic run metrics, hospital limitation notice, unavailable disclosures)*
- [`dashboard/src/components/provenance/ProvenanceModal.tsx`](file:///c:/Users/Abdul/Desktop/FloodSpaceAI/dashboard/src/components/provenance/ProvenanceModal.tsx) *(Dynamic run provenance mode, mandatory attributions, validation isolation)*
- [`dashboard/src/components/copilot/SituationReportCopilot.tsx`](file:///c:/Users/Abdul/Desktop/FloodSpaceAI/dashboard/src/components/copilot/SituationReportCopilot.tsx) *(Added raw run_manifest.json viewer toggle, linked evidence)*
- [`dashboard/src/components/map/MapHero.tsx`](file:///c:/Users/Abdul/Desktop/FloodSpaceAI/dashboard/src/components/map/MapHero.tsx) *(Dynamic bounding box re-centering and unavailable status indicator)*
- [`docs/PHASE5_ORCHESTRATION_REPORT.md`](file:///c:/Users/Abdul/Desktop/FloodSpaceAI/docs/PHASE5_ORCHESTRATION_REPORT.md) *(This report)*

---

**Acceptance Recommendation:** Phase 5 is fully implemented, verified across all regression suites, and ready for evaluation.
