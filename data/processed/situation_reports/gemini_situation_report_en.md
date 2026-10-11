# Flood Situation Report

## Situation Overview

This analysis supports the {'event': 'August 2026 Trishuli flood', 'analysis_area': 'Trishuli valley AOI', 'osm_snapshot': '2026-07-27T00:00:00Z'} case study using
FloodSpaceAI satellite analysis and pre-event OpenStreetMap data.

## Where Flooding Was Detected

The system generated a modelled potential inundation candidate
using Sentinel-1 SAR change, Sentinel-2 NDWI change, post-event
water conditions, pre-event non-water conditions, and
connected-component filtering.

The analysis contains 1286 flood pixels and
84 flood polygons.

These results represent **potential inundation** and should not
be interpreted as confirmed flood extent.

## Potentially Affected Infrastructure

The system identified the following infrastructure as
potentially affected:

- Buildings: 195
- Roads: 115
- Bridges: 13

These are potential impacts and are not confirmed physical
damage or destruction.

## Potentially Cut-Off Settlements

A total of 600 settlements were available
for the analysis, with 589 settlements
analysed for road-network connectivity.

The analysis used 3 town/city hubs.

18 settlements were identified as potentially cut off.

This represents a modelled road-network disconnection and does
not confirm real-world isolation.

## Methodology

The analysis uses Sentinel-1 pre/post SAR comparison,
Sentinel-2 optical comparison, NDWI change, pre-event
OpenStreetMap infrastructure, and road-network connectivity.

## Limitations

- The potential inundation output is not confirmed flood extent.
- Post-event Sentinel-2 optical imagery is cloud contaminated.
- Potentially affected infrastructure is not confirmed physical damage.
- Potentially cut-off settlements are modelled network
  disconnections, not confirmed real-world isolation.
- Historical data limitations prevented full hospital
  connectivity analysis.

## Data Provenance

Pre-event OpenStreetMap snapshot:

2026-07-27T00:00:00Z

This report uses numerical information only from the
system evidence dataset.
