# FloodSpaceAI — Trishuli Flood Intelligence Dashboard

**Multimodal AI Hackathon 2026 — Track B: Mapping Flood Damage from Space**

FloodSpaceAI is an interactive hydrology survey and multimodal satellite evidence intelligence system for the August 2026 Trishuli flood in Nepal. It combines all-weather **Copernicus Sentinel-1 SAR** change detection, **Copernicus Sentinel-2 optical** multispectral analysis, and **OpenStreetMap pre-event infrastructure networks** with **grounded Gemini situation intelligence**.

---

## 🎨 Field-Survey Visual Direction

The frontend is intentionally designed like a printed hydrology survey sheet meeting a live precision instrument.

- **Fog (`#EDF1F0`)**: Page background with subtle drifting contour line SVG patterns.
- **Paper (`#F8F9F6`)**: Primary content panels and survey cards.
- **Ink (`#1E2A32`)**: Primary high-contrast technical typography.
- **River (`#2E6F9E`)**: Water and flood candidate layers.
- **Silt (`#B98A3E`)**: Potentially affected road and infrastructure layers.
- **Brick (`#B04A3A`)**: Potentially cut-off settlements and strict warning indicators.
- **Moss (`#5F7F56`)**: Intact baseline network and safe indicators.
- **Slate (`#8A979E`)**: Borders, tick marks, and structural lines.
- **Typography**: `Fraunces` (classical field-survey serif for titles), `Instrument Sans` (humanist sans for UI), and `Noto Sans Devanagari` (for authentic Nepali language reports).
- **Physical buttons**: Flat, 4–6px radius with true physical press animations (translateY + shadow collapse).

---

## 🚀 Running the Project

All frontend code lives strictly inside `dashboard/`.

```bash
cd dashboard
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 📁 Data Placement & Schema

All processed backend outputs are loaded by a single unified data-loader layer (`src/data/dataLoader.ts`) from `/data` (located in `dashboard/public/data/`):

| File Path in `dashboard/public/data/` | Description & Expected Schema |
|---|---|
| `flood_polygons_v3.geojson` | GeoJSON `FeatureCollection` of V3 flood polygon clusters. |
| `buildings_affected_v3.geojson` | GeoJSON `FeatureCollection` of 195 potentially affected building footprints. |
| `roads_affected_v3.geojson` | GeoJSON `FeatureCollection` of 115 potentially affected vehicle road segments. |
| `bridges_affected_v3.geojson` | GeoJSON `FeatureCollection` of 13 potentially affected bridge crossing points. |
| `settlements_cutoff_v4.geojson` | GeoJSON `FeatureCollection` of 18 potentially cut-off settlements. |
| `evidence.json` | System evidence JSON (`situation_report_evidence.json`) — single source of truth. |
| `assets_summary_v3.json` | Metadata summary for V3 asset overlaps. |
| `connectivity_summary_v4.json` | Graph metrics (589 settlements, 181 -> 252 components, 3 hubs). |
| `report_en.md` | Grounded English situation report document. |
| `report_ne.md` | Grounded Nepali situation report document (नेपाली). |
| `sentinel2_pre_rgb.png` | Pre-event Sentinel-2 cloud-free optical true-color preview (2048×2048 resampled grid). |
| `filtered_vv_visual.png` | Post-event filtered Sentinel-1 VV backscatter change preview. |
| `vh_change_visual.png` | Sentinel-1 VH cross-polarization visual preview. |
| `vvvh_ratio_visual.png` | Dual-polarization ratio change visual preview. |

---

## ⏱ 3-Minute Demo Tour (Storyline for Judges)

Click the **"Start 3-minute tour"** button in the top-right header to auto-play the full 6-step story:

1. **Main Interactive Map (Hero)**:
   - Satellite basemap (Esri World Imagery + OSM overlay).
   - Animated water rise sequence across 84 flood candidate polygons.
   - Sequential drop-in of 195 buildings, 115 roads, 13 bridges, and pulsing Brick markers for 18 cut-off settlements.
2. **Multi-Sensor Satellite Comparison**:
   - Draggable before/after swipe slider comparing pre-event baseline with post-event SAR backscatter drop and optical change.
3. **Potentially Affected Infrastructure**:
   - Animated counter cards (195 buildings, 115 roads, 13 bridges, 1,286 flood pixels).
   - Spatial overlay methodology and V1 vs V3 comparison table.
4. **Road Connectivity & Cut-off Settlements**:
   - Graph disruption metrics (+71 new disconnected components).
   - Interactive Before vs After road severance simulation with animated break lines.
5. **Grounded Situation Copilot**:
   - Bilingual English ⇄ नेपाली reports with stable cross-fade layout.
   - Interactive Q&A query assistant with programmatic validation and citation chips (`#potentially_affected_assets.buildings`, `#road_connectivity.potentially_cut_off_settlements`).
6. **End-to-End Evidence Pipeline**:
   - 10-stage processing chain from Copernicus SAFE archives to validated Gemini reporting with expandable mathematical methodology details.

---

## ⚖️ Strict Terminology Discipline & Provenance

- All impacts are strictly designated as **modelled potential candidates**, **potentially affected**, and **modelled road-network disconnections**.
- Physical damage or ground isolation is never confirmed without on-site field verification.
- Authoritative Attribution: Contains modified Copernicus Sentinel data 2026. Produced using Copernicus WorldDEM-30 © DLR e.V./Airbus DS. © OpenStreetMap contributors (ODbL).
