"use client";

import React, { useEffect, useState } from "react";
import AnimatedCounter from "@/components/common/AnimatedCounter";
import { dataLoader } from "@/data/dataLoader";
import { usePipelineRun } from "@/data/RunContext";
import type { EvidenceData, ConnectivitySummaryV4 } from "@/data/types";

export default function ConnectivityAnalysis() {
  const { manifest, evidence: runEvidence, selectedRunId } = usePipelineRun();
  const [evidence, setEvidence] = useState<EvidenceData | null>(null);
  const [connectivitySummary, setConnectivitySummary] = useState<ConnectivitySummaryV4 | null>(null);
  const [networkMode, setNetworkMode] = useState<"before" | "after">("after");
  const [selectedHub, setSelectedHub] = useState<string>("all");
  const [activeSettlement, setActiveSettlement] = useState<string | null>(null);

  useEffect(() => {
    dataLoader.getEvidence().then(setEvidence);
    dataLoader.getConnectivitySummary().then(setConnectivitySummary);
  }, []);

  const activeMetrics = manifest?.metrics || {};
  const isUnavailable = manifest?.overall_status?.includes("UNAVAILABLE") || manifest?.overall_status === "FAILED";

  const isBenchmark = selectedRunId === "trishuli_benchmark_verified";
  const cutOffList = runEvidence?.cut_off_settlements?.length 
    ? runEvidence.cut_off_settlements 
    : (isBenchmark ? (evidence?.cut_off_settlements || []) : []);
  const filteredList = selectedHub === "all"
    ? cutOffList
    : cutOffList.filter((s) => s.nearest_town_or_city.includes(selectedHub));

  const totalAnalysed = activeMetrics.settlements_analysed ?? (isBenchmark ? (connectivitySummary?.settlements_analysed ?? 589) : 0);
  const cutOffCount = activeMetrics.potentially_cut_off_settlements ?? (isBenchmark ? (connectivitySummary?.potentially_cut_off_settlements ?? 18) : 0);
  const preComponents = activeMetrics.pre_event_components ?? (isBenchmark ? (connectivitySummary?.pre_event_components ?? 181) : 0);
  const postComponents = activeMetrics.post_event_components ?? (isBenchmark ? (connectivitySummary?.post_event_components ?? 252) : 0);
  const newComponents = postComponents >= preComponents ? postComponents - preComponents : 0;

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
        <span className="survey-badge survey-badge-brick" style={{ marginBottom: "6px", fontSize: "11px" }}>
          Road network graph analysis (V4)
        </span>
        <h2
          style={{
            fontFamily: "var(--font-serif)",
            fontSize: "24px",
            fontWeight: 600,
            color: "var(--ink)",
            margin: "4px 0",
          }}
        >
          Modelled road connectivity & cut-off settlements
        </h2>
        <p style={{ fontSize: "13px", color: "var(--ink-secondary)", margin: 0 }}>
          Graph-based topological analysis evaluating vehicle route connectivity between 589 settlements and 3 designated regional hubs.
        </p>
      </div>

      {/* Mandatory Terminology Banner */}
      <div
        style={{
          backgroundColor: "var(--brick-light)",
          border: "1px solid rgba(176, 74, 58, 0.4)",
          borderRadius: "var(--radius-sm)",
          padding: "10px 16px",
          marginBottom: "20px",
          display: "flex",
          alignItems: "center",
          gap: "10px",
        }}
      >
        <span
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "12px",
            fontWeight: 700,
            color: "var(--brick)",
            textTransform: "uppercase",
          }}
        >
          Modelled potential disconnection:
        </span>
        <span style={{ fontSize: "12px", color: "var(--ink)", lineHeight: 1.4 }}>
          A settlement is classified as potentially cut off when its road path to the nearest hub exists in the pre-event network but becomes disconnected upon removing flooded road segments. This does <strong>not</strong> confirm real-world physical isolation.
        </span>
      </div>

      {/* Safeguard Alert for Unavailable Runs */}
      {isUnavailable && (
        <div
          style={{
            backgroundColor: "rgba(100, 116, 139, 0.1)",
            border: "1px solid #94a3b8",
            borderRadius: "var(--radius-sm)",
            padding: "10px 16px",
            marginBottom: "20px",
            display: "flex",
            alignItems: "center",
            gap: "10px",
          }}
        >
          <span
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "12px",
              fontWeight: 700,
              color: "#475569",
              textTransform: "uppercase",
            }}
          >
            Safeguard Active:
          </span>
          <span style={{ fontSize: "12px", color: "var(--ink)", lineHeight: 1.4 }}>
            Road connectivity modeling was safely skipped for run <strong>{selectedRunId}</strong> ({manifest?.overall_status}). Honest reporting requires verified flood perimeters and pre-event topology before executing graph disconnection algorithms.
          </span>
        </div>
      )}

      {/* Hospital Coverage Limitation Disclosure */}
      <div
        style={{
          backgroundColor: "var(--fog)",
          border: "1px solid var(--slate-light)",
          borderRadius: "var(--radius-sm)",
          padding: "8px 14px",
          marginBottom: "20px",
          display: "flex",
          alignItems: "center",
          gap: "8px",
          fontSize: "11px",
          color: "var(--ink-secondary)",
        }}
      >
        <span style={{ fontFamily: "var(--font-mono)", fontWeight: 600, color: "var(--ink)" }}>
          Data Lineage Note:
        </span>
        <span>
          Historical hospital data was not available in the pre-event OSM snapshot ({manifest?.inputs?.snapshot_date || "2026-07-27"}). Modeled vehicle access is calculated with respect to designated regional administrative hubs (Bidur, Galchhi, Belkotgadhi).
        </span>
      </div>

      {/* Metric Cards Row */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "14px",
          marginBottom: "24px",
        }}
      >
        <div className="survey-panel" style={{ padding: "16px" }}>
          <div style={{ fontSize: "11px", color: "var(--ink-muted)", textTransform: "uppercase", marginBottom: "4px" }}>
            Potentially Cut-off
          </div>
          <div
            style={{
              fontFamily: "var(--font-serif)",
              fontSize: "36px",
              fontWeight: 700,
              color: "var(--brick)",
              lineHeight: 1.1,
            }}
          >
            <AnimatedCounter value={cutOffCount} />
          </div>
          <div style={{ fontSize: "12px", color: "var(--ink-secondary)", marginTop: "6px" }}>
            Potentially cut-off settlements
          </div>
          <div style={{ fontSize: "10px", color: "var(--ink-muted)", marginTop: "2px" }}>
            Disconnected from designated hub
          </div>
        </div>

        <div className="survey-panel" style={{ padding: "16px" }}>
          <div style={{ fontSize: "11px", color: "var(--ink-muted)", textTransform: "uppercase", marginBottom: "4px" }}>
            Settlements Evaluated
          </div>
          <div
            style={{
              fontFamily: "var(--font-serif)",
              fontSize: "36px",
              fontWeight: 700,
              color: "var(--ink)",
              lineHeight: 1.1,
            }}
          >
            <AnimatedCounter value={totalAnalysed} />
          </div>
          <div style={{ fontSize: "12px", color: "var(--ink-secondary)", marginTop: "6px" }}>
            Hamlets & villages in AOI
          </div>
          <div style={{ fontSize: "10px", color: "var(--ink-muted)", marginTop: "2px" }}>
            Tested against 3 town/city hubs
          </div>
        </div>

        <div className="survey-panel" style={{ padding: "16px" }}>
          <div style={{ fontSize: "11px", color: "var(--ink-muted)", textTransform: "uppercase", marginBottom: "4px" }}>
            Graph Components
          </div>
          <div
            style={{
              fontFamily: "var(--font-serif)",
              fontSize: "36px",
              fontWeight: 700,
              color: "var(--silt)",
              lineHeight: 1.1,
            }}
          >
            <span>{preComponents} → {postComponents}</span>
          </div>
          <div style={{ fontSize: "12px", color: "var(--ink-secondary)", marginTop: "6px" }}>
            +{newComponents} new fragmented clusters
          </div>
          <div style={{ fontSize: "10px", color: "var(--ink-muted)", marginTop: "2px" }}>
            Post-event road splits
          </div>
        </div>

        <div className="survey-panel" style={{ padding: "16px" }}>
          <div style={{ fontSize: "11px", color: "var(--ink-muted)", textTransform: "uppercase", marginBottom: "4px" }}>
            Regional Hubs
          </div>
          <div
            style={{
              fontFamily: "var(--font-serif)",
              fontSize: "36px",
              fontWeight: 700,
              color: "var(--river)",
              lineHeight: 1.1,
            }}
          >
            3 Hubs
          </div>
          <div style={{ fontSize: "12px", color: "var(--ink-secondary)", marginTop: "6px" }}>
            Bidur · Galchhi · Belkotgadhi
          </div>
          <div style={{ fontSize: "10px", color: "var(--ink-muted)", marginTop: "2px" }}>
            Substitutes for historical hospital data
          </div>
        </div>
      </div>

      {/* Interactive Network State Toggle & Hub Filter */}
      <div
        className="survey-panel"
        style={{
          padding: "12px 18px",
          marginBottom: "20px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: "12px",
        }}
      >
        {/* Before / After Network Switcher */}
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--ink)" }}>
            Network simulation state:
          </span>
          <div style={{ display: "inline-flex", borderRadius: "var(--radius-sm)", border: "1px solid var(--slate)" }}>
            <button
              onClick={() => setNetworkMode("before")}
              style={{
                padding: "6px 12px",
                fontSize: "12px",
                fontWeight: networkMode === "before" ? 600 : 500,
                backgroundColor: networkMode === "before" ? "var(--moss)" : "var(--paper)",
                color: networkMode === "before" ? "#FFFFFF" : "var(--ink)",
                border: "none",
                cursor: "pointer",
                borderRadius: "3px 0 0 3px",
              }}
            >
              Pre-event (intact)
            </button>
            <button
              onClick={() => setNetworkMode("after")}
              style={{
                padding: "6px 12px",
                fontSize: "12px",
                fontWeight: networkMode === "after" ? 600 : 500,
                backgroundColor: networkMode === "after" ? "var(--brick)" : "var(--paper)",
                color: networkMode === "after" ? "#FFFFFF" : "var(--ink)",
                border: "none",
                cursor: "pointer",
                borderRadius: "0 3px 3px 0",
              }}
            >
              Post-event (115 potentially affected road features)
            </button>
          </div>
          <span style={{ fontSize: "11px", color: "var(--ink-muted)", fontStyle: "italic" }}>
            (115 road features yield 3,748 disrupted network segments in V4)
          </span>
        </div>

        {/* Hub Filter */}
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <span style={{ fontSize: "12px", color: "var(--ink-secondary)" }}>Nearest hub:</span>
          {["all", "बिदुर", "गल्छी", "बेलकोटगढी"].map((hub) => (
            <button
              key={hub}
              onClick={() => setSelectedHub(hub)}
              className={`btn-survey ${selectedHub === hub ? "btn-survey-primary" : ""}`}
              style={{ padding: "4px 10px", fontSize: "11px" }}
            >
              {hub === "all" ? "All (18)" : hub === "बिदुर" ? "Bidur (14)" : hub === "गल्छी" ? "Galchhi (2)" : "Belkotgadhi (2)"}
            </button>
          ))}
        </div>
      </div>

      {/* Grid: Cut-off Settlement Cards with Animated Route Break Visualization */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
          gap: "14px",
        }}
      >
        {filteredList.map((settlement, idx) => {
          const isSelected = activeSettlement === settlement.name;
          const isConnected = networkMode === "before";

          return (
            <div
              key={settlement.name + idx}
              onClick={() => setActiveSettlement(settlement.name)}
              className="survey-panel"
              style={{
                padding: "14px",
                cursor: "pointer",
                border: isSelected ? "2px solid var(--brick)" : "1px solid var(--slate-light)",
                transition: "var(--t-smooth)",
              }}
            >
              {/* Header */}
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  marginBottom: "8px",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <span
                    style={{
                      fontFamily: "var(--font-mono)",
                      fontSize: "11px",
                      color: "var(--ink-muted)",
                    }}
                  >
                    #{(idx + 1).toString().padStart(2, "0")}
                  </span>
                  <h3
                    style={{
                      fontFamily: "var(--font-serif)",
                      fontSize: "16px",
                      fontWeight: 600,
                      color: "var(--ink)",
                      margin: 0,
                    }}
                  >
                    {settlement.name}
                  </h3>
                </div>

                <span
                  className={`survey-badge ${isConnected ? "survey-badge-moss" : "survey-badge-brick"}`}
                  style={{ fontSize: "10px" }}
                >
                  {isConnected ? "Connected" : "Potentially cut off"}
                </span>
              </div>

              {/* Settlement Type & Nearest Hub */}
              <div style={{ fontSize: "12px", color: "var(--ink-secondary)", marginBottom: "12px" }}>
                Classification: <strong>{settlement.place}</strong> · Nearest hub: <strong>{settlement.nearest_town_or_city}</strong>
              </div>

              {/* Animated Road Network Path Line */}
              <div
                style={{
                  position: "relative",
                  height: "26px",
                  backgroundColor: "var(--fog)",
                  borderRadius: "var(--radius-sm)",
                  padding: "4px 10px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  fontSize: "11px",
                  overflow: "hidden",
                }}
              >
                {/* Simulated Road Line */}
                <svg
                  style={{
                    position: "absolute",
                    left: "20px",
                    right: "20px",
                    top: "12px",
                    width: "calc(100% - 40px)",
                    height: "4px",
                  }}
                >
                  <line
                    x1="0"
                    y1="2"
                    x2="100%"
                    y2="2"
                    stroke={isConnected ? "var(--moss)" : "var(--brick)"}
                    strokeWidth="2.5"
                    strokeDasharray={isConnected ? "none" : "6,4"}
                    style={{
                      transition: "stroke 250ms ease",
                    }}
                  />
                </svg>

                <span style={{ zIndex: 1, fontWeight: 500, color: "var(--ink)" }}>{settlement.name}</span>
                <span
                  style={{
                    zIndex: 1,
                    fontSize: "10px",
                    color: isConnected ? "var(--moss)" : "var(--brick)",
                    fontWeight: 600,
                    backgroundColor: "var(--paper)",
                    padding: "1px 6px",
                    borderRadius: "3px",
                    border: "1px solid var(--slate-subtle)",
                  }}
                >
                  {isConnected ? "Intact link" : "Severed in V4"}
                </span>
                <span style={{ zIndex: 1, fontWeight: 500, color: "var(--ink)" }}>{settlement.nearest_town_or_city}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
