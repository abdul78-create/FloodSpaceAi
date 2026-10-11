import type { Metadata } from "next";
import { Fraunces, Instrument_Sans, Noto_Sans_Devanagari } from "next/font/google";
import "./globals.css";

const fraunces = Fraunces({
  variable: "--font-fraunces",
  subsets: ["latin"],
  display: "swap",
});

const instrumentSans = Instrument_Sans({
  variable: "--font-instrument",
  subsets: ["latin"],
  display: "swap",
});

const notoSansDevanagari = Noto_Sans_Devanagari({
  variable: "--font-noto-devanagari",
  subsets: ["devanagari"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "FloodSpaceAI — Trishuli Flood Intelligence (Track B)",
  description:
    "Hydrology survey and satellite-based flood evidence system for the August 2026 Trishuli flood. " +
    "Track B: Mapping Flood Damage from Space. Multimodal AI Hackathon 2026.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${fraunces.variable} ${instrumentSans.variable} ${notoSansDevanagari.variable} h-full`}
    >
      <body className="min-h-full flex flex-col bg-topo-sheet antialiased">
        {children}
      </body>
    </html>
  );
}
