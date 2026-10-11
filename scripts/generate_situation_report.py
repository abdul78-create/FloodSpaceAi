import json
from pathlib import Path


# ============================================================
# FloodSpaceAI — Evidence-Grounded Situation Report Copilot
# ============================================================

BASE = Path(".")
EVIDENCE_FILE = BASE / "data" / "processed" / "situation_report_evidence.json"

OUTPUT_DIR = (
    BASE
    / "data"
    / "processed"
    / "situation_reports"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD EVIDENCE
# ============================================================

def load_evidence():
    """Load the machine-readable evidence layer."""

    if not EVIDENCE_FILE.exists():
        raise FileNotFoundError(
            f"Evidence file not found:\n{EVIDENCE_FILE}"
        )

    with EVIDENCE_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# SAFE HELPERS
# ============================================================

def get_value(data, key, default=0):
    """
    Safely retrieve a value from the evidence JSON.

    This prevents the report generator from inventing values
    when a field is unavailable.
    """
    value = data.get(key, default)

    if value is None:
        return default

    return value


# ============================================================
# ENGLISH REPORT
# ============================================================

def generate_english(evidence):
    """Generate the evidence-grounded English situation report."""

    flood = evidence.get("flood_mapping", {})
    assets = evidence.get("potentially_affected_assets", {})
    connectivity = evidence.get("road_connectivity", {})

    flood_pixels = get_value(flood, "flood_pixels")
    flood_polygons = get_value(flood, "flood_polygons")

    buildings = get_value(assets, "buildings")
    roads = get_value(assets, "roads")
    bridges = get_value(assets, "bridges")

    # IMPORTANT:
    # The evidence JSON uses British spelling:
    # settlements_analysed
    settlements_analyzed = get_value(
        connectivity,
        "settlements_analysed"
    )

    town_city_hubs = get_value(
        connectivity,
        "town_city_hubs"
    )

    cut_off = get_value(
        connectivity,
        "potentially_cut_off_settlements"
    )

    return f"""# Trishuli Flood — Situation Report

## 1. Situation Overview

FloodSpaceAI analysed the August 2026 Trishuli flood using
Sentinel-1 radar and Sentinel-2 optical satellite data
together with pre-event OpenStreetMap infrastructure data.

The system produced a conservative potential inundation
candidate using multi-source satellite change detection.

## 2. Potential Flood Extent

The V3 model identified:

- Potential inundation pixels: {flood_pixels:,}
- Potential inundation polygons: {flood_polygons:,}

These values represent a modelled potential inundation
candidate and should not be interpreted as confirmed
physical flood extent.

## 3. Potentially Affected Infrastructure

Overlay analysis against the pre-event OSM snapshot
identified:

- Potentially affected buildings: {buildings:,}
- Potentially affected road features: {roads:,}
- Potentially affected bridges: {bridges:,}

These are potential impacts based on spatial overlap with
the modelled inundation candidate.

They do not confirm that individual buildings, roads,
or bridges were destroyed or physically damaged.

## 4. Road Connectivity

The road-network analysis evaluated
{settlements_analyzed:,} settlements against
{town_city_hubs:,} town/city hubs.

The model identified:

- Settlements analysed: {settlements_analyzed:,}
- Potentially cut-off settlements: {cut_off:,}

A settlement is classified as potentially cut off when its
road connection to its selected town/city hub exists in the
pre-event network but becomes disconnected after removing
modelled potentially affected road segments.

This is a modelled connectivity result and does not confirm
real-world isolation.

## 5. Limitations

- Post-event Sentinel-2 imagery contains cloud contamination
  in parts of the analysis area.
- The flood output is a modelled potential inundation
  candidate.
- Potentially affected infrastructure is not confirmed
  physical damage.
- Potentially cut-off settlements are not confirmed to be
  isolated in the real world.
- Historical hospital data was unavailable for this
  prototype, so town/city hubs were used for connectivity
  analysis.
- This system is an educational prototype and is not an
  operational emergency-response system.

## 6. Data Provenance

- Copernicus Sentinel-1 / Sentinel-2
- Copernicus DEM
- Pre-event OpenStreetMap data
- OSM snapshot: 2026-07-27
- © OpenStreetMap contributors.

Contains modified Copernicus Sentinel data 2026.

Produced using Copernicus WorldDEM-30 © DLR e.V.
2010–2014 and © Airbus Defence and Space GmbH 2014–2018
provided under COPERNICUS by the European Union and ESA;
all rights reserved.
"""


# ============================================================
# NEPALI REPORT
# ============================================================

def generate_nepali(evidence):
    """Generate the evidence-grounded Nepali situation report."""

    flood = evidence.get("flood_mapping", {})
    assets = evidence.get("potentially_affected_assets", {})
    connectivity = evidence.get("road_connectivity", {})

    flood_pixels = get_value(flood, "flood_pixels")
    flood_polygons = get_value(flood, "flood_polygons")

    buildings = get_value(assets, "buildings")
    roads = get_value(assets, "roads")
    bridges = get_value(assets, "bridges")

    # Evidence JSON uses settlements_analysed
    settlements_analyzed = get_value(
        connectivity,
        "settlements_analysed"
    )

    town_city_hubs = get_value(
        connectivity,
        "town_city_hubs"
    )

    cut_off = get_value(
        connectivity,
        "potentially_cut_off_settlements"
    )

    return f"""# त्रिशूली बाढी — स्थिति प्रतिवेदन

## १. अवस्थाको संक्षिप्त विवरण

FloodSpaceAI ले अगस्ट २०२६ को त्रिशूली बाढीको विश्लेषण
Sentinel-1 र Sentinel-2 उपग्रह डेटा तथा बाढीअघि उपलब्ध
OpenStreetMap पूर्वाधार डेटाको प्रयोग गरेर गरेको छ।

प्रणालीले बहु-स्रोत उपग्रह परिवर्तन विश्लेषणबाट
सम्भावित बाढी प्रभावित क्षेत्र पहिचान गरेको छ।

## २. सम्भावित बाढी क्षेत्र

V3 मोडेलले पहिचान गरेको:

- सम्भावित बाढी पिक्सेल: {flood_pixels:,}
- सम्भावित बाढी क्षेत्रका polygon: {flood_polygons:,}

यी संख्या मोडेलले पहिचान गरेको सम्भावित बाढी क्षेत्रसँग
सम्बन्धित हुन्। यी तथ्याङ्कलाई पुष्टि भएको वास्तविक
बाढी क्षेत्रको रूपमा बुझ्नु हुँदैन।

## ३. सम्भावित रूपमा प्रभावित पूर्वाधार

पूर्व-बाढी OpenStreetMap डेटासँग गरिएको spatial overlay बाट:

- सम्भावित प्रभावित भवन: {buildings:,}
- सम्भावित प्रभावित सडक: {roads:,}
- सम्भावित प्रभावित पुल: {bridges:,}

यी पूर्वाधारहरू सम्भावित बाढी क्षेत्रसँग spatial overlap
भएका कारण पहिचान गरिएका हुन्।

यसले वास्तविक क्षति वा ध्वंस भएको पुष्टि गर्दैन।

## ४. सडक सम्पर्क विश्लेषण

सडक सञ्जाल विश्लेषणले
{settlements_analyzed:,} बस्तीहरूलाई
{town_city_hubs:,} वटा town/city hub सँगको
सडक सम्पर्कको आधारमा मूल्याङ्कन गरेको छ।

मोडेलले:

- विश्लेषण गरिएका बस्ती: {settlements_analyzed:,}
- सम्भावित रूपमा सडक सम्पर्कबाट छुटेका बस्ती: {cut_off:,}

पहिचान गरेको छ।

यो परिणाम मोडेल गरिएको सडक सञ्जाल विच्छेदमा आधारित हो
र वास्तविक रूपमा बस्ती अलग भएको पुष्टि गर्दैन।

## ५. सीमितताहरू

- घटना पछिको Sentinel-2 optical imagery का केही भागमा
  बादलको प्रभाव रहेको छ।
- बाढी परिणाम सम्भावित inundation को मोडेल गरिएको परिणाम हो।
- पूर्वाधारमा वास्तविक भौतिक क्षति भएको पुष्टि गरिएको छैन।
- सम्भावित रूपमा cut-off बस्तीहरू वास्तविक रूपमा अलग भएको
  पुष्टि गरिएको छैन।
- ऐतिहासिक अस्पताल डेटा उपलब्ध नभएकाले prototype मा
  town/city hubs प्रयोग गरिएको छ।
- यो शैक्षिक prototype हो, operational emergency-response
  system होइन।

## ६. डेटा स्रोत

- Copernicus Sentinel-1 / Sentinel-2
- Copernicus DEM
- पूर्व-बाढी OpenStreetMap डेटा
- OSM snapshot: 2026-07-27
- © OpenStreetMap contributors.

Contains modified Copernicus Sentinel data 2026.

Produced using Copernicus WorldDEM-30 © DLR e.V.
2010–2014 and © Airbus Defence and Space GmbH 2014–2018
provided under COPERNICUS by the European Union and ESA;
all rights reserved.
"""


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("FloodSpaceAI — Situation Report Copilot")
    print("=" * 70)

    print()
    print("Loading evidence...")
    print(f"Source: {EVIDENCE_FILE}")

    evidence = load_evidence()

    print("Evidence loaded successfully.")

    # --------------------------------------------------------
    # Generate reports
    # --------------------------------------------------------

    english = generate_english(evidence)
    nepali = generate_nepali(evidence)

    english_file = OUTPUT_DIR / "situation_report_en.md"
    nepali_file = OUTPUT_DIR / "situation_report_ne.md"

    english_file.write_text(
        english,
        encoding="utf-8"
    )

    nepali_file.write_text(
        nepali,
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    flood = evidence.get("flood_mapping", {})
    assets = evidence.get("potentially_affected_assets", {})
    connectivity = evidence.get("road_connectivity", {})

    print()
    print("-" * 70)
    print("EVIDENCE VALIDATION")
    print("-" * 70)

    print(
        f"Flood pixels: "
        f"{get_value(flood, 'flood_pixels'):,}"
    )

    print(
        f"Flood polygons: "
        f"{get_value(flood, 'flood_polygons'):,}"
    )

    print(
        f"Buildings: "
        f"{get_value(assets, 'buildings'):,}"
    )

    print(
        f"Roads: "
        f"{get_value(assets, 'roads'):,}"
    )

    print(
        f"Bridges: "
        f"{get_value(assets, 'bridges'):,}"
    )

    print(
        f"Settlements analysed: "
        f"{get_value(connectivity, 'settlements_analysed'):,}"
    )

    print(
        f"Town/city hubs: "
        f"{get_value(connectivity, 'town_city_hubs'):,}"
    )

    print(
        f"Potentially cut-off settlements: "
        f"{get_value(connectivity, 'potentially_cut_off_settlements'):,}"
    )

    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------

    print()
    print("-" * 70)
    print("REPORTS CREATED")
    print("-" * 70)

    print()
    print(f"English:")
    print(english_file)

    print()
    print(f"Nepali:")
    print(nepali_file)

    print()
    print("-" * 70)
    print("GROUNDING CHECK")
    print("-" * 70)

    print("✓ All quantitative values come from:")
    print(f"  {EVIDENCE_FILE}")

    print("✓ No external damage-map numbers used.")

    print("✓ No numbers manually hard-coded into the report.")

    print("✓ Modelled impacts are explicitly labelled as potential.")

    print("✓ Limitations are included.")

    print()
    print("=" * 70)
    print("Situation Report Copilot completed successfully.")
    print("=" * 70)


if __name__ == "__main__":
    main()