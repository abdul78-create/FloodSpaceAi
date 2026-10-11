"use client";

import React, { useState } from "react";
import dynamic from "next/dynamic";
import type { TabId } from "@/data/types";
import Header from "@/components/common/Header";
import TourController from "@/components/common/TourController";
import AmbientContours from "@/components/common/AmbientContours";
import Footer from "@/components/common/Footer";

const MapHero = dynamic(() => import("@/components/map/MapHero"), {
  ssr: false,
  loading: () => (
    <div
      style={{
        width: "100%",
        height: "calc(100vh - 128px)",
        backgroundColor: "var(--fog)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontFamily: "var(--font-mono)",
        fontSize: "12px",
        color: "var(--ink-secondary)",
      }}
    >
      Loading satellite map & geospatial layers...
    </div>
  ),
});
import { RunProvider } from "@/data/RunContext";
import SatelliteComparison from "@/components/satellite/SatelliteComparison";
import AssetAnalysis from "@/components/assets/AssetAnalysis";
import ConnectivityAnalysis from "@/components/connectivity/ConnectivityAnalysis";
import SituationReportCopilot from "@/components/copilot/SituationReportCopilot";
import PipelineDiagram from "@/components/pipeline/PipelineDiagram";
import ProvenanceModal from "@/components/provenance/ProvenanceModal";

function DashboardContent() {
  const [activeTab, setActiveTab] = useState<TabId>("map");
  const [isTourActive, setIsTourActive] = useState(false);

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        minHeight: "100vh",
        backgroundColor: "var(--fog)",
        position: "relative",
      }}
    >
      {/* Subtle ambient drifting contour lines */}
      <AmbientContours />

      {/* Primary Field Survey Navigation Header */}
      <Header
        activeTab={activeTab}
        onTabChange={setActiveTab}
        onStartTour={() => setIsTourActive(true)}
        isTourActive={isTourActive}
      />

      {/* 3-Minute Guided Demo Tour Overlay */}
      <TourController
        isOpen={isTourActive}
        onClose={() => setIsTourActive(false)}
        onNavigateTab={(tab) => setActiveTab(tab)}
      />

      {/* Tab Screen Body */}
      <main
        style={{
          flex: 1,
          position: "relative",
          zIndex: 1,
        }}
      >
        {activeTab === "map" && <MapHero />}
        {activeTab === "satellite" && <SatelliteComparison />}
        {activeTab === "assets" && <AssetAnalysis />}
        {activeTab === "connectivity" && <ConnectivityAnalysis />}
        {activeTab === "copilot" && <SituationReportCopilot />}
        {activeTab === "pipeline" && <PipelineDiagram />}
        {activeTab === "provenance" && <ProvenanceModal />}
      </main>

      {/* Fixed Sticky Footer with Provenance & Disclaimers */}
      <Footer onNavigateTab={setActiveTab} />
    </div>
  );
}

export default function DashboardHome() {
  return (
    <RunProvider>
      <DashboardContent />
    </RunProvider>
  );
}
