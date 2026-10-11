// ============================================================
// StudyHeader — event / metadata banner below the main header
// ============================================================

import { EVIDENCE } from "@/lib/evidence";

interface StudyHeaderProps {
  className?: string;
}

const META_ITEMS = [
  { label: "Case Study", value: EVIDENCE.caseStudy.event },
  { label: "Study Area", value: EVIDENCE.caseStudy.area },
  { label: "OSM Snapshot", value: EVIDENCE.caseStudy.osmSnapshot },
  {
    label: "Sentinel-1 Pre",
    value: EVIDENCE.caseStudy.sentinel1Pre,
    mono: true,
  },
  {
    label: "Sentinel-1 Post",
    value: EVIDENCE.caseStudy.sentinel1Post,
    mono: true,
  },
  {
    label: "Orbit",
    value: EVIDENCE.caseStudy.sentinel1Orbit,
    mono: true,
  },
  {
    label: "Optical",
    value: EVIDENCE.caseStudy.sentinel2Note,
  },
] as const;

export default function StudyHeader({ className = "" }: StudyHeaderProps) {
  return (
    <div
      className={className}
      style={{
        background: "var(--surface-2)",
        borderBottom: "1px solid var(--border-subtle)",
        padding: "8px 20px",
        display: "flex",
        alignItems: "center",
        gap: "0",
        flexWrap: "wrap",
        flexShrink: 0,
        overflowX: "auto",
      }}
    >
      {META_ITEMS.map((item, i) => (
        <div
          key={item.label}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "0",
            flexShrink: 0,
          }}
        >
          <div
            style={{
              padding: "3px 12px",
              display: "flex",
              flexDirection: "column",
              gap: "1px",
            }}
          >
            <span
              style={{
                fontSize: "9px",
                fontFamily: "var(--font-mono)",
                color: "var(--text-muted)",
                textTransform: "uppercase",
                letterSpacing: "0.06em",
                lineHeight: 1,
              }}
            >
              {item.label}
            </span>
            <span
              style={{
                fontSize: "11px",
                fontFamily: "mono" in item && item.mono ? "var(--font-mono)" : "var(--font-sans)",
                color: "var(--text-secondary)",
                lineHeight: 1.3,
                whiteSpace: "nowrap",
              }}
            >
              {item.value}
            </span>
          </div>

          {i < META_ITEMS.length - 1 && (
            <div
              style={{
                width: "1px",
                height: "28px",
                background: "var(--border-subtle)",
                flexShrink: 0,
              }}
            />
          )}
        </div>
      ))}
    </div>
  );
}
