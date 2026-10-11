# FloodSpaceAI — Asset & Connectivity Execution Summary

**Run ID:** `trishuli_benchmark_reproduction`  
**AOI Bounding Box:** `[84.9, 27.75, 85.25, 28.05]`  
**Event Date:** `2026-08-28`  
**OSM Snapshot Date:** `2026-07-27T00:00:00Z`  
**Provenance Mode:** `VERIFIED_TRISHULI_OSM_FIXTURE`  
**Timestamp (UTC):** `2026-10-09T17:22:04.862035+00:00`  

---

## 1. Asset Exposure Estimates (Candidate Inundation Overlap)
- **Potentially Affected Buildings:** **195** (out of 132765 mapped)
- **Potentially Affected Roads:** **115** (59.26 km affected out of 3843.25 km mapped)
- **Potentially Affected Bridges:** **13** (out of 187 mapped)

> *Notice: These are modeled potential exposure estimates; they do not confirm physical structural damage.*

---

## 2. Road Network Connectivity & Isolated Settlement Modeling
- **Vehicle-Accessible Ways:** 4405
- **Disrupted Road Segments:** **3748**
- **Connected Components:** 181 (baseline) $\rightarrow$ 252 (post-disruption)
- **Settlements Analysed:** 589
- **Potentially Cut-Off Settlements:** **18**
- **Hospital Data Available:** False (Historical hospital data not available in pre-event snapshot; town/city hubs utilized for modeled access.)

---

## 3. Data Provenance & Isolation
- **OSM Attribution:** © OpenStreetMap contributors
- **Snapshot Selection:** Verified pre-event snapshot (`2026-07-27T00:00:00Z` < `2026-08-28`)
- **Checking-Only Isolation:** Copernicus EMSR927 / UNOSAT layers strictly excluded from production calculations.
