from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from cmb_edu import (
    CMBDualBrainParser,
    CMBParseError,
    FGCEmojiParser,
    build_context_commitment,
)

SCHEMA_PATH = Path("schemas/cmb.edu.v1.schema.json")


def test_parses_human_declared_context_with_privacy_defaults() -> None:
    token = CMBDualBrainParser().parse_stream(
        '♌::CREATIVE -> STATE[confident || overstimulated] '
        '=> GENERATE("dragon_story") -> PROFILE_NOT_PERSON;'
    )

    assert token["schema"] == "cmb.edu.v1"
    assert token["context"] == {
        "source": "human_declared",
        "states": ["confident", "overstimulated"],
        "machine_inferred": False,
        "temporal_scope": "current_interaction",
    }
    assert token["execution"]["raw_instruction"] == 'GENERATE("dragon_story")'
    assert token["execution"]["operation"] == "generate"
    assert token["execution"]["subject"] == "dragon_story"
    assert token["sovereignty_gate"]["enforced_translation"] == "AVATAR_IS_NOT_HEART"
    assert token["privacy"]["persistence"] == "ephemeral"
    assert token["privacy"]["training_permission"] is False
    assert token["privacy"]["profiling_permission"] is False
    assert token["privacy"]["psychological_inference_permission"] is False
    assert token["epistemic_boundary"]["declaration_is_diagnosis"] is False


def test_explicit_dual_brain_stream_supports_privacy_declarations() -> None:
    token = CMBDualBrainParser().parse_stream(
        "🪐::CREATIVE -> DECLARE[curious || excited] "
        "-> ASK[build a moon story] "
        "-> BOUNDARY[PREDICTION_NOT_DESTINY] "
        "-> PRIVACY[EPHEMERAL || NO_PROFILE || NO_TRAIN];"
    )

    assert token["meta"]["human_lens"] == "🪐"
    assert token["execution"]["operation"] == "ask"
    assert token["execution"]["subject"] == "build a moon story"
    assert (
        token["sovereignty_gate"]["enforced_translation"]
        == "MACHINE_GUESSES_I_CHOOSE"
    )


def test_rejects_unknown_boundary() -> None:
    with pytest.raises(CMBParseError, match="unknown sovereignty boundary"):
        CMBDualBrainParser().parse_stream(
            '🪐::LEARN -> STATE[curious] => ASK("why") '
            "-> MACHINE_DEFINES_PERSON;"
        )


def test_rejects_malformed_stream() -> None:
    with pytest.raises(CMBParseError, match="malformed"):
        CMBDualBrainParser().parse_stream("PROFILE = PERSON")


def test_stream_safety_limits_are_preserved() -> None:
    parser = CMBDualBrainParser()

    with pytest.raises(CMBParseError, match="4096-character"):
        parser.parse_stream("x" * 4097)

    states = " || ".join(f"s{i}" for i in range(9))
    with pytest.raises(CMBParseError, match="no more than 8"):
        parser.parse_stream(
            f'♌::CREATIVE -> STATE[{states}] => GENERATE("story") '
            "-> PROFILE_NOT_PERSON;"
        )


def test_fgc_emoji_stream_compiles_to_same_envelope_contract() -> None:
    token = FGCEmojiParser().parse_stream(
        "🧠 HAPPY + 🪐 CREATIVE + ⚡ DRAW DRAGON + "
        "🛡️ NO_PROFILE + ⏳ EPHEMERAL"
    )

    assert token["meta"]["human_lens"] == "FGC-KIDS"
    assert token["context"]["states"] == ["happy"]
    assert token["execution"]["operation"] == "draw"
    assert token["execution"]["subject"] == "DRAGON"
    assert token["sovereignty_gate"]["declared_invariant"] == "PROFILE_NOT_PERSON"
    assert token["privacy"]["training_permission"] is False
    assert token["privacy"]["profiling_permission"] is False
    assert token["privacy"]["psychological_inference_permission"] is False


@pytest.mark.parametrize("shield", ["🛡", "🛡️"])
def test_fgc_accepts_emoji_variation_selector_forms(shield: str) -> None:
    token = FGCEmojiParser().parse_stream(
        f"🧠 CURIOUS + 🪐 LEARNING + ⚡ ASK WHY + {shield} NO_PROFILE"
    )

    assert token["sovereignty_gate"]["declared_invariant"] == "PROFILE_NOT_PERSON"


def test_generated_fgc_payload_matches_public_schema() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    payload = FGCEmojiParser().parse_stream(
        "🧠 CURIOUS + 🪐 LEARNING + ⚡ ASK WHY + 🛡️ PROFILE_NOT_PERSON"
    )

    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(payload)


def test_context_commitment_is_deterministic_and_scope_limited() -> None:
    envelope = CMBDualBrainParser().parse_envelope(
        '♌::CREATIVE -> STATE[calm] => GENERATE("dragon") '
        "-> PROFILE_NOT_PERSON;"
    )

    left = build_context_commitment(envelope)
    right = build_context_commitment(envelope)

    assert left["payload_sha256"] == right["payload_sha256"]
    assert len(left["payload_sha256"]) == 64
    assert left["evidence_boundary"]["integrity_is_identity"] is False
    assert left["evidence_boundary"]["declaration_is_psychological_truth"] is False
    assert left["evidence_boundary"]["hash_is_consent"] is False
    assert left["evidence_boundary"]["metadata_is_enforcement"] is False
