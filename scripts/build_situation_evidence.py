import json
from pathlib import Path


BASE = Path(".")


def load_json(path):
    if not path.exists():
        print(f"WARNING: Missing {path}")
        return {}
    return json.loads(
        path.read_text(encoding="utf-8")
    )


asset_summary = load_json(
    BASE
    / "data/processed/affected_assets_v3/"
    / "affected_assets_v3_summary.json"
)

connectivity_summary = load_json(
    BASE
    / "data/processed/connectivity_v4/"
    / "connectivity_v4_summary.json"
)

cutoff = load_json(
    BASE
    / "data/processed/connectivity_v4/"
    / "potentially_cut_off_settlements_v4.json"
)

road_summary = load_json(
    BASE
    / "data/processed/road_impact/"
    / "road_impact_summary.json"
)


evidence = {
    "project": "FloodSpaceAI",

    "track": "Track B — Mapping Flood Damage from Space",

    "case_study": {
        "event": "August 2026 Trishuli flood",
        "analysis_area": "Trishuli valley AOI",
        "osm_snapshot": "2026-07-27T00:00:00Z"
    },

    "flood_mapping": {
        "method": (
            "Potential inundation candidate derived from "
            "Sentinel-1 SAR change, Sentinel-2 NDWI change, "
            "post-event water condition, pre-event non-water "
            "condition, and connected-component filtering."
        ),
        "candidate_version": "V3",
        "flood_pixels": 1286,
        "flood_polygons": 84
    },

    "potentially_affected_assets": {
        "buildings": asset_summary.get(
            "potentially_affected_buildings",
            0
        ),
        "roads": asset_summary.get(
            "potentially_affected_roads",
            0
        ),
        "bridges": asset_summary.get(
            "potentially_affected_bridges",
            0
        )
    },

    "road_connectivity": {
        "settlements_available": connectivity_summary.get(
            "settlements_available",
            0
        ),
        "settlements_analysed": connectivity_summary.get(
            "settlements_analysed",
            0
        ),
        "town_city_hubs": connectivity_summary.get(
            "town_city_hubs",
            0
        ),
        "potentially_cut_off_settlements": connectivity_summary.get(
            "potentially_cut_off_settlements",
            0
        ),
        "pre_event_components": connectivity_summary.get(
            "pre_event_components",
            0
        ),
        "post_event_components": connectivity_summary.get(
            "post_event_components",
            0
        )
    },

    "cut_off_settlements": [
        {
            "name": item.get("name"),
            "place": item.get("place"),
            "nearest_town_or_city": item.get(
                "nearest_town_or_city"
            ),
            "connected_before": item.get(
                "connected_before"
            ),
            "connected_after": item.get(
                "connected_after"
            )
        }
        for item in cutoff
    ],

    "road_impact": {
        "v1_reference_only": {
            "potentially_affected_features": road_summary.get(
                "potentially_affected_road_features"
            ),
            "potentially_affected_length_km": road_summary.get(
                "potentially_affected_road_length_km"
            )
        },
        "note": (
            "The road-impact summary above was generated "
            "from the earlier V1 flood candidate and must "
            "not be presented as the final V3 result."
        )
    },

    "limitations": [
        (
            "The flood output is a modelled potential "
            "inundation candidate, not confirmed physical damage."
        ),
        (
            "Post-event Sentinel-2 optical imagery is "
            "cloud contaminated in parts of the AOI."
        ),
        (
            "Potentially affected assets are not confirmed "
            "destroyed or damaged."
        ),
        (
            "Potentially cut-off settlements are modelled "
            "road-network disconnections, not confirmed "
            "real-world isolation."
        ),
        (
            "Hospital connectivity was not included because "
            "the historical hospital query was unavailable; "
            "town/city hubs were used."
        )
    ],

    "data_provenance": {
        "sentinel": "Copernicus Sentinel-1 / Sentinel-2",
        "dem": "Copernicus DEM",
        "osm": "© OpenStreetMap contributors",
        "osm_snapshot": "2026-07-27",
        "analysis_status": "prototype / educational"
    }
}


OUTPUT = (
    BASE
    / "data/processed/"
    / "situation_report_evidence.json"
)

OUTPUT.write_text(
    json.dumps(
        evidence,
        indent=2,
        ensure_ascii=False
    ),
    encoding="utf-8"
)


print("=" * 65)
print("FloodSpaceAI — Situation Report Evidence")
print("=" * 65)

print()
print("Flood pixels:", evidence["flood_mapping"]["flood_pixels"])
print("Flood polygons:", evidence["flood_mapping"]["flood_polygons"])

print(
    "Buildings:",
    evidence["potentially_affected_assets"]["buildings"]
)

print(
    "Roads:",
    evidence["potentially_affected_assets"]["roads"]
)

print(
    "Bridges:",
    evidence["potentially_affected_assets"]["bridges"]
)

print(
    "Potentially cut-off settlements:",
    evidence["road_connectivity"][
        "potentially_cut_off_settlements"
    ]
)

print()
print("Saved:")
print(OUTPUT)

print()
print(
    "This evidence file is the ONLY numerical source "
    "the situation-report copilot should use."
)

print("=" * 65)