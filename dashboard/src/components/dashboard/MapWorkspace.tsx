// ============================================================
// MapWorkspace — main map area (placeholder for Phase 2)
// ============================================================

export default function MapWorkspace() {
  return (
    <div
      style={{
        flex: 1,
        position: "relative",
        display: "flex",
        flexDirection: "column",
        minHeight: 0,
      }}
    >
      {/* Map toolbar */}
      <div
        style={{
          background: "var(--surface-2)",
          borderBottom: "1px solid var(--border-subtle)",
          padding: "8px 16px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: "12px",
          flexShrink: 0,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <span
            style={{
              fontSize: "11px",
              fontWeight: 600,
              color: "var(--text-secondary)",
              fontFamily: "var(--font-mono)",
              textTransform: "uppercase",
              letterSpacing: "0.06em",
            }}
          >
            Map Workspace
          </span>
          <span
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "10px",
              color: "var(--text-muted)",
            }}
          >
            Trishuli Valley AOI
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          {/* Coordinate display placeholder */}
          <span
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "10px",
              color: "var(--text-muted)",
            }}
          >
            27.9°N 85.1°E
          </span>
          <div
            style={{
              width: "1px",
              height: "14px",
              background: "var(--border-subtle)",
            }}
          />
          <span
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "10px",
              color: "var(--text-muted)",
            }}
          >
            EPSG:4326
          </span>
        </div>
      </div>

      {/* Map placeholder */}
      <div
        style={{
          flex: 1,
          position: "relative",
          background: "var(--surface-1)",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: "16px",
          minHeight: 0,
        }}
      >
        {/* Grid overlay for geospatial feel */}
        <div
          aria-hidden="true"
          style={{
            position: "absolute",
            inset: 0,
            backgroundImage:
              "linear-gradient(var(--border-subtle) 1px, transparent 1px), " +
              "linear-gradient(90deg, var(--border-subtle) 1px, transparent 1px)",
            backgroundSize: "40px 40px",
            opacity: 0.4,
          }}
        />

        {/* Corner markers */}
        {(["top-left", "top-right", "bottom-left", "bottom-right"] as const).map(
          (corner) => {
            const styles: React.CSSProperties = {
              position: "absolute",
              width: "16px",
              height: "16px",
              margin: "12px",
            };
            if (corner === "top-left") {
              styles.top = 0;
              styles.left = 0;
              styles.borderTop = "1px solid var(--border-emphasis)";
              styles.borderLeft = "1px solid var(--border-emphasis)";
            } else if (corner === "top-right") {
              styles.top = 0;
              styles.right = 0;
              styles.borderTop = "1px solid var(--border-emphasis)";
              styles.borderRight = "1px solid var(--border-emphasis)";
            } else if (corner === "bottom-left") {
              styles.bottom = 0;
              styles.left = 0;
              styles.borderBottom = "1px solid var(--border-emphasis)";
              styles.borderLeft = "1px solid var(--border-emphasis)";
            } else {
              styles.bottom = 0;
              styles.right = 0;
              styles.borderBottom = "1px solid var(--border-emphasis)";
              styles.borderRight = "1px solid var(--border-emphasis)";
            }
            return <div key={corner} aria-hidden="true" style={styles} />;
          }
        )}

        {/* Centre content */}
        <div
          style={{
            position: "relative",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: "12px",
            zIndex: 1,
          }}
        >
          {/* Icon */}
          <svg
            width="40"
            height="40"
            viewBox="0 0 40 40"
            fill="none"
            aria-hidden="true"
          >
            <rect
              x="4"
              y="4"
              width="32"
              height="32"
              rx="4"
              stroke="var(--border-emphasis)"
              strokeWidth="1"
            />
            <circle cx="20" cy="20" r="8" stroke="var(--border-emphasis)" strokeWidth="1" />
            <circle
              cx="20"
              cy="20"
              r="2"
              fill="var(--accent-primary)"
              opacity="0.5"
            />
            <line
              x1="20"
              y1="12"
              x2="20"
              y2="28"
              stroke="var(--border-emphasis)"
              strokeWidth="0.75"
            />
            <line
              x1="12"
              y1="20"
              x2="28"
              y2="20"
              stroke="var(--border-emphasis)"
              strokeWidth="0.75"
            />
          </svg>

          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: "6px",
            }}
          >
            <span
              style={{
                fontSize: "13px",
                fontWeight: 600,
                color: "var(--text-secondary)",
              }}
            >
              Map visualization will be connected in the next phase.
            </span>
            <span
              style={{
                fontSize: "11px",
                color: "var(--text-muted)",
                textAlign: "center",
                maxWidth: "360px",
                lineHeight: 1.5,
              }}
            >
              Phase 2 will render the V3 flood candidate GeoTIFF, potentially
              affected buildings, roads, bridges, and cut-off settlements as
              interactive GeoJSON layers.
            </span>
          </div>

          {/* Phase tags */}
          <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", justifyContent: "center" }}>
            {[
              "Flood Candidate V3",
              "Buildings (195)",
              "Roads (115)",
              "Bridges (13)",
              "Settlements (18)",
            ].map((tag) => (
              <span
                key={tag}
                style={{
                  padding: "3px 8px",
                  background: "var(--surface-3)",
                  border: "1px solid var(--border-subtle)",
                  borderRadius: "4px",
                  fontFamily: "var(--font-mono)",
                  fontSize: "10px",
                  color: "var(--text-muted)",
                }}
              >
                {tag}
              </span>
            ))}
          </div>
        </div>

        {/* Scale bar placeholder */}
        <div
          aria-hidden="true"
          style={{
            position: "absolute",
            bottom: "16px",
            left: "16px",
            display: "flex",
            flexDirection: "column",
            gap: "3px",
          }}
        >
          <div
            style={{
              width: "60px",
              height: "3px",
              background: "var(--border-emphasis)",
              borderRadius: "1px",
            }}
          />
          <span
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "9px",
              color: "var(--text-muted)",
            }}
          >
            ~ 5 km
          </span>
        </div>

        {/* North arrow placeholder */}
        <div
          aria-hidden="true"
          style={{
            position: "absolute",
            bottom: "16px",
            right: "16px",
            fontFamily: "var(--font-mono)",
            fontSize: "10px",
            color: "var(--text-muted)",
          }}
        >
          ↑ N
        </div>
      </div>
    </div>
  );
}
