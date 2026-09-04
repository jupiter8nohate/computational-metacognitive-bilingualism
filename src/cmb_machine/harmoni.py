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


class DiscoveryStage(str, Enum):
    """Six ordered stages that formalize an anomaly into a justified claim."""

    UNKNOWN = "UNKNOWN"
    MISSINGNO = "MISSINGNO"
    QUESTION = "QUESTION"
    TEST = "TEST"
    EVIDENCE = "EVIDENCE"
    JUSTIFIED_CLAIM = "JUSTIFIED_CLAIM"


DISCOVERY_LADDER: Final[tuple[DiscoveryStage, ...]] = (
    DiscoveryStage.UNKNOWN,
    DiscoveryStage.MISSINGNO,
    DiscoveryStage.QUESTION,
    DiscoveryStage.TEST,
    DiscoveryStage.EVIDENCE,
    DiscoveryStage.JUSTIFIED_CLAIM,
)

TRUTH_DISTINCTIONS: Final[tuple[str, ...]] = (
    "PROVENANCE != MYTHOLOGY",
    "MYTHOLOGY != FALSEHOOD",
    "SYMBOLISM != EVIDENCE",
    "EVIDENCE != TOTAL_MEANING",
)


def next_discovery_stage(stage: DiscoveryStage | str) -> DiscoveryStage | None:
    """Return the only valid next stage in the HARMONI discovery ladder."""

    try:
        current = (
            stage if isinstance(stage, DiscoveryStage)
            else DiscoveryStage(str(stage).upper())
        )
    except ValueError as exc:
        raise ValueError(f"Unknown discovery stage: {stage!r}") from exc

    index = DISCOVERY_LADDER.index(current)
    if index == len(DISCOVERY_LADDER) - 1:
        return None
    return DISCOVERY_LADDER[index + 1]


def validate_discovery_transition(
    current: DiscoveryStage | str,
    proposed: DiscoveryStage | str,
) -> bool:
    """Permit only the next adjacent discovery stage; stage skipping fails closed."""

    try:
        target = (
            proposed if isinstance(proposed, DiscoveryStage)
            else DiscoveryStage(str(proposed).upper())
        )
    except ValueError as exc:
        raise ValueError(f"Unknown discovery stage: {proposed!r}") from exc

    return next_discovery_stage(current) is target


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
        "revelation_13_18_motif": {
            "source": "Revelation 13:18",
            "mode": "LITERARY_SYMBOLIC_DESIGN_KEY",
            "sequence": ["WISDOM", "UNDERSTANDING", "CALCULATION", "HUMAN"],
            "mapping": {
                "WISDOM": "HUMAN_JUDGMENT",
                "UNDERSTANDING": "HARMONI_INTERPRETATION",
                "CALCULATION": "MACHINE_VERIFICATION",
                "HUMAN": HUMAN_FINAL,
            },
            "boundary": "SCRIPTURAL_MOTIF_NOT_EMPIRICAL_PROOF",
        },
        "epistemological_ladder": {
            "creative_model_inputs": ["REALITY", "FICTION", "FANTASY"],
            "creative_model_output": "CREATIVE_MODEL_OF_THE_UNKNOWN",
            "stages": [stage.value for stage in DISCOVERY_LADDER],
            "truth_distinctions": list(TRUTH_DISTINCTIONS),
            "final_authority": HUMAN_FINAL,
            "rules": {
                "stage_skipping": "DENIED",
                "missingno_role": "ANOMALY_PLACEHOLDER_AND_MODEL_BOUNDARY",
                "machine_role": "TEST_AND_VERIFICATION",
                "human_role": "QUESTION_MEANING_JUDGMENT",
                "justified_claim_is_proof": False,
            },
        },
        "epistemic_states": [state.value for state in EpistemicState],
        "proof_gates": [gate.value for gate in ProofGate],
        "sovereignty_failsafes": list(SOVEREIGNTY_FAILSAFES),
        "unknown_sentinel": MISSINGNO_CODE,
        "governing_rule": "CLAIM_STRENGTH <= VERIFIED_EVIDENCE_STRENGTH",
    }
