"""
FloodSpaceAI — Gemini Situation Report Copilot

Track B: Mapping Flood Damage from Space

Purpose
-------
- Generate English and Nepali situation reports from system evidence.
- Ground every quantitative claim in situation_report_evidence.json.
- Use Gemini when available.
- Fall back deterministically when Gemini is unavailable.
- Validate generated reports before accepting them.

Important
---------
- Gemini is NOT part of the flood-mapping pipeline.
- Copernicus EMSR927 is NOT used as a mapping input.
- Published damage maps are NOT used as mapping inputs.
- Numerical situation-report claims must come from the system evidence.
- Potential impacts must not be described as confirmed damage.
"""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any

from google import genai


# ============================================================================
# PROJECT PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

EVIDENCE_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "situation_report_evidence.json"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "situation_reports"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# GEMINI CONFIGURATION
# ============================================================================

PRIMARY_MODEL = "gemini-3.8-flash"

# These models have previously returned temporary 503 availability errors.
#
# Intentionally removed:
#   gemini-2.5-flash
#   gemini-2.0-flash
#   gemini-1.5-flash
#
# Those returned 404/unavailable responses for this account.
FALLBACK_MODELS = [
    "gemini-3.7-flash",
    "gemini-3.6-flash",
]

ALL_MODELS = [
    PRIMARY_MODEL,
    *FALLBACK_MODELS,
]

MAX_ATTEMPTS_PER_MODEL = 2
RETRY_DELAY_SECONDS = 5


# ============================================================================
# OUTPUT FILES
# ============================================================================

ENGLISH_REPORT_PATH = (
    OUTPUT_DIR
    / "gemini_situation_report_en.md"
)

NEPALI_REPORT_PATH = (
    OUTPUT_DIR
    / "gemini_situation_report_ne.md"
)

ENGLISH_VALIDATION_PATH = (
    OUTPUT_DIR
    / "gemini_grounding_validation_en.json"
)

NEPALI_VALIDATION_PATH = (
    OUTPUT_DIR
    / "gemini_grounding_validation_ne.json"
)


# ============================================================================
# GEMINI CLIENT
# ============================================================================


def create_gemini_client() -> genai.Client | None:
    """
    Create the Gemini client using GEMINI_API_KEY.

    The API key is read only from the environment.
    It is never printed or written to files.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("⚠ GEMINI_API_KEY not detected.")
        print("  Gemini generation will be skipped.")
        return None

    print("✓ Gemini API key detected.")

    try:
        client = genai.Client(api_key=api_key)
        print("✓ Gemini client initialized.")
        return client

    except Exception as exc:
        print("⚠ Failed to initialize Gemini client.")
        print(f"  Error: {exc}")
        return None


# ============================================================================
# EVIDENCE LOADING
# ============================================================================


def load_evidence() -> dict[str, Any]:
    """
    Load the authoritative numerical evidence.
    """

    print("Loading evidence...")

    if not EVIDENCE_PATH.exists():
        raise FileNotFoundError(
            f"Evidence file not found:\n{EVIDENCE_PATH}"
        )

    with EVIDENCE_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        evidence = json.load(file)

    print("✓ Evidence loaded.")

    return evidence


# ============================================================================
# NUMBER HANDLING
# ============================================================================


def normalize_number(value: str) -> str:
    """
    Normalize numeric formatting.

    Examples:
        1,286    -> 1286
        1,495.74 -> 1495.74
        1286     -> 1286
    """

    value = value.strip()
    value = value.replace(",", "")

    return value


def extract_numbers_from_text(
    text: str,
) -> list[str]:
    """
    Extract numeric values from ordinary prose.

    Examples:
        1286
        1,286
        1,495.74
        18
        2026
        27.75
    """

    pattern = (
        r"(?<![A-Za-z0-9])"
        r"(?:\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)"
        r"(?![A-Za-z0-9])"
    )

    matches = re.findall(
        pattern,
        text,
    )

    return [
        normalize_number(match)
        for match in matches
    ]


def remove_markdown_heading_numbers(
    text: str,
) -> str:
    """
    Remove Markdown heading/list numbering that is structural
    rather than quantitative.

    Examples removed:

        ## 1. Situation Overview
        ## 2. Methodology
        ### 4. Limitations

    This prevents heading numbers from being treated as evidence
    numbers while preserving actual numerical claims elsewhere.
    """

    lines: list[str] = []

    for line in text.splitlines():

        # Markdown headings:
        # ## 1. Situation Overview
        # ### 4. Limitations
        line = re.sub(
            r"^(\s*#{1,6}\s*)\d+\.\s+",
            r"\1",
            line,
        )

        # Numbered list items:
        # 1. Item
        # 2. Item
        #
        # Only remove when the entire number is clearly structural.
        line = re.sub(
            r"^(\s*)\d+\.\s+(?=[A-Za-z\u0900-\u097F])",
            r"\1",
            line,
        )

        lines.append(line)

    return "\n".join(lines)


# ============================================================================
# EVIDENCE NUMBER COLLECTION
# ============================================================================


def collect_evidence_numbers(
    evidence: Any,
) -> set[str]:
    """
    Recursively collect numbers from the evidence JSON.

    This allows the report to use:
    - counts
    - dates
    - coordinates
    - timestamps
    - model parameters
    - other evidence-backed numeric values
    """

    numbers: set[str] = set()

    def walk(value: Any) -> None:

        if isinstance(value, bool):
            return

        if isinstance(value, int):

            numbers.add(
                normalize_number(str(value))
            )

            return

        if isinstance(value, float):

            normalized = normalize_number(
                str(value)
            )

            numbers.add(normalized)

            if value.is_integer():
                numbers.add(
                    str(int(value))
                )

            return

        if isinstance(value, str):

            for number in extract_numbers_from_text(
                value
            ):
                numbers.add(number)

            return

        if isinstance(value, list):

            for item in value:
                walk(item)

            return

        if isinstance(value, dict):

            for key, item in value.items():

                walk(key)
                walk(item)

    walk(evidence)

    return numbers


# ============================================================================
# NUMERICAL GROUNDING VALIDATION
# ============================================================================


def validate_numerical_grounding(
    report_text: str,
    evidence: dict[str, Any],
) -> dict[str, Any]:
    """
    Verify every actual numerical claim in the report exists
    in the authoritative evidence.

    Markdown structural numbering is ignored.
    """

    evidence_numbers = (
        collect_evidence_numbers(evidence)
    )

    # Important:
    # Remove structural Markdown numbering before extracting numbers.
    cleaned_report = remove_markdown_heading_numbers(
        report_text
    )

    report_numbers = extract_numbers_from_text(
        cleaned_report
    )

    unsupported: list[str] = []

    for number in report_numbers:

        if number in evidence_numbers:
            continue

        # Handle equivalent integer representations.
        try:

            numeric_value = float(number)

            if numeric_value.is_integer():

                integer_form = str(
                    int(numeric_value)
                )

                if integer_form in evidence_numbers:
                    continue

        except ValueError:
            pass

        unsupported.append(number)

    unsupported = sorted(
        set(unsupported)
    )

    return {
        "passed": len(unsupported) == 0,
        "report_numbers": sorted(
            set(report_numbers)
        ),
        "evidence_numbers_count": len(
            evidence_numbers
        ),
        "unsupported_numbers": unsupported,
    }


# ============================================================================
# GEMINI SYSTEM INSTRUCTIONS
# ============================================================================


SYSTEM_INSTRUCTIONS = """
You are the Situation Report Copilot for FloodSpaceAI.

You are working on Track B: Mapping Flood Damage from Space.

Your task is to write a concise, professional emergency-style
situation report using ONLY the supplied system evidence.

CRITICAL RULES:

1. Use ONLY the supplied evidence.
2. Never invent numbers.
3. Every numerical claim must come from the evidence.
4. Do not invent hospitals.
5. Do not invent affected people.
6. Do not invent casualties.
7. Do not invent economic losses.
8. Do not invent rainfall amounts.
9. Do not invent flood depth.
10. Do not claim confirmed destruction unless explicitly supported.
11. Use "potentially affected" for buildings, roads and bridges.
12. Use "potentially cut off" for settlements.
13. Do not call modelled inundation "confirmed flooding".
14. Clearly state limitations.
15. Do not use EMSR927 as a mapping input.
16. Do not use published damage maps as mapping inputs.
17. Keep quantitative claims grounded in the evidence.
18. Keep the report professional and suitable for a hackathon.
"""


# ============================================================================
# PROMPT BUILDERS
# ============================================================================


def build_english_prompt(
    evidence: dict[str, Any],
) -> str:

    evidence_json = json.dumps(
        evidence,
        ensure_ascii=False,
        indent=2,
    )

    return f"""
{SYSTEM_INSTRUCTIONS}

Write the final situation report in English.

Use this structure:

# Flood Situation Report

## Situation Overview

Describe the case study and analysis.

## Where Flooding Was Detected

Explain the modelled potential inundation approach.

## Potentially Affected Infrastructure

Report evidence-backed counts for:
- buildings
- roads
- bridges

Always say "potentially affected".

## Potentially Cut-Off Settlements

Report the evidence-backed number and explain that this
is a modelled road-network disconnection.

## Methodology

Explain:
- Sentinel-1 SAR
- Sentinel-2 optical imagery
- NDWI
- pre-event OSM
- road-network connectivity
- evidence-grounded reporting

## Limitations

Mention:
- cloud contamination
- model uncertainty
- potential rather than confirmed impacts
- connectivity limitations
- hospital limitation if present

## Data Provenance

Use only provenance information contained in the evidence.

Do not introduce any number that is not contained in the evidence.

AUTHORITATIVE SYSTEM EVIDENCE:

{evidence_json}
"""


def build_nepali_prompt(
    evidence: dict[str, Any],
) -> str:

    evidence_json = json.dumps(
        evidence,
        ensure_ascii=False,
        indent=2,
    )

    return f"""
{SYSTEM_INSTRUCTIONS}

Write the final situation report in clear, professional Nepali.

Use this structure:

# बाढी अवस्था प्रतिवेदन

## अवस्थाको संक्षिप्त विवरण

## बाढीको सम्भावित प्रभाव क्षेत्र

## सम्भावित रूपमा प्रभावित पूर्वाधार

## सम्भावित रूपमा सम्पर्क विच्छेद भएका बस्तीहरू

## विधि

## सीमितताहरू

## तथ्यांक तथा स्रोत

IMPORTANT:

- Every number must come from the evidence.
- Do not invent hospitals.
- Do not invent casualties.
- Do not invent affected people.
- Do not invent economic losses.
- Do not invent rainfall or flood depth.
- Clearly distinguish potential inundation from confirmed flooding.
- Clearly distinguish potential infrastructure impacts from confirmed damage.
- Clearly distinguish modelled road disconnection from confirmed isolation.

AUTHORITATIVE SYSTEM EVIDENCE:

{evidence_json}
"""


# ============================================================================
# GEMINI GENERATION
# ============================================================================


def generate_with_model(
    client: genai.Client,
    model_name: str,
    prompt: str,
) -> str | None:
    """
    Generate a report with a Gemini model.
    """

    print(
        f"    Trying {model_name}..."
    )

    for attempt in range(
        1,
        MAX_ATTEMPTS_PER_MODEL + 1,
    ):

        print(
            f"    Attempt {attempt}/"
            f"{MAX_ATTEMPTS_PER_MODEL}..."
        )

        try:

            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )

            response_text = getattr(
                response,
                "text",
                None,
            )

            if (
                response_text
                and response_text.strip()
            ):

                print(
                    "    ✓ Gemini response received."
                )

                return response_text.strip()

            print(
                "    ⚠ Gemini returned an empty response."
            )

        except Exception as exc:

            print(
                "    ⚠ Request failed:"
            )

            print(
                f"      {exc}"
            )

            if attempt < MAX_ATTEMPTS_PER_MODEL:

                print(
                    "      Temporary service issue. "
                    f"Waiting {RETRY_DELAY_SECONDS} seconds..."
                )

                time.sleep(
                    RETRY_DELAY_SECONDS
                )

    return None


# ============================================================================
# EVIDENCE VALUE HELPER
# ============================================================================


def find_value(
    data: Any,
    possible_keys: list[str],
    default: Any = None,
) -> Any:
    """
    Recursively find the first matching key.
    """

    if isinstance(data, dict):

        for key in possible_keys:

            if key in data:
                return data[key]

        for value in data.values():

            result = find_value(
                value,
                possible_keys,
                default=None,
            )

            if result is not None:
                return result

    elif isinstance(data, list):

        for item in data:

            result = find_value(
                item,
                possible_keys,
                default=None,
            )

            if result is not None:
                return result

    return default


# ============================================================================
# DETERMINISTIC FALLBACK
# ============================================================================


def build_deterministic_report(
    evidence: dict[str, Any],
    language_label: str,
) -> str:
    """
    Create a deterministic report using only system evidence.

    Structural heading numbers are intentionally omitted so they
    cannot interfere with numerical grounding validation.
    """

    flood_pixels = find_value(
        evidence,
        ["flood_pixels"],
        default=0,
    )

    flood_polygons = find_value(
        evidence,
        ["flood_polygons"],
        default=0,
    )

    buildings = find_value(
        evidence,
        [
            "buildings",
            "potentially_affected_buildings",
        ],
        default=0,
    )

    roads = find_value(
        evidence,
        [
            "roads",
            "potentially_affected_roads",
        ],
        default=0,
    )

    bridges = find_value(
        evidence,
        [
            "bridges",
            "potentially_affected_bridges",
        ],
        default=0,
    )

    settlements_available = find_value(
        evidence,
        ["settlements_available"],
        default=0,
    )

    settlements_analysed = find_value(
        evidence,
        [
            "settlements_analysed",
            "settlements_analyzed",
        ],
        default=0,
    )

    hubs = find_value(
        evidence,
        [
            "town_city_hubs",
            "hubs",
        ],
        default=0,
    )

    cut_off = find_value(
        evidence,
        [
            "potentially_cut_off_settlements",
            "cut_off_settlements_count",
            "cut_off_count",
        ],
        default=0,
    )

    case_study = find_value(
        evidence,
        ["case_study"],
        default="August 2026 Trishuli flood",
    )

    osm_snapshot = find_value(
        evidence,
        ["osm_snapshot"],
        default="2026-07-27T00:00:00Z",
    )

    # ========================================================================
    # NEPALI
    # ========================================================================

    if language_label.lower().startswith(
        "nep"
    ):

        return f"""# बाढी अवस्था प्रतिवेदन

## अवस्थाको संक्षिप्त विवरण

यो विश्लेषण {case_study} केस स्टडीका लागि FloodSpaceAI को
उपग्रह तथा पूर्व-घटना OpenStreetMap तथ्यांकमा आधारित छ।

## बाढीको सम्भावित प्रभाव क्षेत्र

प्रणालीले Sentinel-1 SAR परिवर्तन, Sentinel-2 NDWI परिवर्तन,
घटना-पछिको पानीको अवस्था, घटना-अघिको गैर-पानी अवस्था र
connected-component filtering प्रयोग गरेर सम्भावित inundation
candidate तयार गरेको छ।

प्रणालीमा {flood_pixels} flood pixels र
{flood_polygons} flood polygons पहिचान भएका छन्।

यी परिणामहरू **सम्भावित inundation** हुन् र निश्चित वास्तविक
बाढी क्षेत्रको पुष्टि मानिनु हुँदैन।

## सम्भावित रूपमा प्रभावित पूर्वाधार

प्रणालीले निम्न पूर्वाधारहरूलाई सम्भावित रूपमा प्रभावित भनेर
पहिचान गरेको छ:

- भवन: {buildings}
- सडक: {roads}
- पुल: {bridges}

यी संख्या पुष्टि भएको भौतिक क्षति वा विनाशको संख्या होइनन्।

## सम्भावित रूपमा सम्पर्क विच्छेद भएका बस्तीहरू

कुल {settlements_available} बस्तीमध्ये
{settlements_analysed} बस्तीको road-network connectivity
विश्लेषण गरिएको छ।

विश्लेषणमा {hubs} town/city hubs प्रयोग गरिएको छ।

{cut_off} बस्तीहरू सम्भावित रूपमा cut off देखिएका छन्।

यो road-network model मा देखिएको disconnect हो र वास्तविक
मैदानस्तरीय isolation को पुष्टि होइन।

## विधि

विश्लेषणमा Sentinel-1 pre/post SAR तुलना,
Sentinel-2 optical comparison, NDWI परिवर्तन,
पूर्व-घटना OpenStreetMap infrastructure र
road-network connectivity प्रयोग गरिएको छ।

## सीमितताहरू

- सम्भावित inundation output पुष्टि भएको flood extent होइन।
- Sentinel-2 optical imagery मा cloud contamination रहेको छ।
- सम्भावित रूपमा प्रभावित infrastructure पुष्टि भएको damage होइन।
- सम्भावित cut-off settlements वास्तविक isolation को पुष्टि होइन।
- उपलब्ध historical data सीमितताका कारण hospital connectivity
  पूर्ण रूपमा समावेश गरिएको छैन।

## तथ्यांक तथा स्रोत

OpenStreetMap पूर्व-घटना snapshot:

{osm_snapshot}

यो प्रतिवेदन प्रणालीको evidence dataset बाट मात्र
संख्यात्मक जानकारी प्रयोग गरेर तयार गरिएको हो।
"""

    # ========================================================================
    # ENGLISH
    # ========================================================================

    return f"""# Flood Situation Report

## Situation Overview

This analysis supports the {case_study} case study using
FloodSpaceAI satellite analysis and pre-event OpenStreetMap data.

## Where Flooding Was Detected

The system generated a modelled potential inundation candidate
using Sentinel-1 SAR change, Sentinel-2 NDWI change, post-event
water conditions, pre-event non-water conditions, and
connected-component filtering.

The analysis contains {flood_pixels} flood pixels and
{flood_polygons} flood polygons.

These results represent **potential inundation** and should not
be interpreted as confirmed flood extent.

## Potentially Affected Infrastructure

The system identified the following infrastructure as
potentially affected:

- Buildings: {buildings}
- Roads: {roads}
- Bridges: {bridges}

These are potential impacts and are not confirmed physical
damage or destruction.

## Potentially Cut-Off Settlements

A total of {settlements_available} settlements were available
for the analysis, with {settlements_analysed} settlements
analysed for road-network connectivity.

The analysis used {hubs} town/city hubs.

{cut_off} settlements were identified as potentially cut off.

This represents a modelled road-network disconnection and does
not confirm real-world isolation.

## Methodology

The analysis uses Sentinel-1 pre/post SAR comparison,
Sentinel-2 optical comparison, NDWI change, pre-event
OpenStreetMap infrastructure, and road-network connectivity.

## Limitations

- The potential inundation output is not confirmed flood extent.
- Post-event Sentinel-2 optical imagery is cloud contaminated.
- Potentially affected infrastructure is not confirmed physical damage.
- Potentially cut-off settlements are modelled network
  disconnections, not confirmed real-world isolation.
- Historical data limitations prevented full hospital
  connectivity analysis.

## Data Provenance

Pre-event OpenStreetMap snapshot:

{osm_snapshot}

This report uses numerical information only from the
system evidence dataset.
"""


# ============================================================================
# REPORT GENERATION
# ============================================================================


def generate_report(
    client: genai.Client | None,
    prompt: str,
    evidence: dict[str, Any],
    language_label: str,
) -> tuple[str, str]:
    """
    Generate and validate one report.
    """

    print()
    print("=" * 70)
    print(
        f"{language_label.upper()} SITUATION REPORT"
    )
    print("=" * 70)

    # ------------------------------------------------------------------------
    # GEMINI
    # ------------------------------------------------------------------------

    if client is not None:

        for index, model_name in enumerate(
            ALL_MODELS,
            start=1,
        ):

            print()
            print(
                f"[{index}/{len(ALL_MODELS)}] "
                f"Trying {model_name}..."
            )

            generated = generate_with_model(
                client,
                model_name,
                prompt,
            )

            if generated is None:

                print(
                    f"⚠ {model_name} failed."
                )

                if index < len(ALL_MODELS):

                    print(
                        "  → Trying next Gemini model..."
                    )

                continue

            validation = validate_numerical_grounding(
                generated,
                evidence,
            )

            if validation["passed"]:

                print(
                    "✓ Numerical grounding passed."
                )

                return (
                    generated,
                    f"Gemini: {model_name}",
                )

            print(
                "⚠ Gemini generated unsupported numbers."
            )

            print(
                "  Unsupported numbers:",
                validation[
                    "unsupported_numbers"
                ],
            )

            print(
                "  → Rejecting response."
            )

    # ------------------------------------------------------------------------
    # DETERMINISTIC FALLBACK
    # ------------------------------------------------------------------------

    print()
    print("-" * 70)
    print(
        "Gemini unavailable — using deterministic "
        "grounded fallback."
    )
    print("-" * 70)

    fallback = build_deterministic_report(
        evidence,
        language_label,
    )

    validation = validate_numerical_grounding(
        fallback,
        evidence,
    )

    if not validation["passed"]:

        raise RuntimeError(
            "Deterministic fallback failed numerical grounding: "
            f"{validation['unsupported_numbers']}"
        )

    print(
        "✓ Deterministic fallback loaded."
    )

    print(
        "✓ Numerical grounding passed."
    )

    print(
        "✓ PASS — No unsupported numbers detected."
    )

    return (
        fallback,
        "Deterministic fallback",
    )


# ============================================================================
# SAVE FUNCTIONS
# ============================================================================


def save_report(
    path: Path,
    report: str,
) -> None:

    path.write_text(
        report,
        encoding="utf-8",
    )


def save_validation(
    path: Path,
    validation: dict[str, Any],
) -> None:

    path.write_text(
        json.dumps(
            validation,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


# ============================================================================
# MAIN
# ============================================================================


def main() -> None:

    print("=" * 70)
    print(
        "FloodSpaceAI — GEMINI Situation Report Copilot"
    )
    print("=" * 70)
    print()

    print("Configured models:")

    for model in ALL_MODELS:
        print(
            f"  • {model}"
        )

    print()

    # ------------------------------------------------------------------------
    # GEMINI CLIENT
    # ------------------------------------------------------------------------

    client = create_gemini_client()

    print()

    # ------------------------------------------------------------------------
    # LOAD EVIDENCE
    # ------------------------------------------------------------------------

    evidence = load_evidence()

    # ------------------------------------------------------------------------
    # ENGLISH REPORT
    # ------------------------------------------------------------------------

    english_prompt = build_english_prompt(
        evidence
    )

    english_report, english_mode = generate_report(
        client,
        english_prompt,
        evidence,
        "English",
    )

    english_validation = (
        validate_numerical_grounding(
            english_report,
            evidence,
        )
    )

    save_report(
        ENGLISH_REPORT_PATH,
        english_report,
    )

    save_validation(
        ENGLISH_VALIDATION_PATH,
        {
            "language": "English",
            "mode": english_mode,
            **english_validation,
        },
    )

    if not english_validation["passed"]:

        raise RuntimeError(
            "English report failed numerical grounding."
        )

    # ------------------------------------------------------------------------
    # NEPALI REPORT
    # ------------------------------------------------------------------------

    nepali_prompt = build_nepali_prompt(
        evidence
    )

    nepali_report, nepali_mode = generate_report(
        client,
        nepali_prompt,
        evidence,
        "Nepali",
    )

    nepali_validation = (
        validate_numerical_grounding(
            nepali_report,
            evidence,
        )
    )

    save_report(
        NEPALI_REPORT_PATH,
        nepali_report,
    )

    save_validation(
        NEPALI_VALIDATION_PATH,
        {
            "language": "Nepali",
            "mode": nepali_mode,
            **nepali_validation,
        },
    )

    if not nepali_validation["passed"]:

        raise RuntimeError(
            "Nepali report failed numerical grounding."
        )

    # ------------------------------------------------------------------------
    # FINAL STATUS
    # ------------------------------------------------------------------------

    print()
    print("=" * 70)
    print(
        "FloodSpaceAI — Situation Report Copilot Complete"
    )
    print("=" * 70)
    print()

    print("English report:")
    print(
        f"  Mode: {english_mode}"
    )
    print(
        f"  Report: {ENGLISH_REPORT_PATH}"
    )
    print(
        f"  Validation: {ENGLISH_VALIDATION_PATH}"
    )

    print()

    print("Nepali report:")
    print(
        f"  Mode: {nepali_mode}"
    )
    print(
        f"  Report: {NEPALI_REPORT_PATH}"
    )
    print(
        f"  Validation: {NEPALI_VALIDATION_PATH}"
    )

    print()
    print(
        "✓ Both reports passed numerical grounding."
    )
    print(
        "✓ Flood mapping pipeline is independent "
        "of Gemini availability."
    )


# ============================================================================
# ENTRY POINT
# ============================================================================


if __name__ == "__main__":
    main()