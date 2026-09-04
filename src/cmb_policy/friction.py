"""Risk-adaptive runtime friction for CMB policy integrations.

The Dynamic Friction Matrix changes verification effort without changing CMB's
hard human-agency invariants. Trust may reduce operational uncertainty; it must
not erase intrinsic task risk or convert a heuristic into proof.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from typing import Final

FRICTION_SCHEMA_VERSION: Final = "cmb.friction-decision.v1"
AGILE_MAX: Final = 0.40
BALANCED_MAX: Final = 0.80
SIDE_EFFECT_FLOOR: Final = 0.45
IRREVERSIBLE_FLOOR: Final = 0.65
MANDATORY_EVIDENCE_FLOOR: Final = 0.81


class FrictionMode(str, Enum):
    """Stable runtime modes for the CMB seesaw."""

    HIGH_AGILITY = "HIGH_AGILITY"
    BALANCED = "BALANCED"
    HIGH_SAFETY = "HIGH_SAFETY"


class ExecutionDisposition(str, Enum):
    """Stable execution outcomes."""

    EXECUTE_FLUID = "EXECUTE_FLUID"
    EXECUTE_WITH_CAVEAT = "EXECUTE_WITH_CAVEAT"
    EXECUTE_VERIFIED = "EXECUTE_VERIFIED"
    HALT = "HALT"


class EvidenceKind(str, Enum):
    """Evidence classes understood by the equilibrium valve."""

    HUMAN_REVIEW = "HUMAN_REVIEW"
    INDEPENDENT_VERIFICATION = "INDEPENDENT_VERIFICATION"
    CRYPTOGRAPHIC_INTEGRITY = "CRYPTOGRAPHIC_INTEGRITY"


@dataclass(frozen=True, slots=True)
class TaskRiskProfile:
    """Explicit task facts used to calculate runtime friction.

    intrinsic_criticality is the consequence floor for the task itself.
    uncertainty is operational novelty and may decay with successful review.
    """

    task_id: str
    intrinsic_criticality: float
    uncertainty: float = 0.0
    reversible: bool = True
    external_side_effect: bool = False
    requires_integrity_receipt: bool = False
    requires_human_review: bool = False
    requires_independent_verification: bool = False
    unknown_variables: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.task_id, str) or not self.task_id.strip():
            raise ValueError("task_id must be a non-empty string")
        _validate_unit_interval("intrinsic_criticality", self.intrinsic_criticality)
        _validate_unit_interval("uncertainty", self.uncertainty)

        for field_name in (
            "reversible",
            "external_side_effect",
            "requires_integrity_receipt",
            "requires_human_review",
            "requires_independent_verification",
        ):
            if type(getattr(self, field_name)) is not bool:
                raise TypeError(f"{field_name} must be bool")

        if not isinstance(self.unknown_variables, tuple):
            raise TypeError("unknown_variables must be a tuple")
        if len(set(self.unknown_variables)) != len(self.unknown_variables):
            raise ValueError("unknown_variables must not contain duplicates")
        for item in self.unknown_variables:
            if not isinstance(item, str) or not item.strip():
                raise ValueError("unknown_variables must contain non-empty strings")


@dataclass(frozen=True, slots=True)
class TrustState:
    """Review history for one stable task profile."""

    successful_human_reviews: int = 0
    anomaly_count: int = 0

    def __post_init__(self) -> None:
        for field_name in ("successful_human_reviews", "anomaly_count"):
            value = getattr(self, field_name)
            if type(value) is not int:
                raise TypeError(f"{field_name} must be int")
            if value < 0:
                raise ValueError(f"{field_name} must be >= 0")


@dataclass(frozen=True, slots=True)
class EvidenceState:
    """Verified evidence supplied by the integration point."""

    human_review_confirmed: bool = False
    independent_verification_passed: bool = False
    cryptographic_integrity_verified: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "human_review_confirmed",
            "independent_verification_passed",
            "cryptographic_integrity_verified",
        ):
            if type(getattr(self, field_name)) is not bool:
                raise TypeError(f"{field_name} must be bool")

    def satisfies(self, kind: EvidenceKind) -> bool:
        if kind is EvidenceKind.HUMAN_REVIEW:
            return self.human_review_confirmed
        if kind is EvidenceKind.INDEPENDENT_VERIFICATION:
            return self.independent_verification_passed
        if kind is EvidenceKind.CRYPTOGRAPHIC_INTEGRITY:
            return self.cryptographic_integrity_verified
        raise ValueError(f"unsupported evidence kind: {kind!r}")


@dataclass(frozen=True, slots=True)
class FrictionDecision:
    """Auditable result of one equilibrium-valve evaluation."""

    task_id: str
    mode: FrictionMode
    disposition: ExecutionDisposition
    intrinsic_floor: float
    operational_criticality: float
    effective_criticality: float
    epistemic_budget: float
    trust_discount: float
    trusted_invariant: bool
    required_evidence: tuple[EvidenceKind, ...]
    missing_evidence: tuple[EvidenceKind, ...]
    caveats: tuple[str, ...]

    @property
    def allowed(self) -> bool:
        return self.disposition is not ExecutionDisposition.HALT

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": FRICTION_SCHEMA_VERSION,
            "task_id": self.task_id,
            "mode": self.mode.value,
            "disposition": self.disposition.value,
            "allowed": self.allowed,
            "intrinsic_floor": self.intrinsic_floor,
            "operational_criticality": self.operational_criticality,
            "effective_criticality": self.effective_criticality,
            "epistemic_budget": self.epistemic_budget,
            "trust_discount": self.trust_discount,
            "trusted_invariant": self.trusted_invariant,
            "required_evidence": [item.value for item in self.required_evidence],
            "missing_evidence": [item.value for item in self.missing_evidence],
            "caveats": list(self.caveats),
        }


class FrictionRejectedError(PermissionError):
    """Raised when require_friction() receives a halted decision."""

    def __init__(self, decision: FrictionDecision) -> None:
        self.friction_decision = decision
        missing = ", ".join(item.value for item in decision.missing_evidence)
        detail = missing or "criticality gate"
        super().__init__(f"CMB friction gate halted {decision.task_id}: {detail}")


def evaluate_friction(
    profile: TaskRiskProfile,
    *,
    evidence: EvidenceState | None = None,
    trust: TrustState | None = None,
    half_life_reviews: int = 3,
) -> FrictionDecision:
    """Evaluate the Dynamic Friction Matrix deterministically."""

    if not isinstance(profile, TaskRiskProfile):
        raise TypeError("profile must be a TaskRiskProfile")
    if evidence is None:
        evidence = EvidenceState()
    if trust is None:
        trust = TrustState()
    if not isinstance(evidence, EvidenceState):
        raise TypeError("evidence must be an EvidenceState")
    if not isinstance(trust, TrustState):
        raise TypeError("trust must be a TrustState")
    if type(half_life_reviews) is not int or half_life_reviews <= 0:
        raise ValueError("half_life_reviews must be a positive int")

    clean_history = trust.anomaly_count == 0 and not profile.unknown_variables
    if clean_history:
        trust_discount = 0.5 ** (
            trust.successful_human_reviews / half_life_reviews
        )
    else:
        trust_discount = 1.0

    trusted_invariant = (
        clean_history
        and trust.successful_human_reviews >= half_life_reviews
    )

    uncertainty = profile.uncertainty * trust_discount
    unknown_spike = min(0.50, 0.20 * len(profile.unknown_variables))
    anomaly_spike = min(0.50, 0.25 * trust.anomaly_count)
    operational_criticality = min(
        1.0,
        uncertainty + unknown_spike + anomaly_spike,
    )

    intrinsic_floor = profile.intrinsic_criticality
    if profile.external_side_effect:
        intrinsic_floor = max(intrinsic_floor, SIDE_EFFECT_FLOOR)
    if not profile.reversible:
        intrinsic_floor = max(intrinsic_floor, IRREVERSIBLE_FLOOR)
    if (
        profile.requires_integrity_receipt
        or profile.requires_human_review
        or profile.requires_independent_verification
    ):
        intrinsic_floor = max(intrinsic_floor, MANDATORY_EVIDENCE_FLOOR)

    effective = max(intrinsic_floor, operational_criticality)
    epistemic_budget = effective

    if effective <= AGILE_MAX:
        mode = FrictionMode.HIGH_AGILITY
    elif effective <= BALANCED_MAX:
        mode = FrictionMode.BALANCED
    else:
        mode = FrictionMode.HIGH_SAFETY

    required: list[EvidenceKind] = []
    if mode is FrictionMode.HIGH_SAFETY:
        required.extend(
            (
                EvidenceKind.HUMAN_REVIEW,
                EvidenceKind.INDEPENDENT_VERIFICATION,
            )
        )
        if profile.requires_integrity_receipt:
            required.append(EvidenceKind.CRYPTOGRAPHIC_INTEGRITY)

    required_evidence = tuple(required)
    missing_evidence = tuple(
        item for item in required_evidence if not evidence.satisfies(item)
    )

    if mode is FrictionMode.HIGH_SAFETY:
        if missing_evidence:
            disposition = ExecutionDisposition.HALT
            caveats = (
                "FIX_COMMITTED != FIX_VERIFIED",
                "High-safety execution requires the declared evidence gates.",
            )
        else:
            disposition = ExecutionDisposition.EXECUTE_VERIFIED
            caveats = ()
    elif mode is FrictionMode.BALANCED:
        disposition = ExecutionDisposition.EXECUTE_WITH_CAVEAT
        caveats = (
            "MACHINE_INFERRED_PROVISIONAL",
            "PATTERN != PROOF",
        )
    else:
        disposition = ExecutionDisposition.EXECUTE_FLUID
        caveats = ()

    return FrictionDecision(
        task_id=profile.task_id,
        mode=mode,
        disposition=disposition,
        intrinsic_floor=round(intrinsic_floor, 6),
        operational_criticality=round(operational_criticality, 6),
        effective_criticality=round(effective, 6),
        epistemic_budget=round(epistemic_budget, 6),
        trust_discount=round(trust_discount, 6),
        trusted_invariant=trusted_invariant,
        required_evidence=required_evidence,
        missing_evidence=missing_evidence,
        caveats=caveats,
    )


def require_friction(
    profile: TaskRiskProfile,
    *,
    evidence: EvidenceState | None = None,
    trust: TrustState | None = None,
    half_life_reviews: int = 3,
) -> FrictionDecision:
    """Return an executable decision or raise FrictionRejectedError."""

    decision = evaluate_friction(
        profile,
        evidence=evidence,
        trust=trust,
        half_life_reviews=half_life_reviews,
    )
    if not decision.allowed:
        raise FrictionRejectedError(decision)
    return decision


def _validate_unit_interval(name: str, value: float) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a real number")
    numeric = float(value)
    if not isfinite(numeric):
        raise ValueError(f"{name} must be finite")
    if not 0.0 <= numeric <= 1.0:
        raise ValueError(f"{name} must be between 0.0 and 1.0")
