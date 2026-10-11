# FloodSpaceAI Situation Report — Run `unseen_aoi_pokhara`

**Event Date:** `2026-09-15`  
**AOI Bounding Box:** `[83.95, 28.18, 84.05, 28.28]`  
**Provenance Mode:** `UNKNOWN`  
**Generated:** `2026-10-09T09:43:09.610166+00:00`

---

## 1. Executive Summary
FloodSpaceAI analyzed potential inundation for the target event date `2026-09-15` using multi-sensor Copernicus satellite imagery and pre-event OpenStreetMap infrastructure data.

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
- **Optical Coverage Status:** Query parameters (bbox=[83.95, 28.18, 84.05, 28.28], flood_date='2026-09-15') represent an unseen AOI or date. While candidate scenes were discovered in STAC catalogues, raw multiband satellite rasters have not yet been fetched for this specific AOI/date. Strict provenance isolation prevents reusing cached Trishuli rasters..

---

## 3. Road Network Disruption & Isolation Modeling
- **Disrupted Road Segments:** 0
- **Baseline Connected Components:** 0
- **Post-Disruption Connected Components:** 0
- **Potentially Cut-Off Settlements:** 0
- **Hospital Data Status:** Town/city hubs utilized.

---

## 4. Mandatory Limitations
- The flood output is a modelled potential inundation candidate, not confirmed physical damage.
- Potentially affected assets are based on candidate spatial overlap; not confirmed structural destruction.
- Potentially cut-off settlements represent modelled topological network disconnections, not confirmed real-world isolation.
- Validation layers (EMSR927 / UNOSAT) are strictly checking-only and excluded from analytical pipelines.
- This system is an educational and research prototype for the Multimodal AI Hackathon 2026.

---

## 5. Authoritative Data Provenance & Legal Disclaimers
- **Copernicus Sentinel:** Contains modified Copernicus Sentinel data (2024/2026), processed under ESA Copernicus Open Access.
- **Copernicus DEM:** Produced using Copernicus WorldDEM-30 © DLR e.V. 2010–2014 and © Airbus Defence and Space GmbH 2014–2018.
- **OpenStreetMap:** © OpenStreetMap contributors, ODbL 1.0 license. Pre-event snapshot verified.
- **Independent Validation:** Copernicus EMSR927 / UNOSAT assessments strictly isolated from analytical pipeline inputs.
