import subprocess
from pathlib import Path

ffmpeg = r"C:\Users\Abdul\Downloads\ffmpeg-9.0.1-full_build\ffmpeg-9.0.1-full_build\bin\ffmpeg.exe"
art_dir = Path(r"C:\Users\Abdul\.gemini\antigravity-ide\brain\da2f9ed0-30c2-487d-8ae4-25e83a31223f")
out_dir = Path("demo/keyframes")
out_dir.mkdir(parents=True, exist_ok=True)

files = [
    "final_live_demo_check_1791563316659.webp",
    "floodspaceai_demo_walkthrough_1791562105714.webp",
    "qc_comprehensive_test_1791482759538.webp"
]

for f in files:
    stem = Path(f).stem
    p = art_dir / f
    cmd = [
        ffmpeg, "-y",
        "-i", str(p),
        "-vf", "fps=0.2", # 1 frame every 5 seconds
        "-q:v", "3",
        str(out_dir / f"{stem}_%03d.jpg")
    ]
    subprocess.run(cmd, capture_output=True)

print("Keyframes extracted to demo/keyframes")
