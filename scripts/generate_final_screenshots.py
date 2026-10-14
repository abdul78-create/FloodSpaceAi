import subprocess
import sys
from pathlib import Path
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

ffmpeg = r"C:\Users\Abdul\Downloads\ffmpeg-9.0.1-full_build\ffmpeg-9.0.1-full_build\bin\ffmpeg.exe"
raw_video = Path("demo/build_hackathon/master_raw_video.mp4")
out_dir = Path("demo/final screenshots")
out_dir.mkdir(parents=True, exist_ok=True)

# 3:2 target dimensions
TARGET_W = 1800
TARGET_H = 1200
BG_COLOR = (11, 26, 36) # Dark slate dashboard background

def fit_to_3x2_image(src_path: Path, dest_path: Path):
    """Formats an existing image to exact 1800x1200 (3:2) ratio without distortion."""
    im = Image.open(src_path).convert("RGB")
    w, h = im.size
    target_ratio = TARGET_W / TARGET_H # 1.5
    current_ratio = w / h

    if abs(current_ratio - target_ratio) < 0.01:
        resized = im.resize((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)
    elif current_ratio > target_ratio:
        # Wider than 3:2 (e.g. 16:9). Scale to width, and pad top/bottom with dashboard theme
        scale = TARGET_W / w
        new_w = TARGET_W
        new_h = int(h * scale)
        scaled = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
        resized = Image.new("RGB", (TARGET_W, TARGET_H), BG_COLOR)
        top_offset = (TARGET_H - new_h) // 2
        resized.paste(scaled, (0, top_offset))
    else:
        # Taller than 3:2
        scale = TARGET_H / h
        new_h = TARGET_H
        new_w = int(w * scale)
        scaled = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
        resized = Image.new("RGB", (TARGET_W, TARGET_H), BG_COLOR)
        left_offset = (TARGET_W - new_w) // 2
        resized.paste(scaled, (left_offset, 0))

    resized.save(dest_path, "PNG", optimize=True)

def extract_from_video(ts_sec: float, dest_path: Path):
    """Extracts a frame from the clean 1080p raw video and formats to 1800x1200 3:2."""
    cmd = [
        ffmpeg, "-y",
        "-ss", str(ts_sec),
        "-i", str(raw_video),
        "-frames:v", "1",
        "-vf", f"scale={TARGET_W}:{TARGET_H}:force_original_aspect_ratio=increase,crop={TARGET_W}:{TARGET_H}",
        "-update", "1",
        str(dest_path)
    ]
    subprocess.run(cmd, check=True, capture_output=True)

# Define the 15 gallery screenshots
screenshots_config = [
    {
        "filename": "01_floodspaceai_overview_hero.png",
        "title": "FloodSpaceAI Operational Hero & Interactive Map",
        "desc": "System banner, operational SAR status, AOI coordinates [84.90E, 27.75N to 85.25E, 28.05N], and Trishuli river corridor overview.",
        "type": "asset",
        "src": Path("docs/assets/hero_interactive_map.png")
    },
    {
        "filename": "02_operational_kpi_dashboard.png",
        "title": "Trishuli Valley Benchmark Analytical Metric Cards",
        "desc": "Verified baseline: 1,286 candidate pixels (35.03 ha), 195 buildings, 115 roads (59.26 km), 13 bridges, 3,748 disrupted edges, 18 cut-offs.",
        "type": "asset",
        "src": Path("docs/assets/affected_assets_breakdown.png")
    },
    {
        "filename": "03_sentinel1_radar_change_analysis.png",
        "title": "Sentinel-1 Dual-Polarization SAR Change Detection",
        "desc": "Dual-polarization (VV + VH) radar backscatter change map over the river corridor.",
        "type": "video",
        "ts": 76.0
    },
    {
        "filename": "04_worlddem30_terrain_slope_filtering.png",
        "title": "Copernicus WorldDEM-30 Terrain Slope Filtering",
        "desc": "Elevation-constrained flood progression eliminating mountain shadows and steep slope false positives.",
        "type": "asset",
        "src": Path("docs/assets/flood_rise_simulation.png")
    },
    {
        "filename": "05_candidate_flood_inundation_polygons.png",
        "title": "Candidate Flood Inundation Polygons (84 Clusters)",
        "desc": "Discrete standing water bodies (>=2 connected pixels) mapped along the valley floor.",
        "type": "video",
        "ts": 90.0
    },
    {
        "filename": "06_optical_radar_split_comparison_slider.png",
        "title": "Interactive Optical vs. Radar Split Comparison Slider",
        "desc": "Direct contrast of Sentinel-2 pre-event optical imagery against candidate radar flood footprint.",
        "type": "asset",
        "src": Path("docs/assets/satellite_comparison_slider.png")
    },
    {
        "filename": "07_infrastructure_building_exposure.png",
        "title": "OpenStreetMap Building Exposure Footprints (195 Structures)",
        "desc": "Overlay of historical building footprints with conservative modeled potential exposure terminology.",
        "type": "video",
        "ts": 140.0
    },
    {
        "filename": "08_road_network_severance_highways.png",
        "title": "Highway & Vehicle Road Network Severance (59.26 km)",
        "desc": "115 vehicle road segments intersecting candidate standing water extents.",
        "type": "video",
        "ts": 158.0
    },
    {
        "filename": "09_critical_bridge_exposure_clearance.png",
        "title": "Critical Bridge Exposure Analysis (13 Bridges)",
        "desc": "2D flood intersection analysis with vertical bridge deck clearance disclaimers.",
        "type": "video",
        "ts": 178.0
    },
    {
        "filename": "10_topological_dijkstra_connectivity.png",
        "title": "Topological Dijkstra Network Fragmentation (181 -> 252 Components)",
        "desc": "Graph partition analysis showing +71 isolated clusters severed by 3,748 disrupted edges.",
        "type": "asset",
        "src": Path("docs/assets/road_connectivity_analysis.png")
    },
    {
        "filename": "11_cutoff_settlements_and_emergency_routing.png",
        "title": "Potentially Cut-Off Settlements & Emergency Hub Access",
        "desc": "18 settlements (Betrawati, Devighat, Simle) with modeled loss of vehicular highway connectivity.",
        "type": "video",
        "ts": 208.0
    },
    {
        "filename": "12_narayani_basin_live_zero_hallucination.png",
        "title": "Multi-Area Generalization: Narayani Basin Live Run",
        "desc": "Live AWS STAC Sentinel stream yielding 0 candidate pixels on persistent water, proving zero hallucination.",
        "type": "video",
        "ts": 116.0
    },
    {
        "filename": "13_bilingual_situation_copilot_nepali.png",
        "title": "Evidence-Grounded Situation Copilot in Nepali (नेपाली)",
        "desc": "Cryptographically tied GroundedClaim responses with full English/Nepali bilingual parity.",
        "type": "asset",
        "src": Path("docs/assets/situation_copilot_nepali.png")
    },
    {
        "filename": "14_adversarial_safety_guardrails.png",
        "title": "Adversarial Query Safety & Casualty Refusal Guardrails",
        "desc": "Explicit refusal to hallucinate unobserved human casualties or economic damages under adversarial prompts.",
        "type": "asset",
        "src": Path("docs/assets/grounded_copilot_refusal.png")
    },
    {
        "filename": "15_verbatim_attributions_and_licensing.png",
        "title": "Standardized Verbatim Attributions & Licensing",
        "desc": "Attribution footer: Copernicus Sentinel, Copernicus WorldDEM-30, OpenStreetMap, and Vertex AI enterprise terms.",
        "type": "video",
        "ts": 282.0
    }
]

print("=== GENERATING 15 DEVPOST GALLERY SCREENSHOTS (1800x1200, 3:2 RATIO) ===")
gallery_log = []

for idx, item in enumerate(screenshots_config, 1):
    dest = out_dir / item["filename"]
    if item["type"] == "asset":
        fit_to_3x2_image(item["src"], dest)
    else:
        extract_from_video(item["ts"], dest)

    # Verify output
    im = Image.open(dest)
    w, h = im.size
    ratio = w / h
    size_bytes = dest.stat().st_size
    size_mb = size_bytes / 1024 / 1024

    assert w == TARGET_W and h == TARGET_H, f"Error: expected {TARGET_W}x{TARGET_H}, got {w}x{h}"
    assert size_mb < 5.0, f"Error: file size {size_mb:.2f} MB exceeds 5.0 MB Devpost limit"

    status = f"[{idx:02d}/15] {item['filename']} | {w}x{h} (3:2) | {size_mb:.2f} MB | {item['title']}"
    print(status)
    gallery_log.append({
        "number": idx,
        "filename": item["filename"],
        "title": item["title"],
        "desc": item["desc"],
        "dimensions": f"{w}x{h}",
        "aspect_ratio": "3:2",
        "size_mb": f"{size_mb:.2f} MB"
    })

# Write index readme in demo/final screenshots
readme_path = out_dir / "README.md"
readme_lines = [
    "# FloodSpaceAI — Devpost Project Media Gallery (15 Screenshots)",
    "",
    "**Image Specification:** PNG format, exact **3:2 aspect ratio (1800 x 1200 px)**, strictly under the 5 MB Devpost upload limit.",
    "",
    "| # | Filename | Aspect Ratio | Dimensions | File Size | Description / Caption |",
    "| :-: | :--- | :-: | :-: | :-: | :--- |"
]

for g in gallery_log:
    readme_lines.append(f"| {g['number']:02d} | `{g['filename']}` | {g['aspect_ratio']} | {g['dimensions']} | {g['size_mb']} | **{g['title']}** — {g['desc']} |")

readme_lines.append("")
readme_lines.append("### Devpost Upload Instructions:")
readme_lines.append("1. Open your project on Devpost -> **Project Media** -> **Image gallery**.")
readme_lines.append("2. Drag and drop all 15 PNG images from this folder (`demo/final screenshots/`).")
readme_lines.append("3. All images are pre-formatted to the recommended 3:2 ratio for crisp, edge-to-edge rendering without black bars.")
readme_lines.append("")

readme_path.write_text("\n".join(readme_lines), encoding="utf-8")
print(f"\nSuccessfully generated all 15 gallery screenshots and index at {readme_path}")
