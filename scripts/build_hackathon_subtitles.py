from pathlib import Path

srt_path = Path("demo/demo_subtitles.srt")
ass_path = Path("demo/demo_subtitles.ass")

# Segments with (start_seconds, end_seconds, text)
subtitles = [
    # Part 1: Intro (0.00s - 42.15s)
    (0.0, 5.5, "Welcome to FloodSpace AI, an evidence-grounded multi-sensor flood intelligence platform."),
    (5.5, 11.2, "Developed for Track B: Mapping Flood Damage from Space at the Multimodal AI Hackathon 2026."),
    (11.2, 18.5, "In mountainous disaster zones like the Himalayas of Nepal, flash floods and glacial lake outburst floods present severe challenges."),
    (18.5, 26.0, "Torrential monsoon clouds blind optical satellites, while rugged topography causes radar shadow and delays emergency response."),
    (26.0, 34.0, "FloodSpace AI streams all-weather Sentinel-1 radar data, terrain-corrected through Copernicus WorldDEM-30,"),
    (34.0, 42.15, "evaluating spatial exposure across strictly pre-event OpenStreetMap infrastructure baselines."),

    # Part 2: Dashboard Walkthrough (42.15s - 91.40s)
    (42.15, 48.0, "Here is the FloodSpace AI operational dashboard running live at 1920x1080 resolution."),
    (48.0, 54.5, "The top navigation provides immediate situational awareness, showing the AOI bounding box, target flood date, and sensor status."),
    (54.5, 62.0, "The analytical overview highlights key empirical findings for the Trishuli Valley benchmark run:"),
    (62.0, 70.0, "1,286 candidate inundation pixels covering 35.03 hectares, 195 potentially exposed buildings,"),
    (70.0, 78.0, "115 vehicle road segments across 59.26 kilometers, 13 bridges, and 18 potentially cut-off settlements."),
    (78.0, 84.5, "Responders can seamlessly toggle layers, adjust raster opacity, and navigate interactive map overlays."),
    (84.5, 91.40, "All UI components adhere to accessibility standards with verified data bindings."),

    # Part 3: Satellite Analysis & Change Thresholding (91.40s - 153.35s)
    (91.40, 98.0, "Examining the satellite processing pipeline, FloodSpace AI performs dual-polarization change detection using Sentinel-1 SAR."),
    (98.0, 105.5, "By comparing post-event acquisitions against pre-event baselines, backscatter drops exceeding -1.5 dB in both VV and VH are flagged."),
    (105.5, 112.5, "Copernicus WorldDEM-30 slope constraints eliminate mountain shadow false positives on steep terrain."),
    (112.5, 120.0, "Using the split comparison slider, analysts can directly contrast pre-event optical baselines against radar inundation footprints."),
    (120.0, 128.5, "Furthermore, our live run on the Narayani Basin demonstrates zero synthetic hallucination:"),
    (128.5, 136.0, "Persistent water bodies without backscatter change correctly yield zero flood pixels, ensuring verifiable intelligence."),
    (136.0, 144.5, "Crucially, candidate flood polygons represent modeled surface water pooling, distinct from confirmed structural damage."),
    (144.5, 153.35, "This strict scientific distinction prevents misleading emergency relief deployments."),

    # Part 4: Infrastructure Exposure & Topological Connectivity (153.35s - 214.07s)
    (153.35, 160.0, "Moving to infrastructure impact, FloodSpace AI overlays candidate inundation onto OpenStreetMap footprints frozen prior to the event."),
    (160.0, 167.0, "The pipeline identifies 195 potentially affected buildings, 59.26 kilometers of road segments, and 13 bridges."),
    (167.0, 175.5, "Beyond 2D overlays, our topological Dijkstra graph model routes between 589 settlements and municipal emergency hubs."),
    (175.5, 183.0, "Inundation severs 3,748 road edges, fragmenting the network from 181 pre-event connected components into 252 isolated clusters."),
    (183.0, 191.0, "18 upstream settlements, including Betrawati, Devighat, and Simle, lose all primary vehicular highway connectivity."),
    (191.0, 199.5, "The system explicitly reminds responders that modeled road loss indicates vehicular cutoff,"),
    (199.5, 206.5, "while foot trails, suspension footbridges, and aerial evacuation routes may remain operable."),
    (206.5, 214.07, "Emergency teams can prioritize targeted reconnaissance for these isolated population pockets."),

    # Part 5: Evidence-Grounded AI Reporting & Copilot (214.07s - 254.14s)
    (214.07, 220.5, "The Situation Copilot provides zero-hallucination operational briefs with full English and Nepali bilingual parity."),
    (220.5, 227.5, "Every numerical metric is cryptographically tied to verified GroundedClaim records in the pipeline manifest."),
    (227.5, 235.5, "When confronted with adversarial prompts asking for casualty estimates or monetary damage, strict guardrails refuse to speculate."),
    (235.5, 243.5, "The copilot explains that satellite radar observes physical surface backscatter rather than casualties or economic valuation."),
    (243.5, 254.14, "Rather than claiming an unverified neural segmentation model, FloodSpace AI relies on deterministic, physics-grounded thresholding."),

    # Part 6: Architecture, Validation & Conclusion (254.14s - 298.89s)
    (254.14, 261.5, "For independent scientific validation, Copernicus Emergency Management Service activation EMSR927 serves as an isolated benchmark."),
    (261.5, 269.0, "FloodSpace AI achieved 10.93 hectares of coincident overlap, capturing 45.2% of our candidate footprint within the activation zone."),
    (269.0, 276.5, "EMSR927 was strictly isolated and never used for parameter tuning, confirming genuine generalization."),
    (276.5, 284.0, "Built with a containerized Docker architecture, 56 passing automated tests, and strict attribution compliance,"),
    (284.0, 291.5, "Contains modified Copernicus Sentinel data 2026, Copernicus WorldDEM-30, and OpenStreetMap contributors."),
    (291.5, 298.89, "FloodSpace AI delivers actionable, truthful disaster intelligence from space. Thank you for evaluating FloodSpace AI.")
]

def format_timestamp_srt(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    if millis >= 1000:
        secs += 1
        millis = 0
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def format_timestamp_ass(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int(round((seconds - int(seconds)) * 100))
    if centis >= 100:
        secs += 1
        centis = 0
    return f"{hours:01d}:{minutes:02d}:{secs:02d}.{centis:02d}"

# Generate SRT
srt_lines = []
for idx, (start, end, text) in enumerate(subtitles, 1):
    srt_lines.append(f"{idx}")
    srt_lines.append(f"{format_timestamp_srt(start)} --> {format_timestamp_srt(end)}")
    srt_lines.append(text)
    srt_lines.append("")

srt_path.write_text("\n".join(srt_lines), encoding="utf-8")
print(f"Generated SRT subtitles at {srt_path} ({len(subtitles)} entries)")

# Generate ASS
ass_header = """[Script Info]
Title: FloodSpaceAI Hackathon Demo Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,36,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,2.5,1.5,2,40,40,45,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

ass_events = []
for start, end, text in subtitles:
    start_s = format_timestamp_ass(start)
    end_s = format_timestamp_ass(end)
    ass_events.append(f"Dialogue: 0,{start_s},{end_s},Default,,0,0,0,,{text}")

ass_path.write_text(ass_header + "\n".join(ass_events), encoding="utf-8")
print(f"Generated ASS subtitles at {ass_path} ({len(subtitles)} entries)")
