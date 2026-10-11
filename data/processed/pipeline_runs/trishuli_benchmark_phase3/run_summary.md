# FloodSpaceAI — Satellite Processing Run Report (`trishuli_benchmark_phase3`)

**Execution Status:** `SUCCESS_COMPLETED`  
**Timestamp:** `2026-10-09T07:26:53.508058+00:00`  
**Target AOI Bbox:** `[84.9, 27.75, 85.25, 28.05]`  
**Target Flood Date:** `2026-08-28`  

---

## 1. Provenance & Input Verification

- **Provenance Mode:** `VERIFIED_TRISHULI_BENCHMARK_CACHE`
- **Strict Anti-Pollution Enforcement:** Active (cached Trishuli inputs restricted strictly to matching Trishuli parameters).

## 2. Processing Metrics

### Sentinel-1 SAR Change Detection
- **Valid Pixels:** 4,177,140 (99.59%)
- **Filter:** 3x3 median filter on linear amplitude
- **VV Mean Change:** -0.077 dB
- **VH Mean Change:** -0.036 dB

### Sentinel-2 Optical NDWI & SCL Masking
- **Pre-Event Valid Coverage:** 83.18% (Cloud-masked: 16.82%)
- **Post-Event Valid Coverage:** 52.66% (Cloud-masked: 47.34%)
- **Common Valid Coverage:** 51.07%
- **SCL Policy:** Retained SCL classes [2, 4, 5, 6, 7]; masked shadows (3), clouds (8,9), cirrus (10), snow (11)

### FloodSpaceAI V3 Candidate Integration
- **Raw Candidate Pixels:** 3,040
- **Final V3 Pixels:** 1,286
- **Patch Filter Reduction:** 57.7%
- **Final Inundation Clusters:** 27 polygons
- **Estimated Candidate Area:** 35.03 ha

## 3. Generated Artifacts

- `filtered_vv_change_db`: `data/processed/pipeline_runs/trishuli_benchmark_phase3/rasters/filtered_vv_change_db.tif`
- `filtered_vh_change_db`: `data/processed/pipeline_runs/trishuli_benchmark_phase3/rasters/filtered_vh_change_db.tif`
- `pre_ndwi_cloudmasked`: `data/processed/pipeline_runs/trishuli_benchmark_phase3/rasters/pre_ndwi_cloudmasked.tif`
- `post_ndwi_cloudmasked`: `data/processed/pipeline_runs/trishuli_benchmark_phase3/rasters/post_ndwi_cloudmasked.tif`
- `ndwi_change`: `data/processed/pipeline_runs/trishuli_benchmark_phase3/rasters/ndwi_change.tif`
- `final_flood_candidate_v3`: `data/processed/pipeline_runs/trishuli_benchmark_phase3/rasters/final_flood_candidate_v3.tif`
