"""HARMONI-666 bounded proof gate for CMB-66.

HARMONI-666 is an epistemic control layer. It does not claim metaphysical
verification. "Axiomatic" represents declared first principles inside the
protocol. MissingNo.666 is a fail-closed sentinel for claims outside a verified
proof domain.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final, Mapping


HARMONI_DECISION_SCHEMA: Final[str] = "cmb.harmoni-666.decision.v1"
HARMONI_MANIFEST_SCHEMA: Final[str] = "cmb.harmoni-666.manifest.v1"
HARMONI_PROTOCOL: Final[str] = "HARMONI-666/1.0"
MISSINGNO_CODE: Final[str] = "MISSINGNO_666"
HUMAN_FINAL: Final[str] = "HUMAN_FINAL"


class HarmoniLayer(str, Enum):
    """The three non-interchangeable jurisdictions in the HARMONI triangle."""

    AXIOMATIC = "AXIOMATIC"
    MACHINE = "MACHINE"
    HUMAN = "HUMAN"


class EpistemicState(str, Enum):
    """Six states used to prevent patterns from silently becoming proof."""

    PATTERN = "PATTERN"
    HYPOTHESIS = "HYPOTHESIS"
    INFERENCE = "INFERENCE"
    EVIDENCE = "EVIDENCE"
    PROOF = "PROOF"
    UNKNOWN = "UNKNOWN"


class ProofGate(str, Enum):
    """Six gates required before CMB may retain a PROOF classification."""

    RULES_DEFINED = "RULES_DEFINED"
    ASSUMPTIONS_DECLARED = "ASSUMPTIONS_DECLARED"
    DOMAIN_BOUNDED = "DOMAIN_BOUNDED"
    DERIVATION_REPRODUCIBLE = "DERIVATION_REPRODUCIBLE"
    COUNTEREXAMPLE_SEARCHED = "COUNTEREXAMPLE_SEARCHED"
    VERIFIER_PASSED = "VERIFIER_PASSED"


SOVEREIGNTY_FAILSAFES: Final[tuple[str, ...]] = (
    "PROFILE != PERSON",
    "MODEL != MIND",
    "INFERENCE != FACT",
    "PREDICTION != DESTINY",
    "CAPABILITY != AUTHORITY",
    "HUMAN_AGENCY > MACHINE_AUTHORITY",
)


@dataclass(frozen=True, slots=True)
class HarmoniDecision:
    """Result of evaluating a claimed epistemic state."""

    requested_state: EpistemicState
    effective_state: EpistemicState
    missingno: bool
    authority: str
    failed_gates: tuple[ProofGate, ...]
    reason: str

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": HARMONI_DECISION_SCHEMA,
            "protocol": HARMONI_PROTOCOL,
            "requested_state": self.requested_state.value,
            "effective_state": self.effective_state.value,
            "missingno": self.missingno,
            "sentinel": MISSINGNO_CODE if self.missingno else None,
            "authority": self.authority,
            "failed_gates": [gate.value for gate in self.failed_gates],
            "reason": self.reason,
        }


def _coerce_gate_results(
    gate_results: Mapping[ProofGate | str, bool] | None,
) -> dict[ProofGate, bool]:
    supplied = gate_results or {}
    normalized: dict[ProofGate, bool] = {}

    for gate in ProofGate:
        raw = supplied.get(gate, supplied.get(gate.value, False))
        if not isinstance(raw, bool):
            raise TypeError(f"{gate.value} must be boolean.")
        normalized[gate] = raw

    unknown_keys = {
        str(key.value if isinstance(key, ProofGate) else key)
        for key in supplied
        if str(key.value if isinstance(key, ProofGate) else key)
        not in {gate.value for gate in ProofGate}
    }
    if unknown_keys:
        joined = ", ".join(sorted(unknown_keys))
        raise ValueError(f"Unknown HARMONI-666 proof gates: {joined}")

    return normalized


def evaluate_claim(
    requested_state: EpistemicState | str,
    *,
    gate_results: Mapping[ProofGate | str, bool] | None = None,
) -> HarmoniDecision:
    """Evaluate a claim and fail closed when proof requirements are incomplete.

    Non-PROOF states are preserved. A requested PROOF requires every gate.
    Any missing proof gate produces UNKNOWN plus the MISSINGNO_666 sentinel.
    """

    try:
        state = (
            requested_state
            if isinstance(requested_state, EpistemicState)
            else EpistemicState(str(requested_state).upper())
        )
    except ValueError as exc:
        raise ValueError(f"Unknown epistemic state: {requested_state!r}") from exc

    gates = _coerce_gate_results(gate_results)

    if state is not EpistemicState.PROOF:
        return HarmoniDecision(
            requested_state=state,
            effective_state=state,
            missingno=False,
            authority=HUMAN_FINAL,
            failed_gates=(),
            reason="No proof escalation requested.",
        )

    failed = tuple(gate for gate in ProofGate if not gates[gate])
    if failed:
        return HarmoniDecision(
            requested_state=state,
            effective_state=EpistemicState.UNKNOWN,
            missingno=True,
            authority=HUMAN_FINAL,
            failed_gates=failed,
            reason=(
                "Proof claim rejected. Claim strength exceeded verified evidence "
                "strength inside the declared domain."
            ),
        )

    return HarmoniDecision(
        requested_state=state,
        effective_state=EpistemicState.PROOF,
        missingno=False,
        authority=HUMAN_FINAL,
        failed_gates=(),
        reason="All six bounded proof gates passed.",
    )


def harmoni_manifest() -> dict[str, object]:
    """Return the canonical machine-readable HARMONI-666 triangle."""

    return {
        "schema_version": HARMONI_MANIFEST_SCHEMA,
        "protocol": HARMONI_PROTOCOL,
        "triangle": {
            "AXIOMATIC": {
                "role": "DECLARED_FIRST_PRINCIPLES",
                "boundary": "NOT_EMPIRICAL_PROOF_BY_ITSELF",
            },
            "MACHINE": {
                "role": "COMPUTATION_SEARCH_SERIALIZATION_VERIFICATION",
                "boundary": "NO_FINAL_HUMAN_AUTHORITY",
            },
            "HUMAN": {
                "role": "MEANING_CONSENT_AUTHORSHIP_JUDGMENT",
                "authority": HUMAN_FINAL,
            },
        },
        "epistemic_states": [state.value for state in EpistemicState],
        "proof_gates": [gate.value for gate in ProofGate],
        "sovereignty_failsafes": list(SOVEREIGNTY_FAILSAFES),
        "unknown_sentinel": MISSINGNO_CODE,
        "governing_rule": "CLAIM_STRENGTH <= VERIFIED_EVIDENCE_STRENGTH",
    }
