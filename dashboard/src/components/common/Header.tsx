"use client";

import React from "react";
import type { TabId } from "@/data/types";
import { usePipelineRun } from "@/data/RunContext";

interface HeaderProps {
  activeTab: TabId;
  onTabChange: (tab: TabId) => void;
  onStartTour: () => void;
  isTourActive: boolean;
}

export default function Header({
  activeTab,
  onTabChange,
  onStartTour,
  isTourActive,
}: HeaderProps) {
  const { runs, selectedRunId, setSelectedRunId, activeRun, manifest } = usePipelineRun();

  const totalAssets = manifest?.metrics?.potentially_affected_buildings !== undefined
    ? (manifest.metrics.potentially_affected_buildings || 0) +
      (manifest.metrics.potentially_affected_roads || 0) +
      (manifest.metrics.potentially_affected_bridges || 0)
    : 323;

  const cutOffCount = manifest?.metrics?.potentially_cut_off_settlements !== undefined
    ? `${manifest.metrics.potentially_cut_off_settlements} cut-off`
    : "18 cut-off";

  const tabs: Array<{ id: TabId; label: string; count?: string }> = [
    { id: "map", label: "Interactive map" },
    { id: "satellite", label: "Satellite comparison" },
    { id: "assets", label: "Potentially affected assets", count: `${totalAssets}` },
    { id: "connectivity", label: "Road connectivity", count: cutOffCount },
    { id: "copilot", label: "Situation copilot" },
    { id: "pipeline", label: "Evidence pipeline" },
    { id: "provenance", label: "Data provenance & limitations" },
  ];

  // Helper for status badge styling
  const renderStatusBadge = (status?: string) => {
    if (!status) return null;
    let bg = "var(--fog)";
    let fg = "var(--ink)";
    let border = "var(--slate-light)";
    let label = status;

    if (status.startsWith("SUCCESS")) {
      bg = "rgba(46, 111, 158, 0.15)";
      fg = "var(--river)";
      border = "var(--river)";
      label = "SUCCESS";
    } else if (status.startsWith("PARTIAL")) {
      bg = "rgba(185, 138, 62, 0.15)";
      fg = "#926818";
      border = "#B98A3E";
      label = status === "PARTIAL_RUN_OPTICAL_UNCONFIRMED"
        ? "PARTIAL: Optical Clouded"
        : status === "PARTIAL_RUN_IMAGERY_UNAVAILABLE"
        ? "PARTIAL: Imagery Unavailable"
        : "PARTIAL RUN";
    } else if (status.startsWith("UNAVAILABLE")) {
      bg = "rgba(100, 116, 139, 0.15)";
      fg = "#475569";
      border = "#94a3b8";
      label = status === "UNAVAILABLE_FUTURE_DATE"
        ? "UNAVAILABLE: Future Date"
        : "UNAVAILABLE";
    } else if (status.startsWith("FAILED")) {
      bg = "var(--brick-light)";
      fg = "var(--brick)";
      border = "var(--brick)";
      label = status === "FAILED_INPUT_VALIDATION"
        ? "FAILED: Invalid Bounds"
        : "FAILED";
    }

    return (
      <span
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: "5px",
          padding: "2px 8px",
          borderRadius: "var(--radius-sm)",
          fontSize: "11px",
          fontFamily: "var(--font-mono)",
          fontWeight: 600,
          backgroundColor: bg,
          color: fg,
          border: `1px solid ${border}`,
        }}
        title={`Pipeline Status: ${status}`}
      >
        <span
          style={{
            width: "6px",
            height: "6px",
            borderRadius: "50%",
            backgroundColor: fg,
            display: "inline-block",
          }}
        />
        {label}
      </span>
    );
  };

  // Helper for provenance badge
  const renderProvenanceBadge = (mode?: string) => {
    if (!mode) return null;
    let text = mode;
    let isBenchmark = false;
    let isLive = false;

    if (mode === "VERIFIED_TRISHULI_BENCHMARK_CACHE" || mode === "BENCHMARK_VERIFIED_FIXTURE") {
      text = "Verified Benchmark Fixture";
      isBenchmark = true;
    } else if (
      mode === "LIVE_AUTHORITATIVE_SATELLITE_RETRIEVAL" ||
      mode === "LIVE_AUTHORITATIVE_API"
    ) {
      text = "Verified Live Satellite Retrieval";
      isLive = true;
    } else if (mode === "UNKNOWN") {
      text = "Unseen AOI / Live Pending";
    }

    return (
      <span
        style={{
          padding: "3px 8px",
          borderRadius: "var(--radius-sm)",
          fontSize: "10px",
          fontFamily: "var(--font-mono)",
          fontWeight: 600,
          backgroundColor: isLive
            ? "rgba(46, 111, 158, 0.15)"
            : isBenchmark
            ? "var(--fog)"
            : "var(--paper-elevated)",
          color: isLive ? "var(--river)" : "var(--ink-secondary)",
          border: isLive ? "1px solid var(--river)" : "1px solid var(--slate-light)",
        }}
        title={`Provenance Mode: ${mode}`}
      >
        {isLive ? "🛰️ " : "📁 "}
        {text}
      </span>
    );
  };

  const aoiBbox = manifest?.inputs?.bbox
    ? `[${manifest.inputs.bbox[0].toFixed(2)}, ${manifest.inputs.bbox[1].toFixed(2)}, ${manifest.inputs.bbox[2].toFixed(2)}, ${manifest.inputs.bbox[3].toFixed(2)}]`
    : activeRun?.bbox
    ? `[${activeRun.bbox[0].toFixed(2)}, ${activeRun.bbox[1].toFixed(2)}, ${activeRun.bbox[2].toFixed(2)}, ${activeRun.bbox[3].toFixed(2)}]`
    : "Trishuli Valley AOI";

  const floodDate = manifest?.inputs?.flood_date || activeRun?.flood_date || "2026-08-28";
  const runStatus = manifest?.overall_status || activeRun?.status || "PARTIAL_RUN_OPTICAL_UNCONFIRMED";
  const provenanceMode = manifest?.provenance_mode || activeRun?.provenance_mode || "VERIFIED_TRISHULI_BENCHMARK_CACHE";

  return (
    <header
      style={{
        backgroundColor: "var(--paper)",
        borderBottom: "1px solid var(--slate-light)",
        boxShadow: "var(--shadow-flat)",
        position: "relative",
        zIndex: 20,
      }}
    >
      {/* Top Banner Row */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "8px 20px",
          borderBottom: "1px solid var(--slate-subtle)",
          flexWrap: "wrap",
          gap: "8px",
        }}
      >
        {/* Brand & Project Metadata */}
        <div style={{ display: "flex", alignItems: "center", gap: "14px", flexWrap: "wrap" }}>
          {/* Survey compass/theodolite icon */}
          <div
            style={{
              width: "28px",
              height: "28px",
              backgroundColor: "var(--ink)",
              borderRadius: "var(--radius-sm)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "var(--paper)",
              flexShrink: 0,
            }}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.5" />
              <line x1="12" y1="3" x2="12" y2="7" stroke="currentColor" strokeWidth="1.5" />
              <line x1="12" y1="17" x2="12" y2="21" stroke="currentColor" strokeWidth="1.5" />
              <line x1="3" y1="12" x2="7" y2="12" stroke="currentColor" strokeWidth="1.5" />
              <line x1="17" y1="12" x2="21" y2="12" stroke="currentColor" strokeWidth="1.5" />
              <circle cx="12" cy="12" r="2" fill="var(--river)" />
            </svg>
          </div>

          <div>
            <div style={{ display: "flex", alignItems: "baseline", gap: "8px" }}>
              <span
                style={{
                  fontFamily: "var(--font-serif)",
                  fontSize: "17px",
                  fontWeight: 600,
                  color: "var(--ink)",
                  letterSpacing: "-0.01em",
                }}
              >
                FloodSpaceAI
              </span>
              <span
                style={{
                  fontSize: "12px",
                  color: "var(--ink-secondary)",
                  fontFamily: "var(--font-sans)",
                }}
              >
                Earth Observation Intelligence
              </span>
            </div>
          </div>

          <div
            style={{
              height: "18px",
              width: "1px",
              backgroundColor: "var(--slate-light)",
            }}
          />

          {/* Phase 5 Interactive Pipeline Run Selector */}
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <label
              htmlFor="pipeline-run-select"
              style={{
                fontSize: "11px",
                fontFamily: "var(--font-mono)",
                color: "var(--ink-secondary)",
                fontWeight: 600,
                textTransform: "uppercase",
              }}
            >
              Run:
            </label>
            <select
              id="pipeline-run-select"
              value={selectedRunId}
              onChange={(e) => setSelectedRunId(e.target.value)}
              style={{
                fontFamily: "var(--font-sans)",
                fontSize: "12px",
                padding: "3px 8px",
                borderRadius: "var(--radius-sm)",
                border: "1px solid var(--slate-light)",
                backgroundColor: "var(--paper-elevated)",
                color: "var(--ink)",
                cursor: "pointer",
                maxWidth: "280px",
              }}
            >
              {runs.map((r) => (
                <option key={r.run_id} value={r.run_id}>
                  {r.title || r.run_id}
                </option>
              ))}
            </select>
          </div>

          {/* Status and Provenance Badges */}
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            {renderStatusBadge(runStatus)}
            {renderProvenanceBadge(provenanceMode)}
          </div>

          {/* Area & Date Metadata */}
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <span
              className="survey-badge"
              style={{
                backgroundColor: "var(--fog)",
                color: "var(--ink)",
                fontSize: "11px",
              }}
              title="Analysis Bounding Box"
            >
              AOI: {aoiBbox}
            </span>
            <span
              className="survey-badge"
              style={{
                backgroundColor: "var(--fog)",
                color: "var(--ink-secondary)",
                fontSize: "11px",
              }}
              title="Target Flood Date"
            >
              Date: {floodDate}
            </span>
          </div>
        </div>

        {/* Right Action: Demo Tour & Modelled Warning */}
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <span
            className="survey-badge survey-badge-brick"
            title="Modelled potential inundation; not confirmed physical damage"
          >
            <span
              style={{
                width: "6px",
                height: "6px",
                borderRadius: "50%",
                backgroundColor: "var(--brick)",
                display: "inline-block",
              }}
            />
            Modelled candidate
          </span>

          <button
            onClick={onStartTour}
            className={`btn-survey ${isTourActive ? "btn-survey-river" : "btn-survey-primary"}`}
            aria-label="Start 3-minute guided tour"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
              <polygon points="5 3 19 12 5 21 5 3" />
            </svg>
            <span>{isTourActive ? "Tour in progress" : "Start 3-minute tour"}</span>
          </button>
        </div>
      </div>

      {/* Tabs Row */}
      <nav
        aria-label="Dashboard sections"
        style={{
          display: "flex",
          alignItems: "center",
          gap: "2px",
          padding: "0 16px",
          backgroundColor: "var(--paper)",
          overflowX: "auto",
        }}
      >
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
                padding: "10px 14px",
                fontFamily: "var(--font-sans)",
                fontSize: "13px",
                fontWeight: isActive ? 600 : 500,
                color: isActive ? "var(--ink)" : "var(--ink-secondary)",
                backgroundColor: isActive ? "var(--paper-elevated)" : "transparent",
                border: "none",
                borderBottom: isActive ? "2px solid var(--river)" : "2px solid transparent",
                cursor: "pointer",
                whiteSpace: "nowrap",
                transition: "color 120ms ease, background-color 120ms ease",
              }}
            >
              <span>{tab.label}</span>
              {tab.count && (
                <span
                  style={{
                    fontSize: "11px",
                    fontFamily: "var(--font-mono)",
                    padding: "1px 5px",
                    borderRadius: "3px",
                    backgroundColor: isActive ? "var(--river-light)" : "var(--fog)",
                    color: isActive ? "var(--river-dark)" : "var(--ink-muted)",
                  }}
                >
                  {tab.count}
                </span>
              )}
            </button>
          );
        })}
      </nav>
    </header>
  );
}
