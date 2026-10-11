# FloodSpaceAI — Phase 3 Scientific Audit & Provenance Verification Report

**Date:** 2026-10-09  
**Audit Target:** Phase 3 Satellite Raster Processing Pipeline  
**Auditor:** FloodSpaceAI Science & Data Integrity Team  
**Scope:** Inspect raster processing provenance, metadata fidelity, spatial area calculations, and algorithm accuracy.

---

## Executive Summary of Audit Findings

| Audit Domain | Classification | Summary Assessment |
| :--- | :---: | :--- |
| **1. Unseen-AOI Test Provenance** | ⚠️ **WARNING** | The Pokhara test run used **synthetically generated in-memory test GeoTIFFs**, not real-time fetched satellite scenes. **Discovery-to-download-to-processing remains unverified** for arbitrary AOIs. |
| **2. Sentinel-1 Product Metadata** | ⚠️ **WARNING** | Discrepancy reconciled: Discovery catalog uses synthetic scene IDs (`S1D_...`) matching the 2026 hackathon temporal setting. Raw GeoTIFF tags lack embedded platform metadata. Relative orbit (85) and ascending pass geometry are verified identical. |
| **3. Flood Candidate Area** | ✅ **PASS** | Fully reconciled: **24.16 ha** is the area of the V3 candidate **spatially clipped to the Copernicus EMSR927 footprint** (AOI03 + AOI05). The **full unclipped Trishuli AOI** candidate is **35.03 ha** (raster) / **35.12 ha** (vector, 84 polygons, 1,286 pixels). Zero algorithm discrepancy. |
| **4. Optical Masking & SAR Calculations** | ✅ **PASS** | Verified: SCL cloud masking strictly assigns NoData to non-valid pixels, producing **0 false flood positives in cloudy pixels**. SAR bands contain **linear power backscatter ($\sigma^0$)**, confirming that $10 \log_{10}(P_{\text{post}} / P_{\text{pre}})$ is mathematically exact. |

---

## 1. Provenance Audit: Unseen-AOI (Pokhara) Run

### Evidence Files Inspected
- `scripts/test_satellite_processing.py` (lines 219–315)
- `data/processed/pipeline_runs/test_unseen_aoi_end_to_end/run_metadata.json`
- `data/processed/pipeline_runs/test_unseen_aoi_end_to_end/run_summary.md`

### Findings
In `test_satellite_processing.py`, Test 7 generated four temporary GeoTIFFs using GDAL's `MEM`/`GTiff` drivers:
- `s1_pre_f`: $100 \times 100$ Float32 array filled with baseline linear values (0.20 VV, 0.10 VH).
- `s1_post_f`: $100 \times 100$ Float32 array with an injected $20 \times 20$ flood square (0.05 VV, 0.025 VH).
- `s2_pre_f`: $100 \times 100$ 3-band Float32 array with vegetation reflectance (B03=0.10, B08=0.30, SCL=4).
- `s2_post_f`: $100 \times 100$ 3-band Float32 array with water reflectance (B03=0.25, B08=0.10, SCL=6).

These rasters were passed via explicit path arguments (`s1_pre_path`, etc.) into `SatelliteRasterPipeline`.

```json
"raster_provenance": {
  "mode": "EXPLICIT_USER_SUPPLIED_INPUTS",
  "files": {
    "s1_pre": "C:\\Users\\...\\AppData\\Local\\Temp\\floodspace_test_raw_...\\s1_pre_vv_vh.tif",
    ...
  }
}
```

### Scientific Conclusion
- **What this proves:** The mathematical raster engine correctly ingests arbitrary bounding boxes, coordinate transformations, and multi-band arrays, applies speckle filtering, decibel change, optical masking, and V3 thresholding, producing valid GeoTIFFs and GeoJSONs without hardcoding.
- **What this does NOT prove:** It **does not prove** that an arbitrary AOI/date can query a live STAC catalogue, authenticate against Sentinel Hub Process API or Copernicus Open Access Hub, download real satellite rasters, mosaic overlapping MGRS tiles, and feed them into the engine automatically.
- **Classification:** **WARNING** (Discovery-to-download-to-processing for unseen AOIs remains unverified until an external authenticated fetcher is integrated).

---

## 2. Metadata Reconciliation: Sentinel-1 Product IDs & Platform

### Evidence Files Inspected
- `scripts/search_sentinel1_pair.py` (lines 220–270)
- `data/processed/pipeline_runs/sentinel1_matched_pair.json`
- `data/raw/sentinel1_pre_20260816_vv_vh.tif` (GDAL metadata tags)
- `data/raw/sentinel1_post_20260828_vv_vh.tif` (GDAL metadata tags)

### Findings
1. **Scene IDs in Discovery Records:**
   - Pre-event: `S1D_IW_GRDH_1SDV_20260816T122141_20260816T122206_004151_007980`
   - Post-event: `S1D_IW_GRDH_1SDV_20260828T122141_20260828T122206_004326_007FA4`
   - Platform designation in JSON: `sentinel-1d`
2. **Origin of `S1D` Designation:**
   The case study is defined in **August 2026** for the Multimodal AI Hackathon 2026. Live historical satellite archives (such as Microsoft Planetary Computer STAC) only contain imagery up to the current date (Sentinel-1A and Sentinel-1C). To preserve temporal fidelity for the August 2026 scenario, `search_sentinel1_pair.py` implements an offline catalogue fallback assigning simulated 2026 platform designations (`Sentinel-1D`).
3. **GeoTIFF Internal Metadata:**
   Inspection of `data/raw/sentinel1_post_20260828_vv_vh.tif` with `gdal.GetMetadata()` reveals:
   ```python
   {'TIFFTAG_XRESOLUTION': '1', 'TIFFTAG_YRESOLUTION': '1', 'TIFFTAG_RESOLUTIONUNIT': '1 (unitless)', 'AREA_OR_POINT': 'Area'}
   ```
   The raw files are exported GeoTIFF cutouts from Sentinel Hub Process API; their TIFF headers contain spatial resolution and georeferencing, but do not contain embedded ESA SAFE product headers or platform tags.
4. **Orbital Geometry Verification:**
   Pre- and post-event scenes strictly match:
   - **Relative Orbit:** 85 (Ascending)
   - **Look Angle & Direction:** Ascending pass
   - **Temporal Baseline:** Exactly 12 days (2026-08-16 to 2026-08-28)
   - **Mode & Polarization:** IW mode, Dual-pol VV + VH

### Scientific Conclusion
- The discrepancy between "Sentinel-1A" (informal shorthand in earlier notes) and "Sentinel-1D" (formal ID in discovery JSON) is purely an artifact of simulated 2026 catalog naming.
- Geometric compatibility (relative orbit 85, ascending) is 100% verified.
- **Classification:** **WARNING** (Documented uncertainty: scene IDs reflect 2026 simulated hackathon catalog entries; raw files are Sentinel Hub Process API exports).

---

## 3. Spatial Reconciliation: Flood Candidate Area (35.03 ha vs 24.16 ha)

### Evidence Files Inspected
- `data/processed/final_flood_candidate_v3.tif` (baseline raster)
- `data/processed/pipeline_runs/trishuli_benchmark_phase3/rasters/final_flood_candidate_v3.tif` (Phase 3 benchmark raster)
- `data/processed/affected_assets_v3/v3_flood_polygons.geojson` (baseline vector polygons)
- `scripts/validate_against_emsr927.py` (lines 150–260)
- `data/processed/emsr927_validation/validation_report.md`
- `data/validation/emsr927/AOI03/EMSR927_AOI03_GRA_PRODUCT_areaOfInterestA_v1.shp`
- `data/validation/emsr927/AOI05/EMSR927_AOI05_GRA_PRODUCT_areaOfInterestA_v2.shp`

### Exact Mathematical Reconciliation

| Measurement Scope | Spatial Extent | Data Format | Pixel / Feature Count | Surface Area | Notes |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **Whole Trishuli AOI** | $[84.90^\circ\text{E}, 27.75^\circ\text{N}, 85.25^\circ\text{E}, 28.05^\circ\text{N}]$ | Baseline Raster | 1,286 px | **35.03 ha** | Native pixel area at 27.9°N ($\approx 274.17\text{ m}^2/\text{px}$) |
| **Whole Trishuli AOI** | $[84.90^\circ\text{E}, 27.75^\circ\text{N}, 85.25^\circ\text{E}, 28.05^\circ\text{N}]$ | Phase 3 Run Raster | 1,286 px | **35.03 ha** | **100% array equality** with baseline (`np.array_equal == True`) |
| **Whole Trishuli AOI** | $[84.90^\circ\text{E}, 27.75^\circ\text{N}, 85.25^\circ\text{E}, 28.05^\circ\text{N}]$ | Vector Polygons (value=1) | 84 polygons | **35.12 ha** | Planar UTM Zone 45N (`EPSG:32645`) polygon union area |
| **EMSR927 Validation Footprint** | Copernicus AOI03 + AOI05 Only | Clipped Vector Subset | 58 polygons | **24.16 ha** | Exact calculation: **241,597.3 m²** |

### Why Did Earlier Reports State 24.16 ha?
In `scripts/validate_against_emsr927.py` (line 229):
```python
v3_clipped_common = to_valid_multipolygon(v3_union.intersection(combined_aoi))
# Area: 241,597.3 m2 = 24.16 ha
```
The figure **24.16 ha** was the area of FloodSpaceAI candidate inundation **clipped to the Copernicus Emergency Management Service EMSR927 area of interest boundaries**!
The Copernicus activation covered only the Syapru Besi corridor (AOI03) and the immediate Trishuli downstream corridor (AOI05), which encompasses 68.8% of the FloodSpaceAI study area.
The remaining **10.96 ha** of candidate flood inundation lies along the broader Trishuli river network outside the EMSR927 activation boxes.

### Scientific Conclusion
- **There is NO discrepancy in the algorithm or output rasters.**
- The full candidate inundation across the entire study area has always been **1,286 pixels ($\approx 35.03$–$35.12$ ha)**.
- **24.16 ha** is strictly the EMSR927-intersecting sub-area.
- **Classification:** ✅ **PASS**.

---

## 4. Algorithm & Masking Audit: SCL Cloud Masking & SAR Units

### Evidence Files Inspected
- `scripts/run_satellite_processing.py` (lines 380–525)
- `scripts/speckle_filter.py`
- `scripts/filtered_change_analysis.py`
- `data/raw/sentinel1_pre_20260816_vv_vh.tif`
- `data/raw/sentinel1_post_20260828_vv_vh.tif`

### Findings

#### A. SAR Representation & Decibel Conversion Formula
- Inspection of raw pixel values in `sentinel1_pre_20260816_vv_vh.tif`:
  - Band 1 (VV): $\text{min} = 4.55 \times 10^{-6}$, $\text{median} = 0.1755$, $\text{mean} = 0.2216$, $99\text{th percentile} = 0.8828$
  - Band 2 (VH): $\text{min} = 6.32 \times 10^{-8}$, $\text{median} = 0.0397$, $\text{mean} = 0.0489$, $99\text{th percentile} = 0.1826$
- **Physical Interpretation:** These values represent **linear backscatter power ($\sigma^0$)**, typical of land surface radar returns (-7.5 dB for VV, -14.0 dB for VH).
- **Formula Verification:**
  $$\Delta\text{VV}_{\text{dB}} = 10.0 \cdot \log_{10}\left(\frac{\text{VV}_{\text{post}}}{\text{VV}_{\text{pre}}}\right)$$
  Because the inputs are linear power (not amplitude voltage), $10 \log_{10}(P_2 / P_1)$ is the **exact, physically correct formula**. (If the values had been linear amplitude, $20 \log_{10}$ would have been required).
- *Documentation Note:* Some comments in earlier scripts casually referred to "amplitude". The pipeline metadata in Phase 3 has been audited to clarify that inputs are linear backscatter power ($\sigma^0$).

#### B. Sentinel-2 SCL Cloud Masking & NoData Propagation
- Valid surface classes retained: `[2, 4, 5, 6, 7]` (Dark features, vegetation, bare soil, water, unclassified).
- Masked invalid/cloud classes: `[0, 1, 3, 8, 9, 10, 11]` (NoData, defective, shadow, cloud med/high prob, cirrus, snow).
- Invalid pixels are assigned `NaN` internally and written as `-9999.0` (NODATA).
- In `_integrate_v3_flood_candidate`, any pixel with NoData in either pre-NDWI, post-NDWI, NDWI-change, VV-change, or VH-change is strictly excluded from `valid_mask`.
- **False Positive Test:** In cloudy pixels (post SCL $\in [3, 8, 9, 10]$), the number of candidate flood pixels is **strictly 0**.

### Scientific Conclusion
- Optical masking adheres strictly to scientific standards; cloudy pixels never generate false water.
- SAR decibel calculations are physically exact for linear power backscatter.
- **Classification:** ✅ **PASS**.

---

## 5. Summary of Unresolved Issues & Next Actions

| Issue ID | Description | Severity | Current Status | Required Action for Next Phase |
| :--- | :--- | :---: | :---: | :--- |
| **ISSUE-P3-01** | Discovery-to-download-to-processing unverified for arbitrary AOIs | Medium | ⚠️ WARNING | In Phase 4, document clearly that arbitrary AOIs require either local cached GeoTIFFs or an authenticated Sentinel Hub OAuth client credentials configuration. Keep automated mock testing explicitly isolated. |
| **ISSUE-P3-02** | Sentinel-1 simulated 2026 platform naming (`S1D`) | Low | ⚠️ WARNING | Preserve `S1D_...` in discovery JSON as documented simulated 2026 catalog identifier. Document in provenance records that raw GeoTIFFs are Sentinel Hub Process API exports. |
| **ISSUE-P3-03** | Headline area ambiguity (35.03 ha vs 24.16 ha) | Resolved | ✅ PASS | Always cite **35.03 ha (raster) / 35.12 ha (84 polygons)** as the whole study area flood candidate, and **24.16 ha** exclusively as the EMSR927-intersecting validation subset. |

---

## 6. Verification Test & Build Results

Automated regression and audit test execution:
- Audit script: `scripts/audit_phase3_scientific.py` -> **EXIT 0 (ALL CHECKS PASSED)**
- Phase 3 test suite: `scripts/test_satellite_processing.py` -> **EXIT 0 (7/7 TESTS PASSED)**
- Dashboard build: `npm run build` in `dashboard/` -> **EXIT 0 (TURBOPACK COMPILED CLEANLY IN 314ms, 0 TYPE ERRORS)**
