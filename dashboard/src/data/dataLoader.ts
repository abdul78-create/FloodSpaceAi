// ============================================================
// FloodSpaceAI — Single Unified Data Loader Layer
// Swapping files or upgrading pipelines requires NO component changes
// ============================================================

import type { 
  EvidenceData, 
  AssetsSummaryV3, 
  ConnectivitySummaryV4,
  RunRegistryEntry,
  RunManifest
} from "./types";

// Default fallback evidence directly from situation_report_evidence.json
export const FALLBACK_EVIDENCE: EvidenceData = {
  project: "FloodSpaceAI",
  track: "Track B — Mapping Flood Damage from Space",
  case_study: {
    event: "August 2026 Trishuli flood",
    analysis_area: "Trishuli valley AOI",
    osm_snapshot: "2026-07-27T00:00:00Z"
  },
  flood_mapping: {
    method: "Potential inundation candidate derived from Sentinel-1 SAR change, Sentinel-2 NDWI change, post-event water condition, pre-event non-water condition, and connected-component filtering.",
    candidate_version: "V3",
    flood_pixels: 1286,
    flood_polygons: 84
  },
  potentially_affected_assets: {
    buildings: 195,
    roads: 115,
    bridges: 13
  },
  road_connectivity: {
    settlements_available: 600,
    settlements_analysed: 589,
    town_city_hubs: 3,
    potentially_cut_off_settlements: 18,
    pre_event_components: 181,
    post_event_components: 252
  },
  cut_off_settlements: [
    { name: "बेत्रावती", place: "hamlet", nearest_town_or_city: "बिदुर", connected_before: true, connected_after: false },
    { name: "भैंसे", place: "hamlet", nearest_town_or_city: "बिदुर", connected_before: true, connected_after: false },
    { name: "सिम्ले", place: "hamlet", nearest_town_or_city: "बिदुर", connected_before: true, connected_after: false },
    { name: "OSM-3476388711", place: "village", nearest_town_or_city: "गल्छी", connected_before: true, connected_after: false },
    { name: "OSM-3484404878", place: "hamlet", nearest_town_or_city: "बिदुर", connected_before: true, connected_after: false },
    { name: "देवीघाट", place: "hamlet", nearest_town_or_city: "बेलकोटगढी", connected_before: true, connected_after: false },
    { name: "धइबुङ", place: "hamlet", nearest_town_or_city: "बिदुर", connected_before: true, connected_after: false },
    { name: "सालिम भित्ता", place: "hamlet", nearest_town_or_city: "बिदुर", connected_before: true, connected_after: false },
    { name: "ढुङ्गे", place: "hamlet", nearest_town_or_city: "बिदुर", connected_before: true, connected_after: false },
    { name: "नौविसे फाँट", place: "hamlet", nearest_town_or_city: "बिदुर", connected_before: true, connected_after: false },
    { name: "खालचेत", place: "hamlet", nearest_town_or_city: "बिदुर", connected_before: true, connected_after: false },
    { name: "सरसिउ", place: "hamlet", nearest_town_or_city: "बिदुर", connected_before: true, connected_after: false },
    { name: "बडहरे", place: "hamlet", nearest_town_or_city: "बिदुर", connected_before: true, connected_after: false },
    { name: "उत्तरगया", place: "village", nearest_town_or_city: "बिदुर", connected_before: true, connected_after: false },
    { name: "कालिका", place: "village", nearest_town_or_city: "बिदुर", connected_before: true, connected_after: false },
    { name: "लिखु", place: "village", nearest_town_or_city: "बिदुर", connected_before: true, connected_after: false },
    { name: "OSM-340415956", place: "village", nearest_town_or_city: "बेलकोटगढी", connected_before: true, connected_after: false },
    { name: "OSM-340415958", place: "village", nearest_town_or_city: "गल्छी", connected_before: true, connected_after: false }
  ],
  limitations: [
    "The flood output is a modelled potential inundation candidate, not confirmed physical damage.",
    "Post-event Sentinel-2 optical imagery is cloud contaminated in parts of the AOI.",
    "Potentially affected assets are not confirmed destroyed or damaged.",
    "Potentially cut-off settlements are modelled road-network disconnections, not confirmed real-world isolation.",
    "Hospital connectivity was not included because the historical hospital query was unavailable; town/city hubs were used."
  ],
  data_provenance: {
    sentinel: "Copernicus Sentinel-1 / Sentinel-2",
    dem: "Copernicus DEM",
    osm: "© OpenStreetMap contributors",
    osm_snapshot: "2026-07-27",
    analysis_status: "prototype / educational"
  }
};

const cache = new Map<string, any>();

async function fetchJson<T>(url: string, fallback: T): Promise<T> {
  if (cache.has(url)) {
    return cache.get(url) as T;
  }
  try {
    const res = await fetch(url);
    if (!res.ok) {
      console.warn(`Failed to fetch ${url}, using fallback`);
      return fallback;
    }
    const data = await res.json();
    cache.set(url, data);
    return data;
  } catch (err) {
    console.warn(`Error loading ${url}:`, err);
    return fallback;
  }
}

async function fetchText(url: string, fallback: string): Promise<string> {
  if (cache.has(url)) {
    return cache.get(url) as string;
  }
  try {
    const res = await fetch(url);
    if (!res.ok) return fallback;
    const text = await res.text();
    cache.set(url, text);
    return text;
  } catch (err) {
    return fallback;
  }
}

export const dataLoader = {
  // 1. Evidence JSON (grounding single source of truth)
  async getEvidence(): Promise<EvidenceData> {
    return fetchJson<EvidenceData>("/data/evidence.json", FALLBACK_EVIDENCE);
  },

  // 2. Asset Summary V3
  async getAssetsSummary(): Promise<AssetsSummaryV3> {
    return fetchJson<AssetsSummaryV3>("/data/assets_summary_v3.json", {
      summary_version: "v3",
      flood_candidate_source: "v3_flood_polygons.geojson",
      potentially_affected_buildings: 195,
      potentially_affected_roads: 115,
      potentially_affected_bridges: 13,
      notes: "Assets overlapping V3 flood candidate polygons."
    });
  },

  // 3. Connectivity Summary V4
  async getConnectivitySummary(): Promise<ConnectivitySummaryV4> {
    return fetchJson<ConnectivitySummaryV4>("/data/connectivity_summary_v4.json", {
      analysis_version: "V4",
      vehicle_accessible_ways: 4405,
      v3_affected_road_features: 115,
      disrupted_road_segments: 3748,
      pre_event_components: 181,
      post_event_components: 252,
      settlements_available: 600,
      settlements_analysed: 589,
      town_city_hubs: 3,
      potentially_cut_off_settlements: 18,
      match_tolerance_m: 5,
      settlement_snap_distance_m: 500,
      interpretation: "Modelled road-network connectivity result."
    });
  },

  // 4. English & Nepali Situation Reports
  async getEnglishReport(): Promise<string> {
    return fetchText("/data/report_en.md", "# Trishuli Flood — Situation Report\n\nLoading report...");
  },

  async getNepaliReport(): Promise<string> {
    return fetchText("/data/report_ne.md", "# त्रिशूली बाढी — स्थिति प्रतिवेदन\n\nलोड हुँदैछ...");
  },

  // 5. GeoJSON paths (MapLibre source endpoints parameterized by run)
  getGeoJsonUrls(runId?: string) {
    if (!runId || runId === "trishuli_benchmark_verified") {
      return {
        floodPolygons: "/data/flood_polygons_v3.geojson",
        buildings: "/data/buildings_affected_v3.geojson",
        roads: "/data/roads_affected_v3.geojson",
        bridges: "/data/bridges_affected_v3.geojson",
        settlements: "/data/settlements_cutoff_v4.geojson",
        connectivityNetwork: "/data/settlement_connectivity_v4.json",
      };
    }
    const base = `/data/pipeline_runs/${runId}`;
    return {
      floodPolygons: `${base}/vectors/final_flood_candidate_v3.geojson`,
      buildings: `${base}/assets/potentially_affected_buildings.geojson`,
      roads: `${base}/assets/potentially_affected_roads.geojson`,
      bridges: `${base}/assets/potentially_affected_bridges.geojson`,
      settlements: `${base}/connectivity/potentially_cut_off_settlements.geojson`,
      connectivityNetwork: `${base}/connectivity/connectivity_summary.json`,
    };
  },

  // 6. Direct GeoJSON FeatureCollection fetchers
  async getGeoJson(layer: "floodPolygons" | "buildings" | "roads" | "bridges" | "settlements", runId?: string): Promise<any> {
    const urls = this.getGeoJsonUrls(runId);
    return fetchJson(urls[layer], { type: "FeatureCollection", features: [] });
  },

  // 7. Phase 5 Orchestrator: Pipeline Runs Registry
  async getPipelineRuns(): Promise<RunRegistryEntry[]> {
    return fetchJson<RunRegistryEntry[]>("/data/pipeline_runs.json", [
      {
        run_id: "trishuli_benchmark_verified",
        title: "Trishuli Benchmark (2026-08-28)",
        status: "PARTIAL_RUN_OPTICAL_UNCONFIRMED",
        message: "SAR analysis completed; optical verification limited by cloud cover.",
        provenance_mode: "VERIFIED_TRISHULI_BENCHMARK_CACHE",
        bbox: [84.90, 27.75, 85.25, 28.05],
        flood_date: "2026-08-28",
        timestamp_utc: "2026-10-09T09:42:58.580692+00:00",
        manifest_relative_path: "/data/pipeline_runs/trishuli_benchmark_verified/run_manifest.json"
      }
    ]);
  },

  // 8. Phase 5 Orchestrator: Run Manifest Loader
  async getRunManifest(runIdOrPath: string): Promise<RunManifest | null> {
    const url = runIdOrPath.startsWith("/")
      ? runIdOrPath
      : `/data/pipeline_runs/${runIdOrPath}/run_manifest.json`;
    return fetchJson<RunManifest | null>(url, null);
  },

  // 9. Phase 5 Orchestrator: Run Evidence Loader (Run-specific fallback, never Trishuli)
  async getRunEvidence(runId: string): Promise<EvidenceData> {
    if (!runId || runId === "trishuli_benchmark_verified") {
      return fetchJson<EvidenceData>("/data/pipeline_runs/trishuli_benchmark_verified/evidence.json", FALLBACK_EVIDENCE);
    }
    const url = `/data/pipeline_runs/${runId}/evidence.json`;
    const honestRunFallback: EvidenceData = {
      project: "FloodSpaceAI",
      track: "Track B — Mapping Flood Damage from Space",
      case_study: {
        event: `Run ${runId}`,
        analysis_area: `Custom AOI`,
        osm_snapshot: "N/A"
      },
      flood_mapping: {
        method: "Copernicus Sentinel Analysis",
        candidate_version: "V3",
        flood_pixels: 0,
        flood_polygons: 0
      },
      potentially_affected_assets: {
        buildings: 0,
        roads: 0,
        bridges: 0
      },
      road_connectivity: {
        settlements_available: 0,
        settlements_analysed: 0,
        town_city_hubs: 0,
        potentially_cut_off_settlements: 0,
        pre_event_components: 0,
        post_event_components: 0
      },
      cut_off_settlements: [],
      limitations: [
        "Analytical evidence generated strictly for this isolated run."
      ],
      data_provenance: {
        sentinel: "Copernicus Sentinel",
        dem: "Copernicus DEM",
        osm: "OpenStreetMap",
        osm_snapshot: "N/A",
        analysis_status: "isolated run"
      }
    };
    return fetchJson<EvidenceData>(url, honestRunFallback);
  },

  // 10. Phase 5 Orchestrator: Run Situation Report Loader
  async getRunReport(runId: string, lang: "en" | "ne"): Promise<string> {
    const filename = lang === "en" ? "situation_report_en.md" : "situation_report_ne.md";
    const url = `/data/pipeline_runs/${runId}/${filename}`;
    const defaultNotice = lang === "en"
      ? `# Situation Report — Run ${runId}\n\nEvidence and reports are scoped specifically to this run.`
      : `# स्थिति प्रतिवेदन — Run ${runId}\n\nयस रनको लागि प्रतिवेदन तयार हुँदैछ।`;
    const fallback = (!runId || runId === "trishuli_benchmark_verified")
      ? (lang === "en" ? await this.getEnglishReport() : await this.getNepaliReport())
      : defaultNotice;
    return fetchText(url, fallback);
  }
};
