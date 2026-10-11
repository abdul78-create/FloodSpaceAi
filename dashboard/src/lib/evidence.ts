// ============================================================
// FloodSpaceAI — shared evidence data
// Source: data/processed/situation_report_evidence.json
// DO NOT invent or modify these numbers.
// ============================================================

export const EVIDENCE = {
  caseStudy: {
    event: "August 2026 Trishuli Flood",
    area: "Trishuli Valley, Nepal",
    osmSnapshot: "27 July 2026",
    sentinel1Pre: "16 August 2026",
    sentinel1Post: "28 August 2026",
    sentinel1Orbit: "Relative orbit 85",
    sentinel2Note: "Post-event optical: cloud limited",
  },

  floodMapping: {
    version: "V3",
    method:
      "Potential inundation candidate derived from Sentinel-1 SAR change, " +
      "Sentinel-2 NDWI change, post-event water condition, " +
      "pre-event non-water condition, and connected-component filtering.",
    floodPixels: 1286,
    floodPolygons: 84,
  },

  potentiallyAffected: {
    buildings: 195,
    roads: 115,
    bridges: 13,
  },

  roadConnectivity: {
    settlementsAnalysed: 589,
    townCityHubs: 3,
    potentiallyCutOff: 18,
    preEventComponents: 181,
    postEventComponents: 252,
  },

  interpretation:
    "These are MODELLED POTENTIAL impacts derived from satellite change " +
    "analysis and geospatial overlay. They are not confirmed physical damage " +
    "or isolation.",

  provenance: {
    sentinel: "Copernicus Sentinel-1 / Sentinel-2",
    dem: "Copernicus DEM",
    osm: "© OpenStreetMap contributors",
    note: "Contains modified Copernicus Sentinel data 2026.",
  },
} as const;
