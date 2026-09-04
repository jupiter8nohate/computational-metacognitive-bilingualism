import pytest

from cmb_edu import CMBDualBrainParser, CMBParseError


def test_parses_human_declared_context_with_privacy_defaults():
    token = CMBDualBrainParser().parse_stream(
        '♌::CREATIVE -> STATE[confident || overstimulated] => GENERATE("dragon_story") -> PROFILE_NOT_PERSON;'
    )

    assert token["schema"] == "cmb.edu.v1"
    assert token["context"] == {
        "source": "human_declared",
        "states": ["confident", "overstimulated"],
        "machine_inferred": False,
        "temporal_scope": "current_interaction",
    }
    assert token["sovereignty_gate"]["enforced_translation"] == "AVATAR_IS_NOT_HEART"
    assert token["privacy"]["persistence"] == "ephemeral"
    assert token["privacy"]["training_permission"] is False
    assert token["privacy"]["profiling_permission"] is False
    assert token["privacy"]["psychological_inference_permission"] is False


def test_rejects_unknown_boundary():
    with pytest.raises(CMBParseError, match="unknown sovereignty boundary"):
        CMBDualBrainParser().parse_stream(
            '🪐::LEARN -> STATE[curious] => ASK("why") -> MACHINE_DEFINES_PERSON;'
        )


def test_rejects_malformed_stream():
    with pytest.raises(CMBParseError, match="malformed"):
        CMBDualBrainParser().parse_stream("PROFILE = PERSON")
