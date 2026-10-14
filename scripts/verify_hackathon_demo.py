import subprocess
import json
from pathlib import Path

ffprobe = r"C:\Users\Abdul\Downloads\ffmpeg-9.0.1-full_build\ffmpeg-9.0.1-full_build\bin\ffprobe.exe"
ffmpeg = r"C:\Users\Abdul\Downloads\ffmpeg-9.0.1-full_build\ffmpeg-9.0.1-full_build\bin\ffmpeg.exe"
mp4_path = Path("demo/floodspaceai_hackathon_demo.mp4")

cmd = [ffprobe, "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", str(mp4_path)]
data = json.loads(subprocess.check_output(cmd, text=True))
fmt = data["format"]
streams = data["streams"]

v_stream = next((s for s in streams if s["codec_type"] == "video"), None)
a_stream = next((s for s in streams if s["codec_type"] == "audio"), None)
s_stream = next((s for s in streams if s["codec_type"] == "subtitle"), None)

duration_sec = float(fmt["duration"])
size_bytes = int(fmt["size"])
size_mb = size_bytes / 1024 / 1024

print("=== HACKATHON DEMO MP4 VALIDATION ===")
print(f"File Path:       {mp4_path.resolve()}")
print(f"File Size:       {size_bytes:,} bytes ({size_mb:.2f} MB)")
print(f"Duration:        {duration_sec:.2f} seconds ({duration_sec/60:.2f} minutes / {int(duration_sec//60)}m {int(duration_sec%60)}s)")

assert size_bytes > 0, "Error: file size is 0"
assert duration_sec >= 180.0, f"Error: duration {duration_sec}s < 180s hard requirement"
assert duration_sec <= 600.0, f"Error: duration {duration_sec}s > 600s hard requirement"

if v_stream:
    print(f"Video Stream:    {v_stream['codec_name']} ({v_stream.get('profile', 'N/A')}), {v_stream['width']}x{v_stream['height']} @ {v_stream['r_frame_rate']} fps, pix_fmt={v_stream.get('pix_fmt', 'N/A')}")
if a_stream:
    bitrate = int(a_stream.get('bit_rate', 0)) / 1000 if 'bit_rate' in a_stream else 0
    print(f"Audio Stream:    {a_stream['codec_name']}, {a_stream.get('sample_rate', 'N/A')} Hz, {a_stream.get('channels', '1')} ch @ {bitrate:.1f} kbps")
if s_stream:
    print(f"Subtitle Stream: {s_stream['codec_name']}, language={s_stream.get('tags', {}).get('language', 'eng')}")

print("\n=== EXTRACTING TEST FRAMES (BEGINNING, MIDDLE, END) ===")
test_frames_dir = Path("demo/test_frames")
test_frames_dir.mkdir(parents=True, exist_ok=True)

test_timestamps = [
    ("frame_start.jpg", 15.0),
    ("frame_dashboard.jpg", 70.0),
    ("frame_satellite.jpg", 130.0),
    ("frame_infrastructure.jpg", 185.0),
    ("frame_copilot.jpg", 235.0),
    ("frame_conclusion.jpg", 285.0),
]

for name, ts in test_timestamps:
    frame_path = test_frames_dir / name
    cmd_f = [
        ffmpeg, "-y",
        "-ss", str(ts),
        "-i", str(mp4_path),
        "-frames:v", "1",
        "-q:v", "2",
        str(frame_path)
    ]
    subprocess.run(cmd_f, check=True, capture_output=True)
    print(f"  Captured {name} at {ts}s: {frame_path.stat().st_size:,} bytes")

print("\n[ALL VALIDATION CHECKS PASSED SUCCESSFULLY]")
