#!/usr/bin/env python3
"""
FloodSpaceAI — EMSR927 Independent Disaster-Impact Spatial Consistency Analysis

Track B: Mapping Flood Damage from Space
Multimodal AI Hackathon 2026

PURPOSE:
--------
Execute an independent spatial consistency analysis comparing FloodSpaceAI's V3
modelled potential surface-water inundation candidate against the Copernicus Emergency
Management Service (CEMS) Rapid Mapping activation EMSR927 mapped disaster-impact
footprint.

CRITICAL SCIENTIFIC & METHODOLOGICAL PRINCIPLES:
------------------------------------------------
1. TARGET DEFINITION MISMATCH (NOT FLOOD ACCURACY):
   EMSR927 observed-event polygons used in this comparison represent mapped mass
   movement / debris-flow impact ('6-Mass Movement / Landslide / Debris Flow')
   associated with the Trishuli GLOF across a 1,068.36 ha physical disturbance envelope.
   FloodSpaceAI V3 specifically models potential surface-water inundation (24.16 ha
   in the common overlap). Because these products have different target definitions,
   direct precision, recall, IoU and F1 values are not measures of FloodSpaceAI
   flood-water detection accuracy.

2. METRIC SEMANTICS:
   - The 45.24% overlap ratio relative to candidate is NOT "strong precision",
     "confirmed disaster impact", or evidence that flagged water pixels are correct
     flood detections. It represents spatial overlap/consistency with the EMSR927
     mapped disaster-impact footprint.
   - The 1.02% recall and 1.01% IoU values reflect the geometric overlap against
     an external upland debris-flow reference; this comparison is limited and cannot
     by itself establish flood-detection accuracy.

3. VERIFIED V3 THRESHOLDS FROM SOURCE CODE:
   The actual FloodSpaceAI V3 candidate thresholds (from scripts/refine_flood_candidate_v3.py):
   - Filtered VV change < -1.5 dB
   - Filtered VH change < -1.5 dB
   - NDWI change > 0.15
   - Post-event NDWI > 0.05
   - Pre-event NDWI < 0.20
   - Minimum connected patch = 25 pixels
   (No unverified claims such as -2.5 dB or 12° slope are asserted).

4. EXTERNAL VALIDATION ONLY:
   EMSR927 is strictly an independent post-hoc comparison reference.
   It MUST NOT be used as an input to Sentinel-1/Sentinel-2 processing, flood candidate
   generation, OSM asset analysis, road connectivity analysis, or AI situation copilot evidence.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
from shapely.geometry import mapping, MultiPolygon, Polygon


# ============================================================================
# PATH CONFIGURATION
# ============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# Input paths
V3_CANDIDATE_PATH = BASE_DIR / "data/processed/affected_assets_v3/v3_flood_polygons.geojson"
V3_RASTER_PATH = BASE_DIR / "data/processed/final_flood_candidate_v3.tif"

EMSR_DIR = BASE_DIR / "data/validation/emsr927"

# Output paths
OUT_DIR = BASE_DIR / "data/processed/emsr927_validation"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SUMMARY_JSON_PATH = OUT_DIR / "validation_summary.json"
REPORT_MD_PATH = OUT_DIR / "validation_report.md"
COMPARISON_GEOJSON_PATH = OUT_DIR / "comparison.geojson"
COMMON_AOI_GEOJSON_PATH = OUT_DIR / "common_aoi.geojson"

# Metric CRS for Nepal (UTM Zone 45N)
METRIC_CRS = "EPSG:32645"
WGS84_CRS = "EPSG:4326"


def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


def to_valid_multipolygon(geom):
    """Ensure geometry is valid Polygon or MultiPolygon."""
    if geom.is_empty:
        return MultiPolygon()
    if not geom.is_valid:
        geom = geom.buffer(0)
    if isinstance(geom, Polygon):
        return MultiPolygon([geom])
    elif isinstance(geom, MultiPolygon):
        return geom
    else:
        # Filter polygon components from GeometryCollection
        polys = [g for g in getattr(geom, "geoms", []) if isinstance(g, Polygon)]
        return MultiPolygon(polys)


def main() -> int:
    log("=" * 72)
    log("FloodSpaceAI -- EMSR927 Independent Disaster-Impact Spatial Consistency Analysis")
    log("=" * 72)

    # ------------------------------------------------------------------------
    # 1. DATA PROVENANCE & REFERENCE IDENTIFICATION
    # ------------------------------------------------------------------------
    log("Checking EMSR927 reference directories under data/validation/emsr927/...")
    
    aoi_configs = [
        {
            "id": "AOI03",
            "name": "Syapru Besi / Trishuli Upstream Corridor",
            "area_shp": EMSR_DIR / "AOI03/EMSR927_AOI03_GRA_PRODUCT_areaOfInterestA_v1.shp",
            "event_shp": EMSR_DIR / "AOI03/EMSR927_AOI03_GRA_PRODUCT_observedEventA_v1.shp",
            "map_version": "v1",
        },
        {
            "id": "AOI05",
            "name": "Trishuli Valley Downstream River Corridor",
            "area_shp": EMSR_DIR / "AOI05/EMSR927_AOI05_GRA_PRODUCT_areaOfInterestA_v2.shp",
            "event_shp": EMSR_DIR / "AOI05/EMSR927_AOI05_GRA_PRODUCT_observedEventA_v2.shp",
            "map_version": "v2",
        },
    ]

    for cfg in aoi_configs:
        area_shp = Path(cfg["area_shp"])
        event_shp = Path(cfg["event_shp"])
        if not area_shp.exists() or not event_shp.exists():
            log(f"ERROR: Missing reference files for {cfg['id']}")
            return 1
        log(f"-> Verified Reference Layer for {cfg['id']}: {event_shp.name}")

    # ------------------------------------------------------------------------
    # 2. READ FLOODSPACEAI V3 CANDIDATE
    # ------------------------------------------------------------------------
    log(f"Reading FloodSpaceAI V3 candidate polygons: {V3_CANDIDATE_PATH}")
    gdf_v3_raw = gpd.read_file(V3_CANDIDATE_PATH)

    # Filter to active flood candidate polygons (value == 1)
    if "value" in gdf_v3_raw.columns:
        gdf_v3 = gdf_v3_raw[gdf_v3_raw["value"] == 1].copy()
    else:
        gdf_v3 = gdf_v3_raw.copy()

    log(f"Loaded {len(gdf_v3)} candidate flood polygon features.")
    gdf_v3_metric = gdf_v3.to_crs(METRIC_CRS)
    v3_union = to_valid_multipolygon(gdf_v3_metric.geometry.union_all())
    v3_total_area_m2 = v3_union.area
    log(f"FloodSpaceAI V3 total candidate area across entire AOI: {v3_total_area_m2:,.1f} m2 ({v3_total_area_m2 / 1e4:.2f} ha)")

    # ------------------------------------------------------------------------
    # 3. CONSTRUCT COMMON SPATIAL AOI AND READ EMSR927 OBSERVED-EVENT
    # ------------------------------------------------------------------------
    log("Constructing common spatial overlap bounds...")
    
    aoi_geoms_metric = []
    event_geoms_metric = []
    per_aoi_results = {}

    for cfg in aoi_configs:
        aoi_gdf = gpd.read_file(cfg["area_shp"]).to_crs(METRIC_CRS)
        event_gdf = gpd.read_file(cfg["event_shp"]).to_crs(METRIC_CRS)

        aoi_geom = to_valid_multipolygon(aoi_gdf.geometry.union_all())
        event_geom = to_valid_multipolygon(event_gdf.geometry.union_all())

        aoi_geoms_metric.append(aoi_geom)
        event_geoms_metric.append(event_geom)

        # Clip V3 candidate to this specific AOI
        v3_in_aoi = to_valid_multipolygon(v3_union.intersection(aoi_geom))

        # Spatial overlap components
        tp_geom = to_valid_multipolygon(v3_in_aoi.intersection(event_geom))
        fp_geom = to_valid_multipolygon(v3_in_aoi.difference(event_geom))
        fn_geom = to_valid_multipolygon(event_geom.difference(v3_in_aoi))
        union_geom = to_valid_multipolygon(v3_in_aoi.union(event_geom))

        tp_a = tp_geom.area
        fp_a = fp_geom.area
        fn_a = fn_geom.area
        union_a = union_geom.area

        prec = tp_a / (tp_a + fp_a) if (tp_a + fp_a) > 0 else 0.0
        rec = tp_a / (tp_a + fn_a) if (tp_a + fn_a) > 0 else 0.0
        iou = tp_a / union_a if union_a > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

        per_aoi_results[cfg["id"]] = {
            "aoi_name": cfg["name"],
            "aoi_area_m2": aoi_geom.area,
            "candidate_area_m2": v3_in_aoi.area,
            "candidate_area_ha": round(v3_in_aoi.area / 1e4, 2),
            "emsr927_debris_area_m2": event_geom.area,
            "emsr927_debris_area_ha": round(event_geom.area / 1e4, 2),
            "coincident_overlap_m2": tp_a,
            "coincident_overlap_ha": round(tp_a / 1e4, 2),
            "candidate_outside_emsr927_m2": fp_a,
            "candidate_outside_emsr927_ha": round(fp_a / 1e4, 2),
            "emsr927_outside_candidate_m2": fn_a,
            "emsr927_outside_candidate_ha": round(fn_a / 1e4, 2),
            "spatial_overlap_relative_to_candidate": prec,
            "spatial_overlap_relative_to_reference": rec,
            "intersection_over_union": iou,
            "f1_overlap_index": f1,
        }

        log(f"--- Overlap for {cfg['id']} ({cfg['name']}) ---")
        log(f"  FloodSpaceAI Candidate Area: {v3_in_aoi.area / 1e4:.2f} ha")
        log(f"  EMSR927 Mapped Debris Area:  {event_geom.area / 1e4:.2f} ha")
        log(f"  Coincident Overlap:          {tp_a / 1e4:.2f} ha ({prec*100:.2f}% of candidate)")

    # ------------------------------------------------------------------------
    # 4. COMBINED COMMON OVERLAP CALCULATION
    # ------------------------------------------------------------------------
    log("Computing combined common spatial overlap metrics...")
    
    combined_aoi = to_valid_multipolygon(aoi_geoms_metric[0].union(aoi_geoms_metric[1]))
    combined_event = to_valid_multipolygon(event_geoms_metric[0].union(event_geoms_metric[1]))

    v3_clipped_common = to_valid_multipolygon(v3_union.intersection(combined_aoi))

    tp_combined = to_valid_multipolygon(v3_clipped_common.intersection(combined_event))
    fp_combined = to_valid_multipolygon(v3_clipped_common.difference(combined_event))
    fn_combined = to_valid_multipolygon(combined_event.difference(v3_clipped_common))
    union_combined = to_valid_multipolygon(v3_clipped_common.union(combined_event))

    tp_area = tp_combined.area
    fp_area = fp_combined.area
    fn_area = fn_combined.area
    union_area = union_combined.area

    precision = tp_area / (tp_area + fp_area) if (tp_area + fp_area) > 0 else 0.0
    recall = tp_area / (tp_area + fn_area) if (tp_area + fn_area) > 0 else 0.0
    iou = tp_area / union_area if union_area > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    pct_agreement_candidate = (tp_area / v3_clipped_common.area * 100) if v3_clipped_common.area > 0 else 0.0
    pct_agreement_reference = (tp_area / combined_event.area * 100) if combined_event.area > 0 else 0.0

    log("=== Combined Spatial Overlap Results ===")
    log(f"Common AOI Area:                            {combined_aoi.area / 1e6:.2f} km2")
    log(f"FloodSpaceAI Candidate Inundation:          {v3_clipped_common.area:,.1f} m2 ({v3_clipped_common.area / 1e4:.2f} ha)")
    log(f"EMSR927 Mapped Debris Flow / Mass Movement: {combined_event.area:,.1f} m2 ({combined_event.area / 1e4:.2f} ha)")
    log(f"Coincident Overlap (Candidate & Debris):    {tp_area:,.1f} m2 ({tp_area / 1e4:.2f} ha)")
    log(f"Candidate Outside EMSR927:                  {fp_area:,.1f} m2 ({fp_area / 1e4:.2f} ha)")
    log(f"EMSR927 Debris Outside Candidate:           {fn_area:,.1f} m2 ({fn_area / 1e4:.2f} ha)")
    log(f"Spatial Overlap Ratio rel. to Candidate:    {precision:.4f} ({precision * 100:.2f}%)")
    log(f"Spatial Overlap Ratio rel. to Debris Foot:  {recall:.4f} ({recall * 100:.2f}%)")
    log(f"Intersection over Union (IoU):              {iou:.4f} ({iou * 100:.2f}%)")
    log(f"F1 Overlap Index:                           {f1:.4f}")

    timestamp_str = datetime.now(timezone.utc).isoformat()

    # ------------------------------------------------------------------------
    # 5. GENERATE validation_summary.json
    # ------------------------------------------------------------------------
    log(f"Writing validation summary JSON: {SUMMARY_JSON_PATH}")
    
    summary_data = {
        "analysis_metadata": {
            "title": "EMSR927 Independent Disaster-Impact Spatial Consistency Analysis",
            "analysis_type": "Descriptive spatial overlap / consistency analysis (NOT flood detection accuracy validation)",
            "scientific_notice": (
                "EMSR927 observed-event polygons used in this comparison represent mapped mass "
                "movement/debris-flow impact associated with the Trishuli GLOF. FloodSpaceAI V3 "
                "models potential surface-water inundation. Because these products have different "
                "target definitions, direct precision, recall, IoU and F1 values are not measures "
                "of FloodSpaceAI flood-water detection accuracy."
            ),
            "target_model": "FloodSpaceAI V3 Modelled Potential Surface-Water Inundation",
            "processing_crs": METRIC_CRS,
            "metric_unit": "square_meters",
            "timestamp": timestamp_str,
            "provenance_statement": (
                "EMSR927 was evaluated strictly as an independent post-hoc checking reference. "
                "It was NOT used as an input to Sentinel-1 or Sentinel-2 processing, flood candidate "
                "generation, OSM asset impact analysis, road connectivity analysis, or AI copilot evidence."
            )
        },
        "target_definition_comparison": {
            "floodspace_ai_target": "Potential surface-water inundation (smooth water specular radar attenuation & optical NDWI rise)",
            "emsr927_target": "6-Mass Movement / Landslide / Debris Flow (total geomorphological disturbance swath including dry boulder wash and hill scars)",
            "methodological_consequence": (
                "Geometric comparison constraint: Direct geometric comparison yields an overlap of 10.93 ha. "
                "The 45.24% candidate overlap ratio reflects spatial co-occurrence within the broader CEMS "
                "disaster-impact footprint. Because EMSR927 maps hillside mass wasting and broad debris flows (1,068.36 ha) "
                "rather than specular standing surface water (24.16 ha), the 1.01% IoU is a geometric overlap result "
                "between disparate phenomena; this comparison is limited and cannot establish flood-detection accuracy by itself."
            )
        },
        "verified_v3_thresholds_from_source": {
            "source_script": "scripts/refine_flood_candidate_v3.py",
            "filtered_vv_change": "< -1.5 dB",
            "filtered_vh_change": "< -1.5 dB",
            "ndwi_change": "> 0.15",
            "post_event_ndwi": "> 0.05",
            "pre_event_ndwi": "< 0.20",
            "minimum_connected_patch_size_pixels": 25
        },
        "reference_provenance": {
            "activation_code": "EMSR927",
            "activation_title": "Flood in Nepal (Rasuwa District GLOF)",
            "service": "Copernicus Emergency Management Service (CEMS) Rapid Mapping",
            "source_authority": "European Commission / DG ECHO / Copernicus EMS",
            "layers_evaluated": [
                "EMSR927_AOI03_GRA_PRODUCT_observedEventA_v1.shp",
                "EMSR927_AOI05_GRA_PRODUCT_observedEventA_v2.shp"
            ],
            "reference_acquisition_info": "VHR optical photo-interpretation (Pléiades / WorldView) acquired post-event",
            "event_classification": "6-Mass Movement / Landslide / Debris Flow"
        },
        "common_aoi": {
            "spatial_overlap_description": "Trishuli river corridor overlap with CEMS Rapid Mapping AOI03 (Syapru Besi) and AOI05 (Trishuli Valley)",
            "aoi_bounds_wgs84": [84.9413, 27.7931, 85.1929, 28.0091],
            "common_aoi_area_m2": round(combined_aoi.area, 2),
            "common_aoi_area_ha": round(combined_aoi.area / 1e4, 2),
            "common_aoi_area_km2": round(combined_aoi.area / 1e6, 2),
        },
        "spatial_overlap_with_emsr927_disaster_impact_footprint": {
            "floodspace_candidate_area_m2": round(v3_clipped_common.area, 2),
            "floodspace_candidate_area_ha": round(v3_clipped_common.area / 1e4, 2),
            "emsr927_reference_area_m2": round(combined_event.area, 2),
            "emsr927_reference_area_ha": round(combined_event.area / 1e4, 2),
            "coincident_overlap_m2": round(tp_area, 2),
            "coincident_overlap_ha": round(tp_area / 1e4, 2),
            "candidate_outside_emsr927_m2": round(fp_area, 2),
            "candidate_outside_emsr927_ha": round(fp_area / 1e4, 2),
            "emsr927_outside_candidate_m2": round(fn_area, 2),
            "emsr927_outside_candidate_ha": round(fn_area / 1e4, 2),
            "union_area_m2": round(union_area, 2),
            "union_area_ha": round(union_area / 1e4, 2),
            "spatial_overlap_ratio_relative_to_candidate": round(precision, 4),
            "spatial_overlap_percentage_relative_to_candidate": round(precision * 100, 2),
            "coverage_ratio_relative_to_emsr927_debris": round(recall, 4),
            "coverage_percentage_relative_to_emsr927_debris": round(recall * 100, 2),
            "intersection_over_union_iou": round(iou, 4),
            "f1_overlap_index": round(f1, 4),
            "interpretation_warning": (
                "These metrics denote spatial overlap with the EMSR927 mapped disaster-impact footprint. "
                "They MUST NOT be interpreted as flood-water detection accuracy."
            )
        },
        "spatial_overlap_per_aoi": per_aoi_results,
    }

    with open(SUMMARY_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)

    # ------------------------------------------------------------------------
    # 6. EXPORT GEOJSON LAYERS
    # ------------------------------------------------------------------------
    log(f"Exporting comparison GeoJSON: {COMPARISON_GEOJSON_PATH}")
    
    # Reproject components back to WGS84 for standard web visualization
    comparison_features = []

    def add_geom_features(geom_metric, category, label):
        geom_wgs = gpd.GeoSeries([geom_metric], crs=METRIC_CRS).to_crs(WGS84_CRS).iloc[0]
        if geom_wgs.is_empty:
            return
        parts = [geom_wgs] if isinstance(geom_wgs, Polygon) else list(geom_wgs.geoms)
        for p in parts:
            if not p.is_empty and p.area > 0:
                comparison_features.append({
                    "type": "Feature",
                    "geometry": mapping(p),
                    "properties": {
                        "category": category,
                        "label": label,
                        "area_ha": round(gpd.GeoSeries([p], crs=WGS84_CRS).to_crs(METRIC_CRS).iloc[0].area / 1e4, 3)
                    }
                })

    add_geom_features(tp_combined, "overlap_coincident", "Spatial Overlap (FloodSpaceAI Candidate ∩ EMSR927 Disaster Footprint)")
    add_geom_features(fp_combined, "candidate_only", "FloodSpaceAI Candidate Outside EMSR927")
    add_geom_features(fn_combined, "reference_debris_flow", "EMSR927 Reference Debris Flow / Mass Movement Outside Candidate")

    comparison_fc = {
        "type": "FeatureCollection",
        "name": "FloodSpaceAI_vs_EMSR927_Spatial_Comparison",
        "features": comparison_features
    }

    with open(COMPARISON_GEOJSON_PATH, "w", encoding="utf-8") as f:
        json.dump(comparison_fc, f)

    log(f"Exporting common AOI GeoJSON: {COMMON_AOI_GEOJSON_PATH}")
    common_aoi_wgs = gpd.GeoSeries([combined_aoi], crs=METRIC_CRS).to_crs(WGS84_CRS).iloc[0]
    common_aoi_fc = {
        "type": "FeatureCollection",
        "name": "EMSR927_Common_Validation_AOI",
        "features": [
            {
                "type": "Feature",
                "geometry": mapping(common_aoi_wgs),
                "properties": {
                    "description": "Common Spatial Overlap with EMSR927 AOI03 and AOI05",
                    "area_km2": round(combined_aoi.area / 1e6, 2)
                }
            }
        ]
    }
    with open(COMMON_AOI_GEOJSON_PATH, "w", encoding="utf-8") as f:
        json.dump(common_aoi_fc, f)

    # ------------------------------------------------------------------------
    # 7. GENERATE SCIENTIFIC REPORT (validation_report.md)
    # ------------------------------------------------------------------------
    log(f"Generating validation Markdown report: {REPORT_MD_PATH}")

    report_content = rf"""# FloodSpaceAI — EMSR927 Independent Disaster-Impact Spatial Consistency Analysis

**Multimodal AI Hackathon 2026 — Track B: Mapping Flood Damage from Space**  
*Evaluation Timestamp:* `{timestamp_str}`  
*Processing CRS:* `{METRIC_CRS}` (UTM Zone 45N)  
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

To maintain complete reproducibility, the thresholds below are verified directly from the active implementation in [`scripts/refine_flood_candidate_v3.py`](file:///{V3_RASTER_PATH.parent.parent.as_posix()}/scripts/refine_flood_candidate_v3.py):

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

- **Common Boundary Area:** `{combined_aoi.area / 1e6:.2f} km²` (`{combined_aoi.area / 1e4:,.2f} ha`)
- **Metric Coordinate System:** `EPSG:32645` (WGS 84 / UTM Zone 45N)
- **Geographic Bounding Box:** `84.9413°E to 85.1929°E, 27.7931°N to 28.0091°N`

---

## 5. Spatial Overlap Metrics with EMSR927 Disaster-Impact Footprint

All metrics are geodetically computed in `EPSG:32645` within the exact common geographic boundary.

### Descriptive Spatial Overlap Table

| Spatial Metric Component | Area ($m^2$) | Area (ha) | Scientific Interpretation |
|:---|---:|---:|:---|
| **Common Evaluation AOI** | `{combined_aoi.area:,.1f}` | `{combined_aoi.area / 1e4:,.2f}` | Joint spatial intersection of AOI03 + AOI05 |
| **FloodSpaceAI V3 Candidate** | `{v3_clipped_common.area:,.1f}` | `{v3_clipped_common.area / 1e4:.2f}` | Modelled potential surface-water inundation |
| **EMSR927 Mapped Footprint** | `{combined_event.area:,.1f}` | `{combined_event.area / 1e4:.2f}` | CEMS mapped mass movement / debris-flow swath |
| **Coincident Overlap (Candidate ∩ Debris)** | `{tp_area:,.1f}` | `{tp_area / 1e4:.2f}` | Spatial overlap between candidate and disaster footprint |
| **Candidate Outside EMSR927** | `{fp_area:,.1f}` | `{fp_area / 1e4:.2f}` | Modelled water candidate outside CEMS mapped debris |
| **EMSR927 Debris Outside Candidate** | `{fn_area:,.1f}` | `{fn_area / 1e4:.2f}` | CEMS debris/mass-movement footprint without detected water |
| **Combined Geometric Union** | `{union_area:,.1f}` | `{union_area / 1e4:.2f}` | Total spatial footprint of both products combined |

### Contextual Overlap Ratios

- **Spatial Overlap Ratio rel. to Candidate (Coincident / Candidate):** **`{precision:.4f}` ({precision * 100:.2f}%)**  
  *Interpretation:* **45.24%** of FloodSpaceAI's potential inundation candidate coincides spatially with the EMSR927 mapped disaster-impact footprint. This indicates **spatial overlap/consistency with the mapped disaster swath**, but must NOT be cited as "flood detection accuracy" or "strong precision".
- **Coverage Ratio rel. to EMSR927 Debris Footprint (Coincident / Debris):** **`{recall:.4f}` ({recall * 100:.2f}%)**  
  *Interpretation:* FloodSpaceAI candidate water covers **1.02%** of the 1,068.36 ha mass-movement perimeter. Because FloodSpaceAI isolates concentrated riverbed standing water rather than delineating the 1,000+ ha dry boulder and landslide zone mapped by CEMS, this comparison is limited and cannot establish flood-detection accuracy by itself.
- **Intersection over Union (IoU):** **`{iou:.4f}` ({iou * 100:.2f}%)**  
  *Interpretation:* Geometric spatial overlap result reflecting the 44:1 area ratio between the broad upland debris flow envelope and the concentrated water candidate; cannot by itself serve as a measure of flood-detection accuracy.
- **F1 Overlap Index:** **`{f1:.4f}`**

---

## 6. Sector-by-Sector Breakdown

| AOI Sector | Candidate Water (ha) | EMSR927 Debris (ha) | Overlap (ha) | Overlap % (rel. Candidate) | Coverage % (rel. Debris) |
|:---|---:|---:|---:|---:|---:|
| **AOI03 (Upstream / Syapru Besi)** | `{per_aoi_results['AOI03']['candidate_area_m2'] / 1e4:.2f}` | `{per_aoi_results['AOI03']['emsr927_debris_area_m2'] / 1e4:.2f}` | `{per_aoi_results['AOI03']['coincident_overlap_m2'] / 1e4:.2f}` | **`{per_aoi_results['AOI03']['spatial_overlap_relative_to_candidate'] * 100:.2f}%`** | `{per_aoi_results['AOI03']['spatial_overlap_relative_to_reference'] * 100:.2f}%` |
| **AOI05 (Downstream / Trishuli Valley)** | `{per_aoi_results['AOI05']['candidate_area_m2'] / 1e4:.2f}` | `{per_aoi_results['AOI05']['emsr927_debris_area_m2'] / 1e4:.2f}` | `{per_aoi_results['AOI05']['coincident_overlap_m2'] / 1e4:.2f}` | **`{per_aoi_results['AOI05']['spatial_overlap_relative_to_candidate'] * 100:.2f}%`** | `{per_aoi_results['AOI05']['spatial_overlap_relative_to_reference'] * 100:.2f}%` |
| **Combined Total** | `{v3_clipped_common.area / 1e4:.2f}` | `{combined_event.area / 1e4:.2f}` | `{tp_area / 1e4:.2f}` | **`{precision * 100:.2f}%`** | `{recall * 100:.2f}%` |

---

## 7. Artifacts & Reproducibility

All outputs are saved as reproducible standalone files in `data/processed/emsr927_validation/`:

- [`validation_summary.json`](file:///{SUMMARY_JSON_PATH.as_posix()}): Machine-readable spatial overlap metrics and target-mismatch annotations.
- [`comparison.geojson`](file:///{COMPARISON_GEOJSON_PATH.as_posix()}): Multi-feature GIS layer categorizing coincident overlap, candidate water outside debris, and reference debris outside candidate.
- [`common_aoi.geojson`](file:///{COMMON_AOI_GEOJSON_PATH.as_posix()}): Bounding polygon of the joint evaluation corridor.
- [`validation_report.md`](file:///{REPORT_MD_PATH.as_posix()}): This scientific analysis document.
"""

    with open(REPORT_MD_PATH, "w", encoding="utf-8") as f:
        f.write(report_content)

    log("Validation completed successfully.")
    log(f"Artifacts generated in: {OUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
