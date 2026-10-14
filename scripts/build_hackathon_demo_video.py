import subprocess
import shutil
from pathlib import Path

ffmpeg = r"C:\Users\Abdul\Downloads\ffmpeg-9.0.1-full_build\ffmpeg-9.0.1-full_build\bin\ffmpeg.exe"
ffprobe = r"C:\Users\Abdul\Downloads\ffmpeg-9.0.1-full_build\ffmpeg-9.0.1-full_build\bin\ffprobe.exe"
art_dir = Path(r"C:\Users\Abdul\.gemini\antigravity-ide\brain\da2f9ed0-30c2-487d-8ae4-25e83a31223f")
work_dir = Path("demo/build_hackathon")
work_dir.mkdir(parents=True, exist_ok=True)

# 1. Source recordings (1920x1080 WebP animations)
src_frontend = art_dir / "verify_dashboard_frontend_1791482266384.webp"
src_qc = art_dir / "qc_comprehensive_test_1791482759538.webp"
src_narayani = art_dir / "final_live_demo_check_1791563316659.webp"
src_walkthrough = art_dir / "floodspaceai_demo_walkthrough_1791562105714.webp"

# 2. Extract video clips for all 6 sections (Total = 298.89s)
video_clips = [
    # Part 1: Intro (42.15s total)
    ("clip1a.mp4", src_frontend, 0.0, 25.0),
    ("clip1b.mp4", src_qc, 0.0, 17.15),
    # Part 2: Dashboard Walkthrough (49.25s total)
    ("clip2.mp4", src_qc, 17.15, 49.25),
    # Part 3: Satellite Analysis (61.95s total)
    ("clip3a.mp4", src_qc, 66.40, 28.00),
    ("clip3b.mp4", src_narayani, 10.00, 33.95),
    # Part 4: Infrastructure Exposure & Topological Connectivity (60.72s total)
    ("clip4a.mp4", src_walkthrough, 0.0, 50.00),
    ("clip4b.mp4", src_walkthrough, 50.0, 10.72),
    # Part 5: Situation Copilot (40.07s total)
    ("clip5a.mp4", src_walkthrough, 60.72, 29.18),
    ("clip5b.mp4", src_qc, 94.40, 10.89),
    # Part 6: Validation & Conclusion (44.75s total)
    ("clip6a.mp4", src_qc, 105.29, 7.71),
    ("clip6b.mp4", src_narayani, 0.0, 10.00),
    ("clip6c.mp4", src_frontend, 0.0, 27.04),
]

print("=== STEP 1: EXTRACTING AND RE-ENCODING VIDEO CLIPS (1080p, 10 fps) ===")
for name, src, ss, dur in video_clips:
    out = work_dir / name
    cmd = [
        ffmpeg, "-y",
        "-i", str(src),
        "-ss", str(ss),
        "-t", str(dur),
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-r", "10",
        str(out)
    ]
    print(f"  Extracting {name} from {src.name} (ss={ss}s, dur={dur}s)...")
    subprocess.run(cmd, check=True)

# 3. Concatenate video clips
concat_v_list = work_dir / "concat_v.txt"
with open(concat_v_list, "w") as f:
    for name, _, _, _ in video_clips:
        f.write(f"file '{name}'\n")

raw_v = work_dir / "master_raw_video.mp4"
cmd_concat_v = [
    ffmpeg, "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", str(concat_v_list),
    "-c", "copy",
    str(raw_v)
]
print("\n=== STEP 2: CONCATENATING MASTER VIDEO ===")
subprocess.run(cmd_concat_v, check=True)

# 4. Prepare and pad audio segments
audio_segments = [
    ("demo/audio_hackathon/part1_intro.wav", 42.15, "a1.wav"),
    ("demo/audio_hackathon/part2_dashboard.wav", 49.25, "a2.wav"),
    ("demo/audio_hackathon/part3_satellite.wav", 61.95, "a3.wav"),
    ("demo/audio_hackathon/part4_infrastructure.wav", 60.72, "a4.wav"),
    ("demo/audio_hackathon/part5_copilot.wav", 40.07, "a5.wav"),
    ("demo/audio_hackathon/part6_conclusion.wav", 44.75, "a6.wav"),
]

print("\n=== STEP 3: PREPARING AND PADDING AUDIO TRACKS ===")
for src_a, target_dur, out_a in audio_segments:
    out_p = work_dir / out_a
    cmd_pad = [
        ffmpeg, "-y",
        "-i", src_a,
        "-af", f"apad=whole_dur={target_dur}",
        str(out_p)
    ]
    subprocess.run(cmd_pad, check=True)

concat_a_list = work_dir / "concat_a.txt"
with open(concat_a_list, "w") as f:
    for _, _, out_a in audio_segments:
        f.write(f"file '{out_a}'\n")

master_a = work_dir / "master_audio.wav"
cmd_concat_a = [
    ffmpeg, "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", str(concat_a_list),
    "-c", "copy",
    str(master_a)
]
print("  Concatenating master audio...")
subprocess.run(cmd_concat_a, check=True)

# 5. Render final master MP4
out_mp4 = Path("demo/floodspaceai_hackathon_demo.mp4")
captions_ass = Path("demo/demo_subtitles.ass").resolve()
captions_srt = Path("demo/demo_subtitles.srt").resolve()

print("\n=== STEP 4: RENDERING FINAL HACKATHON DEMO MP4 (H.264 + AAC + BURN-IN & SOFT SUBTITLES) ===")
# Use subtitles filter with escaped path
cmd_final = [
    ffmpeg, "-y",
    "-i", str(raw_v),
    "-i", str(master_a),
    "-i", str(captions_srt),
    "-vf", f"ass={captions_ass.as_posix()}",
    "-c:v", "libx264",
    "-preset", "medium",
    "-crf", "18",
    "-pix_fmt", "yuv420p",
    "-r", "10",
    "-c:a", "aac",
    "-b:a", "192k",
    "-ar", "44100",
    "-c:s", "mov_text",
    "-metadata:s:s:0", "language=eng",
    "-metadata:s:s:0", "title=English",
    "-shortest",
    str(out_mp4)
]

res = subprocess.run(cmd_final, capture_output=True, text=True)
if res.returncode != 0:
    print("FFmpeg error:", res.stderr)
    raise RuntimeError("Final video rendering failed")

print(f"Final MP4 generated successfully at: {out_mp4} ({out_mp4.stat().st_size} bytes)")
