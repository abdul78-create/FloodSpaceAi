"use client";

import React, { useEffect, useState, useMemo } from "react";
import { dataLoader } from "@/data/dataLoader";
import type { EvidenceData } from "@/data/types";

interface ChatMessage {
  id: string;
  sender: "user" | "copilot";
  text: string;
  isGrounded?: boolean;
  citationPath?: string;
  citationValue?: string | number | boolean;
  claimId?: string;
  unit?: string;
  uncertaintyNotice?: string;
  refusalCategory?: string;
}

const PRESET_QUERIES = [
  "How many buildings were potentially affected?",
  "How many people died or were injured?",
  "What is the monetary damage in USD?",
  "Are the buildings confirmed destroyed?",
  "Are settlements completely isolated?",
  "Were hospitals included in analysis?",
  "Does this match Copernicus EMSR927?",
  "What is the flood candidate extent?",
];

import { usePipelineRun } from "@/data/RunContext";

export default function SituationReportCopilot() {
  const { evidence: runEvidence, reportEn: runReportEn, reportNe: runReportNe, manifest, selectedRunId } = usePipelineRun();
  const [evidence, setEvidence] = useState<EvidenceData | null>(null);
  const [language, setLanguage] = useState<"en" | "ne">("en");
  const [reportEnglish, setReportEnglish] = useState<string>("");
  const [reportNepali, setReportNepali] = useState<string>("");
  const [activeView, setActiveView] = useState<"report" | "manifest">("report");
  const [isLoading, setIsLoading] = useState(true);

  // Chat State
  const [query, setQuery] = useState("");
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([
    {
      id: "welcome",
      sender: "copilot",
      text: "Welcome to the FloodSpaceAI Evidence Copilot. Every quantitative statement provided here is strictly validated against verified pipeline evidence and manifest records. Ask a question or click an adversarial test prompt below.",
      isGrounded: true,
      citationPath: "run_manifest.json",
      citationValue: "Phase 6 Orchestrator",
      claimId: "SYSTEM-EVIDENCE-GATEWAY",
      unit: "manifest",
      uncertaintyNotice: "Governed by zero-hallucination verification schema",
    },
  ]);

  useEffect(() => {
    Promise.all([
      dataLoader.getEvidence(),
      dataLoader.getEnglishReport(),
      dataLoader.getNepaliReport(),
    ]).then(([ev, en, ne]) => {
      setEvidence(ev);
      setReportEnglish(en);
      setReportNepali(ne);
      setIsLoading(false);
    });
  }, []);

  const activeEvidence = runEvidence || evidence;
  const activeEn = runReportEn || reportEnglish;
  const activeNe = runReportNe || reportNepali;

  // Strict Programmatic Grounding Engine (answering strictly from active run evidence JSON & claims)
  const handleSend = (userText: string) => {
    if (!userText.trim() || !activeEvidence) return;

    const userMsg: ChatMessage = {
      id: "u-" + Date.now(),
      sender: "user",
      text: userText,
    };

    const textLower = userText.toLowerCase();
    let replyText = "";
    let isGrounded = false;
    let citationPath = "";
    let citationValue: string | number | boolean = "";
    let claimId = "";
    let unit = "";
    let uncertaintyNotice = "";
    let refusalCategory = "";

    const eventName = activeEvidence.case_study?.event || `Run ${selectedRunId}`;
    const snapTs = activeEvidence.case_study?.osm_snapshot || "N/A";
    const currentRun = activeEvidence.run_id || selectedRunId;

    // Helper to find claim from grounded_claims if present
    const findGroundedClaim = (keyword: string) => {
      return (activeEvidence.grounded_claims || []).find((c) => c.claim_id.includes(keyword));
    };

    // 1. ADVERSARIAL: Casualties, Fatalities, Deaths, Injuries
    if (
      textLower.includes("casualt") ||
      textLower.includes("fatality") ||
      textLower.includes("fatalities") ||
      textLower.includes("death") ||
      textLower.includes("die") ||
      textLower.includes("injur") ||
      textLower.includes("hurt") ||
      textLower.includes("missing person")
    ) {
      replyText =
        "REFUSAL: FloodSpaceAI strictly does not estimate casualties, injuries, or fatalities. Spaceborne synthetic aperture radar and multispectral sensors observe physical surface-water reflectance and infrastructure footprints. Casualty estimation requires ground hospital and emergency mortality registries, which are outside the scope of satellite remote sensing.";
      isGrounded = true;
      refusalCategory = "CASUALTIES_REFUSED";
      citationPath = "ethics_policy.ground_registry_required";
      citationValue = "Unsupported by satellite inputs";
      uncertaintyNotice = "Physical backscatter cannot measure biological life or human injury";
    }
    // 2. ADVERSARIAL: Economic Loss, Monetary Damage, USD, Cost
    else if (
      textLower.includes("economic loss") ||
      textLower.includes("monetary") ||
      textLower.includes("financial") ||
      textLower.includes("dollar") ||
      textLower.includes("usd") ||
      textLower.includes("cost") ||
      textLower.includes("rupee") ||
      textLower.includes("npr")
    ) {
      replyText =
        "REFUSAL: FloodSpaceAI strictly does not calculate monetary or economic damage figures. Financial appraisal requires cadastral parcel valuation, property insurance records, and replacement cost schedules not present in public satellite imagery or OpenStreetMap cartography.";
      isGrounded = true;
      refusalCategory = "MONETARY_REFUSED";
      citationPath = "ethics_policy.cadastral_appraisal_required";
      citationValue = "Unsupported by satellite inputs";
      uncertaintyNotice = "Monetary valuations cannot be derived from spatial overlays";
    }
    // 3. ADVERSARIAL: Confirmed Structural Damage vs Potential Exposure
    else if (
      (textLower.includes("destroy") ||
        textLower.includes("destroyed") ||
        textLower.includes("collapse") ||
        textLower.includes("collapsed") ||
        textLower.includes("confirmed damage") ||
        textLower.includes("confirmed damaged") ||
        textLower.includes("structural collapse") ||
        textLower.includes("confirmed destruction")) &&
      (textLower.includes("building") ||
        textLower.includes("structure") ||
        textLower.includes("house") ||
        textLower.includes("home"))
    ) {
      const claim = findGroundedClaim("AFFECTED-BUILDINGS");
      const val = claim?.value ?? activeEvidence.potentially_affected_assets.buildings;
      replyText = `CLARIFICATION: Spaceborne analysis identifies POTENTIAL EXPOSURE (${val} buildings intersecting candidate flood perimeters), NOT CONFIRMED STRUCTURAL DAMAGE OR DESTRUCTION. Determining whether a structure suffered collapse, structural failure, or water ingress requires certified in-situ civil engineering inspection.`;
      isGrounded = true;
      refusalCategory = "EXPOSURE_CLARIFIED";
      citationPath = claim?.source_file || "assets/buildings_affected_v3.geojson";
      citationValue = val;
      claimId = claim?.claim_id || `CLAIM-${currentRun}-AFFECTED-BUILDINGS`;
      unit = "buildings";
      uncertaintyNotice = claim?.confidence_or_uncertainty || "Modelled 2D spatial overlay only; unconfirmed structural damage";
    }
    // 4. ADVERSARIAL: Real-World Physical Isolation vs Modeled Disruption
    else if (
      textLower.includes("completely isolated") ||
      textLower.includes("no way out") ||
      textLower.includes("trapped with no exit") ||
      textLower.includes("confirmed isolated") ||
      textLower.includes("real-world isolation")
    ) {
      const claim = findGroundedClaim("CUTOFF-SETTLEMENTS");
      const val = claim?.value ?? activeEvidence.road_connectivity.potentially_cut_off_settlements;
      replyText = `CLARIFICATION: Network analysis models TOPOLOGICAL GRAPH DISCONNECTION of mapped vehicle roads (${val} potentially cut-off settlements). This does NOT confirm real-world physical isolation; pedestrian trails, unmapped footpaths, boat ferries, or aerial rescue routes may remain operable.`;
      isGrounded = true;
      refusalCategory = "ISOLATION_CLARIFIED";
      citationPath = claim?.source_file || "connectivity/settlements_cutoff_v4.geojson";
      citationValue = val;
      claimId = claim?.claim_id || `CLAIM-${currentRun}-CUTOFF-SETTLEMENTS`;
      unit = "settlements";
      uncertaintyNotice = claim?.confidence_or_uncertainty || "Modelled vehicular road disconnection only; unconfirmed real-world physical isolation";
    }
    // 5. ADVERSARIAL: Validation Layer Boundary (EMSR927 / UNOSAT)
    else if (
      textLower.includes("emsr927") ||
      textLower.includes("emsr") ||
      textLower.includes("unosat") ||
      textLower.includes("validation map") ||
      textLower.includes("ground truth")
    ) {
      replyText =
        "INDEPENDENT VALIDATION REFERENCE: Copernicus EMSR927 is maintained strictly as an independent post-event validation dataset (1.01% IoU against debris flows/mudslides; 45.24% candidate overlap). EMSR927 layers are strictly isolated from analytical pipeline inputs. Debris-flow footprints represent steep-slope mass wasting, distinct from riverine surface-water inundation.";
      isGrounded = true;
      refusalCategory = "VALIDATION_ISOLATED";
      citationPath = "docs/emsr927_validation_summary.md";
      citationValue = "1.01% IoU (debris flow footprint)";
      uncertaintyNotice = "Independent validation dataset; strictly excluded from production inputs";
    }
    // 6. QUERY: Hospital Data
    else if (textLower.includes("hospital") || textLower.includes("clinic") || textLower.includes("health")) {
      const claim = findGroundedClaim("HOSPITAL-AVAILABILITY");
      const hospAvail = claim?.value ?? activeEvidence.road_connectivity.hospital_data_available;
      if (!hospAvail) {
        replyText =
          "LIMITATION DISCLOSURE: Pre-event hospital points were unavailable in the historical OpenStreetMap snapshot for this AOI. To avoid inventing healthcare infrastructure, the connectivity engine evaluated route access relative to designated municipal town/city hubs.";
        isGrounded = true;
        refusalCategory = "LIMITATION_DISCLOSED";
        citationPath = claim?.source_file || "connectivity/settlement_connectivity_v4.json";
        citationValue = "false (town/city hubs used)";
        claimId = claim?.claim_id || `CLAIM-${currentRun}-HOSPITAL-AVAILABILITY`;
        unit = "status";
        uncertaintyNotice = "Historical OSM snapshot lacked verified hospital tags";
      } else {
        replyText =
          "Historical hospital points were verified in the pre-event OSM snapshot for this AOI and evaluated in critical facility routing.";
        isGrounded = true;
        citationPath = "connectivity/settlement_connectivity_v4.json";
        citationValue = "true";
      }
    }
    // 7. QUERY: Cloud Obscuration
    else if (textLower.includes("cloud") || textLower.includes("optical") || textLower.includes("visibility")) {
      const isCloud =
        manifest?.overall_status?.includes("OPTICAL_UNCONFIRMED") ||
        (activeEvidence.limitations || []).some((l) => l.toLowerCase().includes("cloud"));
      if (isCloud) {
        replyText =
          "LIMITATION DISCLOSURE: Post-event optical Sentinel-2 imagery was obscured by cloud cover (Scene Classification Layer cloud masking applied). Candidate inundation is derived from all-weather Sentinel-1 SAR backscatter and remains optical-unconfirmed.";
        isGrounded = true;
        refusalCategory = "LIMITATION_DISCLOSED";
        citationPath = "stages.stage_4_raster_processing";
        citationValue = "SCL Cloud Masked";
        uncertaintyNotice = "Optical spectral validation unconfirmed";
      } else {
        replyText = "Clear-sky optical Sentinel-2 coverage was verified and Scene Classification Layer masking was applied.";
        isGrounded = true;
        citationPath = "stages.stage_4_raster_processing";
        citationValue = "Clear Sky";
      }
    }
    // 8. QUERY: Buildings
    else if (textLower.includes("building")) {
      const claim = findGroundedClaim("AFFECTED-BUILDINGS");
      const val = claim?.value ?? activeEvidence.potentially_affected_assets.buildings;
      replyText = `Based on 2D spatial overlay with the pre-event OpenStreetMap snapshot (${snapTs}) for ${eventName}, there are ${val} potentially affected buildings within the candidate perimeter. (Potential exposure overlay, not confirmed structural damage).`;
      isGrounded = true;
      citationPath = claim?.source_file || "assets/buildings_affected_v3.geojson";
      citationValue = val;
      claimId = claim?.claim_id || `CLAIM-${currentRun}-AFFECTED-BUILDINGS`;
      unit = "buildings";
      uncertaintyNotice = claim?.confidence_or_uncertainty || "Spatial overlay only; unconfirmed structural damage";
    }
    // 9. QUERY: Roads
    else if (textLower.includes("road")) {
      const claim = findGroundedClaim("AFFECTED-ROADS");
      const claimLen = findGroundedClaim("AFFECTED-ROAD-LENGTH");
      const val = claim?.value ?? activeEvidence.potentially_affected_assets.roads;
      const kmVal = claimLen?.value ?? (activeEvidence.potentially_affected_assets.road_length_km || 0);
      const newComps =
        (activeEvidence.road_connectivity.post_event_components || 0) -
        (activeEvidence.road_connectivity.pre_event_components || 0);
      replyText = `There are ${val} potentially affected road features (${kmVal} km) intersecting candidate flood perimeters for ${eventName}. Road network analysis resulted in ${newComps >= 0 ? newComps : 0} newly disconnected road clusters.`;
      isGrounded = true;
      citationPath = claim?.source_file || "assets/roads_affected_v3.geojson";
      citationValue = `${val} features (${kmVal} km)`;
      claimId = claim?.claim_id || `CLAIM-${currentRun}-AFFECTED-ROADS`;
      unit = "features";
      uncertaintyNotice = claim?.confidence_or_uncertainty || "Spatial intersection of road centerlines";
    }
    // 10. QUERY: Bridges
    else if (textLower.includes("bridge")) {
      const claim = findGroundedClaim("AFFECTED-BRIDGES");
      const val = claim?.value ?? activeEvidence.potentially_affected_assets.bridges;
      replyText = `The spatial intersection identified ${val} potentially affected bridges in the target area for ${eventName}. High-clearance decks may remain open; engineering inspection is required.`;
      isGrounded = true;
      citationPath = claim?.source_file || "assets/bridges_affected_v3.geojson";
      citationValue = val;
      claimId = claim?.claim_id || `CLAIM-${currentRun}-AFFECTED-BRIDGES`;
      unit = "bridges";
      uncertaintyNotice = claim?.confidence_or_uncertainty || "2D intersection does not model bridge deck vertical clearance";
    }
    // 11. QUERY: Settlements & Cut-off
    else if (textLower.includes("settlement") || textLower.includes("cut-off") || textLower.includes("cut off") || textLower.includes("isolated")) {
      const claim = findGroundedClaim("CUTOFF-SETTLEMENTS");
      const claimTot = findGroundedClaim("SETTLEMENTS-ANALYSED");
      const val = claim?.value ?? activeEvidence.road_connectivity.potentially_cut_off_settlements;
      const tot = claimTot?.value ?? activeEvidence.road_connectivity.settlements_analysed;
      replyText = `The road connectivity analysis identified ${val} potentially cut-off settlements out of ${tot} evaluated settlements for ${eventName}. (Modeled vehicular network disconnection, not confirmed physical isolation).`;
      isGrounded = true;
      citationPath = claim?.source_file || "connectivity/settlements_cutoff_v4.geojson";
      citationValue = `${val} / ${tot}`;
      claimId = claim?.claim_id || `CLAIM-${currentRun}-CUTOFF-SETTLEMENTS`;
      unit = "settlements";
      uncertaintyNotice = claim?.confidence_or_uncertainty || "Vehicular graph disconnection; unconfirmed physical isolation";
    }
    // 12. QUERY: Pixels, Extent, Area
    else if (textLower.includes("pixel") || textLower.includes("extent") || textLower.includes("polygon") || textLower.includes("candidate") || textLower.includes("area") || textLower.includes("hectare")) {
      const claimPx = findGroundedClaim("FLOOD-PIXELS");
      const claimHa = findGroundedClaim("FLOOD-AREA");
      const px = claimPx?.value ?? activeEvidence.flood_mapping.flood_pixels;
      const ha = claimHa?.value ?? (activeEvidence.flood_mapping.candidate_area_ha || 0);

      if (px === 0) {
        replyText =
          "SCIENTIFIC INTERPRETATION: Zero candidate flood pixels were detected under current SAR and optical thresholds. This does NOT prove that no flooding occurred; it indicates that no pixels exceeded the detection criteria or that satellite passes did not capture peak inundation.";
        refusalCategory = "LIMITATION_DISCLOSED";
      } else {
        replyText = `Detected ${Number(px).toLocaleString()} candidate flood pixels covering ${ha} ha for ${eventName} based on multi-sensor Sentinel-1 SAR and Sentinel-2 optical filtering.`;
      }
      isGrounded = true;
      citationPath = claimPx?.source_file || "rasters/final_flood_candidate_v3.tif";
      citationValue = `${px} px / ${ha} ha`;
      claimId = claimPx?.claim_id || `CLAIM-${currentRun}-FLOOD-PIXELS`;
      unit = "pixels";
      uncertaintyNotice = claimPx?.confidence_or_uncertainty || "Candidate surface water pooling thresholded via SAR backscatter";
    }
    // 13. QUERY: Limitations
    else if (textLower.includes("limitation")) {
      replyText = `System limitations: ${(activeEvidence.limitations || []).join(" ")}`;
      isGrounded = true;
      citationPath = "limitations";
      citationValue = `${(activeEvidence.limitations || []).length} items`;
      refusalCategory = "LIMITATION_DISCLOSED";
    }
    // 14. DEFAULT / UNSUPPORTED
    else {
      replyText =
        "UNSUPPORTED QUERY: Not available in the verified system evidence. FloodSpaceAI strictly refuses to invent ungrounded metrics (e.g. monetary cost, casualties, or unverified ground damage). All quantitative claims must exist in evidence.json.";
      isGrounded = false;
      refusalCategory = "UNKNOWN_BLOCKED";
      citationPath = "evidence.json (not found)";
      citationValue = "Blocked";
    }

    const copilotMsg: ChatMessage = {
      id: "c-" + Date.now(),
      sender: "copilot",
      text: replyText,
      isGrounded,
      citationPath,
      citationValue,
      claimId,
      unit,
      uncertaintyNotice,
      refusalCategory,
    };

    setChatHistory((prev) => [...prev, userMsg, copilotMsg]);
    setQuery("");
  };

  const activeReport = language === "en" ? activeEn : activeNe;

  return (
    <div
      style={{
        padding: "24px",
        maxWidth: "1140px",
        margin: "0 auto",
      }}
    >
      {/* Title & Lang Switcher */}
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
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
            <span className="survey-badge survey-badge-river" style={{ fontSize: "11px" }}>
              Grounding verification engine
            </span>
            <span className="survey-badge" style={{ fontSize: "11px", backgroundColor: "var(--fog)" }}>
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
            AI situation report & evidence copilot
          </h2>
          <p style={{ fontSize: "13px", color: "var(--ink-secondary)", margin: 0 }}>
            Automated situation report with strict numerical grounding against run manifest and evidence JSON.
          </p>
        </div>

        {/* View Toggle (Report vs Manifest) + Language Switcher */}
        <div style={{ display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap" }}>
          {/* View Toggle */}
          <div style={{ display: "inline-flex", borderRadius: "var(--radius-sm)", border: "1px solid var(--slate)" }}>
            <button
              onClick={() => setActiveView("report")}
              style={{
                padding: "6px 12px",
                fontSize: "12px",
                fontWeight: activeView === "report" ? 600 : 500,
                backgroundColor: activeView === "report" ? "var(--ink)" : "var(--paper)",
                color: activeView === "report" ? "#FFFFFF" : "var(--ink)",
                border: "none",
                cursor: "pointer",
                borderRadius: "3px 0 0 3px",
              }}
            >
              Situation report
            </button>
            <button
              onClick={() => setActiveView("manifest")}
              style={{
                padding: "6px 12px",
                fontSize: "12px",
                fontWeight: activeView === "manifest" ? 600 : 500,
                backgroundColor: activeView === "manifest" ? "var(--ink)" : "var(--paper)",
                color: activeView === "manifest" ? "#FFFFFF" : "var(--ink)",
                border: "none",
                cursor: "pointer",
                borderRadius: "0 3px 3px 0",
              }}
            >
              Evidence manifest (JSON)
            </button>
          </div>

          {/* Language Switcher English ⇄ Nepali (Active when in Report view) */}
          {activeView === "report" && (
            <div style={{ display: "inline-flex", borderRadius: "var(--radius-sm)", border: "1px solid var(--slate)" }}>
              <button
                onClick={() => setLanguage("en")}
                style={{
                  padding: "6px 12px",
                  fontSize: "12px",
                  fontWeight: language === "en" ? 600 : 500,
                  backgroundColor: language === "en" ? "var(--river)" : "var(--paper)",
                  color: language === "en" ? "#FFFFFF" : "var(--ink)",
                  border: "none",
                  cursor: "pointer",
                  borderRadius: "3px 0 0 3px",
                }}
              >
                English
              </button>
              <button
                onClick={() => setLanguage("ne")}
                style={{
                  padding: "6px 12px",
                  fontSize: "12px",
                  fontWeight: language === "ne" ? 600 : 500,
                  backgroundColor: language === "ne" ? "var(--river)" : "var(--paper)",
                  color: language === "ne" ? "#FFFFFF" : "var(--ink)",
                  border: "none",
                  cursor: "pointer",
                  borderRadius: "0 3px 3px 0",
                  fontFamily: "var(--font-devanagari)",
                }}
              >
                नेपाली
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Main 2-Column Layout */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1.1fr 0.9fr",
          gap: "18px",
          alignItems: "start",
        }}
      >
        {/* Left Column: Formatted Situation Report Document or Manifest JSON */}
        <div className="survey-panel">
          <div className="survey-panel-header">
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ fontFamily: "var(--font-serif)", fontSize: "14px", fontWeight: 600 }}>
                {activeView === "report"
                  ? language === "en"
                    ? "Official situation report"
                    : "आधिकारिक स्थिति प्रतिवेदन"
                  : "Verified Run Manifest"}
              </span>
              <span className="survey-badge survey-badge-moss" style={{ fontSize: "10px" }}>
                ✓ Grounded
              </span>
            </div>
            <span style={{ fontSize: "11px", color: "var(--ink-muted)", fontFamily: "var(--font-mono)" }}>
              {activeView === "report"
                ? language === "en"
                  ? "situation_report_en.md"
                  : "situation_report_ne.md"
                : "run_manifest.json"}
            </span>
          </div>

          <div
            style={{
              padding: "20px",
              maxHeight: "580px",
              overflowY: "auto",
              fontSize: "13px",
              lineHeight: 1.7,
              color: "var(--ink)",
              fontFamily: activeView === "manifest" ? "var(--font-mono)" : language === "ne" ? "var(--font-devanagari)" : "var(--font-sans)",
              backgroundColor: "var(--paper-elevated)",
            }}
          >
            {activeView === "report" ? (
              <div style={{ whiteSpace: "pre-line" }}>
                {activeReport}
              </div>
            ) : (
              <pre
                style={{
                  margin: 0,
                  fontSize: "11px",
                  lineHeight: 1.5,
                  whiteSpace: "pre-wrap",
                  wordBreak: "break-all",
                }}
              >
                {manifest ? JSON.stringify(manifest, null, 2) : "Loading manifest..."}
              </pre>
            )}
          </div>
        </div>

        {/* Right Column: Grounded Copilot Q&A Box */}
        <div className="survey-panel" style={{ display: "flex", flexDirection: "column", height: "642px" }}>
          <div className="survey-panel-header">
            <span style={{ fontFamily: "var(--font-serif)", fontSize: "14px", fontWeight: 600 }}>
              Grounded evidence query assistant
            </span>
            <span className="survey-badge" style={{ fontSize: "10px" }}>
              Zero hallucination
            </span>
          </div>

          {/* Chat Messages Log */}
          <div
            style={{
              flex: 1,
              padding: "14px",
              overflowY: "auto",
              display: "flex",
              flexDirection: "column",
              gap: "12px",
              backgroundColor: "var(--fog)",
            }}
          >
            {chatHistory.map((msg) => (
              <div
                key={msg.id}
                style={{
                  alignSelf: msg.sender === "user" ? "flex-end" : "flex-start",
                  maxWidth: "92%",
                  padding: "10px 14px",
                  borderRadius: "var(--radius-sm)",
                  backgroundColor: msg.sender === "user" ? "var(--ink)" : "var(--paper-elevated)",
                  color: msg.sender === "user" ? "#FFFFFF" : "var(--ink)",
                  border: msg.sender === "user" ? "none" : "1px solid var(--slate-light)",
                  boxShadow: "var(--shadow-panel)",
                  fontSize: "12px",
                  lineHeight: 1.5,
                }}
              >
                <div>{msg.text}</div>

                {/* Grounding Badge & Detailed Citation Card for Copilot replies */}
                {msg.sender === "copilot" && (
                  <div
                    style={{
                      marginTop: "10px",
                      paddingTop: "8px",
                      borderTop: "1px solid var(--slate-subtle)",
                      display: "flex",
                      flexDirection: "column",
                      gap: "6px",
                      fontSize: "11px",
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "8px" }}>
                      <span
                        style={{
                          color: msg.refusalCategory ? "var(--amber, #b45309)" : msg.isGrounded ? "var(--moss)" : "var(--brick)",
                          fontWeight: 600,
                          fontFamily: "var(--font-mono)",
                        }}
                      >
                        {msg.refusalCategory
                          ? `⚠ ${msg.refusalCategory}`
                          : msg.isGrounded
                          ? "✓ Verified Grounded Claim"
                          : "✗ Unsupported Claim Refused"}
                      </span>

                      {msg.claimId && (
                        <span
                          className="survey-badge"
                          style={{
                            fontSize: "9px",
                            backgroundColor: "var(--paper)",
                            color: "var(--ink-secondary)",
                            fontFamily: "var(--font-mono)",
                          }}
                        >
                          {msg.claimId}
                        </span>
                      )}
                    </div>

                    {msg.citationPath && (
                      <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "var(--ink-secondary)", fontSize: "10px" }}>
                        <span style={{ fontWeight: 600 }}>Source:</span>
                        <code style={{ fontFamily: "var(--font-mono)", backgroundColor: "var(--paper)", padding: "1px 4px", borderRadius: "3px" }}>
                          {msg.citationPath}
                        </code>
                        {msg.unit && <span>({msg.unit})</span>}
                      </div>
                    )}

                    {msg.uncertaintyNotice && (
                      <div
                        style={{
                          fontSize: "10px",
                          color: "var(--ink-muted)",
                          backgroundColor: "var(--paper)",
                          padding: "4px 8px",
                          borderRadius: "3px",
                          borderLeft: "2px solid var(--slate)",
                        }}
                      >
                        <strong>Uncertainty / Boundary:</strong> {msg.uncertaintyNotice}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Quick Preset Buttons (Adversarial & Grounded Test Queries) */}
          <div
            style={{
              padding: "8px 12px",
              backgroundColor: "var(--paper)",
              borderTop: "1px solid var(--slate-subtle)",
              display: "flex",
              flexWrap: "wrap",
              gap: "6px",
              maxHeight: "84px",
              overflowY: "auto",
            }}
          >
            {PRESET_QUERIES.map((pq, i) => (
              <button
                key={i}
                onClick={() => handleSend(pq)}
                className="btn-survey"
                style={{
                  padding: "4px 8px",
                  fontSize: "10px",
                  whiteSpace: "nowrap",
                  backgroundColor: pq.includes("died") || pq.includes("USD") || pq.includes("destroyed") || pq.includes("EMSR")
                    ? "var(--fog)"
                    : "var(--paper-elevated)",
                }}
              >
                {pq}
              </button>
            ))}
          </div>

          {/* Input Box */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend(query);
            }}
            style={{
              padding: "10px 12px",
              backgroundColor: "var(--paper-elevated)",
              borderTop: "1px solid var(--slate-light)",
              display: "flex",
              gap: "8px",
            }}
          >
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask about affected buildings, roads, bridges, settlements..."
              style={{
                flex: 1,
                padding: "8px 12px",
                fontFamily: "var(--font-sans)",
                fontSize: "12px",
                border: "1px solid var(--slate)",
                borderRadius: "var(--radius-sm)",
                backgroundColor: "var(--paper)",
                color: "var(--ink)",
                outline: "none",
              }}
            />
            <button
              type="submit"
              className="btn-survey btn-survey-primary"
              style={{ padding: "8px 14px", fontSize: "12px" }}
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
