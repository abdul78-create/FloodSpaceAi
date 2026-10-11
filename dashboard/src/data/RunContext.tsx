"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { dataLoader, FALLBACK_EVIDENCE } from "./dataLoader";
import type { RunRegistryEntry, RunManifest, EvidenceData } from "./types";

interface RunContextValue {
  runs: RunRegistryEntry[];
  selectedRunId: string;
  setSelectedRunId: (id: string) => void;
  activeRun: RunRegistryEntry | null;
  manifest: RunManifest | null;
  evidence: EvidenceData;
  reportEn: string;
  reportNe: string;
  isLoading: boolean;
}

const RunContext = createContext<RunContextValue | undefined>(undefined);

export function RunProvider({ children }: { children: ReactNode }) {
  const [runs, setRuns] = useState<RunRegistryEntry[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<string>("trishuli_benchmark_verified");
  const [manifest, setManifest] = useState<RunManifest | null>(null);
  const [evidence, setEvidence] = useState<EvidenceData>(FALLBACK_EVIDENCE);
  const [reportEn, setReportEn] = useState<string>("");
  const [reportNe, setReportNe] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Load runs registry on mount
  useEffect(() => {
    dataLoader.getPipelineRuns().then((list) => {
      setRuns(list);
      if (list.length > 0 && !list.some((r) => r.run_id === "trishuli_benchmark_verified")) {
        setSelectedRunId(list[0].run_id);
      }
    });
  }, []);

  // When selectedRunId changes, load manifest, evidence, and reports
  useEffect(() => {
    if (!selectedRunId) return;
    setIsLoading(true);

    Promise.all([
      dataLoader.getRunManifest(selectedRunId),
      dataLoader.getRunEvidence(selectedRunId),
      dataLoader.getRunReport(selectedRunId, "en"),
      dataLoader.getRunReport(selectedRunId, "ne"),
    ])
      .then(([m, ev, en, ne]) => {
        setManifest(m);
        setEvidence(ev);
        setReportEn(en);
        setReportNe(ne);
        setIsLoading(false);
      })
      .catch((err) => {
        console.warn("Error loading pipeline run details:", err);
        setIsLoading(false);
      });
  }, [selectedRunId]);

  const activeRun = runs.find((r) => r.run_id === selectedRunId) || null;

  return (
    <RunContext.Provider
      value={{
        runs,
        selectedRunId,
        setSelectedRunId,
        activeRun,
        manifest,
        evidence,
        reportEn,
        reportNe,
        isLoading,
      }}
    >
      {children}
    </RunContext.Provider>
  );
}

export function usePipelineRun() {
  const context = useContext(RunContext);
  if (!context) {
    throw new Error("usePipelineRun must be used within a RunProvider");
  }
  return context;
}
