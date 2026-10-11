# Trishuli Flood — Situation Report

## 1. Situation Overview

FloodSpaceAI analysed the August 2026 Trishuli flood using
Sentinel-1 radar and Sentinel-2 optical satellite data
together with pre-event OpenStreetMap infrastructure data.

The system produced a conservative potential inundation
candidate using multi-source satellite change detection.

## 2. Potential Flood Extent

The V3 model identified:

- Potential inundation pixels: 1,286
- Potential inundation polygons: 84

These values represent a modelled potential inundation
candidate and should not be interpreted as confirmed
physical flood extent.

## 3. Potentially Affected Infrastructure

Overlay analysis against the pre-event OSM snapshot
identified:

- Potentially affected buildings: 195
- Potentially affected road features: 115
- Potentially affected bridges: 13

These are potential impacts based on spatial overlap with
the modelled inundation candidate.

They do not confirm that individual buildings, roads,
or bridges were destroyed or physically damaged.

## 4. Road Connectivity

The road-network analysis evaluated
589 settlements against
3 town/city hubs.

The model identified:

- Settlements analysed: 589
- Potentially cut-off settlements: 18

A settlement is classified as potentially cut off when its
road connection to its selected town/city hub exists in the
pre-event network but becomes disconnected after removing
modelled potentially affected road segments.

This is a modelled connectivity result and does not confirm
real-world isolation.

## 5. Limitations

- Post-event Sentinel-2 imagery contains cloud contamination
  in parts of the analysis area.
- The flood output is a modelled potential inundation
  candidate.
- Potentially affected infrastructure is not confirmed
  physical damage.
- Potentially cut-off settlements are not confirmed to be
  isolated in the real world.
- Historical hospital data was unavailable for this
  prototype, so town/city hubs were used for connectivity
  analysis.
- This system is an educational prototype and is not an
  operational emergency-response system.

## 6. Data Provenance

- Copernicus Sentinel-1 / Sentinel-2
- Copernicus DEM
- Pre-event OpenStreetMap data
- OSM snapshot: 2026-07-27
- © OpenStreetMap contributors.

Contains modified Copernicus Sentinel data 2026.

Produced using Copernicus WorldDEM-30 © DLR e.V.
2010–2014 and © Airbus Defence and Space GmbH 2014–2018
provided under COPERNICUS by the European Union and ESA;
all rights reserved.
