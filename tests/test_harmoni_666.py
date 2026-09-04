from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from cmb_machine.harmoni import (
    DiscoveryStage,
    EpistemicState,
    HUMAN_FINAL,
    MISSINGNO_CODE,
    ProofGate,
    evaluate_claim,
    harmoni_manifest,
    next_discovery_stage,
    validate_discovery_transition,
)


def all_gates(value: bool) -> dict[ProofGate, bool]:
    return {gate: value for gate in ProofGate}


def test_proof_requires_all_six_gates() -> None:
    gates = all_gates(True)
    gates[ProofGate.VERIFIER_PASSED] = False

    decision = evaluate_claim(EpistemicState.PROOF, gate_results=gates)

    assert decision.effective_state is EpistemicState.UNKNOWN
    assert decision.missingno is True
    assert decision.authority == HUMAN_FINAL
    assert decision.failed_gates == (ProofGate.VERIFIER_PASSED,)
    payload = decision.to_dict()
    assert payload["schema_version"] == "cmb.harmoni-666.decision.v1"
    assert payload["sentinel"] == MISSINGNO_CODE


def test_complete_bounded_proof_is_retained() -> None:
    decision = evaluate_claim("proof", gate_results=all_gates(True))

    assert decision.effective_state is EpistemicState.PROOF
    assert decision.missingno is False
    assert decision.failed_gates == ()


@pytest.mark.parametrize(
    "state",
    [
        EpistemicState.PATTERN,
        EpistemicState.HYPOTHESIS,
        EpistemicState.INFERENCE,
        EpistemicState.EVIDENCE,
        EpistemicState.UNKNOWN,
    ],
)
def test_non_proof_states_never_require_fake_proof(state: EpistemicState) -> None:
    decision = evaluate_claim(state)

    assert decision.effective_state is state
    assert decision.missingno is False
    assert decision.authority == HUMAN_FINAL


def test_unknown_gate_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unknown HARMONI-666 proof gates"):
        evaluate_claim("PROOF", gate_results={"NOT_A_GATE": True})


def test_non_boolean_gate_is_rejected() -> None:
    with pytest.raises(TypeError, match="RULES_DEFINED must be boolean"):
        evaluate_claim("PROOF", gate_results={"RULES_DEFINED": "yes"})  # type: ignore[dict-item]


def test_manifest_is_exactly_six_six_six() -> None:
    manifest = harmoni_manifest()

    assert manifest["schema_version"] == "cmb.harmoni-666.manifest.v1"
    assert len(manifest["epistemic_states"]) == 6
    assert len(manifest["proof_gates"]) == 6
    assert len(manifest["sovereignty_failsafes"]) == 6
    assert manifest["unknown_sentinel"] == MISSINGNO_CODE
    motif = manifest["revelation_13_18_motif"]
    assert motif["source"] == "Revelation 13:18"
    assert motif["sequence"] == ["WISDOM", "UNDERSTANDING", "CALCULATION", "HUMAN"]
    assert motif["mapping"]["CALCULATION"] == "MACHINE_VERIFICATION"
    assert motif["mapping"]["HUMAN"] == HUMAN_FINAL
    assert motif["boundary"] == "SCRIPTURAL_MOTIF_NOT_EMPIRICAL_PROOF"


def test_epistemological_ladder_is_ordered_and_fail_closed() -> None:
    assert next_discovery_stage(DiscoveryStage.UNKNOWN) is DiscoveryStage.MISSINGNO
    assert next_discovery_stage("MISSINGNO") is DiscoveryStage.QUESTION
    assert next_discovery_stage("QUESTION") is DiscoveryStage.TEST
    assert next_discovery_stage("TEST") is DiscoveryStage.EVIDENCE
    assert next_discovery_stage("EVIDENCE") is DiscoveryStage.JUSTIFIED_CLAIM
    assert next_discovery_stage("JUSTIFIED_CLAIM") is None

    assert validate_discovery_transition("MISSINGNO", "QUESTION") is True
    assert validate_discovery_transition("MISSINGNO", "EVIDENCE") is False
    assert validate_discovery_transition("UNKNOWN", "JUSTIFIED_CLAIM") is False


def test_manifest_distinguishes_myth_symbol_evidence_and_meaning() -> None:
    ladder = harmoni_manifest()["epistemological_ladder"]

    assert ladder["creative_model_inputs"] == ["REALITY", "FICTION", "FANTASY"]
    assert ladder["creative_model_output"] == "CREATIVE_MODEL_OF_THE_UNKNOWN"
    assert ladder["stages"] == [
        "UNKNOWN",
        "MISSINGNO",
        "QUESTION",
        "TEST",
        "EVIDENCE",
        "JUSTIFIED_CLAIM",
    ]
    assert ladder["truth_distinctions"] == [
        "PROVENANCE != MYTHOLOGY",
        "MYTHOLOGY != FALSEHOOD",
        "SYMBOLISM != EVIDENCE",
        "EVIDENCE != TOTAL_MEANING",
    ]
    assert ladder["rules"]["stage_skipping"] == "DENIED"
    assert ladder["rules"]["justified_claim_is_proof"] is False
    assert ladder["final_authority"] == HUMAN_FINAL


def test_harmoni_manifest_matches_public_schema() -> None:
    repository_root = Path(__file__).resolve().parents[1]
    schema = json.loads(
        (repository_root / "schemas" / "cmb.harmoni-666.manifest.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )

    Draft202012Validator(schema).validate(harmoni_manifest())
