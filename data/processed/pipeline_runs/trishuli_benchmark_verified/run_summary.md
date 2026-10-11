# FloodSpaceAI — Pipeline Run Summary

**Run ID:** `trishuli_benchmark_verified`  
**Overall Status:** `PARTIAL_RUN_OPTICAL_UNCONFIRMED`  
**Message:** SAR analysis completed; optical verification limited by cloud cover.  
**Provenance Mode:** `VERIFIED_TRISHULI_BENCHMARK_CACHE`  
**Event Date:** `2026-08-28`  
**AOI Bounding Box:** `[84.9, 27.75, 85.25, 28.05]`  
**Completed:** `2026-10-09T15:34:09.355434+00:00`  

---

## Stage Breakdown
| Stage | Name | Status | Message |
| :---: | :--- | :---: | :--- |
| 1 | Input Validation | `SUCCESS` | Valid AOI [84.9, 27.75, 85.25, 28.05] and event date 2026-08-28. |
| 2 | Satellite Discovery | `PARTIAL` | S1 SAR pair matched (Orbit 85); S2 optical scene cloud-limited (75.9% cloud). |
| 3 | Satellite Acquisition | `SUCCESS` | Acquisition mode: VERIFIED_TRISHULI_BENCHMARK_CACHE |
| 4 | Raster Processing | `SUCCESS` | Generated 1,286 candidate pixels across 27 clusters. |
| 5 | Historical OSM | `SUCCESS` | Verified pre-event snapshot at 2026-07-27T00:00:00Z. |
| 6 | Asset & Connectivity | `SUCCESS` | Potentially affected: 195 bldgs, 115 roads, 13 bridges. 18 potentially cut-off settlements. |
| 7 | Situation Evidence | `SUCCESS` | Grounded multilingual situation reports generated (13 claims linked). |
| 8 | Manifest Publishing | `SUCCESS` | Run manifest published. |

---

## Key Metrics
- Candidate Flood Pixels: **1,286**
- Candidate Flood Area: **35.03 ha**
- Potentially Affected Buildings: **195**
- Potentially Affected Roads: **115** (59.26 km)
- Potentially Affected Bridges: **13**
- Modeled Cut-Off Settlements: **18**
