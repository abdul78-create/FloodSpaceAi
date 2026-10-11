# FloodSpaceAI — EMSR927 Independent Disaster-Impact Spatial Consistency Analysis

**Multimodal AI Hackathon 2026 — Track B: Mapping Flood Damage from Space**  
*Evaluation Timestamp:* `2026-10-09T11:07:06.164714+00:00`  
*Processing CRS:* `EPSG:32645` (UTM Zone 45N)  
*Status:* Scientifically Honest Contextual Validation (Not Flood Accuracy Score)

---

## 1. Executive Scientific Notice & Target Definition Boundary

> **CRITICAL SCIENTIFIC PRINCIPLE:**  
> **EMSR927 observed-event polygons used in this comparison represent mapped mass movement/debris-flow impact associated with the Trishuli GLOF. FloodSpaceAI V3 models potential surface-water inundation. Because these products have different target definitions, direct precision, recall, IoU and F1 values are not measures of FloodSpaceAI flood-water detection accuracy.**

### Strict Grounding & Isolation Constraints
1. **Validation Only:** Copernicus EMS Rapid Mapping activation `EMSR927` was evaluated **strictly as an independent post-hoc comparison reference**.
2. **Strict Pipeline Isolation:** It was **NOT** used as an input to:
   - Sentinel-1 SAR pre-processing or change detection
   - Sentinel-2 optical pre-processing or NDWI change calculation
   - Flood candidate generation (V1, V2, or V3)
   - OpenStreetMap asset impact analysis (buildings, roads, bridges)
   - Road network connectivity analysis (V4 isolation modelling)
   - Situation report evidence (`situation_report_evidence.json` remains untouched)
   - AI situation copilot groundings
3. **Modelled Candidate Notice:** The FloodSpaceAI V3 product represents a **modelled potential surface-water inundation candidate**, not ground-truth physical flood extent.

---

## 2. Why EMSR927 Cannot Serve as Direct Flood-Water Ground Truth

A direct numerical comparison between EMSR927 and FloodSpaceAI must be interpreted with complete scientific rigor. The two products cannot be treated as measuring identical physical phenomena:

1. **Emergency Mapping Scope:**  
   EMSR927 is a rapid emergency mapping product generated under extreme disaster response timelines to guide civil protection and humanitarian logistics, rather than a hydrologic steady-state water mask.

2. **Observed Event Classification (`6-Mass Movement / Landslide / Debris Flow`):**  
   The Copernicus CEMS cartographers classified `observedEventA` as *Mass Movement / Landslide / Debris Flow*. The mapped polygons delineate the **total geomorphological disturbance envelope** (1,068.36 ha in the common overlap)—including hillside boulder washes, stripped soil terraces, scoured canyon flanks, and rocky sediment deposits.

3. **Target Phenomenon Divergence:**  
   FloodSpaceAI V3 specifically isolates **potential surface-water inundation** (24.16 ha in the common overlap). Water detection requires active surface water that creates specular backscatter decay in SAR and positive optical water index anomalies. Dry gravel terraces and stripped bedrock flanks within the debris-flow path do not exhibit standing water characteristics.

4. **Sensor Resolution & Photo-Interpretation:**  
   EMSR927 delineations were derived by manual visual photo-interpretation from commercial Very High Resolution (VHR) optical platforms (Pléiades / WorldView) at sub-meter to 2-meter ground sampling distance. FloodSpaceAI operates autonomously from open public satellite constellations (Sentinel-1 SAR at 10m, Sentinel-2 at 10m/20m resampled).

5. **Spectral & Physical Modality Differences:**  
   Radar backscatter responds to surface roughness and dielectric permittivity, whereas high-resolution optical photo-interpretation traces visible texture changes, scouring scars, and sediment deposits.

6. **Acquisition Timing & Cloud Dynamics:**  
   The Himalayan GLOF event unfolded along an extremely steep canyon with rapid hydrologic surging. Optical commercial passes and Sentinel radar passes occurred at different times during the event hydrograph, under severe monsoon cloud cover that obscured optical sensors in steep valley sections.

---

## 3. Verified FloodSpaceAI V3 Methodology & Thresholds

To maintain complete reproducibility, the thresholds below are verified directly from the active implementation in [`scripts/refine_flood_candidate_v3.py`](file:///C:/Users/Abdul/Desktop/FloodSpaceAI/data/scripts/refine_flood_candidate_v3.py):

| Criterion | Source Threshold | Physical Rationale |
|:---|:---|:---|
| **Filtered VV Change** | `vv < -1.5 dB` | Detects specular backscatter loss over newly smoothed water surfaces |
| **Filtered VH Change** | `vh < -1.5 dB` | Cross-polarization confirmation of volume scatter reduction |
| **NDWI Change** | `ndwi_change > 0.15` | Positive shift in Normalized Difference Water Index (Green - NIR) / (Green + NIR) |
| **Post-Event Water Index** | `post_ndwi > 0.05` | Confirms post-event pixel matches open-water spectral envelope |
| **Pre-Event Non-Water Index** | `pre_ndwi < 0.20` | Eliminates baseline perennial river channel and pre-existing lakes |
| **Spatial Clutter Filter** | `sizes >= 25 pixels` | Connected component filter (8-connectivity) eliminating isolated speckle noise |

*(Note: Earlier informal drafts referencing unverified thresholds such as -2.5 dB SAR change or slope < 12 deg were not present in the V3 processing pipeline and have been formally removed).*

---

## 4. Geographic Common AOI Definition

The Copernicus EMSR927 activation covers multiple discrete sectors. A rigorous spatial intersection identified that **two EMSR927 AOIs directly overlap** our Trishuli Valley processing boundary (`84.90–85.25°E, 27.75–28.05°N`):

1. **AOI03 (Syapru Besi / Trishuli Upstream Corridor):**  
   - Layer: `EMSR927_AOI03_GRA_PRODUCT_observedEventA_v1.shp`
   - Geographic extent: Langtang / Trishuli confluence north of Dhunche.
2. **AOI05 (Trishuli Valley Downstream River Corridor):**  
   - Layer: `EMSR927_AOI05_GRA_PRODUCT_observedEventA_v2.shp`
   - Geographic extent: Trishuli Bazaar down toward Galchhi confluence.

- **Common Boundary Area:** `44.89 km²` (`4,489.04 ha`)
- **Metric Coordinate System:** `EPSG:32645` (WGS 84 / UTM Zone 45N)
- **Geographic Bounding Box:** `84.9413°E to 85.1929°E, 27.7931°N to 28.0091°N`

---

## 5. Spatial Overlap Metrics with EMSR927 Disaster-Impact Footprint

All metrics are geodetically computed in `EPSG:32645` within the exact common geographic boundary.

### Descriptive Spatial Overlap Table

| Spatial Metric Component | Area ($m^2$) | Area (ha) | Scientific Interpretation |
|:---|---:|---:|:---|
| **Common Evaluation AOI** | `44,890,423.9` | `4,489.04` | Joint spatial intersection of AOI03 + AOI05 |
| **FloodSpaceAI V3 Candidate** | `241,597.3` | `24.16` | Modelled potential surface-water inundation |
| **EMSR927 Mapped Footprint** | `10,683,591.6` | `1068.36` | CEMS mapped mass movement / debris-flow swath |
| **Coincident Overlap (Candidate ∩ Debris)** | `109,298.6` | `10.93` | Spatial overlap between candidate and disaster footprint |
| **Candidate Outside EMSR927** | `132,298.8` | `13.23` | Modelled water candidate outside CEMS mapped debris |
| **EMSR927 Debris Outside Candidate** | `10,574,293.0` | `1057.43` | CEMS debris/mass-movement footprint without detected water |
| **Combined Geometric Union** | `10,815,890.3` | `1081.59` | Total spatial footprint of both products combined |

### Contextual Overlap Ratios

- **Spatial Overlap Ratio rel. to Candidate (Coincident / Candidate):** **`0.4524` (45.24%)**  
  *Interpretation:* **45.24%** of FloodSpaceAI's potential inundation candidate coincides spatially with the EMSR927 mapped disaster-impact footprint. This indicates **spatial overlap/consistency with the mapped disaster swath**, but must NOT be cited as "flood detection accuracy" or "strong precision".
- **Coverage Ratio rel. to EMSR927 Debris Footprint (Coincident / Debris):** **`0.0102` (1.02%)**  
  *Interpretation:* FloodSpaceAI candidate water covers **1.02%** of the 1,068.36 ha mass-movement perimeter. Because FloodSpaceAI isolates concentrated riverbed standing water rather than delineating the 1,000+ ha dry boulder and landslide zone mapped by CEMS, this comparison is limited and cannot establish flood-detection accuracy by itself.
- **Intersection over Union (IoU):** **`0.0101` (1.01%)**  
  *Interpretation:* Geometric spatial overlap result reflecting the 44:1 area ratio between the broad upland debris flow envelope and the concentrated water candidate; cannot by itself serve as a measure of flood-detection accuracy.
- **F1 Overlap Index:** **`0.0200`**

---

## 6. Sector-by-Sector Breakdown

| AOI Sector | Candidate Water (ha) | EMSR927 Debris (ha) | Overlap (ha) | Overlap % (rel. Candidate) | Coverage % (rel. Debris) |
|:---|---:|---:|---:|---:|---:|
| **AOI03 (Upstream / Syapru Besi)** | `13.56` | `589.08` | `7.34` | **`54.13%`** | `1.25%` |
| **AOI05 (Downstream / Trishuli Valley)** | `10.60` | `479.28` | `3.59` | **`33.88%`** | `0.75%` |
| **Combined Total** | `24.16` | `1068.36` | `10.93` | **`45.24%`** | `1.02%` |

---

## 7. Artifacts & Reproducibility

All outputs are saved as reproducible standalone files in `data/processed/emsr927_validation/`:

- [`validation_summary.json`](file:///C:/Users/Abdul/Desktop/FloodSpaceAI/data/processed/emsr927_validation/validation_summary.json): Machine-readable spatial overlap metrics and target-mismatch annotations.
- [`comparison.geojson`](file:///C:/Users/Abdul/Desktop/FloodSpaceAI/data/processed/emsr927_validation/comparison.geojson): Multi-feature GIS layer categorizing coincident overlap, candidate water outside debris, and reference debris outside candidate.
- [`common_aoi.geojson`](file:///C:/Users/Abdul/Desktop/FloodSpaceAI/data/processed/emsr927_validation/common_aoi.geojson): Bounding polygon of the joint evaluation corridor.
- [`validation_report.md`](file:///C:/Users/Abdul/Desktop/FloodSpaceAI/data/processed/emsr927_validation/validation_report.md): This scientific analysis document.
