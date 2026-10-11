# FloodSpaceAI — Executive Disaster Situation Report

**Incident:** Trishuli River Basin Flash Flood / GLOF  
**Target Flood Date:** August 28, 2026  
**Analysis Area (AOI):** Trishuli River Corridor, Nepal `[84.90°E, 27.75°N to 85.25°E, 28.05°N]`  
**Operational Status:** `PARTIAL_RUN_OPTICAL_UNCONFIRMED` (All-Weather SAR Verified; Optical Cloud-Obscured)  
**Historical Infrastructure Baseline:** OpenStreetMap Snapshot `2026-07-27T00:00:00Z` (Strictly Pre-Event)  

---

## 1. Operational Overview & Key Metrics

FloodSpaceAI executed end-to-end multi-sensor satellite change detection and road network connectivity modeling to evaluate potential inundation and accessibility disruption across the Trishuli valley.

| Analytical Metric | Modeled Value | Analytical Unit | Source Artifact | Scientific Interpretation Notice |
| :--- | :---: | :---: | :--- | :--- |
| **Candidate Inundation Extent** | **1,286** | pixels | `rasters/final_flood_candidate_v3.tif` | SAR backscatter drop < -1.5 dB; 16.8m x 16.2m resampled grid. |
| **Candidate Surface Water Area**| **35.03** | hectares | `rasters/final_flood_candidate_v3.tif` | 2D water pooling extent (24.16 ha in EMSR927 overlap); depth not modeled. |
| **Discrete Water Clusters** | **27 / 84** | polygons | `vectors/flood_polygons_v3.geojson` | Contiguous standing water bodies (>=2 connected pixels). |
| **Potentially Affected Buildings**| **195** | structures | `assets/buildings_affected_v3.geojson` | **Potential exposure only; unconfirmed structural damage.** |
| **Potentially Affected Roads** | **115** | features | `assets/roads_affected_v3.geojson` | Centerlines intersecting candidate water polygons. |
| **Exposed Highway Length** | **59.26** | kilometers | `assets/roads_affected_v3.geojson` | Cumulative exposed highway length; not destroyed pavement. |
| **Potentially Affected Bridges**| **13** | bridges | `assets/bridges_affected_v3.geojson` | 2D overlay; vertical bridge deck clearance not modeled. |
| **Disrupted Network Edges** | **3,748** | segments | `connectivity/settlement_connectivity_v4.json`| Routable road edges severed in topological routing graph. |
| **Potentially Cut-Off Settlements**| **18** | settlements | `connectivity/settlements_cutoff_v4.geojson`| **Modelled road network disconnection; not physical isolation.**|

---

## 2. Priority Settlements with Modeled Vehicular Access Loss

Topological Dijkstra shortest-path pathfinding from 589 settlements to municipal town/city hubs (Bidur, Galchhi, Belkotgadhi) identified **18 settlements** that lost all vehicular access routes:

| Settlement Name | OSM Classification | Nearest Municipal Hub | Pre-Flood Status | Modeled Post-Flood Access |
| :--- | :--- | :--- | :---: | :---: |
| **Betrawati (बेत्रावती)** | Hamlet | Bidur (बिदुर) | Connected | **Disconnected (Bridge/Highway Cut)** |
| **Bhaise (भैंसे)** | Hamlet | Bidur (बिदुर) | Connected | **Disconnected (Riverbank Overwash)** |
| **Simle (सिम्ले)** | Hamlet | Bidur (बिदुर) | Connected | **Disconnected (Highway Segment Severed)** |
| **Devighat (देवीघाट)** | Hamlet | Belkotgadhi (बेलकोटगढी) | Connected | **Disconnected (Bridge Approach Cut)** |
| **Dhaibung (धइबुङ)** | Hamlet | Bidur (बिदुर) | Connected | **Disconnected (Corridor Inundation)** |
| **Salim Bhitta (सालिम भित्ता)**| Hamlet | Bidur (बिदुर) | Connected | **Disconnected (Valley Floor Submergence)** |
| **Dhungye (ढुङ्गे)** | Hamlet | Bidur (बिदुर) | Connected | **Disconnected (Access Road Blocked)** |
| **Uttargaya (उत्तरगया)** | Village | Bidur (बिदुर) | Connected | **Disconnected (Primary Feeder Severed)** |
| **Kalika (कालिका)** | Village | Bidur (बिदुर) | Connected | **Disconnected (Route Impassable)** |

> **Responder Guidance:** Modelled cut-offs reflect vehicular highway disruption. Emergency teams should prioritize foot patrols, unmapped pack trails, boat crossings, or helicopter reconnaissance for these locations.

---

## 3. Mandatory Scientific Limitations & Attributions

1. **Exposure vs. Confirmed Damage:** All figures represent modeled potential inundation and spatial intersection with OpenStreetMap infrastructure footprints. They **do not confirm physical destruction, structural collapse, or water ingress**. In-situ engineering inspection is required before declaring structural losses.
2. **Topological Disruption vs. Physical Isolation:** Cut-off settlements represent vehicular graph disconnects. Footpaths, mule trails, river ferries, or aerial access routes may remain open.
3. **Sensor Limitations & Cloud Cover:** Post-event Sentinel-2 optical imagery had 75.9% mean cloud obscuration. Inundation is derived primarily from all-weather Sentinel-1 C-band synthetic aperture radar and remains optical-unconfirmed.
4. **Independent Validation Isolation:** Copernicus Emergency Management Service EMSR927 debris-flow footprints (1,068.36 ha, 1.01% IoU geometric overlap) are maintained strictly as an independent post-hoc co-location check isolated from pipeline inputs; this comparison is limited and cannot establish flood-detection accuracy by itself.
5. **Attribution:** Contains modified Copernicus Sentinel data 2026. Produced using Copernicus WorldDEM-30 © DLR e.V./Airbus DS. Infrastructure data © OpenStreetMap contributors (ODbL 1.0).
