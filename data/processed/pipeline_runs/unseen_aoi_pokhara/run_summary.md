# FloodSpaceAI — Pipeline Run Summary

**Run ID:** `unseen_aoi_pokhara`  
**Overall Status:** `PARTIAL_RUN_IMAGERY_UNAVAILABLE`  
**Message:** Satellite imagery not yet acquired/cached for requested AOI/date.  
**Provenance Mode:** `UNKNOWN`  
**Event Date:** `2026-09-15`  
**AOI Bounding Box:** `[83.95, 28.18, 84.05, 28.28]`  
**Completed:** `2026-10-09T09:43:09.616510+00:00`  

---

## Stage Breakdown
| Stage | Name | Status | Message |
| :---: | :--- | :---: | :--- |
| 1 | Input Validation | `SUCCESS` | Valid AOI [83.95, 28.18, 84.05, 28.28] and event date 2026-09-15. |
| 2 | Satellite Discovery | `SUCCESS` | Both S1 SAR (Orbit 19) and S2 optical pairs discovered. |
| 3 | Satellite Acquisition | `UNAVAILABLE` | Acquisition mode: UNKNOWN |
| 4 | Raster Processing | `UNAVAILABLE` | Query parameters (bbox=[83.95, 28.18, 84.05, 28.28], flood_date='2026-09-15') represent an unseen AOI or date. While candidate scenes were discovered in STAC catalogues, raw multiband satellite rasters have not yet been fetched for this specific AOI/date. Strict provenance isolation prevents reusing cached Trishuli rasters. |
| 5 | Historical OSM | `SKIPPED` | Skipped because flood raster was not generated. |
| 6 | Asset & Connectivity | `SKIPPED` | Skipped because flood raster was not generated. |
| 7 | Situation Evidence | `SUCCESS` | Grounded multilingual situation reports generated. |
| 8 | Manifest Publishing | `SUCCESS` | Run manifest published. |

---

## Key Metrics
- Candidate Flood Pixels: **0**
- Candidate Flood Area: **0.00 ha**
- Potentially Affected Buildings: **0**
- Potentially Affected Roads: **0** (0.00 km)
- Potentially Affected Bridges: **0**
- Modeled Cut-Off Settlements: **0**
