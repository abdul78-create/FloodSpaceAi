# FloodSpaceAI Situation Report — Run `test_p5_manifest_sync`

**Event Date:** `2026-08-28`  
**AOI Bounding Box:** `[84.9, 27.75, 85.25, 28.05]`  
**OSM Snapshot Date:** `2026-07-27T00:00:00Z`  
**Provenance Mode:** `VERIFIED_TRISHULI_BENCHMARK_CACHE`  
**Generated:** `2026-10-09T17:21:41.293131+00:00`

---

## 1. Executive Summary
FloodSpaceAI analyzed potential inundation for the target event date `2026-08-28` using multi-sensor Copernicus satellite imagery and pre-event OpenStreetMap infrastructure data.

- **Candidate Flood Pixels:** **1,286**
- **Candidate Area:** **35.26 ha**
- **Potentially Affected Buildings:** **195** (exposure overlay)
- **Potentially Affected Roads:** **115** (59.26 km)
- **Potentially Affected Bridges:** **13**
- **Modeled Cut-Off Settlements:** **18**

> **Scientific Notice:** All figures represent modeled candidate inundation and topological network disruption. They do *not* confirm physical destruction or ground-truth isolation.

---

## 2. Satellite Observation & Coverage
- **SAR Sensor:** Sentinel-1 C-band synthetic aperture radar (all-weather penetrative observation).
- **Optical Sensor:** Sentinel-2 multispectral MSI (Scene Classification Layer cloud masking applied).
- **Optical Coverage Status:** Generated 1,286 candidate pixels across 27 clusters..
- **Candidate Interpretation:** Detected 1,286 pixels (35.26 ha) of candidate surface water accumulation.

---

## 3. Road Network Disruption & Isolation Modeling
- **Disrupted Road Segments:** 3,748
- **Baseline Connected Components:** 181
- **Post-Disruption Connected Components:** 252
- **Settlements Evaluated:** 589
- **Potentially Cut-Off Settlements:** 18
- **Hospital Data Status:** Historical hospital data not available in pre-event snapshot; town/city hubs utilized for modeled access.

---

## 4. Grounded Claims Index
Every quantitative claim in this report links to an explicit record in `evidence.json`:
| Claim ID | Metric | Value | Unit | Source Artifact |
| :--- | :--- | :---: | :--- | :--- |
| `CLAIM-test_p5_manifest_sync-FLOOD-PIXELS` | Candidate Flood Pixels | 1,286 | pixels | `rasters/final_flood_candidate_v3.tif` |
| `CLAIM-test_p5_manifest_sync-FLOOD-AREA` | Candidate Flood Area | 35.26 | ha | `rasters/final_flood_candidate_v3.tif` |
| `CLAIM-test_p5_manifest_sync-AFFECTED-BUILDINGS` | Potentially Affected Buildings | 195 | buildings | `assets/buildings_affected_v3.geojson` |
| `CLAIM-test_p5_manifest_sync-AFFECTED-ROADS` | Potentially Affected Roads | 115 | road_features | `assets/roads_affected_v3.geojson` |
| `CLAIM-test_p5_manifest_sync-AFFECTED-ROAD-LENGTH` | Affected Road Length | 59.26 | km | `assets/roads_affected_v3.geojson` |
| `CLAIM-test_p5_manifest_sync-AFFECTED-BRIDGES` | Potentially Affected Bridges | 13 | bridges | `assets/bridges_affected_v3.geojson` |
| `CLAIM-test_p5_manifest_sync-CUTOFF-SETTLEMENTS` | Potentially Cut-Off Settlements | 18 | settlements | `connectivity/settlements_cutoff_v4.geojson` |

---

## 5. Mandatory Limitations
- The flood output is a modelled potential inundation candidate, not confirmed physical damage.
- Potentially affected assets are based on candidate spatial overlap; not confirmed structural destruction.
- Potentially cut-off settlements represent modelled topological network disconnections, not confirmed real-world isolation.
- Validation layers (EMSR927 / UNOSAT) are strictly checking-only and excluded from analytical pipelines.
- This system is an educational and research prototype for the Multimodal AI Hackathon 2026.
- Historical hospital data was unavailable in the pre-event snapshot; municipal town/city hubs were utilized for modeled road connectivity.

---

## 6. Authoritative Data Provenance & Legal Disclaimers
- **Copernicus Sentinel:** Contains modified Copernicus Sentinel data (2024/2026), processed under ESA Copernicus Open Access.
- **Copernicus DEM:** Produced using Copernicus WorldDEM-30 © DLR e.V. 2010–2014 and © Airbus Defence and Space GmbH 2014–2018.
- **OpenStreetMap:** © OpenStreetMap contributors, ODbL 1.0 license. Pre-event snapshot verified.
- **Independent Validation:** Copernicus EMSR927 / UNOSAT assessments strictly isolated from analytical pipeline inputs.
