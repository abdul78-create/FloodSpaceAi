# FloodSpaceAI — Pipeline Run Summary

**Run ID:** `narayani_2024_live`  
**Overall Status:** `PARTIAL_RUN_OPTICAL_UNCONFIRMED`  
**Message:** SAR analysis completed; optical verification limited by cloud cover.  
**Provenance Mode:** `LIVE_AUTHORITATIVE_SATELLITE_RETRIEVAL`  
**Event Date:** `2024-08-20`  
**AOI Bounding Box:** `[84.3, 27.55, 84.5, 27.72]`  
**Completed:** `2026-10-09T15:34:31.930558+00:00`  

---

## Stage Breakdown
| Stage | Name | Status | Message |
| :---: | :--- | :---: | :--- |
| 1 | Input Validation | `SUCCESS` | Valid AOI [84.3, 27.55, 84.5, 27.72] and event date 2024-08-20. |
| 2 | Satellite Discovery | `PARTIAL` | S1 SAR pair matched (Orbit 158); S2 optical scene cloud-limited (77.8% cloud). |
| 3 | Satellite Acquisition | `SUCCESS` | Acquisition mode: LIVE_AUTHORITATIVE_SATELLITE_RETRIEVAL |
| 4 | Raster Processing | `SUCCESS` | Generated 0 candidate pixels across 0 clusters. |
| 5 | Historical OSM | `SUCCESS` | Verified pre-event snapshot at 2024-08-13T00:00:00Z. |
| 6 | Asset & Connectivity | `SUCCESS` | Potentially affected: 0 bldgs, 0 roads, 0 bridges. 0 potentially cut-off settlements. |
| 7 | Situation Evidence | `SUCCESS` | Grounded multilingual situation reports generated (13 claims linked). |
| 8 | Manifest Publishing | `SUCCESS` | Run manifest published. |

---

## Key Metrics
- Candidate Flood Pixels: **0**
- Candidate Flood Area: **0.00 ha**
- Potentially Affected Buildings: **0**
- Potentially Affected Roads: **0** (0.00 km)
- Potentially Affected Bridges: **0**
- Modeled Cut-Off Settlements: **0**
