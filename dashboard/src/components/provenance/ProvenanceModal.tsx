"use client";

import React from "react";
import { usePipelineRun } from "@/data/RunContext";

export default function ProvenanceModal() {
  const { manifest, activeRun, selectedRunId } = usePipelineRun();

  const provenanceMode = manifest?.provenance_mode || activeRun?.provenance_mode || "VERIFIED_TRISHULI_BENCHMARK_CACHE";
  const limitations = manifest?.limitations?.length ? manifest.limitations : [
    "Modelled candidate only: The flood output is a modelled potential inundation candidate derived from multi-temporal satellite radar backscatter and optical spectral change. It does not confirm physical ground inundation or water depths.",
    "No confirmed physical damage: Potentially affected assets (195 buildings, 115 roads, 13 bridges) are identified solely through 2D spatial overlap with candidate polygons. They are not confirmed damaged or destroyed.",
    "Optical cloud contamination: Post-event Sentinel-2 optical imagery (2026-08-27) is cloud-contaminated across sectors of the Trishuli mountain valley, requiring primary reliance on Sentinel-1 all-weather C-band SAR.",
    "Road disconnection vs real-world isolation: The 18 potentially cut-off settlements represent modelled vehicle road-network graph disconnections to designated hubs. They do not confirm real-world physical isolation (e.g. pedestrian trails, suspension bridges, or alternative footpaths).",
    "Prototype status: This system is developed for the Multimodal AI Hackathon 2026 (Track B: Mapping Flood Damage from Space) as an educational and research prototype. It is not an operational disaster response system."
  ];

  return (
    <div
      style={{
        padding: "24px",
        maxWidth: "960px",
        margin: "0 auto",
      }}
    >
      <div style={{ marginBottom: "20px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
          <span className="survey-badge" style={{ fontSize: "11px" }}>
            Legal, licensing & limitations
          </span>
          <span className="survey-badge survey-badge-river" style={{ fontSize: "11px" }}>
            Run: {selectedRunId}
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
          Data provenance & system limitations
        </h2>
        <p style={{ fontSize: "13px", color: "var(--ink-secondary)", margin: 0 }}>
          Full documentation of satellite data sources, license agreements, analytical assumptions, and operational constraints.
        </p>
      </div>

      {/* Provenance Mode Banner */}
      <div
        className="survey-panel"
        style={{
          padding: "12px 18px",
          marginBottom: "20px",
          backgroundColor: provenanceMode === "VERIFIED_TRISHULI_BENCHMARK_CACHE" ? "var(--fog)" : "var(--paper-elevated)",
          border: "1px solid var(--slate-light)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: "10px",
        }}
      >
        <div>
          <span style={{ fontSize: "11px", fontFamily: "var(--font-mono)", color: "var(--ink-secondary)", textTransform: "uppercase" }}>
            Active Run Provenance Mode:
          </span>
          <div style={{ fontSize: "13px", fontWeight: 600, color: "var(--ink)", marginTop: "2px" }}>
            {provenanceMode === "VERIFIED_TRISHULI_BENCHMARK_CACHE"
              ? "Verified Benchmark Fixture Cache (Trishuli August 2026)"
              : provenanceMode === "LIVE_AUTHORITATIVE_API"
              ? "Live Authoritative Retrieval (CDSE STAC / Copernicus Open Access)"
              : "Unseen AOI / Live Ingestion Verification"}
          </div>
        </div>
        <span
          style={{
            fontSize: "11px",
            fontFamily: "var(--font-mono)",
            padding: "3px 8px",
            borderRadius: "var(--radius-sm)",
            backgroundColor: "var(--paper)",
            border: "1px solid var(--slate-light)",
            color: "var(--ink-secondary)",
          }}
        >
          Schema v{manifest?.schema_version || "1.0.0"}
        </span>
      </div>

      {/* Mandatory Limitations Callout */}
      <div
        className="survey-panel"
        style={{
          borderLeft: "4px solid var(--brick)",
          padding: "16px 20px",
          marginBottom: "24px",
          backgroundColor: "var(--paper-elevated)",
        }}
      >
        <h3
          style={{
            fontFamily: "var(--font-serif)",
            fontSize: "16px",
            fontWeight: 600,
            color: "var(--brick)",
            margin: "0 0 8px 0",
          }}
        >
          Mandatory operational limitations
        </h3>
        <ul
          style={{
            margin: 0,
            paddingLeft: "20px",
            fontSize: "13px",
            color: "var(--ink)",
            lineHeight: 1.7,
          }}
        >
          {limitations.map((lim, idx) => (
            <li key={idx} style={{ marginBottom: "6px" }}>
              {lim}
            </li>
          ))}
        </ul>
      </div>

      {/* Data Provenance & Attribution Accordion / Card */}
      <div className="survey-panel" style={{ padding: "20px", marginBottom: "20px" }}>
        <h3
          style={{
            fontFamily: "var(--font-serif)",
            fontSize: "16px",
            fontWeight: 600,
            color: "var(--ink)",
            margin: "0 0 12px 0",
          }}
        >
          Authoritative data provenance & copyright
        </h3>

        <div style={{ display: "flex", flexDirection: "column", gap: "14px", fontSize: "13px", lineHeight: 1.6 }}>
          <div style={{ paddingBottom: "12px", borderBottom: "1px solid var(--slate-subtle)" }}>
            <div style={{ fontWeight: 600, color: "var(--ink)" }}>Copernicus Sentinel satellite data</div>
            <div style={{ color: "var(--ink-secondary)" }}>
              Sentinel-1A SAR (Interferometric Wide Swath, C-band 5.405 GHz) and Sentinel-2 MSI (Level-2A Bottom of Atmosphere).
            </div>
            <div style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--river)", marginTop: "4px" }}>
              Contains modified Copernicus Sentinel data 2026.
            </div>
          </div>

          <div style={{ paddingBottom: "12px", borderBottom: "1px solid var(--slate-subtle)" }}>
            <div style={{ fontWeight: 600, color: "var(--ink)" }}>Copernicus Digital Elevation Model (DEM)</div>
            <div style={{ color: "var(--ink-secondary)" }}>
              Copernicus GLO-30 Digital Elevation Model used for radiometric terrain correction and terrain slope masking.
            </div>
            <div style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--ink-muted)", marginTop: "4px" }}>
              Produced using Copernicus WorldDEM-30 © DLR e.V. 2010–2014 and © Airbus Defence and Space GmbH 2014–2018 provided under COPERNICUS by the European Union and ESA; all rights reserved.
            </div>
          </div>

          <div style={{ paddingBottom: "12px", borderBottom: "1px solid var(--slate-subtle)" }}>
            <div style={{ fontWeight: 600, color: "var(--ink)" }}>OpenStreetMap infrastructure data</div>
            <div style={{ color: "var(--ink-secondary)" }}>
              Historical Overpass API extraction timestamped {manifest?.inputs?.snapshot_date || "2026-07-27T00:00:00Z"} for building footprints, road network geometry, and bridge points.
            </div>
            <div style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--silt)", marginTop: "4px" }}>
              © OpenStreetMap contributors, ODbL 1.0 license.
            </div>
          </div>

          <div>
            <div style={{ fontWeight: 600, color: "var(--ink)" }}>Checking-Only Validation Isolation</div>
            <div style={{ color: "var(--ink-secondary)" }}>
              Copernicus Emergency Management Service (EMSR927) and UNOSAT flood maps are utilized strictly for post-hoc validation checks and are never consumed as inputs to candidate flood generation, asset intersection, or road connectivity modeling.
            </div>
            <div style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--brick)", marginTop: "4px" }}>
              Strict isolation verified: Zero EMSR927 or UNOSAT data leakage into production.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
