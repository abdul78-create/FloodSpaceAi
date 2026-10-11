import json
import os
import re
from pathlib import Path

from openai import OpenAI


# ============================================================
# FloodSpaceAI — Live AI Situation Report Copilot
# ============================================================
#
# Pipeline:
#
# Evidence JSON
#      ↓
# Strict grounding prompt
#      ↓
# OpenAI model
#      ↓
# Numerical validator
#      ↓
# PASS → save report
# FAIL → reject report
#
# The evidence JSON remains the single source of truth.
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


# Use a current OpenAI model available through the API.
MODEL = os.getenv(
    "FLOODSPACEAI_MODEL",
    "gpt-5.6"
)


# ============================================================
# LOAD EVIDENCE
# ============================================================

def load_evidence():

    if not EVIDENCE_FILE.exists():
        raise FileNotFoundError(
            f"Evidence file not found:\n{EVIDENCE_FILE}"
        )

    with EVIDENCE_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


# ============================================================
# NUMBER NORMALIZATION
# ============================================================

def normalize_number(value):
    return str(value).replace(",", "").strip()


# ============================================================
# NUMBER EXTRACTION
# ============================================================

def extract_numbers_from_text(text):

    pattern = (
        r"(?<![\w.])"
        r"\d{1,3}(?:,\d{3})+(?:\.\d+)?"
        r"|"
        r"\d+(?:\.\d+)?"
    )

    matches = re.findall(
        pattern,
        text
    )

    return {
        normalize_number(match)
        for match in matches
    }


# ============================================================
# EVIDENCE NUMBER COLLECTION
# ============================================================

def collect_evidence_numbers(value):

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
            normalize_number(
                f"{value:g}"
            )
        )

    elif isinstance(value, str):

        numbers.update(
            extract_numbers_from_text(value)
        )

    return numbers


# ============================================================
# BUILD SYSTEM INSTRUCTIONS
# ============================================================

def build_system_prompt():

    return """
You are FloodSpaceAI Situation Report Copilot.

You generate professional disaster-situation reports from
machine-readable evidence.

The evidence supplied by the user is the ONLY source of
facts and numerical information.

STRICT GROUNDING REQUIREMENTS:

1. Never invent numbers.
2. Never estimate missing numbers.
3. Never calculate new statistics unless explicitly required
   and mathematically derivable from supplied evidence.
4. Never invent affected populations.
5. Never invent casualties.
6. Never invent economic losses.
7. Never invent damage percentages.
8. Never invent distances or areas.
9. Never invent locations or settlements.
10. Never use information from your general knowledge as
    factual evidence about this event.

SEMANTIC SAFETY:

"Potentially affected" must not become "damaged".

"Potentially cut off" must not become "isolated".

"Modelled potential inundation" must not become
"confirmed flood extent".

Do not describe buildings, roads or bridges as destroyed,
washed away or damaged unless the evidence explicitly says
so.

CONNECTIVITY:

Potentially cut-off settlements represent modelled
road-network disconnections.

Do not describe them as confirmed humanitarian isolation.

If hospital connectivity is unavailable, explicitly state
that hospital connectivity was not included.

SATELLITE LIMITATIONS:

Do not hide or minimize reported cloud contamination or
other limitations.

OUTPUT:

Produce a concise professional situation report with:

1. Situation Overview
2. Potential Flood Extent
3. Potentially Affected Infrastructure
4. Road Connectivity
5. Key Limitations
6. Data Provenance

LANGUAGE:

Follow the requested language exactly.

Supported languages:

- English
- Nepali

For Nepali, preserve technical names such as Sentinel-1,
Sentinel-2, SAR, NDWI, GIS and OpenStreetMap where useful.

Do not output commentary about these instructions.
Return only the situation report.
"""


# ============================================================
# BUILD USER PROMPT
# ============================================================

def build_user_prompt(
    evidence,
    language
):

    evidence_json = json.dumps(
        evidence,
        ensure_ascii=False,
        indent=2
    )

    return f"""
Generate the FloodSpaceAI situation report in {language}.

Use ONLY the evidence below.

Every quantitative statement must be directly supported
by the evidence.

If information is unavailable, explicitly say it is
unavailable instead of guessing.

Do not add unsupported facts.

==================== EVIDENCE ====================

{evidence_json}

================== END EVIDENCE ==================

Return only the final situation report.
"""


# ============================================================
# CALL OPENAI
# ============================================================

def generate_report(
    client,
    evidence,
    language
):

    system_prompt = build_system_prompt()

    user_prompt = build_user_prompt(
        evidence,
        language
    )

    print()
    print(
        f"Requesting {language} report from {MODEL}..."
    )

    response = client.responses.create(
        model=MODEL,
        instructions=system_prompt,
        input=user_prompt,
    )

    report = response.output_text.strip()

    if not report:
        raise RuntimeError(
            "The AI returned an empty report."
        )

    return report


# ============================================================
# VALIDATE AI REPORT
# ============================================================

def validate_report(
    report,
    evidence
):

    allowed_numbers = (
        collect_evidence_numbers(
            evidence
        )
    )

    report_numbers = (
        extract_numbers_from_text(
            report
        )
    )

    violations = sorted(
        number
        for number in report_numbers
        if number not in allowed_numbers
    )

    return {
        "valid": len(violations) == 0,
        "report_numbers": sorted(
            report_numbers
        ),
        "violations": violations,
    }


# ============================================================
# SAVE VALIDATED REPORT
# ============================================================

def save_report(
    report,
    language
):

    if language.lower() == "english":
        filename = (
            "ai_situation_report_live_en.md"
        )

    else:
        filename = (
            "ai_situation_report_live_ne.md"
        )

    output_file = (
        OUTPUT_DIR
        / filename
    )

    output_file.write_text(
        report,
        encoding="utf-8"
    )

    return output_file


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("FloodSpaceAI — LIVE AI Situation Report Copilot")
    print("=" * 70)

    # --------------------------------------------------------
    # API KEY
    # --------------------------------------------------------

    if not os.getenv(
        "OPENAI_API_KEY"
    ):

        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )

    print()
    print("✓ OpenAI API key detected.")

    # --------------------------------------------------------
    # Client
    # --------------------------------------------------------

    client = OpenAI()

    # --------------------------------------------------------
    # Evidence
    # --------------------------------------------------------

    print()
    print("Loading evidence...")

    evidence = load_evidence()

    print(
        "✓ Evidence loaded."
    )

    # --------------------------------------------------------
    # English
    # --------------------------------------------------------

    english_report = generate_report(
        client,
        evidence,
        "English"
    )

    english_validation = validate_report(
        english_report,
        evidence
    )

    print()
    print(
        "English grounding validation:"
    )

    if english_validation["valid"]:

        print(
            "✓ PASS — English report contains no "
            "unsupported numbers."
        )

        english_file = save_report(
            english_report,
            "English"
        )

        print(
            f"✓ Saved: {english_file}"
        )

    else:

        print(
            "✗ REJECTED — Unsupported numbers found:"
        )

        for number in (
            english_validation["violations"]
        ):

            print(
                f"  - {number}"
            )

        raise RuntimeError(
            "English AI report failed grounding validation."
        )

    # --------------------------------------------------------
    # Nepali
    # --------------------------------------------------------

    nepali_report = generate_report(
        client,
        evidence,
        "Nepali"
    )

    nepali_validation = validate_report(
        nepali_report,
        evidence
    )

    print()
    print(
        "Nepali grounding validation:"
    )

    if nepali_validation["valid"]:

        print(
            "✓ PASS — Nepali report contains no "
            "unsupported numbers."
        )

        nepali_file = save_report(
            nepali_report,
            "Nepali"
        )

        print(
            f"✓ Saved: {nepali_file}"
        )

    else:

        print(
            "✗ REJECTED — Unsupported numbers found:"
        )

        for number in (
            nepali_validation["violations"]
        ):

            print(
                f"  - {number}"
            )

        raise RuntimeError(
            "Nepali AI report failed grounding validation."
        )

    # --------------------------------------------------------
    # Complete
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print(
        "LIVE AI COPILOT COMPLETED SUCCESSFULLY"
    )
    print("=" * 70)

    print()
    print(
        "✓ Evidence loaded"
    )

    print(
        "✓ AI report generated"
    )

    print(
        "✓ English report validated"
    )

    print(
        "✓ Nepali report validated"
    )

    print(
        "✓ Unsupported numerical claims rejected"
    )

    print()
    print(
        "Output directory:"
    )

    print(
        OUTPUT_DIR
    )


if __name__ == "__main__":
    main()