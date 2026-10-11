// ============================================================
// LeftPanel — layer controls + impact stats sidebar
// ============================================================
"use client";

import { useState } from "react";
import StatCard from "./StatCard";
import { EVIDENCE } from "@/lib/evidence";

const LAYERS = [
  {
    id: "sentinel1",
    label: "Sentinel-1 SAR (Pre/Post)",
    color: "#8b98a9",
    enabled: true,
  },
  {
    id: "floodCandidate",
    label: "Modelled Potential Inundation (V3)",
    color: "#22d3ee",
    enabled: true,
  },
  {
    id: "buildings",
    label: "Potentially Affected Buildings",
    color: "#f59e0b",
    enabled: true,
  },
  {
    id: "roads",
    label: "Potentially Affected Roads",
    color: "#ef4444",
    enabled: true,
  },
  {
    id: "bridges",
    label: "Potentially Affected Bridges",
    color: "#a78bfa",
    enabled: true,
  },
  {
    id: "settlements",
    label: "Potentially Cut-off Settlements",
    color: "#fb923c",
    enabled: false,
  },
] as const;

export default function LeftPanel() {
  const [layerStates, setLayerStates] = useState<Record<string, boolean>>(
    Object.fromEntries(LAYERS.map((l) => [l.id, l.enabled]))
  );

  function toggleLayer(id: string) {
    setLayerStates((prev) => ({ ...prev, [id]: !prev[id] }));
  }

  return (
    <aside
      style={{
        width: "260px",
        flexShrink: 0,
        display: "flex",
        flexDirection: "column",
        background: "var(--surface-1)",
        borderRight: "1px solid var(--border-subtle)",
        overflowY: "auto",
      }}
    >
      {/* ── Section: Impact Summary ── */}
      <div style={{ padding: "12px" }}>
        <div className="panel-header" style={{ borderRadius: "6px 6px 0 0" }}>
          <span className="panel-title">Modelled Impact Summary</span>
          <span
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "9px",
              color: "var(--status-warning)",
              letterSpacing: "0.04em",
            }}
          >
            V3
          </span>
        </div>

        <div
          style={{
            background: "var(--surface-2)",
            border: "1px solid var(--border-subtle)",
            borderTop: "none",
            borderRadius: "0 0 6px 6px",
            padding: "10px",
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "6px",
          }}
        >
          <StatCard
            label="Flood Pixels"
            value={EVIDENCE.floodMapping.floodPixels}
            description="10 m SAR pixels"
            color="var(--accent-primary)"
            mono
          />
          <StatCard
            label="Flood Polygons"
            value={EVIDENCE.floodMapping.floodPolygons}
            description="connected regions"
            color="var(--accent-primary)"
            mono
          />
        </div>
      </div>

      {/* ── Section: Potentially Affected ── */}
      <div style={{ padding: "0 12px 12px" }}>
        <div className="panel-header" style={{ borderRadius: "6px 6px 0 0" }}>
          <span className="panel-title">Potentially Affected</span>
          <span className="badge-modelled" style={{ fontSize: "9px", padding: "1px 5px" }}>
            est.
          </span>
        </div>
        <div
          style={{
            background: "var(--surface-2)",
            border: "1px solid var(--border-subtle)",
            borderTop: "none",
            borderRadius: "0 0 6px 6px",
            padding: "10px",
            display: "grid",
            gridTemplateColumns: "1fr 1fr 1fr",
            gap: "6px",
          }}
        >
          <StatCard
            label="Buildings"
            value={EVIDENCE.potentiallyAffected.buildings}
            color="var(--status-warning)"
            mono
          />
          <StatCard
            label="Roads"
            value={EVIDENCE.potentiallyAffected.roads}
            description="segments"
            color="var(--status-danger)"
            mono
          />
          <StatCard
            label="Bridges"
            value={EVIDENCE.potentiallyAffected.bridges}
            color="#a78bfa"
            mono
          />
        </div>
      </div>

      {/* ── Section: Road Connectivity ── */}
      <div style={{ padding: "0 12px 12px" }}>
        <div className="panel-header" style={{ borderRadius: "6px 6px 0 0" }}>
          <span className="panel-title">Road Connectivity</span>
        </div>
        <div
          style={{
            background: "var(--surface-2)",
            border: "1px solid var(--border-subtle)",
            borderTop: "none",
            borderRadius: "0 0 6px 6px",
            padding: "10px",
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "6px",
          }}
        >
          <StatCard
            label="Cut-off Settlements"
            value={EVIDENCE.roadConnectivity.potentiallyCutOff}
            description="potentially isolated"
            color="var(--status-danger)"
            mono
          />
          <StatCard
            label="New Components"
            value={
              EVIDENCE.roadConnectivity.postEventComponents -
              EVIDENCE.roadConnectivity.preEventComponents
            }
            description="road graph splits"
            color="var(--status-warning)"
            mono
          />
        </div>
      </div>

      {/* ── Section: Layer Controls ── */}
      <div style={{ padding: "0 12px 12px", flex: 1 }}>
        <div className="panel-header" style={{ borderRadius: "6px 6px 0 0" }}>
          <span className="panel-title">Map Layers</span>
          <span
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "9px",
              color: "var(--text-muted)",
            }}
          >
            Phase 2
          </span>
        </div>
        <div
          style={{
            background: "var(--surface-2)",
            border: "1px solid var(--border-subtle)",
            borderTop: "none",
            borderRadius: "0 0 6px 6px",
            padding: "8px 12px",
          }}
        >
          {LAYERS.map((layer) => {
            const isOn = layerStates[layer.id];
            return (
              <div key={layer.id} className="layer-row">
                <div
                  style={{ display: "flex", alignItems: "center", gap: "8px" }}
                >
                  <div
                    className="layer-dot"
                    style={{
                      background: isOn ? layer.color : "var(--text-muted)",
                      opacity: isOn ? 1 : 0.4,
                    }}
                  />
                  <span style={{ fontSize: "11px", color: "var(--text-secondary)" }}>
                    {layer.label}
                  </span>
                </div>

                {/* Toggle */}
                <button
                  id={`layer-toggle-${layer.id}`}
                  aria-label={`${isOn ? "Hide" : "Show"} ${layer.label} layer`}
                  aria-pressed={isOn}
                  onClick={() => toggleLayer(layer.id)}
                  style={{
                    width: "28px",
                    height: "16px",
                    borderRadius: "8px",
                    border: "none",
                    cursor: "pointer",
                    background: isOn ? "var(--accent-primary)" : "var(--surface-4)",
                    position: "relative",
                    transition: "background 0.15s ease",
                    flexShrink: 0,
                  }}
                >
                  <span
                    style={{
                      position: "absolute",
                      top: "2px",
                      left: isOn ? "14px" : "2px",
                      width: "12px",
                      height: "12px",
                      borderRadius: "50%",
                      background: "#fff",
                      transition: "left 0.15s ease",
                    }}
                  />
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── Section: Methodology ── */}
      <div style={{ padding: "0 12px 12px" }}>
        <div className="panel-header" style={{ borderRadius: "6px 6px 0 0" }}>
          <span className="panel-title">Analysis Method</span>
        </div>
        <div
          style={{
            background: "var(--surface-2)",
            border: "1px solid var(--border-subtle)",
            borderTop: "none",
            borderRadius: "0 0 6px 6px",
            padding: "10px 12px",
            display: "flex",
            flexDirection: "column",
            gap: "6px",
          }}
        >
          {[
            "Sentinel-1 SAR change detection",
            "Sentinel-2 NDWI change analysis",
            "Post-event water condition",
            "Pre-event non-water condition",
            "Connected-component filtering",
          ].map((step, i) => (
            <div
              key={step}
              style={{ display: "flex", alignItems: "flex-start", gap: "8px" }}
            >
              <span
                style={{
                  fontFamily: "var(--font-mono)",
                  fontSize: "9px",
                  color: "var(--accent-primary)",
                  paddingTop: "1px",
                  flexShrink: 0,
                }}
              >
                {(i + 1).toString().padStart(2, "0")}
              </span>
              <span style={{ fontSize: "11px", color: "var(--text-muted)", lineHeight: 1.4 }}>
                {step}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* ── Provenance footer ── */}
      <div
        style={{
          borderTop: "1px solid var(--border-subtle)",
          padding: "10px 14px",
        }}
      >
        <p
          style={{
            fontSize: "9px",
            color: "var(--text-muted)",
            lineHeight: 1.5,
            margin: 0,
          }}
        >
          {EVIDENCE.provenance.note}
          <br />
          {EVIDENCE.provenance.osm}
        </p>
      </div>
    </aside>
  );
}
