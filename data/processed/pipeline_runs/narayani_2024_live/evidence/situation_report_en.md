# FloodSpaceAI Situation Report — Run `narayani_2024_live`

**Event Date:** `2024-08-20`  
**AOI Bounding Box:** `[84.3, 27.55, 84.5, 27.72]`  
**OSM Snapshot Date:** `2024-08-13T00:00:00Z`  
**Provenance Mode:** `LIVE_AUTHORITATIVE_SATELLITE_RETRIEVAL`  
**Generated:** `2026-10-09T15:34:31.929555+00:00`

---

## 1. Executive Summary
FloodSpaceAI analyzed potential inundation for the target event date `2024-08-20` using multi-sensor Copernicus satellite imagery and pre-event OpenStreetMap infrastructure data.

- **Candidate Flood Pixels:** **0**
- **Candidate Area:** **0.00 ha**
- **Potentially Affected Buildings:** **0** (exposure overlay)
- **Potentially Affected Roads:** **0** (0.00 km)
- **Potentially Affected Bridges:** **0**
- **Modeled Cut-Off Settlements:** **0**

> **Scientific Notice:** All figures represent modeled candidate inundation and topological network disruption. They do *not* confirm physical destruction or ground-truth isolation.

---

## 2. Satellite Observation & Coverage
- **SAR Sensor:** Sentinel-1 C-band synthetic aperture radar (all-weather penetrative observation).
- **Optical Sensor:** Sentinel-2 multispectral MSI (Scene Classification Layer cloud masking applied).
- **Optical Coverage Status:** Generated 0 candidate pixels across 0 clusters..
- **Candidate Interpretation:** Zero candidate flood pixels were detected under current SAR and optical thresholds. This reflects sensor/threshold criteria and does not prove absence of flooding.

---

## 3. Road Network Disruption & Isolation Modeling
- **Disrupted Road Segments:** 0
- **Baseline Connected Components:** 35
- **Post-Disruption Connected Components:** 35
- **Settlements Evaluated:** 25
- **Potentially Cut-Off Settlements:** 0
- **Hospital Data Status:** Historical hospital locations present and evaluated.

---

## 4. Grounded Claims Index
Every quantitative claim in this report links to an explicit record in `evidence.json`:
| Claim ID | Metric | Value | Unit | Source Artifact |
| :--- | :--- | :---: | :--- | :--- |
| `CLAIM-narayani_2024_live-FLOOD-PIXELS` | Candidate Flood Pixels | 0 | pixels | `rasters/final_flood_candidate_v3.tif` |
| `CLAIM-narayani_2024_live-FLOOD-AREA` | Candidate Flood Area | 0.00 | ha | `rasters/final_flood_candidate_v3.tif` |
| `CLAIM-narayani_2024_live-AFFECTED-BUILDINGS` | Potentially Affected Buildings | 0 | buildings | `assets/buildings_affected_v3.geojson` |
| `CLAIM-narayani_2024_live-AFFECTED-ROADS` | Potentially Affected Roads | 0 | road_features | `assets/roads_affected_v3.geojson` |
| `CLAIM-narayani_2024_live-AFFECTED-ROAD-LENGTH` | Affected Road Length | 0.00 | km | `assets/roads_affected_v3.geojson` |
| `CLAIM-narayani_2024_live-AFFECTED-BRIDGES` | Potentially Affected Bridges | 0 | bridges | `assets/bridges_affected_v3.geojson` |
| `CLAIM-narayani_2024_live-CUTOFF-SETTLEMENTS` | Potentially Cut-Off Settlements | 0 | settlements | `connectivity/settlements_cutoff_v4.geojson` |

---

## 5. Mandatory Limitations
- The flood output is a modelled potential inundation candidate, not confirmed physical damage.
- Potentially affected assets are based on candidate spatial overlap; not confirmed structural destruction.
- Potentially cut-off settlements represent modelled topological network disconnections, not confirmed real-world isolation.
- Validation layers (EMSR927 / UNOSAT) are strictly checking-only and excluded from analytical pipelines.
- This system is an educational and research prototype for the Multimodal AI Hackathon 2026.

---

## 6. Authoritative Data Provenance & Legal Disclaimers
- **Copernicus Sentinel:** Contains modified Copernicus Sentinel data (2024/2026), processed under ESA Copernicus Open Access.
- **Copernicus DEM:** Produced using Copernicus WorldDEM-30 © DLR e.V. 2010–2014 and © Airbus Defence and Space GmbH 2014–2018.
- **OpenStreetMap:** © OpenStreetMap contributors, ODbL 1.0 license. Pre-event snapshot verified.
- **Independent Validation:** Copernicus EMSR927 / UNOSAT assessments strictly isolated from analytical pipeline inputs.
