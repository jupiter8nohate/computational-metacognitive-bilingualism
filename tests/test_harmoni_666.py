from __future__ import annotations

import pytest

from cmb_machine.harmoni import (
    EpistemicState,
    HUMAN_FINAL,
    MISSINGNO_CODE,
    ProofGate,
    evaluate_claim,
    harmoni_manifest,
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
