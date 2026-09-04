from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from cmb_edu import CMBDualBrainParser, FGCEmojiParser, build_context_commitment


SCHEMA_PATH = Path("schemas/cmb.edu.v1.schema.json")


def test_legacy_dual_brain_stream_is_normalized() -> None:
    stream = (
        '♌::CREATIVE -> STATE[confident || overstimulated] '
        '=> GENERATE("dragon_story") -> PROFILE_NOT_PERSON;'
    )

    payload = CMBDualBrainParser().parse_stream(stream)

    assert payload["schema"] == "cmb.edu.v1"
    assert payload["context"]["source"] == "human_declared"
    assert payload["context"]["states"] == ["confident", "overstimulated"]
    assert payload["context"]["machine_inferred"] is False
    assert payload["request"]["operation"] == "generate"
    assert payload["request"]["subject"] == "dragon_story"
    assert payload["sovereignty"]["boundary"] == "PROFILE_NOT_PERSON"
    assert payload["privacy"]["persistence"] == "ephemeral"
    assert payload["privacy"]["training_permission"] is False
    assert payload["privacy"]["profiling_permission"] is False


def test_modern_dual_brain_stream_supports_explicit_privacy() -> None:
    stream = (
        "🪐::CREATIVE -> DECLARE[curious || excited] "
        "-> ASK[build a moon story] "
        "-> BOUNDARY[PREDICTION_NOT_DESTINY] "
        "-> PRIVACY[EPHEMERAL || NO_PROFILE || NO_TRAIN];"
    )

    payload = CMBDualBrainParser().parse_stream(stream)

    assert payload["meta"]["human_lens"] == "🪐"
    assert payload["request"]["operation"] == "ask"
    assert payload["request"]["subject"] == "build a moon story"
    assert payload["sovereignty"]["translation"] == "MACHINE_GUESSES_I_CHOOSE"


def test_fgc_emoji_stream_compiles_to_same_envelope_contract() -> None:
    stream = "🧠 HAPPY + 🪐 CREATIVE + ⚡ DRAW DRAGON + 🛡️ NO_PROFILE + ⏳ EPHEMERAL"

    payload = FGCEmojiParser().parse_stream(stream)

    assert payload["meta"]["human_lens"] == "FGC-KIDS"
    assert payload["context"]["states"] == ["happy"]
    assert payload["request"]["operation"] == "draw"
    assert payload["request"]["subject"] == "DRAGON"
    assert payload["sovereignty"]["boundary"] == "PROFILE_NOT_PERSON"


def test_unknown_boundary_is_rejected() -> None:
    stream = '♌::CREATE -> STATE[curious] => GENERATE("story") -> MACHINE_OWNS_ME;'

    with pytest.raises(ValueError, match="Unknown CMB-EDU boundary"):
        CMBDualBrainParser().parse_stream(stream)


def test_schema_accepts_generated_payload() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    payload = FGCEmojiParser().parse_stream(
        "🧠 CURIOUS + 🪐 LEARNING + ⚡ ASK WHY + 🛡️ PROFILE_NOT_PERSON"
    )

    jsonschema.Draft202012Validator(schema).validate(payload)


def test_context_commitment_is_deterministic_and_scope_limited() -> None:
    envelope = CMBDualBrainParser().parse_envelope(
        '♌::CREATIVE -> STATE[calm] => GENERATE("dragon") -> PROFILE_NOT_PERSON;'
    )

    left = build_context_commitment(envelope)
    right = build_context_commitment(envelope)

    assert left["payload_sha256"] == right["payload_sha256"]
    assert len(left["payload_sha256"]) == 64
    assert left["evidence_boundary"]["integrity_is_identity"] is False
    assert left["evidence_boundary"]["hash_is_consent"] is False


@pytest.mark.parametrize("shield", ["🛡", "🛡️"])
def test_fgc_accepts_emoji_variation_selector_forms(shield: str) -> None:
    payload = FGCEmojiParser().parse_stream(
        f"🧠 CURIOUS + 🪐 LEARNING + ⚡ ASK WHY + {shield} NO_PROFILE"
    )

    assert payload["sovereignty"]["boundary"] == "PROFILE_NOT_PERSON"
