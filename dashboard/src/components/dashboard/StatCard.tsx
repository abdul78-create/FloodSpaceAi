// ============================================================
// StatCard — single impact metric card
// ============================================================

interface StatCardProps {
  label: string;
  value: number | string;
  unit?: string;
  description?: string;
  color?: string;
  mono?: boolean;
}

export default function StatCard({
  label,
  value,
  unit,
  description,
  color = "var(--text-primary)",
  mono = false,
}: StatCardProps) {
  const formattedValue =
    typeof value === "number" ? value.toLocaleString("en-US") : value;

  return (
    <div className="stat-card" role="figure" aria-label={`${label}: ${formattedValue}`}>
      {/* Label */}
      <span
        style={{
          fontSize: "9px",
          fontFamily: "var(--font-mono)",
          color: "var(--text-muted)",
          textTransform: "uppercase",
          letterSpacing: "0.08em",
          lineHeight: 1,
        }}
      >
        {label}
      </span>

      {/* Value + unit */}
      <div style={{ display: "flex", alignItems: "baseline", gap: "4px" }}>
        <span
          style={{
            fontFamily: mono ? "var(--font-mono)" : "var(--font-sans)",
            fontSize: "22px",
            fontWeight: 700,
            color,
            lineHeight: 1.1,
            letterSpacing: mono ? "0.02em" : undefined,
          }}
        >
          {formattedValue}
        </span>
        {unit && (
          <span
            style={{
              fontSize: "11px",
              color: "var(--text-muted)",
              fontFamily: "var(--font-mono)",
            }}
          >
            {unit}
          </span>
        )}
      </div>

      {/* Description */}
      {description && (
        <span
          style={{
            fontSize: "10px",
            color: "var(--text-muted)",
            lineHeight: 1.4,
            marginTop: "2px",
          }}
        >
          {description}
        </span>
      )}
    </div>
  );
}
