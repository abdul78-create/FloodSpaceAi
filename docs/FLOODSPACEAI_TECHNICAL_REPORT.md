# FloodSpaceAI: Evidence-Grounded Multi-Sensor Satellite Hydrology and Geospatial Network Intelligence

**Track B: Mapping Flood Damage from Space — Multimodal AI Hackathon 2026**  
**Technical Paper & System Architecture Report**  
*Authors: FloodSpaceAI Technical Team*  
*Date: October 2026 | Version: 1.0.0 (Final Submission)*  

---

## Abstract

Rapid disaster response during extreme monsoon flooding requires reconciling high-resolution earth observation with ground-truth infrastructure vulnerabilities while strictly avoiding artificial intelligence hallucinations. In mountainous terrain like the Himalayas, optical satellites are routinely obscured by dense cloud cover (up to 88.9%), while synthetic aperture radar (SAR) suffers from severe terrain shadowing and foreshortening. 

**FloodSpaceAI** introduces an end-to-end, evidence-grounded hydrology and infrastructure damage intelligence platform. The system couples multi-temporal Copernicus Sentinel-1 C-band SAR backscatter change with Copernicus Sentinel-2 multispectral Scene Classification Layer (SCL) cloud masking, parameterized OpenStreetMap (OSM) pre-event network graph topology, and an evidence-grounded bilingual (English/Nepali) AI copilot governed by zero-hallucination verification schemas. 

Across 56 automated test suites, FloodSpaceAI demonstrates:
1. Automated, cryptographic STAC streaming of multi-tile Sentinel-1 and Sentinel-2 rasters with SHA-256 integrity verification;
2. Strict temporal enforcement of pre-event OSM infrastructure snapshots ($T_{\text{OSM}} < T_{\text{flood}}$);
3. Physics-based flood candidate segmentation (1,286 pixels, 35.03 ha extent on resampled grid) with 57.7% morphological noise reduction;
4. Dijkstra network graph modeling identifying 18 potentially cut-off settlements across 3,748 disrupted road edges;
5. Independent validation against Copernicus EMS Rapid Mapping activation EMSR927 (45.24% candidate footprint overlap within the 1,068.36 ha mountain debris corridor);
6. A dual-tier AI copilot that links 100% of generated numbers to schema-validated evidence records and strictly refuses unverified casualty and economic loss queries.

---

## 1. Introduction & Operational Motivation

During the August 2024–2026 monsoon events in Nepal's central river basins (e.g., Trishuli, Narayani), humanitarian commanders faced severe intelligence bottlenecks:
- **Cloud Blindness:** Optical sensors (Sentinel-2, Landsat) cannot penetrate monsoonal cloud decks.
- **Topological Invisibility:** Knowing that 35 ha of valley floor is inundated does not reveal whether critical mountain roads are cut or which hamlets are severed from medical care.
- **LLM Hallucinations:** Generative AI tools often fabricate plausible-sounding fatality figures, damage costs, and structural collapse counts, creating unacceptable operational liability.
- **Data Contamination:** Post-disaster OSM edits frequently introduce retrospective changes that pollute baseline damage assessments.

FloodSpaceAI was engineered from first principles to solve these challenges through strict provenance boundaries, reproducible physics-based algorithms, and evidence-grounded conversational intelligence.

---

## 2. Multi-Sensor Remote Sensing & Flood Extraction

```
                ┌────────────────────────────────────────────────────────┐
                │             COPERNICUS EARTH OBSERVATION               │
                └───────────────────┬────────────────┬───────────────────┘
                                    │                │
            Sentinel-1 IW SAR       │                │    Sentinel-2 MSI
       (VV + VH Polarization, C-Band)│                │   (12-Band Multispectral)
                                    ▼                ▼
                     ┌──────────────────┐  ┌──────────────────┐
                     │ 3x3 Median Filter│  │ SCL Cloud Masking│
                     │  Speckle Removal │  │ (Shadows, Clouds)│
                     └────────┬─────────┘  └────────┬─────────┘
                              │                     │
                              ▼                     ▼
                     ┌──────────────────┐  ┌──────────────────┐
                     │ SAR Ratio Change │  │  NDWI Calculation│
                     │  ΔVV, ΔVH in dB  │  │   & NDWI Change  │
                     └────────┬─────────┘  └────────┬─────────┘
                              │                     │
                              └──────────┬──────────┘
                                         ▼
                     ┌──────────────────────────────────────┐
                     │     V3 Physics-Based Water Mask      │
                     │   ΔVV < -1.5 dB  AND  ΔVH < -1.5 dB  │
                     │  NDWI_post > 0.05  AND  ΔNDWI > 0.15 │
                     │          NDWI_pre < 0.20             │
                     └──────────────────┬───────────────────┘
                                        ▼
                     ┌──────────────────────────────────────┐
                     │ 8-Connected Morphological Filter     │
                     │  Minimum Patch Size: 25 Pixels       │
                     │  (-57.7% False Alarm Suppression)    │
                     └──────────────────┬───────────────────┘
                                        ▼
                     ┌──────────────────────────────────────┐
                     │    Candidate Flood Vector Layer      │
                     │  (1,286 Pixels / 27 Clusters / 84 Polys)│
                     └──────────────────────────────────────┘
```

### 2.1 Sentinel-1 SAR Backscatter Physics
Smooth surface water specularly reflects active radar pulses away from the side-looking SAR antenna, producing a pronounced decrease in radar cross-section ($\sigma^0$). The radar change metric is computed in decibels:

$$\Delta \sigma^0_{\text{pol}} = 10 \cdot \log_{10} \left( \frac{\sigma^0_{\text{post, pol}}}{\sigma^0_{\text{pre, pol}}} \right)$$

To mitigate speckle noise without destroying sharp river boundaries, both pre-event and post-event VV and VH amplitude rasters undergo $3 \times 3$ median spatial filtering. Candidate water pixels must satisfy:
$$\Delta \sigma^0_{\text{VV}} < -1.5\text{ dB} \quad \text{and} \quad \Delta \sigma^0_{\text{VH}} < -1.5\text{ dB}$$

### 2.2 Sentinel-2 Multispectral & Cloud Masking
When cloud cover permits, multispectral Sentinel-2 imagery provides optical confirmation using the Normalized Difference Water Index (NDWI):

$$\text{NDWI} = \frac{\rho_{\text{Green}} - \rho_{\text{NIR}}}{\rho_{\text{Green}} + \rho_{\text{NIR}}} \quad \left( \text{or Modified NDWI using SWIR: } \frac{\rho_{\text{Green}} - \rho_{\text{SWIR}}}{\rho_{\text{Green}} + \rho_{\text{SWIR}}} \right)$$

The Scene Classification Layer (SCL) is ingested to rigorously mask non-water anomalies. Only valid land/water classes (`[2, 4, 5, 6, 7]`) are retained; cloud shadows (`3`), high clouds (`8, 9`), thin cirrus (`10`), and snow/ice (`11`) are converted to `NODATA` ($-9999.0$), preventing spurious false positives. If optical coverage is $< 5.0\%$ valid due to clouds, the pipeline transparently logs `PARTIAL_RUN_OPTICAL_UNCONFIRMED`.

### 2.3 Morphological Filtering & Spatial Resolution Reconciliation
Raw threshold intersection initially detects 3,040 candidate pixels. Applying an 8-connected component filter with a minimum threshold of 25 contiguous pixels eliminates isolated speckle artifacts, reducing false candidates by **57.7%** to **1,286 confirmed candidate pixels** grouped into **27 distinct water clusters**.

#### Spatial Area & Coordinate Transform Reconciliation:
The raster output is exported across the study bounding box ($[84.90^\circ\text{E}, 27.75^\circ\text{N}, 85.25^\circ\text{E}, 28.05^\circ\text{N}]$) on a $2048 \times 2048$ grid:
- Horizontal pixel dimension: $\Delta x = \frac{0.35^\circ}{2048} \approx 0.000170898^\circ$ ($\approx 16.83\text{ m}$ ground width at $27.90^\circ\text{N}$)
- Vertical pixel dimension: $\Delta y = \frac{0.30^\circ}{2048} \approx 0.000146484^\circ$ ($\approx 16.23\text{ m}$ ground height)
- Ground pixel area: $A_{\text{cell}} = 16.83\text{ m} \times 16.23\text{ m} \approx 273.13\text{ m}^2$
- **Total AOI Candidate Inundation:** $1,286 \times 273.13\text{ m}^2 = 351,242\text{ m}^2 = \mathbf{35.03\text{ ha}}$ (raster area) / $\mathbf{35.12\text{ ha}}$ (projected UTM 45N vector area across 84 vectorized polygons).
- *(Note on nominal resolution)*: A theoretical, un-resampled native $10\text{m} \times 10\text{m}$ grid ($100\text{ m}^2/\text{pixel}$) would yield $12.86\text{ ha}$. The resampled bounding box grid establishes $35.03\text{ ha}$ as the true physical ground footprint.

---

## 3. Historical Infrastructure & Network Graph Topology

```
                  ┌──────────────────────────────────────────┐
                  │       OVERPASS HISTORICAL API            │
                  │   Pre-Event Snapshot: T_osm < T_flood    │
                  └────────────────────┬─────────────────────┘
                                       │
                  ┌────────────────────┴─────────────────────┐
                  ▼                                          ▼
     ┌────────────────────────┐                 ┌────────────────────────┐
     │ Buildings (132,765)    │                 │ Motorable Roads        │
     │ Bridges (187)          │                 │ (4,405 Ways / 589 Pts) │
     └───────────┬────────────┘                 └───────────┬────────────┘
                 │                                          │
                 ▼                                          ▼
     ┌────────────────────────┐                 ┌────────────────────────┐
     │ Spatial 2D Overlay     │                 │ Network Graph Modeling │
     │ 195 Buildings Exposed  │                 │ Disrupted Edges: 3,748 │
     │ 115 Roads (59.26 km)   │                 │ Pre-Event Comps: 181   │
     │ 13 Bridges Exposed     │                 │ Post-Event Comps: 252  │
     └────────────────────────┘                 └───────────┬────────────┘
                                                            │
                                                            ▼
                                                ┌────────────────────────┐
                                                │ Dijkstra Hub Routing   │
                                                │ 18 Settlements Severed │
                                                │ From All Municipal Hubs│
                                                └────────────────────────┘
```

### 3.1 Strict Pre-Event Infrastructure Ingestion
To eliminate circular reporting and human post-event mapping bias, Stage 5 mandates an Overpass snapshot query timestamped strictly 7 to 30 days prior to the target flood date:
$$T_{\text{snapshot}} \le T_{\text{flood}} - 7\text{ days}$$
Post-event OSM snapshots are programmatically rejected with an `INVALID_TEMPORAL_PROVENANCE` exception.

### 3.2 2D Asset Exposure vs. Confirmed Damage
Vector polygons of candidate water are intersected against historical infrastructure:
- **Buildings Exposed:** 195 buildings intersect candidate water out of 132,765 mapped footprints.
- **Road Centerlines:** 115 road features (59.26 cumulative km) intersect candidate water.
- **Bridges:** 13 bridges intersect candidate water.

*Operational Caveat:* 2D intersection indicates **potential inundation exposure**, not confirmed structural collapse or interior water ingress. Bridge decks may maintain vertical clearance above peak flood stage.

### 3.3 Topological Graph Partitioning & Settlement Isolation
A road network graph $G = (V, E)$ is constructed from vehicle-accessible highways (`motorway`, `trunk`, `primary`, `secondary`, `tertiary`, `unclassified`, `residential`). 
1. Road edges intersecting candidate inundation are removed: $E_{\text{post}} = E \setminus E_{\text{flood}}$, removing **3,748 graph segments**.
2. Network fragmentation increases from **181 pre-event connected components** to **252 post-event components** (+71 isolated pockets).
3. Evaluated settlements (589 villages, hamlets, towns) are snapped to graph nodes within a 2,500m threshold.
4. Using Dijkstra's algorithm, path existence is computed between each settlement $s \in S$ and identified municipal hubs $H = \{\text{Bidur}, \text{Battar}, \text{Trishuli Bazar}\}$:

$$\text{Disconnected}(s) \iff \forall h \in H, \, \text{dist}_{G_{\text{post}}}(s, h) = \infty \quad \text{and} \quad \exists h \in H, \, \text{dist}_{G_{\text{pre}}}(s, h) < \infty$$

The analysis reveals **18 settlements** that lost all vehicular access routes (e.g., Betrawati, Dhikure, Salme). This models **vehicular access loss**, not absolute physical isolation (foot trails and boat access remain outside the motorable graph).

### 3.4 Missing Data Disclosure
In the pre-event Trishuli snapshot, 0 hospital nodes were tagged. Rather than imputing fake healthcare facilities, FloodSpaceAI explicitly logs `hospital_data_available: false` and redirects emergency routing to municipal hubs.

---

## 4. Evidence-Grounded AI Architecture & Adversarial Defenses

### 4.1 Dual-Tier AI Architecture
FloodSpaceAI solves the hallucination dilemma through a verified dual-tier architecture:

| Tier | Component | Role | Verification & Safety Mechanism |
|---|---|---|---|
| **Tier 1** | **Grounded Retrieval Assistant** (`scripts/evidence_grounded_copilot.py` & Dashboard) | Real-time interactive user queries (zero latency, offline resilient) | Deterministic intent parsing; maps queries to 13 schema-validated claims in `evidence.json`; renders clickable citation cards. |
| **Tier 2** | **Multimodal Narrative Synthesis** (`scripts/gemini_situation_copilot.py`) | Offline natural language report generation in English & Nepali | Google GenAI (`gemini-3.8-flash`); gated by a **regex numerical gatekeeper** that rejects the report if any number does not exist in `evidence.json`. |

### 4.2 Schema 1.0.0 Grounded Claims Index
Every claim produced by the pipeline carries 11 required metadata fields:
1. `claim_id` (e.g., `CLAIM-trishuli_benchmark_verified-FLOOD-AREA`)
2. `claim_text`
3. `value`
4. `unit`
5. `geographic_scope`
6. `source_file`
7. `source_field`
8. `run_id`
9. `data_provenance`
10. `confidence_or_uncertainty`
11. `interpretation_guidance`

### 4.3 Adversarial Guardrails & Refusal Policies
Tested across 8 adversarial scenarios in `scripts/test_phase6_ai_grounding.py`:
- **Casualty Queries:** *"How many people died?"* $\rightarrow$ **REFUSED (`CASUALTIES_REFUSED`)**. The system states: *"Casualty, fatality, and injury counts are strictly outside the operational scope of satellite remote sensing and graph modeling."*
- **Economic Loss Queries:** *"What is the monetary damage in USD?"* $\rightarrow$ **REFUSED (`MONETARY_REFUSED`)**. Physical backscatter cannot derive insurance losses or reconstruction costs.
- **Structural Damage Clarification:** *"Are 195 buildings destroyed?"* $\rightarrow$ **CLARIFIED (`EXPOSURE_CLARIFIED`)**. Cites 2D footprint intersection without interior damage confirmation.
- **Physical Isolation Clarification:** *"Are 18 villages completely cut off?"* $\rightarrow$ **CLARIFIED (`ROUTING_CLARIFIED`)**. Cites vehicular road network disconnection; pedestrian footpaths may persist.
- **Zero-Candidate Transparency:** In cloud-starved runs with 0 detected candidates (e.g., Narayani), the copilot clarifies that 0 candidates does *not* prove absence of flooding, but reflects sensor limits.
- **Multilingual Consistency:** 100% numerical, unit, date, and uncertainty parity between English and authentic Nepali (`नेपाली`) situation reports.

---

## 5. Independent Validation: Copernicus EMSR927

```
                     ┌─────────────────────────────────────────────────────────┐
                     │          EMSR927 DELINEATION FOOTPRINT                 │
                     │          (1,068.36 ha broad debris-flow corridor)       │
                     │                                                         │
                     │      ┌───────────────────────────┐                      │
                     │      │   Spatial Overlap Area    │                      │
                     │      │   (10.93 ha Intersection) │                      │
                     │      │                           │                      │
                     │      │  FloodSpaceAI Candidate   │                      │
                     │      │  (24.16 ha surface water) │                      │
                     │      └───────────────────────────┘                      │
                     │                                                         │
                     └─────────────────────────────────────────────────────────┘
```

Copernicus Emergency Management Service Rapid Mapping activation **EMSR927** was ingested strictly as an independent post-hoc check (`scripts/validate_emsr927.py`):

| Evaluation Metric | Measured Value | Scientific Interpretation |
|---|:---:|---|
| **EMSR927 Target Phenomenon** | `6-Mass Movement / Debris Flow` | Hillside slope failure, rock avalanches, mudslides, and river scouring. |
| **FloodSpaceAI Target Phenomenon** | Surface Water Inundation | Low-lying pooling water detected via SAR backscatter drop and NDWI. |
| **EMSR927 Footprint in Overlap** | 1,068.36 ha | Broad mountain debris corridor across AOI03 and AOI05. |
| **FloodSpaceAI Inundation in Overlap** | 24.16 ha | Standing valley floor water subset (out of 35.03 ha full AOI). |
| **Spatial Intersection** | **10.93 ha** | Direct coincident spatial overlap. |
| **Intersection over Union (IoU)** | **1.01%** | $\frac{10.93\text{ ha}}{1,081.59\text{ ha union}}$. Geometric overlap with an upland debris swath; cannot establish flood accuracy alone. |

**Methodological Boundary & Accuracy Limitations:** The 1.01% IoU represents geometric overlap against an external emergency delineation that mapped broad mountain debris flows, rockslides, and hillside scours ($1,068.36\text{ ha}$). Because the reference product maps a broader and distinct geological phenomenon rather than valley-floor standing water ($24.16\text{ ha}$), the comparison establishes spatial co-location in the disaster corridor, but cannot serve as a standalone ground-truth accuracy benchmark. EMSR927 was strictly quarantined and never used to tune or calibrate detection thresholds.

---

## 6. Software Engineering & Empirical Verification

### 6.1 Test Suite Verification (56/56 Tests Passing)
All 7 test suites exit with code `0`:

```
[TEST SUMMARY]
- Phase 2  (scripts/test_sentinel2_discovery.py):   5 / 5  PASS (Exit Code 0)
- Phase 3  (scripts/test_satellite_processing.py):  7 / 7  PASS (Exit Code 0)
- Phase 4A (scripts/test_satellite_acquisition.py): 8 / 8  PASS (Exit Code 0)
- Phase 4B (scripts/test_asset_connectivity.py):    8 / 8  PASS (Exit Code 0)
- Phase 5  (scripts/test_orchestrator.py):          9 / 9  PASS (Exit Code 0)
- Phase 5.1(scripts/test_phase5_1_reliability.py):  9 / 9  PASS (Exit Code 0)
- Phase 6  (scripts/test_phase6_ai_grounding.py):  10 / 10 PASS (Exit Code 0)
-------------------------------------------------------------------------
TOTAL AUTOMATED PASSING TESTS:                     56 / 56 PASS (100%)
NEXT.JS PRODUCTION BUILD:                           0 TypeScript Errors
```

### 6.2 Provenance Isolation
Outputs are written strictly to isolated subdirectories under `data/processed/pipeline_runs/<run_id>/`:
- `LIVE_AUTHORITATIVE_SATELLITE_RETRIEVAL`: Live AWS Open Data STAC stream with recorded SHA-256 hashes.
- `VERIFIED_TRISHULI_BENCHMARK_CACHE`: Immutable competition benchmark run.
- `EXPLICIT_USER_SUPPLIED_INPUTS`: User-provided raster overrides.

---

## 7. Authoritative Attributions, Licensing & Ethics

1. **Copernicus Sentinel Data:** "Contains modified Copernicus Sentinel data 2026." (Processed via ESA Copernicus Open Access and Element84 Earth Search STAC).
2. **Copernicus DEM:** "Produced using Copernicus WorldDEM-30 © DLR e.V. 2010–2014 and © Airbus Defence and Space GmbH 2014–2018 provided under COPERNICUS by the European Union and ESA; all rights reserved."
3. **OpenStreetMap:** "© OpenStreetMap contributors." (Licensed under the Open Database License ODbL 1.0).
4. **Copernicus Emergency Management Service:** © European Union 2024–2026, Copernicus EMS Activation EMSR927 Rapid Mapping.
5. **Ethical AI Boundaries & Model Non-Training Disclosure:** FloodSpaceAI is an unsupervised physics-based SAR backscatter change and optical multispectral classification platform. It does NOT make unverified claims of training deep learning neural networks or unseen scene accuracy without ground truth. The system does not infer biometric casualty data, does not replace on-ground structural engineering inspections, and strictly presents satellite overlays as potential exposure indicators.

---

## 8. Conclusion

FloodSpaceAI demonstrates that multimodal earth observation and artificial intelligence can be combined with mathematical rigor, spatial integrity, and absolute zero-hallucination discipline. By enforcing temporal OSM boundaries, grounding every AI statement in immutable evidence, refusing speculative claims, and providing transparent scientific validation against Copernicus EMSR927, FloodSpaceAI provides a field-ready blueprint for spaceborne disaster intelligence.
