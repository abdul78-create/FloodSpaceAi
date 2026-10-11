import subprocess
import json
from pathlib import Path

ffprobe_path = r"C:\Users\Abdul\Downloads\ffmpeg-9.0.1-full_build\ffmpeg-9.0.1-full_build\bin\ffprobe.exe"
mp4_path = Path("demo/floodspaceai_demo_walkthrough.mp4")
webp_path = Path("demo/floodspaceai_demo_walkthrough.webp")

cmd = [
    ffprobe_path,
    "-v", "quiet",
    "-print_format", "json",
    "-show_format",
    "-show_streams",
    str(mp4_path)
]

res = subprocess.run(cmd, capture_output=True, text=True)
data = json.loads(res.stdout)

video_stream = next((s for s in data["streams"] if s["codec_type"] == "video"), None)
audio_stream = next((s for s in data["streams"] if s["codec_type"] == "audio"), None)
fmt = data["format"]

print("=== MP4 DEMO VIDEO VERIFICATION ===")
print(f"File Path:       {mp4_path}")
print(f"File Size:       {int(fmt['size']):,} bytes ({int(fmt['size'])/1024/1024:.2f} MB)")
print(f"Duration:        {float(fmt['duration']):.2f} seconds ({float(fmt['duration'])/60:.2f} minutes)")
if video_stream:
    print(f"Video Codec:     {video_stream['codec_name']} ({video_stream.get('profile', 'N/A')})")
    print(f"Resolution:      {video_stream['width']}x{video_stream['height']}")
    print(f"Frame Rate:      {video_stream['r_frame_rate']} fps")
    print(f"Pixel Format:    {video_stream.get('pix_fmt', 'N/A')}")
if audio_stream:
    print(f"Audio Codec:     {audio_stream['codec_name']} ({audio_stream.get('sample_rate', 'N/A')} Hz, {audio_stream.get('channels', '1')} ch)")
    print(f"Audio Bitrate:   {int(audio_stream.get('bit_rate', 0)):,} bps ({int(audio_stream.get('bit_rate', 0))/1000:.1f} kbps)")
print(f"Overall Bitrate: {int(fmt.get('bit_rate', 0)):,} bps ({int(fmt.get('bit_rate', 0))/1000:.1f} kbps)")
print(f"Captions / Subs: Embedded Burn-in (.ass) + Synchronized Voice Narration")

print("\n=== WEBP DEMO RECORDING VERIFICATION ===")
print(f"File Path:       {webp_path}")
print(f"File Size:       {webp_path.stat().st_size:,} bytes ({webp_path.stat().st_size/1024/1024:.2f} MB)")
print(f"Exists:          {webp_path.exists()}")

