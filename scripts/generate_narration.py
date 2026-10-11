import subprocess
from pathlib import Path

audio_dir = Path("demo/audio")
audio_dir.mkdir(parents=True, exist_ok=True)

segments = [
    (
        "part1_intro.wav",
        "Welcome to FloodSpace AI, an evidence-grounded multi-sensor flood intelligence platform for Track B. "
        "We begin by demonstrating live satellite acquisition on the Narayani Basin. The orchestrator streams raw "
        "Sentinel-1 SAR and Sentinel-2 optical GeoTIFFs from AWS STAC, verifying cryptographic SHA-256 checksums "
        "and strictly enforcing pre-event OpenStreetMap snapshots. The copilot transparently discloses heavy cloud "
        "obscuration and explains why zero false-positive inundation candidates are reported."
    ),
    (
        "part2_hydrology.wav",
        "Switching to the Trishuli Valley benchmark run, FloodSpace AI analyzes 1,286 candidate inundation pixels, "
        "representing 35.03 hectares on a resampled 16.8 meter grid. The interactive MapLibre map renders terrain-constrained "
        "water masks alongside pre-event optical baselines. Users can inspect individual flood polygons, adjust layer opacity, "
        "replay the elevation flood-rise sequence, and use the split comparison slider to contrast optical surface features "
        "against radar backscatter change."
    ),
    (
        "part3_assets.wav",
        "Next, the pipeline overlays inundation candidates with pre-event OpenStreetMap infrastructure, identifying "
        "195 potentially affected buildings, 115 road segments spanning 59 kilometers, and 13 bridges. Crucially, assets are "
        "strictly classified as potentially affected based on 2D footprint overlay rather than assumed structural collapse. "
        "Topological Dijkstra graph modeling reveals 18 upstream settlements cut off from primary municipal and hospital hubs."
    ),
    (
        "part4_copilot.wav",
        "The Situation Copilot delivers zero-hallucination emergency reporting with full English and Nepali parity. "
        "Every numerical claim is bound to a verified GroundedClaim record. Under adversarial queries, strict safety guardrails "
        "refuse to estimate casualties or monetary losses, explaining that physical sensors measure surface backscatter, "
        "not human casualties. When asked about building destruction, it clarifies spatial exposure versus structural failure."
    ),
    (
        "part5_emsr927.wav",
        "Finally, Copernicus Emergency Management Service activation EMSR927 serves strictly as an independent "
        "post-hoc benchmark. FloodSpace AI identified 10.93 hectares of coincident overlap, representing 45.2 percent of "
        "our candidate footprint within the disaster zone. EMSR927 was never used to tune detection parameters. "
        "With all 56 automated tests passing and end-to-end provenance verified, FloodSpace AI delivers truthful, "
        "evidence-grounded disaster intelligence from space."
    )
]

for filename, text in segments:
    out_path = audio_dir / filename
    # Use powershell System.Speech.Synthesis
    ps_cmd = f"""
    Add-Type -AssemblyName System.Speech;
    $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer;
    $synth.SelectVoice('Microsoft Zira Desktop');
    $synth.Rate = 0;
    $synth.SetOutputToWaveFile('{str(out_path.resolve())}');
    $synth.Speak('{text}');
    $synth.Dispose();
    """
    cmd = ["powershell", "-NoProfile", "-Command", ps_cmd]
    subprocess.run(cmd, check=True)
    print(f"Generated {filename}: {out_path.stat().st_size} bytes")

print("All audio segments generated successfully.")
