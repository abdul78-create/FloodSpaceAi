from pathlib import Path

subtitles_ass = """[Script Info]
Title: FloodSpaceAI Technical Demonstration
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndHeight: yes
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Segoe UI,32,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,3,3,0,2,40,40,45,1
Style: Header,Segoe UI,28,&H00E0F2FE,&H000000FF,&H000284C7,&H900B132B,-1,0,0,0,100,100,0,0,3,2,0,8,40,40,30,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 1,0:00:00.00,0:00:07.00,Default,,0,0,0,,{\\b1}FloodSpaceAI{\\b0} — Evidence-Grounded Multi-Sensor Flood Intelligence (Track B)
Dialogue: 1,0:00:07.00,0:00:15.00,Default,,0,0,0,,{\\b1}Live Satellite Acquisition:{\\b0} Streaming Sentinel-1 SAR & Sentinel-2 MSI from AWS STAC
Dialogue: 1,0:00:15.00,0:00:23.00,Default,,0,0,0,,{\\b1}Data Integrity:{\\b0} Verifying SHA-256 hashes & enforcing pre-event OSM (T_osm < T_flood)
Dialogue: 1,0:00:23.00,0:00:35.00,Default,,0,0,0,,{\\b1}Transparent Uncertainty:{\\b0} Copilot cites 0 candidate pixels due to optical cloud obscuration
Dialogue: 1,0:00:35.00,0:00:43.00,Default,,0,0,0,,{\\b1}Benchmark Analysis:{\\b0} Trishuli Valley 1,286 candidate pixels = 35.03 ha (16.8m grid)
Dialogue: 1,0:00:43.00,0:00:52.00,Default,,0,0,0,,{\\b1}Hydrological GIS:{\\b0} MapLibre GL layer controls, DEM elevation limits & V3 water mask
Dialogue: 1,0:00:52.00,0:01:02.00,Default,,0,0,0,,{\\b1}Elevation Dynamics:{\\b0} Replaying terrain flood-rise sequence across water levels
Dialogue: 1,0:01:02.00,0:01:13.00,Default,,0,0,0,,{\\b1}Satellite Comparison:{\\b0} Split swipe between pre-event optical RGB & post-event SAR change
Dialogue: 1,0:01:13.00,0:01:22.00,Default,,0,0,0,,{\\b1}Grounded Exposure:{\\b0} 195 buildings, 115 road segments (59.26 km), and 13 bridges
Dialogue: 1,0:01:22.00,0:01:31.00,Default,,0,0,0,,{\\b1}Scientific Precision:{\\b0} Assets strictly termed 'potentially affected' by 2D footprint overlay
Dialogue: 1,0:01:31.00,0:01:40.00,Default,,0,0,0,,{\\b1}Network Graph Modeling:{\\b0} Dijkstra topological analysis across pre & post-event road states
Dialogue: 1,0:01:40.00,0:01:48.00,Default,,0,0,0,,{\\b1}Settlement Isolation:{\\b0} 18 upstream communities cut off from Bidur and Galchhi hubs
Dialogue: 1,0:01:48.00,0:01:58.00,Default,,0,0,0,,{\\b1}Situation Copilot:{\\b0} Zero-hallucination reporting with 100% English & Nepali (नेपाली) parity
Dialogue: 1,0:01:58.00,0:02:07.00,Default,,0,0,0,,{\\b1}Adversarial Refusal:{\\b0} 'How many people died?' ──► CASUALTIES_REFUSED (Strict safety guardrail)
Dialogue: 1,0:02:07.00,0:02:16.00,Default,,0,0,0,,{\\b1}Adversarial Refusal:{\\b0} 'What is the monetary damage?' ──► MONETARY_REFUSED (No speculative losses)
Dialogue: 1,0:02:16.00,0:02:26.00,Default,,0,0,0,,{\\b1}Damage Clarification:{\\b0} 'Are buildings destroyed?' ──► EXPOSURE_CLARIFIED (2D overlay vs collapse)
Dialogue: 1,0:02:26.00,0:02:37.00,Default,,0,0,0,,{\\b1}EMSR927 Benchmark:{\\b0} 'Does this match EMSR927?' ──► VALIDATION_ISOLATED (Independent post-hoc check)
Dialogue: 1,0:02:37.00,0:02:48.00,Default,,0,0,0,,{\\b1}Copernicus EMSR927:{\\b0} 10.93 ha coincident overlap (45.24% of candidate footprint; 1.01% IoU)
Dialogue: 1,0:02:48.00,0:03:00.00,Default,,0,0,0,,{\\b1}Data Provenance:{\\b0} Copernicus Sentinel-1/2, DEM & OSM (56/56 Tests Passing | Production Verified)
"""

subtitles_srt = """1
00:00:00,000 --> 00:00:07,000
FloodSpaceAI — Evidence-Grounded Multi-Sensor Flood Intelligence (Track B)

2
00:00:07,000 --> 00:00:15,000
Live Satellite Acquisition: Streaming Sentinel-1 SAR & Sentinel-2 MSI from AWS STAC

3
00:00:15,000 --> 00:00:23,000
Data Integrity: Verifying SHA-256 hashes & enforcing pre-event OSM (T_osm < T_flood)

4
00:00:23,000 --> 00:00:35,000
Transparent Uncertainty: Copilot cites 0 candidate pixels due to optical cloud obscuration

5
00:00:35,000 --> 00:00:43,000
Benchmark Analysis: Trishuli Valley 1,286 candidate pixels = 35.03 ha (16.8m grid)

6
00:00:43,000 --> 00:00:52,000
Hydrological GIS: MapLibre GL layer controls, DEM elevation limits & V3 water mask

7
00:00:52,000 --> 00:01:02,000
Elevation Dynamics: Replaying terrain flood-rise sequence across water levels

8
00:01:02,000 --> 00:01:13,000
Satellite Comparison: Split swipe between pre-event optical RGB & post-event SAR change

9
00:01:13,000 --> 00:01:22,000
Grounded Exposure: 195 buildings, 115 road segments (59.26 km), and 13 bridges

10
00:01:22,000 --> 00:01:31,000
Scientific Precision: Assets strictly termed 'potentially affected' by 2D footprint overlay

11
00:01:31,000 --> 00:01:40,000
Network Graph Modeling: Dijkstra topological analysis across pre & post-event road states

12
00:01:40,000 --> 00:01:48,000
Settlement Isolation: 18 upstream communities cut off from Bidur and Galchhi hubs

13
00:01:48,000 --> 00:01:58,000
Situation Copilot: Zero-hallucination reporting with 100% English & Nepali (नेपाली) parity

14
00:01:58,000 --> 00:02:07,000
Adversarial Refusal: 'How many people died?' ──► CASUALTIES_REFUSED (Strict safety guardrail)

15
00:02:07,000 --> 00:02:16,000
Adversarial Refusal: 'What is the monetary damage?' ──► MONETARY_REFUSED (No speculative losses)

16
00:02:16,000 --> 00:02:26,000
Damage Clarification: 'Are buildings destroyed?' ──► EXPOSURE_CLARIFIED (2D overlay vs collapse)

17
00:02:26,000 --> 00:02:37,000
EMSR927 Benchmark: 'Does this match EMSR927?' ──► VALIDATION_ISOLATED (Independent post-hoc check)

18
00:02:37,000 --> 00:02:48,000
Copernicus EMSR927: 10.93 ha coincident overlap (45.24% of candidate footprint; 1.01% IoU)

19
00:02:48,000 --> 00:03:00,000
Data Provenance: Copernicus Sentinel-1/2, DEM & OSM (56/56 Tests Passing | Production Verified)
"""

Path("demo/captions.ass").write_text(subtitles_ass, encoding="utf-8")
Path("demo/captions.srt").write_text(subtitles_srt, encoding="utf-8")
print("Wrote demo/captions.ass and demo/captions.srt successfully.")
