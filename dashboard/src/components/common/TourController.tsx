"use client";

import React, { useEffect, useState } from "react";
import type { TabId, TourStep } from "@/data/types";

interface TourControllerProps {
  isOpen: boolean;
  onClose: () => void;
  onNavigateTab: (tab: TabId) => void;
}

const TOUR_STEPS: TourStep[] = [
  {
    stepIndex: 0,
    tab: "map",
    title: "1. Main interactive flood candidate map",
    explanation:
      "Observe the Trishuli river corridor. The V3 model detected 1,286 potential flood pixels across 84 polygon clusters by combining Sentinel-1 SAR backscatter loss, Sentinel-2 NDWI change, and water connectivity.",
    durationSeconds: 28,
  },
  {
    stepIndex: 1,
    tab: "satellite",
    title: "2. Multi-sensor satellite comparison",
    explanation:
      "Swipe between pre-event and post-event satellite acquisitions. Sentinel-1 SAR (August 16 vs 28) penetrates monsoon cloud cover to detect surface specular reflection changes, corroborated by Sentinel-2 optical.",
    durationSeconds: 30,
  },
  {
    stepIndex: 2,
    tab: "assets",
    title: "3. Potentially affected infrastructure overlay",
    explanation:
      "Spatial intersection against OpenStreetMap identifies 195 buildings, 115 road segments, and 13 bridges within the candidate perimeter. These are labelled exclusively as modelled potential impacts.",
    durationSeconds: 28,
  },
  {
    stepIndex: 3,
    tab: "connectivity",
    title: "4. Road connectivity & 18 cut-off settlements",
    explanation:
      "Graph analysis on 589 settlements across 3 town/city hubs (Bidur, Galchhi, Belkotgadhi) reveals 18 settlements whose vehicle road connectivity to their nearest hub was potentially severed.",
    durationSeconds: 32,
  },
  {
    stepIndex: 4,
    tab: "copilot",
    title: "5. Grounded situation copilot (English & Nepali)",
    explanation:
      "The Gemini Copilot generates multi-lingual situation reports strictly constrained by system evidence JSON. Hallucinated numbers are blocked by programmatic numerical validation.",
    durationSeconds: 32,
  },
  {
    stepIndex: 5,
    tab: "pipeline",
    title: "6. End-to-end evidence pipeline",
    explanation:
      "Inspect the data transformation sequence from raw ESA Copernicus Sentinel radar/optical SAFE files, speckle filtering, NDWI thresholds, to asset intersections and final report generation.",
    durationSeconds: 30,
  },
];

export default function TourController({
  isOpen,
  onClose,
  onNavigateTab,
}: TourControllerProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);
  const [progress, setProgress] = useState(0);

  const step = TOUR_STEPS[currentStep];

  useEffect(() => {
    if (!isOpen) {
      setCurrentStep(0);
      setProgress(0);
      return;
    }

    onNavigateTab(step.tab);
    setProgress(0);
  }, [isOpen, currentStep, onNavigateTab, step.tab]);

  useEffect(() => {
    if (!isOpen || !isPlaying) return;

    const intervalMs = 100;
    const totalMs = step.durationSeconds * 1000;
    const increment = (intervalMs / totalMs) * 100;

    const timer = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          if (currentStep < TOUR_STEPS.length - 1) {
            setCurrentStep((c) => c + 1);
            return 0;
          } else {
            setIsPlaying(false);
            return 100;
          }
        }
        return prev + increment;
      });
    }, intervalMs);

    return () => clearInterval(timer);
  }, [isOpen, isPlaying, currentStep, step.durationSeconds]);

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: "fixed",
        bottom: "24px",
        left: "50%",
        transform: "translateX(-50%)",
        width: "90%",
        maxWidth: "680px",
        backgroundColor: "var(--paper-elevated)",
        border: "1px solid var(--slate)",
        borderRadius: "var(--radius-md)",
        boxShadow: "var(--shadow-dropdown)",
        zIndex: 50,
        overflow: "hidden",
      }}
    >
      {/* Progress Bar Top */}
      <div
        style={{
          height: "4px",
          width: "100%",
          backgroundColor: "var(--slate-subtle)",
        }}
      >
        <div
          style={{
            height: "100%",
            width: `${progress}%`,
            backgroundColor: "var(--river)",
            transition: "width 100ms linear",
          }}
        />
      </div>

      <div style={{ padding: "14px 18px" }}>
        {/* Header */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            marginBottom: "6px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span
              className="survey-badge survey-badge-river"
              style={{ fontSize: "11px" }}
            >
              Step {currentStep + 1} of {TOUR_STEPS.length}
            </span>
            <span
              style={{
                fontFamily: "var(--font-serif)",
                fontSize: "15px",
                fontWeight: 600,
                color: "var(--ink)",
              }}
            >
              {step.title}
            </span>
          </div>

          <button
            onClick={onClose}
            className="btn-survey"
            style={{ padding: "3px 8px", fontSize: "11px" }}
            aria-label="Exit tour"
          >
            Exit tour
          </button>
        </div>

        {/* Narrative text */}
        <p
          style={{
            fontSize: "13px",
            color: "var(--ink-secondary)",
            lineHeight: 1.5,
            margin: "0 0 12px 0",
          }}
        >
          {step.explanation}
        </p>

        {/* Controls Bar */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            borderTop: "1px solid var(--slate-subtle)",
            paddingTop: "10px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="btn-survey"
              style={{ padding: "4px 10px", fontSize: "12px" }}
            >
              {isPlaying ? "Pause" : "Resume"}
            </button>
            <span
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "11px",
                color: "var(--ink-muted)",
              }}
            >
              {Math.max(0, Math.ceil((step.durationSeconds * (100 - progress)) / 100))}s remaining
            </span>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <button
              disabled={currentStep === 0}
              onClick={() => {
                if (currentStep > 0) setCurrentStep(currentStep - 1);
              }}
              className="btn-survey"
              style={{
                padding: "4px 10px",
                fontSize: "12px",
                opacity: currentStep === 0 ? 0.5 : 1,
              }}
            >
              Previous
            </button>
            <button
              onClick={() => {
                if (currentStep < TOUR_STEPS.length - 1) {
                  setCurrentStep(currentStep + 1);
                } else {
                  onClose();
                }
              }}
              className="btn-survey btn-survey-primary"
              style={{ padding: "4px 12px", fontSize: "12px" }}
            >
              {currentStep < TOUR_STEPS.length - 1 ? "Next step" : "Finish tour"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
