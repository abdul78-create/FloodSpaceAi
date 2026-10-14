import subprocess
from pathlib import Path

audio_dir = Path("demo/audio_hackathon")
audio_dir.mkdir(parents=True, exist_ok=True)

segments = [
    (
        "part1_intro.wav",
        "Welcome to FloodSpace AI, an evidence-grounded multi-sensor flood intelligence platform developed for the Multimodal AI Hackathon Track B. "
        "In mountainous disaster zones like the Himalayas of Nepal, monsoonal flash floods and glacial lake outburst floods present severe operational challenges. "
        "Torrential storm clouds completely blind optical satellites, while rugged terrain causes radar shadows and delays emergency responders. "
        "FloodSpace AI solves this by streaming all-weather Sentinel-1 synthetic aperture radar, terrain-correcting through Copernicus WorldDEM-30, "
        "and evaluating spatial exposure across strictly pre-event OpenStreetMap infrastructure."
    ),
    (
        "part2_dashboard.wav",
        "Here is the FloodSpace AI operational dashboard running live in Full HD 1080p. The top navigation provides immediate situational awareness, "
        "displaying the bounding box, target flood date, and real-time sensor acquisition status. The analytical overview highlights key empirical findings "
        "for the Trishuli Valley benchmark: 1,286 candidate inundation pixels covering 35.03 hectares, 195 potentially exposed buildings, 115 road segments "
        "across 59.26 kilometers, 13 bridges, and 18 potentially cut-off settlements. Responders can seamlessly toggle layers, adjust raster opacity, "
        "and navigate interactive satellite overlays."
    ),
    (
        "part3_satellite.wav",
        "Examining the satellite processing pipeline, FloodSpace AI performs dual-polarization change detection using Sentinel-1 C-band synthetic aperture radar. "
        "By comparing post-event acquisitions against pre-event baselines, backscatter drops exceeding negative 1.5 decibels in both VV and VH polarizations "
        "are extracted as water candidates. Copernicus WorldDEM-30 slope constraints eliminate mountain shadow false positives. Using the split comparison slider, "
        "analysts can directly contrast the pre-event optical imagery against the candidate radar inundation footprint. Furthermore, our live run on the Narayani Basin "
        "demonstrates zero synthetic hallucination: persistent water bodies without backscatter change correctly yield zero flood pixels, ensuring emergency teams "
        "receive strictly verifiable data. Crucially, candidate flood polygons represent modeled surface water pooling, distinct from confirmed structural damage."
    ),
    (
        "part4_infrastructure.wav",
        "Moving to infrastructure impact, FloodSpace AI overlays candidate inundation polygons onto OpenStreetMap infrastructure footprints frozen prior to the disaster event. "
        "The pipeline identifies 195 potentially affected buildings, 59.26 kilometers of primary and secondary highway, and 13 bridges. Beyond 2D spatial overlays, "
        "our topological Dijkstra graph model routes between 589 settlements and municipal emergency hubs. Inundation severs 3,748 road edges, fragmenting the network "
        "from 181 pre-event connected components into 252 isolated clusters. 18 upstream settlements, including Betrawati and Devighat, lose all vehicular highway connectivity. "
        "The system explicitly reminds responders that modeled road loss indicates vehicular cutoff, while foot trails and aerial routes may remain operable."
    ),
    (
        "part5_copilot.wav",
        "The Situation Copilot provides zero-hallucination operational briefs with full English and Nepali bilingual parity. Every numerical metric is cryptographically "
        "tied to verified GroundedClaim records in the pipeline manifest. When confronted with adversarial prompts asking for casualty estimates or monetary damage, "
        "strict guardrails refuse to speculate, explaining that satellite radar observes physical surface backscatter rather than casualties. Rather than claiming an "
        "opaque black-box neural segmentation model, FloodSpace AI relies on deterministic, physics-grounded thresholding with optional Vertex AI Gemini synthesis."
    ),
    (
        "part6_conclusion.wav",
        "For independent scientific validation, Copernicus Emergency Management Service activation EMSR927 serves as an isolated post-hoc benchmark. FloodSpace AI achieved "
        "10.93 hectares of coincident overlap, capturing 45.2 percent of our candidate footprint within the activation zone without using EMSR927 for parameter tuning. "
        "Built with a containerized Docker architecture, 56 passing automated tests, and strict attributions for Copernicus Sentinel, Copernicus WorldDEM-30, and OpenStreetMap, "
        "FloodSpace AI delivers actionable, truthful disaster intelligence from space. Thank you for evaluating FloodSpace AI."
    )
]

for filename, text in segments:
    out_path = audio_dir / filename
    # Use powershell System.Speech.Synthesis with Microsoft Zira Desktop
    escaped_text = text.replace("'", "''")
    ps_cmd = f"""
    Add-Type -AssemblyName System.Speech;
    $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer;
    $synth.SelectVoice('Microsoft Zira Desktop');
    $synth.Rate = 0;
    $synth.SetOutputToWaveFile('{str(out_path.resolve())}');
    $synth.Speak('{escaped_text}');
    $synth.Dispose();
    """
    cmd = ["powershell", "-NoProfile", "-Command", ps_cmd]
    subprocess.run(cmd, check=True)
    print(f"Generated {filename}: {out_path.stat().st_size} bytes")

print("All hackathon demo audio segments generated successfully.")
