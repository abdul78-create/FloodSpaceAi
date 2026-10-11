"use client";

import React from "react";

export default function AmbientContours() {
  return (
    <div
      aria-hidden="true"
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        pointerEvents: "none",
        zIndex: 0,
        overflow: "hidden",
        opacity: 0.35,
      }}
    >
      <svg
        width="100%"
        height="100%"
        style={{
          width: "140%",
          height: "140%",
          animation: "driftContours 80s linear infinite alternate",
        }}
        viewBox="0 0 1000 1000"
        preserveAspectRatio="none"
      >
        <path
          d="M 0,200 Q 250,150 500,220 T 1000,180"
          fill="none"
          stroke="#8A979E"
          strokeWidth="0.7"
          strokeDasharray="4 3"
        />
        <path
          d="M 0,340 Q 300,290 600,360 T 1000,310"
          fill="none"
          stroke="#8A979E"
          strokeWidth="0.75"
        />
        <path
          d="M 0,480 Q 200,430 450,500 T 1000,460"
          fill="none"
          stroke="#8A979E"
          strokeWidth="0.8"
          strokeDasharray="8 4"
        />
        <path
          d="M 0,620 Q 350,560 700,650 T 1000,600"
          fill="none"
          stroke="#8A979E"
          strokeWidth="0.75"
        />
        <path
          d="M 0,780 Q 250,720 550,810 T 1000,750"
          fill="none"
          stroke="#8A979E"
          strokeWidth="0.7"
        />
      </svg>
      <style jsx>{`
        @keyframes driftContours {
          0% {
            transform: translate3d(-3%, -2%, 0);
          }
          100% {
            transform: translate3d(2%, 3%, 0);
          }
        }
        @media (prefers-reduced-motion: reduce) {
          svg {
            animation: none !important;
          }
        }
      `}</style>
    </div>
  );
}
