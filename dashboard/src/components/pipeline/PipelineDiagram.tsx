"use client";

import React, { useState } from "react";
import { usePipelineRun } from "@/data/RunContext";
import type { PipelineStageInfo } from "@/data/types";

interface PipelineNode {
  id: string;
  stage: number;
  title: string;
  subtitle: string;
  sensorOrSource: string;
  inputs: string[];
  outputs: string[];
  method: string;
  thresholds: string;
}

const PIPELINE_NODES: PipelineNode[] = [
  {
    id: "node-s1",
    stage: 1,
    title: "Sentinel-1 SAR acquisition",
    subtitle: "All-weather C-band radar",
    sensorOrSource: "ESA Copernicus Sentinel-1A (IW mode, VV+VH)",
    inputs: ["S1A Pre (2026-08-16, Orbit 85)", "S1A Post (2026-08-28, Orbit 85)"],
    outputs: ["Calibrated gamma0 backscatter rasters"],
    method: "Radiometric calibration to sigma0/gamma0, thermal noise removal, and range Doppler terrain correction using Copernicus DEM 30m.",
    thresholds: "Resolution: 10m · Pixel spacing: 10m · Polarizations: VV, VH",
  },
  {
    id: "node-filter",
    stage: 2,
    title: "3×3 median speckle filtering & change detection",
    subtitle: "Radar backscatter difference",
    sensorOrSource: "Python GDAL / scipy.ndimage pipeline",
    inputs: ["Pre/Post VV & VH rasters"],
    outputs: ["filtered_vv_change_db.tif", "filtered_vh_change_db.tif"],
    method: "Applied 3×3 median filter (scipy.ndimage.median_filter) to pre- and post-event VV and VH SAR amplitude rasters to suppress coherent speckle noise while preserving riverbank edge sharpness. Logarithmic difference computes backscatter change: Δσ° = σ°_post - σ°_pre (dB).",
    thresholds: "Change dynamic range: -6.0 dB to +6.0 dB · Water threshold: ΔVV < -2.5 dB",
  },
  {
    id: "node-s2",
    stage: 3,
    title: "Sentinel-2 optical acquisition",
    subtitle: "High-resolution multispectral",
    sensorOrSource: "Copernicus Sentinel-2 MSI (Level-2A BOA)",
    inputs: ["S2 Pre (2026-08-12 cloud-free)", "S2 Post (2026-08-27 cloud-limited)"],
    outputs: ["Bands B3 (Green), B8 (NIR), Scene Classification Layer (SCL)"],
    method: "Surface reflectance retrieval with atmospheric correction. SCL cloud-mask filter isolates cloud-free river valley sectors.",
    thresholds: "Resolution: 10m (B3, B8) · SCL cloud confidence mask applied",
  },
  {
    id: "node-ndwi",
    stage: 4,
    title: "NDWI water index change",
    subtitle: "Normalized difference water index",
    sensorOrSource: "Green vs NIR optical band ratio",
    inputs: ["B03 Green (560 nm)", "B08 NIR (842 nm)"],
    outputs: ["ndwi_change_20260827_vs_20260812.tif"],
    method: "NDWI = (Green - NIR) / (Green + NIR). Water exhibits positive NDWI values; vegetated terrain exhibits negative NDWI.",
    thresholds: "Water threshold: NDWI > 0.0 · Change threshold: ΔNDWI > +0.15",
  },
  {
    id: "node-v3",
    stage: 5,
    title: "V3 candidate multi-sensor fusion",
    subtitle: "Inundation mask refinement",
    sensorOrSource: "Multi-criteria spatial logic",
    inputs: ["SAR change", "NDWI change", "Copernicus DEM slope mask"],
    outputs: ["final_flood_candidate_v3.tif", "v3_flood_polygons.geojson"],
    method: "Logical combination: (ΔVV < -2.5 dB OR ΔNDWI > +0.15) AND (Post water == 1) AND (Pre water == 0) AND (Slope < 12°). Connected-component 8-neighbor sieve removes solitary noise pixels.",
    thresholds: "Minimum cluster size: 10 pixels · Total result: 1,286 px / 84 polygons",
  },
  {
    id: "node-osm",
    stage: 6,
    title: "OpenStreetMap snapshot",
    subtitle: "Pre-event baseline infrastructure",
    sensorOrSource: "Overpass API historical snapshot",
    inputs: ["Snapshot timestamp: 2026-07-27T00:00:00Z"],
    outputs: ["Buildings (6,400+), Roads (4,405 ways), Bridges (34 crossings)"],
    method: "Historical Overpass query extracts authentic pre-event infrastructure topology, ensuring assets were intact before the monsoon surge.",
    thresholds: "AOI bounding box: [84.90, 27.75, 85.25, 28.05]",
  },
  {
    id: "node-assets",
    stage: 7,
    title: "Asset impact intersection",
    subtitle: "2D spatial overlay",
    sensorOrSource: "OGR / Shapely geometric predicate",
    inputs: ["V3 Flood Polygons", "OSM Infrastructure Layers"],
    outputs: ["potentially_affected_buildings_v3", "potentially_affected_roads_v3", "potentially_affected_bridges_v3"],
    method: "Geometric ST_Intersects and ST_Overlaps testing against building footprint polygons and road linear networks.",
    thresholds: "Result: 195 buildings, 115 road features, 13 bridges",
  },
  {
    id: "node-graph",
    stage: 8,
    title: "Road network graph construction",
    subtitle: "Topological transport model",
    sensorOrSource: "NetworkX directed multigraph",
    inputs: ["Vehicle-accessible road ways", "589 settlement nodes"],
    outputs: ["pre_event_road_graph (181 components)"],
    method: "LineString snapping to junction nodes with 5-meter tolerance. Settlements snapped to nearest accessible road vertex within 500 meters.",
    thresholds: "4,405 vehicle ways · 3,748 edge segments · 3 hubs (Bidur, Galchhi, Belkotgadhi)",
  },
  {
    id: "node-v4",
    stage: 9,
    title: "V4 connectivity severance",
    subtitle: "Graph reachability analysis",
    sensorOrSource: "Dijkstra / BFS path validation",
    inputs: ["Pre-event graph", "115 flooded road edges"],
    outputs: ["potentially_cut_off_settlements_v4.geojson", "252 post-event components"],
    method: "Removing inundated road edges creates subgraph G_post. For each settlement s, check if path exists to designated hub in G_pre and G_post.",
    thresholds: "Result: 18 settlements connected in G_pre but disconnected in G_post",
  },
  {
    id: "node-copilot",
    stage: 10,
    title: "Grounded Gemini Copilot",
    subtitle: "Numerical validation & synthesis",
    sensorOrSource: "Gemini 2.5/Flash + Deterministic validator",
    inputs: ["situation_report_evidence.json"],
    outputs: ["situation_report_en.md", "situation_report_ne.md"],
    method: "Report synthesis where all quantitative assertions are regex-extracted and compared against evidence JSON. Discrepancies trigger deterministic template fallback.",
    thresholds: "100% numerical adherence · Zero ungrounded statistics allowed",
  },
];

const STAGE_KEYS: Array<{ key: string; num: number; label: string }> = [
  { key: "stage_1_input_validation", num: 1, label: "Input Validation" },
  { key: "stage_2_satellite_discovery", num: 2, label: "Satellite Discovery" },
  { key: "stage_3_satellite_acquisition", num: 3, label: "Satellite Acquisition" },
  { key: "stage_4_raster_processing", num: 4, label: "SAR & Optical Processing" },
  { key: "stage_5_historical_osm", num: 5, label: "Historical OSM Ingestion" },
  { key: "stage_6_asset_connectivity", num: 6, label: "Asset & Connectivity" },
  { key: "stage_7_situation_evidence", num: 7, label: "Situation Evidence" },
  { key: "stage_8_publish_manifest", num: 8, label: "Manifest Publishing" },
];

export default function PipelineDiagram() {
  const { manifest, activeRun, selectedRunId } = usePipelineRun();
  const [selectedNode, setSelectedNode] = useState<PipelineNode>(PIPELINE_NODES[0]);
  const [activeStageKey, setActiveStageKey] = useState<string>("stage_1_input_validation");

  const runTitle = manifest?.title || activeRun?.title || `Run ${selectedRunId}`;
  const overallStatus = manifest?.overall_status || activeRun?.status || "PENDING";
  const overallMsg = manifest?.overall_message || activeRun?.message || "";
  const stages = manifest?.stages || {};

  const getStageBadge = (status?: string) => {
    switch (status) {
      case "SUCCESS":
        return { label: "SUCCESS", bg: "rgba(46, 111, 158, 0.15)", fg: "var(--river)", border: "var(--river)" };
      case "PARTIAL":
        return { label: "PARTIAL", bg: "rgba(185, 138, 62, 0.15)", fg: "#926818", border: "#B98A3E" };
      case "UNAVAILABLE":
        return { label: "UNAVAILABLE", bg: "rgba(100, 116, 139, 0.15)", fg: "#475569", border: "#94a3b8" };
      case "FAILED":
        return { label: "FAILED", bg: "var(--brick-light)", fg: "var(--brick)", border: "var(--brick)" };
      case "SKIPPED":
        return { label: "SKIPPED", bg: "var(--fog)", fg: "var(--ink-muted)", border: "var(--slate-subtle)" };
      default:
        return { label: status || "PENDING", bg: "var(--fog)", fg: "var(--ink-muted)", border: "var(--slate-subtle)" };
    }
  };

  const selectedStage = (stages as any)[activeStageKey] as PipelineStageInfo | undefined;

  return (
    <div
      style={{
        padding: "24px",
        maxWidth: "1140px",
        margin: "0 auto",
      }}
    >
      {/* Header */}
      <div style={{ marginBottom: "20px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
          <span className="survey-badge survey-badge-river" style={{ fontSize: "11px" }}>
            Phase 5 Orchestrator
          </span>
          <span className="survey-badge" style={{ fontSize: "11px", backgroundColor: "var(--fog)" }}>
            {runTitle}
          </span>
        </div>
        <h2
          style={{
            fontFamily: "var(--font-serif)",
            fontSize: "24px",
            fontWeight: 600,
            color: "var(--ink)",
            margin: "4px 0",
          }}
        >
          End-to-end evidence & data processing pipeline
        </h2>
        <p style={{ fontSize: "13px", color: "var(--ink-secondary)", margin: 0 }}>
          Interactive trace of the 8-stage automated pipeline execution for the active run, alongside the 10-stage scientific methodology.
        </p>
      </div>

      {/* Phase 5 Live Orchestrator Execution State Panel */}
      <div
        className="survey-panel"
        style={{
          padding: "16px 20px",
          marginBottom: "24px",
          backgroundColor: "var(--paper-elevated)",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            marginBottom: "12px",
            paddingBottom: "10px",
            borderBottom: "1px solid var(--slate-subtle)",
            flexWrap: "wrap",
            gap: "8px",
          }}
        >
          <div>
            <span
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "11px",
                fontWeight: 600,
                color: "var(--ink-secondary)",
                textTransform: "uppercase",
              }}
            >
              Active Run Execution Trace · Run ID: {selectedRunId}
            </span>
            <div style={{ fontSize: "13px", color: "var(--ink)", marginTop: "2px", fontWeight: 500 }}>
              {overallMsg}
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span
              style={{
                padding: "3px 9px",
                borderRadius: "var(--radius-sm)",
                fontFamily: "var(--font-mono)",
                fontSize: "11px",
                fontWeight: 700,
                backgroundColor: overallStatus.includes("SUCCESS")
                  ? "rgba(46, 111, 158, 0.15)"
                  : overallStatus.includes("PARTIAL")
                  ? "rgba(185, 138, 62, 0.15)"
                  : overallStatus.includes("UNAVAILABLE")
                  ? "rgba(100, 116, 139, 0.15)"
                  : "var(--brick-light)",
                color: overallStatus.includes("SUCCESS")
                  ? "var(--river)"
                  : overallStatus.includes("PARTIAL")
                  ? "#926818"
                  : overallStatus.includes("UNAVAILABLE")
                  ? "#475569"
                  : "var(--brick)",
                border: "1px solid currentColor",
              }}
            >
              Overall: {overallStatus}
            </span>
          </div>
        </div>

        {/* 8-Stage Execution Grid */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
            gap: "10px",
            marginBottom: "14px",
          }}
        >
          {STAGE_KEYS.map(({ key, num, label }) => {
            const stageData = (stages as any)[key] as PipelineStageInfo | undefined;
            const stageStatus = stageData?.status || "PENDING";
            const badge = getStageBadge(stageStatus);
            const isSelected = activeStageKey === key;

            return (
              <div
                key={key}
                onClick={() => setActiveStageKey(key)}
                style={{
                  padding: "10px 12px",
                  borderRadius: "var(--radius-sm)",
                  border: isSelected ? "2px solid var(--river)" : "1px solid var(--slate-light)",
                  backgroundColor: isSelected ? "var(--paper)" : "var(--fog)",
                  cursor: "pointer",
                  transition: "var(--t-smooth)",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "4px" }}>
                  <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--ink-secondary)" }}>
                    Stage {num}
                  </span>
                  <span
                    style={{
                      fontSize: "10px",
                      fontFamily: "var(--font-mono)",
                      fontWeight: 600,
                      padding: "1px 6px",
                      borderRadius: "3px",
                      backgroundColor: badge.bg,
                      color: badge.fg,
                      border: `1px solid ${badge.border}`,
                    }}
                  >
                    {badge.label}
                  </span>
                </div>
                <div style={{ fontWeight: 600, fontSize: "12px", color: "var(--ink)", marginBottom: "2px" }}>
                  {label}
                </div>
                <div
                  style={{
                    fontSize: "11px",
                    color: "var(--ink-secondary)",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                  title={stageData?.message}
                >
                  {stageData?.message || "No telemetry recorded"}
                </div>
                {stageData?.duration_s !== undefined && (
                  <div style={{ fontSize: "10px", fontFamily: "var(--font-mono)", color: "var(--ink-muted)", marginTop: "4px" }}>
                    Duration: {stageData.duration_s.toFixed(3)}s
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Selected Stage Detail Inspector */}
        {selectedStage && (
          <div
            style={{
              padding: "12px 14px",
              backgroundColor: "var(--paper)",
              borderRadius: "var(--radius-sm)",
              border: "1px solid var(--slate-light)",
              fontSize: "12px",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
              <span style={{ fontWeight: 600, color: "var(--ink)" }}>
                {selectedStage.stage || activeStageKey}:
              </span>
              <span style={{ color: "var(--ink-secondary)" }}>{selectedStage.message}</span>
            </div>
            {selectedStage.provenance_mode && (
              <div style={{ fontSize: "11px", fontFamily: "var(--font-mono)", color: "var(--ink-muted)" }}>
                Provenance Mode: {selectedStage.provenance_mode}
              </div>
            )}
            {selectedStage.files && Object.keys(selectedStage.files).length > 0 && (
              <div style={{ marginTop: "6px" }}>
                <span style={{ fontSize: "11px", fontWeight: 600, color: "var(--ink-secondary)" }}>Artifacts: </span>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--river-dark)" }}>
                  {Object.entries(selectedStage.files)
                    .map(([k, v]) => `${k}: ${v.split(/[\\/]/).pop()}`)
                    .join(" · ")}
                </span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Main 2-Column: Left Flowchart, Right Detail Inspector */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1.2fr 0.8fr",
          gap: "18px",
          alignItems: "start",
        }}
      >
        {/* Left Column: Interactive Node Cards Chain */}
        <div
          className="survey-panel"
          style={{
            padding: "16px",
            display: "flex",
            flexDirection: "column",
            gap: "10px",
            maxHeight: "680px",
            overflowY: "auto",
          }}
        >
          {PIPELINE_NODES.map((node) => {
            const isSelected = selectedNode.id === node.id;
            return (
              <div
                key={node.id}
                onClick={() => setSelectedNode(node)}
                style={{
                  padding: "10px 14px",
                  borderRadius: "var(--radius-sm)",
                  border: isSelected ? "2px solid var(--river)" : "1px solid var(--slate-light)",
                  backgroundColor: isSelected ? "var(--paper-elevated)" : "var(--fog)",
                  boxShadow: isSelected ? "var(--shadow-panel)" : "none",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  transition: "var(--t-smooth)",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <span
                    style={{
                      fontFamily: "var(--font-mono)",
                      fontSize: "11px",
                      fontWeight: 700,
                      color: isSelected ? "var(--river)" : "var(--ink-muted)",
                      backgroundColor: "var(--paper)",
                      padding: "2px 6px",
                      borderRadius: "3px",
                      border: "1px solid var(--slate-subtle)",
                    }}
                  >
                    Stage {node.stage}
                  </span>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: "13px", color: "var(--ink)" }}>
                      {node.title}
                    </div>
                    <div style={{ fontSize: "11px", color: "var(--ink-secondary)" }}>
                      {node.subtitle}
                    </div>
                  </div>
                </div>

                <span
                  style={{
                    fontSize: "10px",
                    fontFamily: "var(--font-mono)",
                    color: "var(--ink-muted)",
                  }}
                >
                  {node.stage < 10 ? "↓" : "Done"}
                </span>
              </div>
            );
          })}
        </div>

        {/* Right Column: Detailed Node Inspector */}
        <div
          className="survey-panel"
          style={{
            position: "sticky",
            top: "20px",
          }}
        >
          <div className="survey-panel-header">
            <span style={{ fontFamily: "var(--font-serif)", fontSize: "14px", fontWeight: 600 }}>
              Methodology details
            </span>
            <span className="survey-badge survey-badge-river" style={{ fontSize: "10px" }}>
              Stage {selectedNode.stage} of 10
            </span>
          </div>

          <div style={{ padding: "18px" }}>
            <h3
              style={{
                fontFamily: "var(--font-serif)",
                fontSize: "18px",
                fontWeight: 600,
                color: "var(--ink)",
                margin: "0 0 4px 0",
              }}
            >
              {selectedNode.title}
            </h3>
            <div style={{ fontSize: "12px", color: "var(--river)", fontWeight: 500, marginBottom: "14px" }}>
              {selectedNode.sensorOrSource}
            </div>

            {/* Scientific Method */}
            <div style={{ marginBottom: "14px" }}>
              <div style={{ fontSize: "11px", color: "var(--ink-muted)", textTransform: "uppercase", marginBottom: "4px" }}>
                Scientific Method & Algorithmic Principle
              </div>
              <p style={{ margin: 0, fontSize: "13px", color: "var(--ink-secondary)", lineHeight: 1.6 }}>
                {selectedNode.method}
              </p>
            </div>

            {/* Thresholds & Parameters */}
            <div
              style={{
                backgroundColor: "var(--fog)",
                padding: "10px 12px",
                borderRadius: "var(--radius-sm)",
                border: "1px solid var(--slate-subtle)",
                marginBottom: "14px",
              }}
            >
              <div style={{ fontSize: "10px", color: "var(--ink-muted)", textTransform: "uppercase", marginBottom: "3px" }}>
                Operational Thresholds & Resolution
              </div>
              <div style={{ fontSize: "12px", fontFamily: "var(--font-mono)", color: "var(--ink)" }}>
                {selectedNode.thresholds}
              </div>
            </div>

            {/* Inputs & Outputs */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", fontSize: "12px" }}>
              <div>
                <div style={{ fontSize: "10px", color: "var(--ink-muted)", textTransform: "uppercase", marginBottom: "3px" }}>
                  Inputs
                </div>
                <ul style={{ margin: 0, paddingLeft: "16px", color: "var(--ink-secondary)", fontSize: "11px" }}>
                  {selectedNode.inputs.map((inp, i) => (
                    <li key={i}>{inp}</li>
                  ))}
                </ul>
              </div>

              <div>
                <div style={{ fontSize: "10px", color: "var(--ink-muted)", textTransform: "uppercase", marginBottom: "3px" }}>
                  Outputs
                </div>
                <ul style={{ margin: 0, paddingLeft: "16px", color: "var(--ink)", fontWeight: 500, fontSize: "11px" }}>
                  {selectedNode.outputs.map((out, i) => (
                    <li key={i}>{out}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
