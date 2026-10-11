// ============================================================
// BottomBar — status / provenance footer
// ============================================================

import { EVIDENCE } from "@/lib/evidence";

export default function BottomBar() {
  return (
    <footer
      style={{
        background: "var(--surface-2)",
        borderTop: "1px solid var(--border-subtle)",
        padding: "0 20px",
        height: "28px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        gap: "12px",
        flexShrink: 0,
      }}
    >
      {/* Left — provenance */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "12px",
          fontSize: "9px",
          fontFamily: "var(--font-mono)",
          color: "var(--text-muted)",
          letterSpacing: "0.04em",
          overflow: "hidden",
        }}
      >
        <span style={{ whiteSpace: "nowrap" }}>{EVIDENCE.provenance.sentinel}</span>
        <span
          style={{ width: "1px", height: "12px", background: "var(--border-subtle)", flexShrink: 0 }}
        />
        <span style={{ whiteSpace: "nowrap" }}>{EVIDENCE.provenance.dem}</span>
        <span
          style={{ width: "1px", height: "12px", background: "var(--border-subtle)", flexShrink: 0 }}
        />
        <span style={{ whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
          {EVIDENCE.provenance.osm}
        </span>
      </div>

      {/* Centre — disclaimer */}
      <span
        style={{
          fontSize: "9px",
          fontFamily: "var(--font-mono)",
          color: "var(--status-warning)",
          letterSpacing: "0.04em",
          whiteSpace: "nowrap",
          flexShrink: 0,
        }}
      >
        ⚠ All values represent modelled potential impact — not confirmed damage
      </span>

      {/* Right — build info */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "8px",
          fontSize: "9px",
          fontFamily: "var(--font-mono)",
          color: "var(--text-muted)",
          flexShrink: 0,
        }}
      >
        <span>Flood Candidate {EVIDENCE.floodMapping.version}</span>
        <span
          style={{ width: "1px", height: "12px", background: "var(--border-subtle)" }}
        />
        <span>Phase 1</span>
      </div>
    </footer>
  );
}
