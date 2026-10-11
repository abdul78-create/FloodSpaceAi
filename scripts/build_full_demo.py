import subprocess
from pathlib import Path

ffmpeg = r"C:\Users\Abdul\Downloads\ffmpeg-9.0.1-full_build\ffmpeg-9.0.1-full_build\bin\ffmpeg.exe"
ffprobe = r"C:\Users\Abdul\Downloads\ffmpeg-9.0.1-full_build\ffmpeg-9.0.1-full_build\bin\ffprobe.exe"
art_dir = Path(r"C:\Users\Abdul\.gemini\antigravity-ide\brain\da2f9ed0-30c2-487d-8ae4-25e83a31223f")
work_dir = Path("demo/build")
work_dir.mkdir(parents=True, exist_ok=True)

# 1. Source files
src_narayani = art_dir / "final_live_demo_check_1791563316659.webp"
src_qc = art_dir / "qc_comprehensive_test_1791482759538.webp"
src_walkthrough = art_dir / "floodspaceai_demo_walkthrough_1791562105714.webp"

# 2. Extract video clips
video_clips = [
    ("clip1.mp4", src_narayani, 0.0, 36.0),
    ("clip2.mp4", src_qc, 12.0, 38.0),
    ("clip3.mp4", src_qc, 55.0, 35.0),
    ("clip4.mp4", src_walkthrough, 55.0, 33.0),
    ("clip5a.mp4", src_walkthrough, 75.0, 15.0),
    ("clip5b.mp4", src_qc, 90.0, 23.0),
]

for name, src, ss, dur in video_clips:
    out = work_dir / name
    cmd = [
        ffmpeg, "-y",
        "-i", str(src),
        "-ss", str(ss),
        "-t", str(dur),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-r", "10",
        str(out)
    ]
    print(f"Extracting {name} ({dur}s)...")
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
print("Concatenating raw video...")
subprocess.run(cmd_concat_v, check=True)

# 4. Prepare and pad audio segments
audio_segments = [
    ("demo/audio/part1_intro.wav", 36.0, "a1.wav"),
    ("demo/audio/part2_hydrology.wav", 38.0, "a2.wav"),
    ("demo/audio/part3_assets.wav", 35.0, "a3.wav"),
    ("demo/audio/part4_copilot.wav", 33.0, "a4.wav"),
    ("demo/audio/part5_emsr927.wav", 38.0, "a5.wav"),
]

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
print("Concatenating master audio...")
subprocess.run(cmd_concat_a, check=True)

print("Master raw video and master audio successfully built.")
