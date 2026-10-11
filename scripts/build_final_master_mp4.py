import subprocess
from pathlib import Path

ffmpeg = r"C:\Users\Abdul\Downloads\ffmpeg-9.0.1-full_build\ffmpeg-9.0.1-full_build\bin\ffmpeg.exe"
ffprobe = r"C:\Users\Abdul\Downloads\ffmpeg-9.0.1-full_build\ffmpeg-9.0.1-full_build\bin\ffprobe.exe"

raw_v = Path("demo/build/master_raw_video.mp4")
raw_a = Path("demo/build/master_audio.wav")
captions = Path("demo/captions.ass")
out_mp4 = Path("demo/floodspaceai_demo_walkthrough.mp4")

# FFmpeg command to combine video, audio, burn-in subtitles, and embed subtitle stream
cmd = [
    ffmpeg, "-y",
    "-i", str(raw_v),
    "-i", str(raw_a),
    "-vf", f"ass={captions.as_posix()}",
    "-c:v", "libx264",
    "-preset", "medium",
    "-crf", "19",
    "-pix_fmt", "yuv420p",
    "-r", "10",
    "-c:a", "aac",
    "-b:a", "192k",
    "-ar", "44100",
    "-shortest",
    str(out_mp4)
]

print("Rendering final master MP4 with video, audio narration, and subtitles...")
res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode != 0:
    print("FFmpeg stderr:", res.stderr)
    raise RuntimeError("FFmpeg rendering failed")

print("Rendering completed successfully.")
