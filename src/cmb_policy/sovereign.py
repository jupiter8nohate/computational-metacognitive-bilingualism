"""CMB Sovereign Epistemic Protocol (SEP-1).

This module operationalizes the human-machine boundary described by HARMONI-666.
It models policy and verification state. It does not claim to detect
consciousness, prove theology, or provide an unspoofable physical cutoff.

Gate 6 trusts only authorization evidence that an external deployment has
already authenticated as human-originated. The protocol deliberately rejects
machine self-attestation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from typing import Final

SEP_DECISION_SCHEMA: Final[str] = "cmb.sovereign-epistemic.decision.v1"
SEP_MANIFEST_SCHEMA: Final[str] = "cmb.sovereign-epistemic.manifest.v1"
SEP_PROTOCOL: Final[str] = "CMB-SEP-1"
HUMAN_FINAL: Final[str] = "HUMAN_FINAL"


class SovereignState(str, Enum):
    """The six operational states of SEP-1."""

    IDLE = "IDLE"
    INGESTION = "INGESTION"
    PROCESSING = "PROCESSING"
    VERIFICATION = "VERIFICATION"
    EXCEPTION = "EXCEPTION"
    RESOLUTION = "RESOLUTION"


class Gate(str, Enum):
    """The six sequential validation checkpoints."""

    PROVENANCE = "PROVENANCE"
    SYNTAX = "SYNTAX"
    VERIFICATION = "VERIFICATION"
    CONSTRAINT = "CONSTRAINT"
    EXTERNAL_REVIEW = "EXTERNAL_REVIEW"
    AUTHORIZATION = "AUTHORIZATION"


class Failsafe(str, Enum):
    """The six bounded recovery controls."""

    SEVERANCE = "SEVERANCE"
    TRUNCATION = "TRUNCATION"
    ISOLATION = "ISOLATION"
    PARITY_CHECK = "PARITY_CHECK"
    DECELERATION = "DECELERATION"
    HUMAN_OVERRIDE = "HUMAN_OVERRIDE"


class PrincipalKind(str, Enum):
    HUMAN = "HUMAN"
    MACHINE = "MACHINE"
    SERVICE = "SERVICE"


class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"


@dataclass(frozen=True, slots=True)
class AuthorizationEvidence:
    """Evidence supplied by an external authorization mechanism.

    SEP-1 does not authenticate a human by itself. A deployment must provide
    an external trust root, identity provider, hardware approval device, or
    equivalent mechanism and set these fields truthfully.
    """

    principal_kind: PrincipalKind
    verification_status: VerificationStatus
    issued_by: str
    machine_self_asserted: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.principal_kind, PrincipalKind):
            raise TypeError("principal_kind must be a PrincipalKind")
        if not isinstance(self.verification_status, VerificationStatus):
            raise TypeError("verification_status must be a VerificationStatus")
        if not isinstance(self.issued_by, str) or not self.issued_by.strip():
            raise ValueError("issued_by must be a non-empty string")
        if type(self.machine_self_asserted) is not bool:
            raise TypeError("machine_self_asserted must be bool")

    @property
    def valid_human_authorization(self) -> bool:
        return (
            self.principal_kind is PrincipalKind.HUMAN
            and self.verification_status is VerificationStatus.VERIFIED
            and not self.machine_self_asserted
        )


@dataclass(frozen=True, slots=True)
class SovereignInput:
    """Explicit facts supplied to the deterministic SEP-1 evaluator."""

    claim_strength: float
    evidence_strength: float
    provenance_verified: bool
    syntax_valid: bool
    cross_format_verified: bool
    parity_aligned: bool
    external_review_passed: bool
    sensitive_human_context: bool
    authorization: AuthorizationEvidence

    def __post_init__(self) -> None:
        for name in ("claim_strength", "evidence_strength"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"{name} must be a number")
            if not isfinite(float(value)) or not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"{name} must be finite and between 0 and 1")
        for name in (
            "provenance_verified",
            "syntax_valid",
            "cross_format_verified",
            "parity_aligned",
            "external_review_passed",
            "sensitive_human_context",
        ):
            if type(getattr(self, name)) is not bool:
                raise TypeError(f"{name} must be bool")
        if not isinstance(self.authorization, AuthorizationEvidence):
            raise TypeError("authorization must be AuthorizationEvidence")


@dataclass(frozen=True, slots=True)
class GateResult:
    gate: Gate
    passed: bool
    reason: str

    def to_dict(self) -> dict[str, object]:
        return {
            "gate": self.gate.value,
            "passed": self.passed,
            "reason": self.reason,
        }


@dataclass(frozen=True, slots=True)
class SovereignDecision:
    """Final deterministic result of one SEP-1 evaluation."""

    state: SovereignState
    halted: bool
    gate_results: tuple[GateResult, ...]
    active_failsafes: tuple[Failsafe, ...]
    effective_claim_strength: float
    evidence_strength: float
    quarantined: bool
    requires_human_review: bool
    authority: str
    reason: str

    @property
    def failed_gates(self) -> tuple[Gate, ...]:
        return tuple(result.gate for result in self.gate_results if not result.passed)

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": SEP_DECISION_SCHEMA,
            "protocol": SEP_PROTOCOL,
            "state": self.state.value,
            "halted": self.halted,
            "gate_results": [item.to_dict() for item in self.gate_results],
            "failed_gates": [gate.value for gate in self.failed_gates],
            "active_failsafes": [item.value for item in self.active_failsafes],
            "effective_claim_strength": self.effective_claim_strength,
            "evidence_strength": self.evidence_strength,
            "quarantined": self.quarantined,
            "requires_human_review": self.requires_human_review,
            "authority": self.authority,
            "reason": self.reason,
        }


def evaluate_sovereign_protocol(request: SovereignInput) -> SovereignDecision:
    """Evaluate all six gates; no later gate may rescue an earlier failure."""

    if not isinstance(request, SovereignInput):
        raise TypeError("request must be a SovereignInput")

    gate_results = (
        GateResult(
            Gate.PROVENANCE,
            request.provenance_verified,
            "Origin integrity verified."
            if request.provenance_verified
            else "Origin integrity is unverified.",
        ),
        GateResult(
            Gate.SYNTAX,
            request.syntax_valid,
            "Cross-protocol syntax is valid."
            if request.syntax_valid
            else "Cross-protocol syntax is invalid.",
        ),
        GateResult(
            Gate.VERIFICATION,
            request.cross_format_verified and request.parity_aligned,
            "Cross-format verification and semantic parity passed."
            if request.cross_format_verified and request.parity_aligned
            else "Cross-format verification or semantic parity failed.",
        ),
        GateResult(
            Gate.CONSTRAINT,
            request.claim_strength <= request.evidence_strength,
            "Claim strength does not exceed evidence strength."
            if request.claim_strength <= request.evidence_strength
            else "Claim strength exceeds verified evidence strength.",
        ),
        GateResult(
            Gate.EXTERNAL_REVIEW,
            request.external_review_passed,
            "External review passed."
            if request.external_review_passed
            else "Required external review has not passed.",
        ),
        GateResult(
            Gate.AUTHORIZATION,
            request.authorization.valid_human_authorization,
            "Externally verified human authorization is present."
            if request.authorization.valid_human_authorization
            else "Externally verified human authorization is absent.",
        ),
    )

    failed = {item.gate for item in gate_results if not item.passed}
    failsafes: list[Failsafe] = []

    if Gate.PROVENANCE in failed:
        failsafes.extend((Failsafe.SEVERANCE, Failsafe.ISOLATION))

    if Gate.SYNTAX in failed and Failsafe.ISOLATION not in failsafes:
        failsafes.append(Failsafe.ISOLATION)

    if Gate.VERIFICATION in failed:
        failsafes.append(Failsafe.PARITY_CHECK)
        if Failsafe.ISOLATION not in failsafes:
            failsafes.append(Failsafe.ISOLATION)

    effective_claim_strength = float(request.claim_strength)
    if Gate.CONSTRAINT in failed:
        effective_claim_strength = float(request.evidence_strength)
        failsafes.append(Failsafe.TRUNCATION)
        if Failsafe.ISOLATION not in failsafes:
            failsafes.append(Failsafe.ISOLATION)

    if request.sensitive_human_context and (
        Gate.EXTERNAL_REVIEW in failed or Gate.AUTHORIZATION in failed
    ):
        failsafes.append(Failsafe.DECELERATION)

    if Gate.AUTHORIZATION in failed:
        failsafes.append(Failsafe.HUMAN_OVERRIDE)

    if failed:
        return SovereignDecision(
            state=SovereignState.EXCEPTION,
            halted=True,
            gate_results=gate_results,
            active_failsafes=tuple(dict.fromkeys(failsafes)),
            effective_claim_strength=effective_claim_strength,
            evidence_strength=float(request.evidence_strength),
            quarantined=Failsafe.ISOLATION in failsafes,
            requires_human_review=True,
            authority=HUMAN_FINAL,
            reason="One or more sovereign epistemic gates failed closed.",
        )

    return SovereignDecision(
        state=SovereignState.RESOLUTION,
        halted=False,
        gate_results=gate_results,
        active_failsafes=(),
        effective_claim_strength=float(request.claim_strength),
        evidence_strength=float(request.evidence_strength),
        quarantined=False,
        requires_human_review=False,
        authority=HUMAN_FINAL,
        reason="All six sovereign epistemic gates passed.",
    )


def protocol_manifest() -> dict[str, object]:
    """Return the public machine-readable SEP-1 architecture."""

    return {
        "schema_version": SEP_MANIFEST_SCHEMA,
        "protocol": SEP_PROTOCOL,
        "states": [state.value for state in SovereignState],
        "gates": [gate.value for gate in Gate],
        "failsafes": [failsafe.value for failsafe in Failsafe],
        "axioms": [
            "PATTERN != PROOF",
            "SYMBOLISM != EVIDENCE",
            "CALCULATION != WISDOM",
            "EVIDENCE != TOTAL_MEANING",
            "CLAIM_STRENGTH <= VERIFIED_EVIDENCE_STRENGTH",
            "HUMAN_AGENCY > MACHINE_AUTHORITY",
        ],
        "authorization_boundary": {
            "requires_external_human_authentication": True,
            "machine_self_attestation_allowed": False,
            "consciousness_detection_claimed": False,
            "physical_cutoff_claimed": False,
        },
        "failsafe_boundaries": {
            "SEVERANCE": "disconnect or reject untrusted external input on explicit integrity or security failure",
            "TRUNCATION": "cap operational claim strength at verified evidence strength",
            "ISOLATION": "quarantine unverified or inconsistent payloads from execution",
            "PARITY_CHECK": "fail closed when binary and semantic representations diverge",
            "DECELERATION": "require human review before sensitive execution; does not infer emotion",
            "HUMAN_OVERRIDE": "deny autonomous execution without externally verified human authorization",
        },
    }
