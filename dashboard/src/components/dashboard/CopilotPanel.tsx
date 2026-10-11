// ============================================================
// CopilotPanel — AI Situation Copilot right sidebar (placeholder)
// ============================================================

export default function CopilotPanel() {
  return (
    <aside
      style={{
        width: "300px",
        flexShrink: 0,
        display: "flex",
        flexDirection: "column",
        background: "var(--surface-1)",
        borderLeft: "1px solid var(--border-subtle)",
        overflow: "hidden",
      }}
    >
      {/* ── Panel header ── */}
      <div
        style={{
          background: "var(--surface-2)",
          borderBottom: "1px solid var(--border-subtle)",
          padding: "10px 14px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexShrink: 0,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <svg
            width="14"
            height="14"
            viewBox="0 0 14 14"
            fill="none"
            aria-hidden="true"
          >
            <circle
              cx="7"
              cy="7"
              r="6"
              stroke="var(--accent-primary)"
              strokeWidth="1"
              opacity="0.5"
            />
            <circle cx="7" cy="7" r="2.5" fill="var(--accent-primary)" />
          </svg>
          <span className="panel-title">AI Situation Copilot</span>
        </div>
        <span
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "9px",
            color: "var(--text-muted)",
            letterSpacing: "0.04em",
            padding: "1px 6px",
            border: "1px solid var(--border-subtle)",
            borderRadius: "4px",
          }}
        >
          Phase 5
        </span>
      </div>

      {/* ── Gemini model info ── */}
      <div
        style={{
          background: "var(--surface-1)",
          borderBottom: "1px solid var(--border-subtle)",
          padding: "8px 14px",
          display: "flex",
          alignItems: "center",
          gap: "8px",
          flexShrink: 0,
        }}
      >
        <div
          style={{
            width: "6px",
            height: "6px",
            borderRadius: "50%",
            background: "var(--status-warning)",
            flexShrink: 0,
          }}
        />
        <span
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "10px",
            color: "var(--text-muted)",
          }}
        >
          gemini-situation-copilot.py
        </span>
      </div>

      {/* ── Report section placeholder ── */}
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "14px",
          display: "flex",
          flexDirection: "column",
          gap: "12px",
        }}
      >
        {/* Grounded report placeholder */}
        <div className="panel">
          <div className="panel-header">
            <span className="panel-title">Situation Report</span>
            <span
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "9px",
                color: "var(--text-muted)",
              }}
            >
              LLM grounded
            </span>
          </div>
          <div
            className="panel-body"
            style={{ display: "flex", flexDirection: "column", gap: "10px" }}
          >
            {["Executive Summary", "Flood Extent", "Affected Assets", "Road Connectivity", "Methodology"].map(
              (section) => (
                <div key={section}>
                  <div
                    style={{
                      fontSize: "10px",
                      fontWeight: 600,
                      color: "var(--text-muted)",
                      textTransform: "uppercase",
                      letterSpacing: "0.06em",
                      marginBottom: "4px",
                      fontFamily: "var(--font-mono)",
                    }}
                  >
                    {section}
                  </div>
                  <div
                    style={{
                      height: "8px",
                      background: "var(--surface-3)",
                      borderRadius: "3px",
                      marginBottom: "3px",
                    }}
                  />
                  <div
                    style={{
                      height: "8px",
                      background: "var(--surface-3)",
                      borderRadius: "3px",
                      width: "80%",
                    }}
                  />
                </div>
              )
            )}

            <p
              style={{
                fontSize: "10px",
                color: "var(--text-muted)",
                lineHeight: 1.5,
                marginTop: "4px",
                fontStyle: "italic",
              }}
            >
              The Gemini-powered situation report with numerical grounding will
              appear here in Phase 5. All values will be validated against
              situation_report_evidence.json.
            </p>
          </div>
        </div>

        {/* Provenance / grounding status placeholder */}
        <div className="panel">
          <div className="panel-header">
            <span className="panel-title">Numerical Grounding</span>
            <span
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "9px",
                color: "var(--text-muted)",
              }}
            >
              validation
            </span>
          </div>
          <div className="panel-body">
            <p
              style={{
                fontSize: "11px",
                color: "var(--text-muted)",
                lineHeight: 1.5,
                margin: 0,
              }}
            >
              Every number in the AI report is validated against the evidence
              JSON. Hallucinated values are flagged and replaced with
              deterministic fallback.
            </p>

            {/* Grounding indicator rows */}
            <div style={{ marginTop: "10px", display: "flex", flexDirection: "column", gap: "5px" }}>
              {[
                { key: "Flood pixels", value: "1,286", ok: true },
                { key: "Flood polygons", value: "84", ok: true },
                { key: "Buildings", value: "195", ok: true },
                { key: "Roads", value: "115", ok: true },
                { key: "Bridges", value: "13", ok: true },
                { key: "Cut-off settlements", value: "18", ok: true },
              ].map((row) => (
                <div
                  key={row.key}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "3px 0",
                    borderBottom: "1px solid var(--border-subtle)",
                  }}
                >
                  <span
                    style={{
                      fontSize: "10px",
                      color: "var(--text-muted)",
                      fontFamily: "var(--font-mono)",
                    }}
                  >
                    {row.key}
                  </span>
                  <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                    <span
                      style={{
                        fontSize: "10px",
                        fontFamily: "var(--font-mono)",
                        color: "var(--text-secondary)",
                      }}
                    >
                      {row.value}
                    </span>
                    <span
                      style={{
                        fontSize: "9px",
                        color: row.ok ? "var(--status-success)" : "var(--status-danger)",
                        fontFamily: "var(--font-mono)",
                      }}
                    >
                      {row.ok ? "✓" : "✗"}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* ── Query input placeholder ── */}
      <div
        style={{
          background: "var(--surface-2)",
          borderTop: "1px solid var(--border-subtle)",
          padding: "10px 14px",
          flexShrink: 0,
        }}
      >
        <div
          style={{
            background: "var(--surface-1)",
            border: "1px solid var(--border-default)",
            borderRadius: "6px",
            padding: "8px 12px",
            display: "flex",
            alignItems: "center",
            gap: "8px",
            cursor: "not-allowed",
            opacity: 0.5,
          }}
          title="Copilot query input — available in Phase 5"
          role="textbox"
          aria-label="AI Copilot query input (not yet available)"
          aria-disabled="true"
        >
          <span
            style={{
              flex: 1,
              fontSize: "12px",
              color: "var(--text-muted)",
              fontStyle: "italic",
            }}
          >
            Ask the Copilot about flood impacts…
          </span>
          <svg
            width="14"
            height="14"
            viewBox="0 0 14 14"
            fill="none"
            aria-hidden="true"
          >
            <path
              d="M1 7L6 2L11 7"
              stroke="var(--text-muted)"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>
        <p
          style={{
            fontSize: "9px",
            color: "var(--text-muted)",
            margin: "5px 0 0",
            textAlign: "center",
            fontFamily: "var(--font-mono)",
          }}
        >
          Gemini integration · Phase 5
        </p>
      </div>
    </aside>
  );
}
