from __future__ import annotations

import json
from pathlib import Path


REGISTRY = Path(__file__).resolve().parents[1] / "library" / "cmb-z13.registry.json"


def _load() -> dict[str, object]:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def test_guardian_modes_match_canonical_languages_and_operators() -> None:
    registry = _load()

    expected = {
        "Capricorn": ("C", "FOUNDATION", "The Foundation Warden", "EARTH"),
        "Aquarius": ("Rust", "FUTURE", "The Future Architect", "AIR"),
        "Pisces": ("Haskell", "MEANING", "The Dream Keeper", "WATER"),
        "Aries": ("C++", "ACTION", "The Action Engine", "FIRE"),
        "Taurus": ("Java", "STABILITY", "The Iron Covenant", "EARTH"),
        "Gemini": ("TypeScript", "BILINGUALISM", "The Twin Translator", "AIR"),
        "Cancer": ("Python", "CONTEXT", "The Context Shield", "WATER"),
        "Leo": ("Swift", "EXPRESSION", "The Author Crown", "FIRE"),
        "Virgo": ("Go", "PRECISION", "The Verification Sentinel", "EARTH"),
        "Libra": ("Kotlin", "BALANCE", "The Balance Gate", "AIR"),
        "Scorpio": ("Prolog", "INFERENCE", "The Forensic Oracle", "WATER"),
        "Ophiuchus": (
            "Common Lisp",
            "METACOGNITION",
            "The Override Architect",
            "OPHIUCHUS",
        ),
        "Sagittarius": ("Julia", "EXPLORATION", "The Horizon Scout", "FIRE"),
    }

    archetypes = registry["archetypes"]
    assert len(archetypes) == 13
    actual = {
        entry["sign"]: (
            entry["software_language"],
            entry["operator"],
            entry["guardian_name"],
            entry["guardian_team"],
        )
        for entry in archetypes
    }

    assert actual == expected


def test_guardian_modes_are_story_aliases_not_person_profiles() -> None:
    registry = _load()
    presentation = registry["presentation_model"]
    boundary = registry["guardian_boundary"]

    assert registry["version"] == "1.1.0"
    assert presentation["guardian_modes_are_story_aliases"] is True
    assert presentation["guardian_modes_define_people"] is False
    assert presentation["canonical_semantics_remain_operators"] is True
    assert presentation["human_authority_remains_final"] is True

    assert boundary["ophiuchus_is_supreme_leader"] is False
    assert boundary["machine_has_final_authority"] is False
    assert boundary["story_alias_changes_canonical_operator"] is False
    assert boundary["zodiac_symbol_defines_person"] is False
    assert boundary["code_defines_identity"] is False


def test_guardian_pipeline_ends_in_human_decision() -> None:
    registry = _load()
    pipeline = registry["guardian_pipeline"]

    assert [step["sign"] for step in pipeline] == [
        "Scorpio",
        "Virgo",
        "Cancer",
        "Gemini",
        "Libra",
        "Ophiuchus",
        "Aries",
        "Human",
    ]
    assert pipeline[-1] == {
        "sign": "Human",
        "language": None,
        "operation": "DECIDE",
        "result": "HUMAN_DECISION",
    }


def test_guardian_invariants_preserve_identity_boundary() -> None:
    registry = _load()
    invariants = set(registry["invariants"])

    assert "PROFILE != PERSON" in invariants
    assert "PREDICTION != DESTINY" in invariants
    assert "ZODIAC_SYMBOL != PERSON" in invariants
    assert "CODE != IDENTITY" in invariants
    assert "GUARDIAN_MODE != PERSONALITY" in invariants
    assert "HUMAN_AGENCY > MACHINE_AUTHORITY" in invariants
