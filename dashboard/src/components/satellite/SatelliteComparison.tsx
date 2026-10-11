"use client";

import React, { useState, useRef, useCallback } from "react";

interface ComparisonPair {
  id: string;
  name: string;
  sensor: string;
  leftTitle: string;
  rightTitle: string;
  leftDate: string;
  rightDate: string;
  leftImage: string;
  rightImage: string;
  description: string;
}

const COMPARISON_PAIRS: ComparisonPair[] = [
  {
    id: "s1-change",
    name: "Sentinel-1 SAR change (VV visual)",
    sensor: "Copernicus Sentinel-1 (C-band SAR)",
    leftTitle: "Pre-event SAR backscatter",
    rightTitle: "Post-event backscatter change (dB)",
    leftDate: "16 August 2026",
    rightDate: "28 August 2026",
    leftImage: "/data/vv_change_visual.png",
    rightImage: "/data/filtered_vv_visual.png",
    description: "Specular water reflection creates marked negative backscatter change (up to -6 dB) along the Trishuli River corridor.",
  },
  {
    id: "vh-cross",
    name: "SAR cross-polarization (VH visual)",
    sensor: "Sentinel-1 IW VH Polarization",
    leftTitle: "Pre-event volumetric scatter",
    rightTitle: "Post-event VH change",
    leftDate: "16 August 2026",
    rightDate: "28 August 2026",
    leftImage: "/data/vh_change_visual.png",
    rightImage: "/data/vh_change_db_visual.png",
    description: "Cross-polarization highlights flooded vegetation and structural interactions along riverbanks.",
  },
  {
    id: "s2-optical",
    name: "Sentinel-2 optical RGB vs SAR change",
    sensor: "Copernicus Sentinel-2 MSI + Sentinel-1",
    leftTitle: "Pre-event cloud-free optical (2048×2048 grid)",
    rightTitle: "SAR change detection overlay",
    leftDate: "12 August 2026",
    rightDate: "28 August 2026",
    leftImage: "/data/sentinel2_pre_rgb.png",
    rightImage: "/data/filtered_vv_visual.png",
    description: "Cross-comparing pre-event optical baseline with all-weather radar change to verify valley geography.",
  },
  {
    id: "ratio-change",
    name: "VV/VH ratio change",
    sensor: "Dual-polarization ratio",
    leftTitle: "Pre-event polarization baseline",
    rightTitle: "VV/VH ratio anomaly",
    leftDate: "16 August 2026",
    rightDate: "28 August 2026",
    leftImage: "/data/vv_change_visual.png",
    rightImage: "/data/vvvh_ratio_visual.png",
    description: "Ratio change aids in discriminating open water from terrain shadow in steep Himalayan valley topography.",
  },
];

import { usePipelineRun } from "@/data/RunContext";

export default function SatelliteComparison() {
  const { manifest, selectedRunId, activeRun } = usePipelineRun();
  const [selectedPairIndex, setSelectedPairIndex] = useState(0);
  const [sliderPosition, setSliderPosition] = useState(50); // percentage 0 - 100
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const pair = COMPARISON_PAIRS[selectedPairIndex];
  const isBenchmark = selectedRunId === "trishuli_benchmark_verified";
  const s1Meta = manifest?.stages?.stage_2_satellite_discovery?.details?.sentinel1 || manifest?.stages?.stage_3_satellite_acquisition;
  const s2Meta = manifest?.stages?.stage_2_satellite_discovery?.details?.sentinel2;

  const handlePointerDown = () => {
    setIsDragging(true);
  };

  const handlePointerUp = () => {
    setIsDragging(false);
  };

  const updatePosition = useCallback((clientX: number) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = clientX - rect.left;
    const pct = Math.max(0, Math.min(100, (x / rect.width) * 100));
    setSliderPosition(pct);
  }, []);

  const handlePointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!isDragging) return;
    updatePosition(e.clientX);
  };

  return (
    <div
      style={{
        padding: "24px",
        maxWidth: "1140px",
        margin: "0 auto",
      }}
    >
      {/* Title & Selector Row */}
      <div
        style={{
          display: "flex",
          alignItems: "flex-end",
          justifyContent: "space-between",
          marginBottom: "16px",
          flexWrap: "wrap",
          gap: "12px",
        }}
      >
        <div>
          <span
            className="survey-badge survey-badge-river"
            style={{ marginBottom: "6px", fontSize: "11px" }}
          >
            Multi-sensor evidence
          </span>
          <h2
            style={{
              fontFamily: "var(--font-serif)",
              fontSize: "22px",
              fontWeight: 600,
              color: "var(--ink)",
              margin: "4px 0",
            }}
          >
            Satellite comparison & swipe analysis
          </h2>
          <p
            style={{
              fontSize: "13px",
              color: "var(--ink-secondary)",
              margin: 0,
            }}
          >
            Drag the vertical divider to evaluate pre-event baseline against post-event radar and optical change.
          </p>
        </div>

        {/* Pair Mode Switcher */}
        <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
          {COMPARISON_PAIRS.map((p, idx) => (
            <button
              key={p.id}
              onClick={() => {
                setSelectedPairIndex(idx);
                setSliderPosition(50);
              }}
              className={`btn-survey ${selectedPairIndex === idx ? "btn-survey-primary" : ""}`}
              style={{ fontSize: "12px", padding: "6px 10px" }}
            >
              {p.name}
            </button>
          ))}
        </div>
      </div>

      {/* Main Swipe Container Card */}
      <div
        className="survey-panel"
        style={{
          overflow: "hidden",
          boxShadow: "var(--shadow-dropdown)",
        }}
      >
        {/* Top Info Bar */}
        <div
          style={{
            padding: "10px 16px",
            backgroundColor: "var(--paper-elevated)",
            borderBottom: "1px solid var(--slate-light)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            fontSize: "12px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <span style={{ fontWeight: 600, color: "var(--ink)" }}>{pair.sensor}</span>
            <span style={{ color: "var(--slate)" }}>·</span>
            <span style={{ color: "var(--ink-secondary)" }}>
              {isBenchmark 
                ? "Trishuli Benchmark Reference (Relative Orbit 85)" 
                : `${manifest?.title || selectedRunId} — SAR Orbit ${s1Meta?.relative_orbit || 'Matched'}`}
            </span>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span className="survey-badge" style={{ fontSize: "10px" }}>
              Divider: {Math.round(sliderPosition)}%
            </span>
            <button
              onClick={() => setSliderPosition(50)}
              className="btn-survey"
              style={{ padding: "2px 8px", fontSize: "11px" }}
            >
              Reset 50%
            </button>
          </div>
        </div>

        {/* The Interactive Swipe Area */}
        <div
          ref={containerRef}
          onPointerDown={handlePointerDown}
          onPointerUp={handlePointerUp}
          onPointerMove={handlePointerMove}
          style={{
            position: "relative",
            width: "100%",
            height: "560px",
            backgroundColor: "#0F1418",
            cursor: "ew-resize",
            userSelect: "none",
            touchAction: "none",
            overflow: "hidden",
          }}
        >
          {/* Left Layer (Pre-event baseline) */}
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: "100%",
              height: "100%",
              backgroundImage: `url(${pair.leftImage})`,
              backgroundSize: "cover",
              backgroundPosition: "center",
            }}
          >
            {/* Left Label */}
            <div
              style={{
                position: "absolute",
                top: "16px",
                left: "16px",
                backgroundColor: "rgba(248, 249, 246, 0.95)",
                border: "1px solid var(--slate)",
                borderRadius: "var(--radius-sm)",
                padding: "6px 12px",
                boxShadow: "var(--shadow-panel)",
                zIndex: 2,
              }}
            >
              <div style={{ fontSize: "10px", color: "var(--ink-muted)", textTransform: "uppercase" }}>
                Baseline
              </div>
              <div style={{ fontWeight: 600, fontSize: "13px", color: "var(--ink)" }}>
                {pair.leftTitle}
              </div>
              <div style={{ fontSize: "11px", color: "var(--moss)", fontFamily: "var(--font-mono)" }}>
                {pair.leftDate}
              </div>
            </div>
          </div>

          {/* Right Layer (Post-event change) clipped by sliderPosition */}
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: "100%",
              height: "100%",
              backgroundImage: `url(${pair.rightImage})`,
              backgroundSize: "cover",
              backgroundPosition: "center",
              clipPath: `polygon(${sliderPosition}% 0, 100% 0, 100% 100%, ${sliderPosition}% 100%)`,
            }}
          >
            {/* Right Label */}
            <div
              style={{
                position: "absolute",
                top: "16px",
                right: "16px",
                backgroundColor: "rgba(248, 249, 246, 0.95)",
                border: "1px solid var(--slate)",
                borderRadius: "var(--radius-sm)",
                padding: "6px 12px",
                boxShadow: "var(--shadow-panel)",
                zIndex: 2,
                textAlign: "right",
              }}
            >
              <div style={{ fontSize: "10px", color: "var(--ink-muted)", textTransform: "uppercase" }}>
                Evidence / Change
              </div>
              <div style={{ fontWeight: 600, fontSize: "13px", color: "var(--ink)" }}>
                {pair.rightTitle}
              </div>
              <div style={{ fontSize: "11px", color: "var(--river)", fontFamily: "var(--font-mono)" }}>
                {pair.rightDate}
              </div>
            </div>
          </div>

          {/* Draggable Divider Line & Physical Handle */}
          <div
            style={{
              position: "absolute",
              top: 0,
              bottom: 0,
              left: `${sliderPosition}%`,
              width: "2px",
              backgroundColor: "#FFFFFF",
              boxShadow: "0 0 4px rgba(0,0,0,0.4)",
              zIndex: 10,
              transform: "translateX(-50%)",
            }}
          >
            <div
              style={{
                position: "absolute",
                top: "50%",
                left: "50%",
                transform: "translate(-50%, -50%)",
                width: "36px",
                height: "36px",
                backgroundColor: "var(--paper-elevated)",
                border: "2px solid var(--ink)",
                borderRadius: "var(--radius-sm)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                boxShadow: "0 2px 6px rgba(0,0,0,0.3)",
                color: "var(--ink)",
                cursor: "ew-resize",
              }}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="15 18 9 12 15 6" />
                <polyline points="9 18 3 12 9 6" />
              </svg>
            </div>
          </div>
        </div>

        {/* Technical Interpretation Note */}
        <div
          style={{
            padding: "12px 18px",
            backgroundColor: "var(--paper)",
            borderTop: "1px solid var(--slate-light)",
            fontSize: "12px",
            color: "var(--ink-secondary)",
            lineHeight: 1.5,
          }}
        >
          <strong>Hydrology analysis note:</strong> {pair.description}
        </div>
      </div>
    </div>
  );
}
