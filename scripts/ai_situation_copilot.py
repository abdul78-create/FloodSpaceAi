import json
import re
from pathlib import Path


# ============================================================
# FloodSpaceAI — AI Situation Report Copilot
# ============================================================

BASE = Path(".")

EVIDENCE_FILE = (
    BASE
    / "data"
    / "processed"
    / "situation_report_evidence.json"
)

OUTPUT_DIR = (
    BASE
    / "data"
    / "processed"
    / "situation_reports"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PROMPT_FILE = OUTPUT_DIR / "ai_copilot_prompt.txt"
GROUNDING_FILE = OUTPUT_DIR / "ai_grounding_rules.txt"


# ============================================================
# LOAD EVIDENCE
# ============================================================

def load_evidence():
    if not EVIDENCE_FILE.exists():
        raise FileNotFoundError(
            f"Evidence file not found:\n{EVIDENCE_FILE}"
        )

    with EVIDENCE_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


# ============================================================
# NUMBER NORMALIZATION
# ============================================================

def normalize_number(value):
    """
    Normalize numbers so:

        1,286
        1286

    are treated as the same value.
    """

    return str(value).replace(",", "").strip()


# ============================================================
# EXTRACT NUMBERS FROM TEXT
# ============================================================

def extract_numbers_from_text(text):
    """
    Extract integers and decimals, including comma-separated
    thousands values such as 1,286.
    """

    pattern = r"(?<![\w.])\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?"

    matches = re.findall(pattern, text)

    return {
        normalize_number(match)
        for match in matches
    }


# ============================================================
# COLLECT NUMBERS FROM EVIDENCE
# ============================================================

def collect_evidence_numbers(value):
    """
    Recursively collect actual numerical values from the
    evidence JSON.

    Dictionary keys are NEVER interpreted as numbers.
    """

    numbers = set()

    if isinstance(value, dict):

        for item in value.values():
            numbers.update(
                collect_evidence_numbers(item)
            )

    elif isinstance(value, list):

        for item in value:
            numbers.update(
                collect_evidence_numbers(item)
            )

    elif isinstance(value, bool):
        pass

    elif isinstance(value, int):

        numbers.add(
            normalize_number(value)
        )

    elif isinstance(value, float):

        numbers.add(
            normalize_number(value)
        )

        numbers.add(
            normalize_number(f"{value:g}")
        )

    elif isinstance(value, str):

        numbers.update(
            extract_numbers_from_text(value)
        )

    return numbers


# ============================================================
# BUILD STRICT AI PROMPT
# ============================================================

def build_ai_prompt(evidence):

    evidence_json = json.dumps(
        evidence,
        ensure_ascii=False,
        indent=2
    )

    return f"""
You are FloodSpaceAI Situation Report Copilot.

Your task is to transform the supplied machine-readable
evidence into a concise emergency-style situation report.

============================================================
CRITICAL GROUNDING RULE
============================================================

The supplied evidence JSON is the ONLY source of facts
and numerical information.

NEVER invent:

- numbers
- percentages
- distances
- areas
- damage counts
- population counts
- dates
- confidence values
- casualty figures
- economic losses
- infrastructure totals
- locations
- affected communities

If information is not present in the evidence, say that it
is unavailable.

============================================================
INTERPRETATION RULES
============================================================

Always distinguish:

"potentially affected"

from:

"confirmed damaged"

Always distinguish:

"potentially cut off"

from:

"confirmed isolated"

Never convert a modelled result into a confirmed event.

Do not claim that a building, road, bridge or settlement
was actually damaged or isolated unless the evidence
explicitly supports that conclusion.

============================================================
SATELLITE DATA RULES
============================================================

The flood mapping result is a modelled potential inundation
candidate.

Sentinel-1 SAR and Sentinel-2 optical information may be
described only according to the evidence.

Post-event optical cloud contamination must not be ignored
when the evidence reports it.

Do not claim complete satellite coverage if the evidence
does not support it.

============================================================
INFRASTRUCTURE RULES
============================================================

Buildings, roads and bridges identified by spatial overlap
must be described as:

"potentially affected"

not:

"destroyed"

"damaged"

"washed away"

unless explicitly supported by evidence.

============================================================
CONNECTIVITY RULES
============================================================

Potentially cut-off settlements are modelled road-network
disconnections.

Do not describe them as confirmed humanitarian isolation.

Hospital connectivity must not be claimed if hospital
information is unavailable.

============================================================
OUTPUT FORMAT
============================================================

Generate:

1. Situation Overview
2. Potential Flood Extent
3. Potentially Affected Infrastructure
4. Road Connectivity
5. Key Limitations
6. Data Provenance

Keep the language concise and professional.

The report must be suitable for a disaster-response
situation-report demonstration.

============================================================
LANGUAGE
============================================================

The copilot must support:

- English
- Nepali

When Nepali is requested, preserve technical terms such as
Sentinel-1, Sentinel-2, OpenStreetMap, SAR, NDWI and GIS
where appropriate.

============================================================
MACHINE-READABLE EVIDENCE
============================================================

{evidence_json}

============================================================
END OF EVIDENCE
============================================================
"""


# ============================================================
# GROUNDING RULES
# ============================================================

def build_grounding_rules(evidence):

    numbers = sorted(
        collect_evidence_numbers(evidence),
        key=lambda x: (
            not x.replace(".", "", 1).isdigit(),
            float(x) if x.replace(".", "", 1).isdigit() else 0,
            x,
        )
    )

    return f"""FloodSpaceAI Numerical Grounding Rules
======================================

SOURCE OF TRUTH:

{EVIDENCE_FILE}

Every numerical statement in an AI-generated situation
report must be traceable to the evidence JSON.

The AI must NEVER invent a numerical value.

Evidence numbers:

{", ".join(numbers)}

IMPORTANT:

Comma-separated numbers are equivalent to their unformatted
values.

For example:

1,286 == 1286

1,495.74 == 1495.74

The number must still be used in the correct context.

MODELLED ≠ CONFIRMED

Potential inundation ≠ confirmed flood extent

Potentially affected ≠ confirmed damage

Potentially cut off ≠ confirmed isolation
"""


# ============================================================
# SAFE FALLBACK REPORT
# ============================================================

def build_fallback_report(evidence):

    flood = evidence.get(
        "flood_mapping",
        {}
    )

    assets = evidence.get(
        "potentially_affected_assets",
        {}
    )

    connectivity = evidence.get(
        "road_connectivity",
        {}
    )

    flood_pixels = flood.get(
        "flood_pixels",
        0
    )

    flood_polygons = flood.get(
        "flood_polygons",
        0
    )

    buildings = assets.get(
        "buildings",
        0
    )

    roads = assets.get(
        "roads",
        0
    )

    bridges = assets.get(
        "bridges",
        0
    )

    settlements = connectivity.get(
        "settlements_analysed",
        0
    )

    hubs = connectivity.get(
        "town_city_hubs",
        0
    )

    cut_off = connectivity.get(
        "potentially_cut_off_settlements",
        0
    )

    return f"""# FloodSpaceAI Situation Report

## Situation Overview

FloodSpaceAI analysed the August 2026 Trishuli flood using
Sentinel-1 and Sentinel-2 satellite information together
with pre-event OpenStreetMap infrastructure data.

The system produced a modelled potential inundation
candidate.

## Potential Flood Extent

The V3 model identified:

- {flood_pixels:,} potential inundation pixels
- {flood_polygons:,} potential inundation polygons

These represent modelled potential inundation and are not
confirmed physical flood extent.

## Potentially Affected Infrastructure

Spatial overlay identified:

- {buildings:,} potentially affected buildings
- {roads:,} potentially affected road features
- {bridges:,} potentially affected bridges

These results indicate potential spatial impact only.
They do not confirm physical damage.

## Road Connectivity

The network analysis evaluated:

- {settlements:,} settlements
- {hubs:,} town/city hubs
- {cut_off:,} potentially cut-off settlements

The cut-off classification represents modelled road-network
disconnection and does not confirm real-world isolation.

## Limitations

Post-event Sentinel-2 imagery contains cloud contamination
in parts of the analysis area.

The flood output is a modelled potential inundation
candidate.

Infrastructure impacts are not confirmed physical damage.

Settlement cut-off results are not confirmed real-world
isolation.

Historical hospital data was unavailable for this
prototype.

## Data Provenance

- Copernicus Sentinel-1 / Sentinel-2
- Copernicus DEM
- Pre-event OpenStreetMap data
- OSM snapshot: 2026-07-27
- © OpenStreetMap contributors.

Contains modified Copernicus Sentinel data 2026.
"""


# ============================================================
# VALIDATE REPORT NUMBERS
# ============================================================

def validate_report_numbers(report, evidence):

    allowed_numbers = collect_evidence_numbers(
        evidence
    )

    report_numbers = extract_numbers_from_text(
        report
    )

    violations = sorted(
        number
        for number in report_numbers
        if number not in allowed_numbers
    )

    return {
        "valid": len(violations) == 0,
        "report_numbers": sorted(
            report_numbers,
            key=lambda x: (
                not x.replace(".", "", 1).isdigit(),
                float(x) if x.replace(".", "", 1).isdigit() else 0
            )
        ),
        "allowed_numbers": sorted(
            allowed_numbers,
            key=lambda x: (
                not x.replace(".", "", 1).isdigit(),
                float(x) if x.replace(".", "", 1).isdigit() else 0
            )
        ),
        "violations": violations,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("FloodSpaceAI — AI Situation Report Copilot")
    print("=" * 70)

    print()
    print("Loading evidence...")

    evidence = load_evidence()

    print("Evidence loaded.")

    # --------------------------------------------------------
    # Build AI prompt
    # --------------------------------------------------------

    print()
    print("Building strict AI prompt...")

    prompt = build_ai_prompt(
        evidence
    )

    PROMPT_FILE.write_text(
        prompt,
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # Build grounding rules
    # --------------------------------------------------------

    rules = build_grounding_rules(
        evidence
    )

    GROUNDING_FILE.write_text(
        rules,
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # Generate fallback
    # --------------------------------------------------------

    print(
        "Generating grounded fallback report..."
    )

    report = build_fallback_report(
        evidence
    )

    fallback_file = (
        OUTPUT_DIR
        / "ai_situation_report_fallback.md"
    )

    fallback_file.write_text(
        report,
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    print()
    print(
        "Running numerical grounding validation..."
    )

    validation = validate_report_numbers(
        report,
        evidence
    )

    print()
    print("-" * 70)
    print("GROUNDING VALIDATION")
    print("-" * 70)

    if validation["valid"]:

        print(
            "✓ PASS — No unsupported numbers detected."
        )

    else:

        print(
            "✗ FAIL — Unsupported numbers detected:"
        )

        for number in validation["violations"]:
            print(
                f"  - {number}"
            )

    # --------------------------------------------------------
    # Save validation
    # --------------------------------------------------------

    validation_file = (
        OUTPUT_DIR
        / "ai_grounding_validation.json"
    )

    validation_file.write_text(
        json.dumps(
            validation,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------

    print()
    print("-" * 70)
    print("FILES CREATED")
    print("-" * 70)

    print()
    print(
        f"AI prompt:\n{PROMPT_FILE}"
    )

    print()
    print(
        f"Grounding rules:\n{GROUNDING_FILE}"
    )

    print()
    print(
        f"Fallback report:\n{fallback_file}"
    )

    print()
    print(
        f"Validation:\n{validation_file}"
    )

    print()
    print("=" * 70)

    if validation["valid"]:

        print(
            "Step 3 AI grounding layer completed successfully."
        )

    else:

        print(
            "Step 3 completed with grounding validation errors."
        )

    print("=" * 70)


if __name__ == "__main__":
    main()