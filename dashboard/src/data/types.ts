// ============================================================
// FloodSpaceAI — Data & Pipeline Interfaces
// ============================================================

export interface GroundedClaim {
  claim_id: string;
  claim_text: string;
  value: number | string | boolean;
  unit: string;
  geographic_scope: string;
  source_file: string;
  source_field: string;
  run_id: string;
  data_provenance: string;
  confidence_or_uncertainty: string;
  interpretation_guidance: string;
}

export interface EvidenceData {
  project: string;
  track: string;
  run_id?: string;
  case_study: {
    event: string;
    analysis_area: string;
    osm_snapshot: string;
    provenance_mode?: string;
  };
  flood_mapping: {
    method: string;
    candidate_version: string;
    flood_pixels: number;
    flood_polygons: number;
    flood_clusters?: number;
    candidate_area_ha?: number;
  };
  potentially_affected_assets: {
    buildings: number;
    roads: number;
    bridges: number;
    road_length_km?: number;
  };
  road_connectivity: {
    settlements_available?: number;
    settlements_analysed: number;
    town_city_hubs?: number;
    potentially_cut_off_settlements: number;
    pre_event_components: number;
    post_event_components: number;
    vehicle_accessible_ways?: number;
    disrupted_road_segments?: number;
    hospital_data_available?: boolean;
  };
  cut_off_settlements?: Array<{
    name: string;
    place: string;
    nearest_town_or_city: string;
    connected_before: boolean;
    connected_after: boolean;
  }>;
  grounded_claims?: GroundedClaim[];
  road_impact?: {
    v1_reference_only?: {
      potentially_affected_features: number;
      potentially_affected_length_km: number;
    };
    note?: string;
  };
  limitations: string[];
  data_provenance: {
    sentinel?: string;
    sentinel_sar?: string;
    sentinel_optical?: string;
    dem: string;
    osm: string;
    osm_snapshot: string;
    analysis_status?: string;
    provenance_mode?: string;
  };
}

export interface AssetsSummaryV3 {
  summary_version: string;
  flood_candidate_source: string;
  potentially_affected_buildings: number;
  potentially_affected_roads: number;
  potentially_affected_bridges: number;
  notes: string;
}

export interface ConnectivitySummaryV4 {
  analysis_version: string;
  vehicle_accessible_ways: number;
  v3_affected_road_features: number;
  disrupted_road_segments: number;
  pre_event_components: number;
  post_event_components: number;
  settlements_available: number;
  settlements_analysed: number;
  town_city_hubs: number;
  potentially_cut_off_settlements: number;
  match_tolerance_m: number;
  settlement_snap_distance_m: number;
  interpretation: string;
}

export interface GroundingValidation {
  validated_against_evidence: boolean;
  extracted_claims?: Record<string, string | number>;
  status?: string;
}

export type TabId = 
  | "map" 
  | "satellite" 
  | "assets" 
  | "connectivity" 
  | "copilot" 
  | "pipeline" 
  | "provenance";

export interface TourStep {
  stepIndex: number;
  tab: TabId;
  title: string;
  explanation: string;
  focusTarget?: string;
  durationSeconds: number;
}

// ============================================================
// Phase 5 Orchestrator & Manifest Types
// ============================================================

export interface RunRegistryEntry {
  run_id: string;
  title: string;
  status: string;
  message: string;
  provenance_mode: string;
  bbox: [number, number, number, number];
  flood_date: string;
  timestamp_utc: string;
  metrics?: Record<string, any>;
  manifest_relative_path: string;
}

export interface PipelineStageInfo {
  stage: string;
  status: "SUCCESS" | "PARTIAL" | "UNAVAILABLE" | "FAILED" | "SKIPPED";
  duration_s?: number;
  message?: string;
  provenance_mode?: string;
  files?: Record<string, string>;
  rasters?: Record<string, string>;
  vectors?: Record<string, string>;
  details?: Record<string, any>;
  valid_optical_percentage?: number;
  optical_confirmation?: string;
  v3_flood_metrics?: Record<string, any>;
  snapshot_timestamp?: string;
  provider?: string;
  attribution?: string;
  files_used?: Record<string, string>;
  metrics?: Record<string, any>;
  [key: string]: any;
}

export interface RunManifest {
  schema_version: string;
  run_id: string;
  title: string;
  overall_status: string;
  overall_message: string;
  provenance_mode: string;
  timestamp_utc: string;
  inputs: {
    bbox: [number, number, number, number];
    flood_date: string;
    snapshot_date?: string | null;
  };
  stages: {
    stage_1_input_validation?: PipelineStageInfo;
    stage_2_satellite_discovery?: PipelineStageInfo;
    stage_3_satellite_acquisition?: PipelineStageInfo;
    stage_4_raster_processing?: PipelineStageInfo;
    stage_5_historical_osm?: PipelineStageInfo;
    stage_6_asset_connectivity?: PipelineStageInfo;
    stage_7_situation_evidence?: PipelineStageInfo;
    stage_8_publish_manifest?: PipelineStageInfo;
    [key: string]: any;
  };
  metrics: {
    candidate_flood_pixels?: number;
    candidate_flood_clusters?: number;
    candidate_flood_area_ha?: number;
    potentially_affected_buildings?: number;
    total_mapped_buildings?: number;
    potentially_affected_roads?: number;
    potentially_affected_road_length_km?: number;
    potentially_affected_bridges?: number;
    total_mapped_bridges?: number;
    disrupted_road_segments?: number;
    pre_event_components?: number;
    post_event_components?: number;
    settlements_analysed?: number;
    potentially_cut_off_settlements?: number;
    hospital_data_available?: boolean;
    [key: string]: any;
  };
  limitations: string[];
  attributions: {
    copernicus_sentinel: string;
    copernicus_dem: string;
    openstreetmap: string;
    validation_isolation: string;
    [key: string]: any;
  };
}
