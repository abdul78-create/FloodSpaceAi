"use client";

import React, { useEffect, useRef, useState, useCallback } from "react";
import * as maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { dataLoader } from "@/data/dataLoader";
import { usePipelineRun } from "@/data/RunContext";

interface LayerState {
  id: string;
  label: string;
  count: string;
  color: string;
  visible: boolean;
  opacity: number;
}

export default function MapHero() {
  const { manifest, activeRun, selectedRunId } = usePipelineRun();
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [coordinates, setCoordinates] = useState({ lat: 27.901, lng: 85.125 });
  const [isAnimatingRise, setIsAnimatingRise] = useState(false);

  const metrics = manifest?.metrics || {};
  const isUnavailable = manifest?.overall_status?.includes("UNAVAILABLE") || manifest?.overall_status === "FAILED";

  // Dynamic layer control states updating on active run
  const isBenchmark = selectedRunId === "trishuli_benchmark_verified";
  const clusters = metrics.candidate_flood_clusters ?? (isBenchmark ? 84 : 0);
  const bldgs = metrics.potentially_affected_buildings ?? (isBenchmark ? 195 : 0);
  const roads = metrics.potentially_affected_roads ?? (isBenchmark ? 115 : 0);
  const bridges = metrics.potentially_affected_bridges ?? (isBenchmark ? 13 : 0);
  const cutoffs = metrics.potentially_cut_off_settlements ?? (isBenchmark ? 18 : 0);

  const [layers, setLayers] = useState<LayerState[]>([
    { id: "flood-v3", label: "Modelled potential inundation (V3)", count: `${clusters} candidate polygons`, color: "#2E6F9E", visible: true, opacity: 0.65 },
    { id: "buildings-v3", label: "Potentially affected buildings", count: `${bldgs} structures`, color: "#B98A3E", visible: true, opacity: 0.85 },
    { id: "roads-v3", label: "Potentially affected roads", count: `${roads} features`, color: "#B98A3E", visible: true, opacity: 0.9 },
    { id: "bridges-v3", label: "Potentially affected bridges", count: `${bridges} bridges`, color: "#1E2A32", visible: true, opacity: 1.0 },
    { id: "settlements-v4", label: "Potentially cut-off settlements", count: `${cutoffs} settlements`, color: "#B04A3A", visible: true, opacity: 1.0 },
  ]);

  // Sync layer state and sources when run changes
  useEffect(() => {
    setLayers([
      { id: "flood-v3", label: "Modelled potential inundation (V3)", count: `${clusters} candidate polygons`, color: "#2E6F9E", visible: true, opacity: 0.65 },
      { id: "buildings-v3", label: "Potentially affected buildings", count: `${bldgs} structures`, color: "#B98A3E", visible: true, opacity: 0.85 },
      { id: "roads-v3", label: "Potentially affected roads", count: `${roads} features`, color: "#B98A3E", visible: true, opacity: 0.9 },
      { id: "bridges-v3", label: "Potentially affected bridges", count: `${bridges} bridges`, color: "#1E2A32", visible: true, opacity: 1.0 },
      { id: "settlements-v4", label: "Potentially cut-off settlements", count: `${cutoffs} settlements`, color: "#B04A3A", visible: true, opacity: 1.0 },
    ]);

    if (!mapRef.current) return;
    const map = mapRef.current;
    const urls = dataLoader.getGeoJsonUrls(selectedRunId);

    const updateSource = async (srcId: string, url: string) => {
      try {
        const src = map.getSource(srcId) as maplibregl.GeoJSONSource | undefined;
        if (!src) return;
        const res = await fetch(url);
        if (res.ok) {
          const geojson = await res.json();
          src.setData(geojson);
        } else {
          src.setData({ type: "FeatureCollection", features: [] });
        }
      } catch {
        const src = map.getSource(srcId) as maplibregl.GeoJSONSource | undefined;
        if (src) src.setData({ type: "FeatureCollection", features: [] });
      }
    };

    if (map.isStyleLoaded()) {
      updateSource("src-flood-v3", urls.floodPolygons);
      updateSource("src-buildings-v3", urls.buildings);
      updateSource("src-roads-v3", urls.roads);
      updateSource("src-bridges-v3", urls.bridges);
      updateSource("src-settlements-v4", urls.settlements);
    }

    const currentBbox = manifest?.inputs?.bbox || activeRun?.bbox;
    if (currentBbox && currentBbox.length === 4) {
      map.fitBounds(
        [[currentBbox[0], currentBbox[1]], [currentBbox[2], currentBbox[3]]],
        { padding: 50, duration: 1000 }
      );
    }
  }, [selectedRunId, manifest, clusters, bldgs, roads, bridges, cutoffs]);

  // Center of Trishuli AOI or active run bbox
  const bbox = manifest?.inputs?.bbox || activeRun?.bbox || [84.9, 27.75, 85.25, 28.05];
  const defaultCenter: [number, number] = [
    (bbox[0] + bbox[2]) / 2,
    (bbox[1] + bbox[3]) / 2
  ];
  const defaultZoom = 11.2;

  // Initialize MapLibre
  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return;

    if (typeof window !== "undefined") {
      try {
        (maplibregl as unknown as { setWorkerUrl?: (url: string) => void }).setWorkerUrl?.("/maplibre-gl-worker.mjs");
      } catch {
        // Fallback to default worker loader
      }
    }

    const map = new maplibregl.Map({
      container: mapContainerRef.current,
      style: {
        version: 8,
        sources: {
          "satellite-tiles": {
            type: "raster",
            tiles: [
              "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
            ],
            tileSize: 256,
            attribution: "Esri, Maxar, Earthstar Geographics, CNES/Airbus DS",
          },
          "osm-overlay": {
            type: "raster",
            tiles: [
              "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png"
            ],
            tileSize: 256,
            attribution: "© OpenStreetMap contributors",
          }
        },
        layers: [
          {
            id: "satellite-layer",
            type: "raster",
            source: "satellite-tiles",
            minzoom: 0,
            maxzoom: 19,
          },
          {
            id: "osm-layer",
            type: "raster",
            source: "osm-overlay",
            minzoom: 0,
            maxzoom: 19,
            paint: {
              "raster-opacity": 0.18,
            }
          }
        ]
      },
      center: defaultCenter,
      zoom: defaultZoom,
    });

    map.addControl(new maplibregl.NavigationControl({ showCompass: true }), "top-right");
    map.addControl(new maplibregl.ScaleControl({ maxWidth: 120, unit: "metric" }), "bottom-left");

    map.on("mousemove", (e) => {
      setCoordinates({
        lat: Number(e.lngLat.lat.toFixed(4)),
        lng: Number(e.lngLat.lng.toFixed(4)),
      });
    });

    map.on("load", () => {
      const urls = dataLoader.getGeoJsonUrls();

      // 1. Flood Polygons Source & Layers
      map.addSource("src-flood-v3", {
        type: "geojson",
        data: urls.floodPolygons,
      });

      map.addLayer({
        id: "flood-v3-fill",
        type: "fill",
        source: "src-flood-v3",
        paint: {
          "fill-color": "#2E6F9E",
          "fill-opacity": 0.65,
        },
      });

      map.addLayer({
        id: "flood-v3-line",
        type: "line",
        source: "src-flood-v3",
        paint: {
          "line-color": "#1E4E70",
          "line-width": 1.2,
          "line-opacity": 0.9,
        },
      });

      // 2. Buildings Layer
      map.addSource("src-buildings-v3", {
        type: "geojson",
        data: urls.buildings,
      });

      map.addLayer({
        id: "buildings-v3-fill",
        type: "fill",
        source: "src-buildings-v3",
        paint: {
          "fill-color": "#B98A3E",
          "fill-opacity": 0.85,
        },
      });

      map.addLayer({
        id: "buildings-v3-stroke",
        type: "line",
        source: "src-buildings-v3",
        paint: {
          "line-color": "#4A3512",
          "line-width": 0.8,
        },
      });

      // 3. Roads Layer
      map.addSource("src-roads-v3", {
        type: "geojson",
        data: urls.roads,
      });

      map.addLayer({
        id: "roads-v3-line",
        type: "line",
        source: "src-roads-v3",
        paint: {
          "line-color": "#DDA74F",
          "line-width": 2.2,
          "line-dasharray": [3, 1],
        },
      });

      // 4. Bridges Layer
      map.addSource("src-bridges-v3", {
        type: "geojson",
        data: urls.bridges,
      });

      map.addLayer({
        id: "bridges-v3-circle",
        type: "circle",
        source: "src-bridges-v3",
        paint: {
          "circle-radius": 5,
          "circle-color": "#1E2A32",
          "circle-stroke-width": 2,
          "circle-stroke-color": "#FFFFFF",
        },
      });

      // 5. Potentially Cut-off Settlements
      map.addSource("src-settlements-v4", {
        type: "geojson",
        data: urls.settlements,
      });

      map.addLayer({
        id: "settlements-v4-pulse",
        type: "circle",
        source: "src-settlements-v4",
        paint: {
          "circle-radius": 12,
          "circle-color": "#B04A3A",
          "circle-opacity": 0.25,
        },
      });

      map.addLayer({
        id: "settlements-v4-center",
        type: "circle",
        source: "src-settlements-v4",
        paint: {
          "circle-radius": 6,
          "circle-color": "#B04A3A",
          "circle-stroke-width": 1.5,
          "circle-stroke-color": "#FFFFFF",
        },
      });

      // Interactive Click Popups
      map.on("click", "settlements-v4-center", (e) => {
        if (!e.features || !e.features[0]) return;
        const feat = e.features[0];
        const props = feat.properties || {};
        const coords = (feat.geometry as any).coordinates.slice();

        new maplibregl.Popup()
          .setLngLat(coords)
          .setHTML(`
            <div style="font-family: var(--font-sans); padding: 4px;">
              <span class="survey-badge survey-badge-brick" style="font-size:10px; margin-bottom:4px;">
                Potentially cut-off settlement
              </span>
              <h4 style="margin: 4px 0 2px 0; font-family: var(--font-serif); font-size: 15px; color: var(--ink);">
                ${props.name || props.settlement_name || "Settlement"}
              </h4>
              <p style="margin: 0; font-size: 12px; color: var(--ink-secondary);">
                Nearest hub: <strong>${props.nearest_town_or_city || "Bidur"}</strong><br/>
                Pre-event connection: <span style="color:var(--moss)">Connected</span><br/>
                Post-event status: <span style="color:var(--brick)">Potential road disconnection</span>
              </p>
              <div style="margin-top: 6px; font-size: 10px; color: var(--ink-muted); font-style: italic;">
                Modelled connectivity result; not confirmed real-world isolation.
              </div>
            </div>
          `)
          .addTo(map);
      });

      map.on("mouseenter", "settlements-v4-center", () => {
        map.getCanvas().style.cursor = "pointer";
      });
      map.on("mouseleave", "settlements-v4-center", () => {
        map.getCanvas().style.cursor = "";
      });

      // Buildings Click Popup
      map.on("click", "buildings-v3-fill", (e) => {
        if (!e.features || !e.features[0]) return;
        const coords = e.lngLat;
        new maplibregl.Popup()
          .setLngLat(coords)
          .setHTML(`
            <div style="font-family: var(--font-sans); padding: 4px;">
              <span class="survey-badge survey-badge-silt" style="font-size:10px;">
                Potentially affected building
              </span>
              <p style="margin: 4px 0 0 0; font-size: 12px; color: var(--ink-secondary);">
                OSM Building footprint intersects V3 flood candidate polygon.<br/>
                <span style="font-size: 10px; color: var(--ink-muted);">
                  Spatial intersection only; does not confirm physical structure damage.
                </span>
              </p>
            </div>
          `)
          .addTo(map);
      });

      // Roads Click Popup
      map.on("click", "roads-v3-line", (e) => {
        if (!e.features || !e.features[0]) return;
        new maplibregl.Popup()
          .setLngLat(e.lngLat)
          .setHTML(`
            <div style="font-family: var(--font-sans); padding: 4px;">
              <span class="survey-badge survey-badge-silt" style="font-size:10px;">
                Potentially affected road segment
              </span>
              <p style="margin: 4px 0 0 0; font-size: 12px; color: var(--ink-secondary);">
                Vehicle road feature overlapping candidate inundation boundary.
              </p>
            </div>
          `)
          .addTo(map);
      });

      setIsLoaded(true);
      mapRef.current = map;
    });

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  // Update layer visibility and opacity
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !isLoaded) return;

    layers.forEach((l) => {
      const vis = l.visible ? "visible" : "none";
      if (l.id === "flood-v3") {
        if (map.getLayer("flood-v3-fill")) {
          map.setLayoutProperty("flood-v3-fill", "visibility", vis);
          map.setPaintProperty("flood-v3-fill", "fill-opacity", l.opacity);
        }
        if (map.getLayer("flood-v3-line")) {
          map.setLayoutProperty("flood-v3-line", "visibility", vis);
        }
      } else if (l.id === "buildings-v3") {
        if (map.getLayer("buildings-v3-fill")) {
          map.setLayoutProperty("buildings-v3-fill", "visibility", vis);
          map.setPaintProperty("buildings-v3-fill", "fill-opacity", l.opacity);
        }
        if (map.getLayer("buildings-v3-stroke")) {
          map.setLayoutProperty("buildings-v3-stroke", "visibility", vis);
        }
      } else if (l.id === "roads-v3") {
        if (map.getLayer("roads-v3-line")) {
          map.setLayoutProperty("roads-v3-line", "visibility", vis);
          map.setPaintProperty("roads-v3-line", "line-opacity", l.opacity);
        }
      } else if (l.id === "bridges-v3") {
        if (map.getLayer("bridges-v3-circle")) {
          map.setLayoutProperty("bridges-v3-circle", "visibility", vis);
        }
      } else if (l.id === "settlements-v4") {
        if (map.getLayer("settlements-v4-pulse")) {
          map.setLayoutProperty("settlements-v4-pulse", "visibility", vis);
        }
        if (map.getLayer("settlements-v4-center")) {
          map.setLayoutProperty("settlements-v4-center", "visibility", vis);
        }
      }
    });
  }, [layers, isLoaded]);

  // Animation: Trigger Opening Sequence / Water Rise
  const playFloodRiseSequence = useCallback(() => {
    const map = mapRef.current;
    if (!map || !isLoaded || isAnimatingRise) return;

    setIsAnimatingRise(true);

    // 1. Hide flood & asset layers
    map.setPaintProperty("flood-v3-fill", "fill-opacity", 0);
    map.setLayoutProperty("buildings-v3-fill", "visibility", "none");
    map.setLayoutProperty("roads-v3-line", "visibility", "none");
    map.setLayoutProperty("bridges-v3-circle", "visibility", "none");
    map.setLayoutProperty("settlements-v4-center", "visibility", "none");
    map.setLayoutProperty("settlements-v4-pulse", "visibility", "none");

    // Smooth fly to river valley
    map.flyTo({
      center: [85.14, 27.92],
      zoom: 12.0,
      pitch: 20,
      duration: 1800,
    });

    // 2. Animate flood water rise (0.0 -> 0.70)
    setTimeout(() => {
      let currentOpacity = 0;
      const targetOpacity = 0.7;
      const interval = setInterval(() => {
        currentOpacity += 0.05;
        if (currentOpacity >= targetOpacity) {
          clearInterval(interval);
          map.setPaintProperty("flood-v3-fill", "fill-opacity", targetOpacity);

          // 3. Drop in infrastructure layers sequentially
          setTimeout(() => {
            map.setLayoutProperty("roads-v3-line", "visibility", "visible");
          }, 400);

          setTimeout(() => {
            map.setLayoutProperty("buildings-v3-fill", "visibility", "visible");
            map.setLayoutProperty("bridges-v3-circle", "visibility", "visible");
          }, 800);

          // 4. Cut-off settlements pulse in Brick
          setTimeout(() => {
            map.setLayoutProperty("settlements-v4-center", "visibility", "visible");
            map.setLayoutProperty("settlements-v4-pulse", "visibility", "visible");
            setIsAnimatingRise(false);
          }, 1400);
        } else {
          map.setPaintProperty("flood-v3-fill", "fill-opacity", currentOpacity);
        }
      }, 50);
    }, 1800);
  }, [isLoaded, isAnimatingRise]);

  const toggleLayer = (id: string) => {
    setLayers((prev) =>
      prev.map((l) => (l.id === id ? { ...l, visible: !l.visible } : l))
    );
  };

  const updateOpacity = (id: string, opacity: number) => {
    setLayers((prev) =>
      prev.map((l) => (l.id === id ? { ...l, opacity } : l))
    );
  };

  const resetView = () => {
    if (mapRef.current) {
      mapRef.current.flyTo({
        center: defaultCenter,
        zoom: defaultZoom,
        pitch: 0,
        bearing: 0,
        duration: 1200,
      });
    }
  };

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "calc(100vh - 128px)",
        backgroundColor: "var(--fog)",
        overflow: "hidden",
      }}
    >
      {/* The MapLibre Canvas Container */}
      <div
        ref={mapContainerRef}
        style={{
          width: "100%",
          height: "100%",
        }}
      />

      {/* Floating Alert for Unavailable Runs */}
      {isUnavailable && (
        <div
          className="survey-panel"
          style={{
            position: "absolute",
            top: "16px",
            left: "50%",
            transform: "translateX(-50%)",
            padding: "8px 16px",
            backgroundColor: "rgba(30, 42, 50, 0.9)",
            color: "#FFFFFF",
            borderRadius: "var(--radius-sm)",
            fontSize: "12px",
            fontFamily: "var(--font-mono)",
            zIndex: 15,
            boxShadow: "var(--shadow-panel)",
            display: "flex",
            alignItems: "center",
            gap: "8px",
          }}
        >
          <span style={{ color: "#E0A852" }}>⚠️</span>
          <span>
            Run <strong>{selectedRunId}</strong>: Candidate flood raster not generated ({manifest?.overall_status}). Viewing AOI spatial boundary.
          </span>
        </div>
      )}

      {/* Floating Left: Interactive Layer Panel & Legend */}
      <div
        className="survey-panel"
        style={{
          position: "absolute",
          top: "16px",
          left: "16px",
          width: "320px",
          maxHeight: "calc(100% - 32px)",
          overflowY: "auto",
          zIndex: 10,
        }}
      >
        <div className="survey-panel-header">
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <span
              style={{
                fontFamily: "var(--font-serif)",
                fontSize: "14px",
                fontWeight: 600,
                color: "var(--ink)",
              }}
            >
              Geospatial evidence layers
            </span>
          </div>
          <span className="survey-badge" style={{ fontSize: "10px" }}>
            5 layers
          </span>
        </div>

        <div style={{ padding: "12px 14px" }}>
          {/* Replay Sequence Button */}
          <div style={{ marginBottom: "12px" }}>
            <button
              onClick={playFloodRiseSequence}
              disabled={isAnimatingRise}
              className="btn-survey btn-survey-river"
              style={{ width: "100%", fontSize: "12px" }}
              aria-label="Replay candidate polygon visualization"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" />
                <path d="M21 3v5h-5" />
                <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" />
                <path d="M3 21v-5h5" />
              </svg>
              <span>{isAnimatingRise ? "Visualizing candidate overlay..." : "Replay candidate visualization (84 polygons)"}</span>
            </button>
            <div style={{ fontSize: "10px", color: "var(--ink-muted)", marginTop: "3px", textAlign: "center" }}>
              Visualization of static modelled candidate polygons (not a time-series progression)
            </div>
          </div>

          {/* Layer Controls List */}
          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            {layers.map((layer) => (
              <div
                key={layer.id}
                style={{
                  border: "1px solid var(--slate-subtle)",
                  borderRadius: "var(--radius-sm)",
                  padding: "8px 10px",
                  backgroundColor: layer.visible ? "var(--paper-elevated)" : "var(--fog)",
                  opacity: layer.visible ? 1 : 0.7,
                  transition: "var(--t-smooth)",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    marginBottom: "4px",
                  }}
                >
                  <label
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                      cursor: "pointer",
                      fontSize: "12px",
                      fontWeight: 500,
                      color: "var(--ink)",
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={layer.visible}
                      onChange={() => toggleLayer(layer.id)}
                      style={{ accentColor: "var(--river)", cursor: "pointer" }}
                    />
                    <span
                      style={{
                        width: "10px",
                        height: "10px",
                        borderRadius: "2px",
                        backgroundColor: layer.color,
                        display: "inline-block",
                        flexShrink: 0,
                      }}
                    />
                    <span>{layer.label}</span>
                  </label>
                </div>

                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    paddingLeft: "26px",
                    fontSize: "11px",
                    color: "var(--ink-secondary)",
                  }}
                >
                  <span style={{ fontFamily: "var(--font-mono)" }}>{layer.count}</span>
                  
                  {/* Opacity slider */}
                  <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                    <span style={{ fontSize: "10px", color: "var(--ink-muted)" }}>Opacity</span>
                    <input
                      type="range"
                      min="0.1"
                      max="1.0"
                      step="0.05"
                      value={layer.opacity}
                      disabled={!layer.visible}
                      onChange={(e) => updateOpacity(layer.id, parseFloat(e.target.value))}
                      style={{
                        width: "60px",
                        height: "4px",
                        accentColor: "var(--river)",
                        cursor: "pointer",
                      }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Panel Footer: Terminology & Validation Isolation Note */}
        <div
          style={{
            padding: "8px 14px",
            backgroundColor: "var(--paper)",
            borderTop: "1px solid var(--slate-subtle)",
            fontSize: "10px",
            color: "var(--ink-muted)",
            lineHeight: 1.4,
          }}
        >
          <div><strong>Candidate Layer:</strong> Modelled surface-water inundation from Sentinel-1 SAR &amp; Sentinel-2.</div>
          <div style={{ marginTop: "4px" }}><strong>Validation Boundary:</strong> External references (EMSR927 debris flows) are strictly isolated from analytical inputs.</div>
        </div>
      </div>

      {/* Floating Bottom: Live Instrument Readout */}
      <div
        className="survey-panel"
        style={{
          position: "absolute",
          bottom: "16px",
          right: "16px",
          padding: "6px 14px",
          display: "flex",
          alignItems: "center",
          gap: "14px",
          fontSize: "11px",
          fontFamily: "var(--font-mono)",
          color: "var(--ink-secondary)",
          zIndex: 10,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
          <span
            style={{
              width: "6px",
              height: "6px",
              borderRadius: "50%",
              backgroundColor: "var(--river)",
              animation: "pulseLive 2s infinite ease-in-out",
            }}
          />
          <span>Cursor: {coordinates.lat.toFixed(4)}°N, {coordinates.lng.toFixed(4)}°E</span>
        </div>

        <div style={{ width: "1px", height: "14px", backgroundColor: "var(--slate-light)" }} />

        <span>EPSG:4326</span>

        <div style={{ width: "1px", height: "14px", backgroundColor: "var(--slate-light)" }} />

        <button
          onClick={resetView}
          className="btn-survey"
          style={{ padding: "2px 8px", fontSize: "11px" }}
          aria-label="Reset map view to Trishuli bounds"
        >
          Reset view
        </button>
      </div>

      {/* Embedded Attribution on Map */}
      <div
        style={{
          position: "absolute",
          bottom: "4px",
          left: "140px",
          fontSize: "10px",
          color: "rgba(30, 42, 50, 0.85)",
          backgroundColor: "rgba(248, 249, 246, 0.92)",
          padding: "2px 8px",
          borderRadius: "2px",
          border: "1px solid var(--slate-subtle)",
          zIndex: 5,
        }}
      >
        Contains modified Copernicus Sentinel data (2026) · Produced using Copernicus WorldDEM-30 © DLR e.V./Airbus DS · © OpenStreetMap contributors (ODbL)
      </div>

      <style jsx>{`
        @keyframes pulseLive {
          0%, 100% {
            opacity: 1;
            transform: scale(1);
          }
          50% {
            opacity: 0.4;
            transform: scale(0.85);
          }
        }
      `}</style>
    </div>
  );
}
