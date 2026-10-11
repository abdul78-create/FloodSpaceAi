// ============================================================
// Header — top navigation bar
// ============================================================

interface HeaderProps {
  className?: string;
}

export default function Header({ className = "" }: HeaderProps) {
  return (
    <header
      className={className}
      style={{
        background: "var(--surface-1)",
        borderBottom: "1px solid var(--border-subtle)",
        padding: "0 20px",
        height: "48px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        flexShrink: 0,
        gap: "16px",
      }}
    >
      {/* Left — branding */}
      <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
        {/* Logo mark */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "10px",
          }}
        >
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            aria-hidden="true"
          >
            {/* Satellite dish icon */}
            <circle
              cx="12"
              cy="12"
              r="10"
              stroke="var(--accent-primary)"
              strokeWidth="1"
              opacity="0.25"
            />
            <circle
              cx="12"
              cy="12"
              r="6"
              stroke="var(--accent-primary)"
              strokeWidth="1"
              opacity="0.5"
            />
            <circle cx="12" cy="12" r="2" fill="var(--accent-primary)" />
            <line
              x1="12"
              y1="2"
              x2="12"
              y2="4"
              stroke="var(--accent-primary)"
              strokeWidth="1.5"
              strokeLinecap="round"
            />
            <line
              x1="12"
              y1="20"
              x2="12"
              y2="22"
              stroke="var(--accent-primary)"
              strokeWidth="1.5"
              strokeLinecap="round"
            />
            <line
              x1="2"
              y1="12"
              x2="4"
              y2="12"
              stroke="var(--accent-primary)"
              strokeWidth="1.5"
              strokeLinecap="round"
            />
            <line
              x1="20"
              y1="12"
              x2="22"
              y2="12"
              stroke="var(--accent-primary)"
              strokeWidth="1.5"
              strokeLinecap="round"
            />
          </svg>

          <span
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "14px",
              fontWeight: 700,
              color: "var(--text-primary)",
              letterSpacing: "0.04em",
            }}
          >
            FloodSpaceAI
          </span>
        </div>

        {/* Separator */}
        <div
          style={{
            width: "1px",
            height: "20px",
            background: "var(--border-default)",
          }}
        />

        {/* Track indicator */}
        <span
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "10px",
            color: "var(--accent-primary)",
            letterSpacing: "0.06em",
            textTransform: "uppercase",
          }}
        >
          Track B — Mapping Flood Damage from Space
        </span>
      </div>

      {/* Right — status indicators */}
      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        {/* Modelled badge */}
        <span className="badge-modelled">
          <span
            style={{
              width: "5px",
              height: "5px",
              borderRadius: "50%",
              background: "var(--status-warning)",
            }}
          />
          Modelled Output
        </span>

        {/* Hackathon tag */}
        <span
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "10px",
            color: "var(--text-muted)",
            letterSpacing: "0.04em",
          }}
        >
          Multimodal AI Hackathon 2026
        </span>
      </div>
    </header>
  );
}
