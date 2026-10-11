import subprocess
import json
from pathlib import Path

ffprobe = r"C:\Users\Abdul\Downloads\ffmpeg-9.0.1-full_build\ffmpeg-9.0.1-full_build\bin\ffprobe.exe"
art_dir = Path(r"C:\Users\Abdul\.gemini\antigravity-ide\brain\da2f9ed0-30c2-487d-8ae4-25e83a31223f")

for p in sorted(art_dir.glob("*.webp")):
    cmd = [
        ffprobe,
        "-v", "error",
        "-count_frames",
        "-select_streams", "v:0",
        "-show_entries", "stream=nb_read_frames,r_frame_rate,width,height",
        "-of", "json",
        str(p)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
        st = d["streams"][0]
        n_frames = int(st.get("nb_read_frames", 0))
        fps_str = st.get("r_frame_rate", "10/1")
        num, den = map(int, fps_str.split("/"))
        fps = num / den
        dur = n_frames / fps if fps else 0
        print(f"{p.name:45}: {st.get('width')}x{st.get('height')} | frames: {n_frames:4d} | fps: {fps:4.1f} | dur: {dur:6.2f}s | size: {p.stat().st_size/1024/1024:.2f} MB")
    except Exception as e:
        print(p.name, e)
