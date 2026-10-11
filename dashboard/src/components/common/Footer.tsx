"use client";

import React from "react";
import type { TabId } from "@/data/types";

interface FooterProps {
  onNavigateTab: (tab: TabId) => void;
}

export default function Footer({ onNavigateTab }: FooterProps) {
  return (
    <footer
      style={{
        backgroundColor: "var(--paper)",
        borderTop: "1px solid var(--slate-light)",
        padding: "8px 20px",
        fontSize: "12px",
        color: "var(--ink-secondary)",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        flexWrap: "wrap",
        gap: "12px",
        position: "relative",
        zIndex: 10,
      }}
    >
      {/* Left: Strict Terminology Disclaimer */}
      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
        <span
          style={{
            color: "var(--brick)",
            fontWeight: 600,
            fontFamily: "var(--font-mono)",
            fontSize: "11px",
          }}
        >
          Notice:
        </span>
        <span>
          Modelled potential inundation candidate — not confirmed physical damage or ground isolation.
        </span>
      </div>

      {/* Middle & Right: Provenance Links & Attribution */}
      <div style={{ display: "flex", alignItems: "center", gap: "14px", fontSize: "11px" }}>
        <span>Contains modified Copernicus Sentinel data (2026) · Produced using Copernicus WorldDEM-30 © DLR e.V./Airbus DS · © OpenStreetMap contributors (ODbL)</span>
        
        <button
          onClick={() => onNavigateTab("provenance")}
          className="btn-survey"
          style={{
            padding: "2px 8px",
            fontSize: "11px",
            backgroundColor: "transparent",
            boxShadow: "none",
            border: "1px solid var(--slate)",
          }}
        >
          View provenance & limitations
        </button>
      </div>
    </footer>
  );
}
