import subprocess
import json
from pathlib import Path

ffmpeg = r"C:\Users\Abdul\Downloads\ffmpeg-9.0.1-full_build\ffmpeg-9.0.1-full_build\bin\ffmpeg.exe"
ffprobe = r"C:\Users\Abdul\Downloads\ffmpeg-9.0.1-full_build\ffmpeg-9.0.1-full_build\bin\ffprobe.exe"
art_dir = Path(r"C:\Users\Abdul\.gemini\antigravity-ide\brain\da2f9ed0-30c2-487d-8ae4-25e83a31223f")
temp_dir = Path("demo/temp_segments")
temp_dir.mkdir(parents=True, exist_ok=True)

# 1. Source files
src_narayani = art_dir / "final_live_demo_check_1791563316659.webp"
src_qc = art_dir / "qc_comprehensive_test_1791482759538.webp"
src_walkthrough = art_dir / "floodspaceai_demo_walkthrough_1791562105714.webp"

# Define the 5 segments
# (name, src_file, ss, t_dur, audio_file)
segments = [
    ("seg1_narayani.mp4", src_narayani, 0.0, 36.0, "demo/audio/part1_intro.wav"),
    ("seg2_hydrology.mp4", src_qc, 12.0, 38.0, "demo/audio/part2_hydrology.wav"),
    ("seg3_assets.mp4", src_qc, 55.0, 35.0, "demo/audio/part3_assets.wav"),
    ("seg4_copilot.mp4", src_walkthrough, 55.0, 33.0, "demo/audio/part4_copilot.wav"),
    ("seg5a_emsr.mp4", src_walkthrough, 75.0, 15.0, None),
    ("seg5b_prov.mp4", src_qc, 90.0, 23.0, None),
]

for name, src, ss, dur, _ in segments:
    out_path = temp_dir / name
    cmd = [
        ffmpeg, "-y",
        "-ss", str(ss),
        "-i", str(src),
        "-t", str(dur),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-r", "10",
        str(out_path)
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"Rendered {name} (duration: {dur}s)")

print("All visual segments rendered.")
