"""Risk-adaptive CMB sovereignty runtime.

Friction changes verification depth. It never changes what counts as proof.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib  # type: ignore[no-redef]

from .authorization import AuthorizationToken, verify_authorization


class RuntimePolicyError(ValueError):
    """Raised when the CMB runtime policy is malformed."""


class FrictionMode(str, Enum):
    LOW_FRICTION = "LOW_FRICTION"
    HIGH_FRICTION = "HIGH_FRICTION"


class VerificationState(str, Enum):
    GENERATED = "GENERATED"
    FIX_PROPOSED = "FIX_PROPOSED"
    FIX_COMMITTED = "FIX_COMMITTED"
    FIX_TESTED = "FIX_TESTED"
    FIX_REVIEWED = "FIX_REVIEWED"
    FIX_ATTESTED = "FIX_ATTESTED"
    FIX_VERIFIED = "FIX_VERIFIED"
    FIX_RELEASED = "FIX_RELEASED"


_STATE_ORDER = tuple(VerificationState)
_ALLOWED_TRANSITIONS = {
    state: {_STATE_ORDER[index + 1]} if index + 1 < len(_STATE_ORDER) else set()
    for index, state in enumerate(_STATE_ORDER)
}
_SUPPORTED_PROTOCOLS = {
    "cmb.sovereignty-runtime.v1",
    "cmb.sovereignty-runtime.v2",
}


@dataclass(frozen=True, slots=True)
class OperationRule:
    name: str
    criticality: float
    controls: tuple[str, ...] = ()
    reversible: bool = False

    def __post_init__(self) -> None:
        if not self.name or self.name != self.name.strip():
            raise RuntimePolicyError("operation name must be non-empty")
        if not 0.0 <= self.criticality <= 1.0:
            raise RuntimePolicyError(f"{self.name}: criticality must be between 0 and 1")
        if any(not item or item != item.strip() for item in self.controls):
            raise RuntimePolicyError(f"{self.name}: controls must be non-empty")


@dataclass(frozen=True, slots=True)
class RuntimePolicy:
    protocol: str
    default_friction: float
    high_friction_threshold: float
    critical_threshold: float
    operations: Mapping[str, OperationRule]
    digest: str
    source: Path

    @classmethod
    def load(cls, path: Path) -> "RuntimePolicy":
        raw = path.read_bytes()
        payload = tomllib.loads(raw.decode("utf-8"))
        cmb = payload.get("cmb")
        principles = payload.get("principles")
        operations = payload.get("operations")
        if not isinstance(cmb, dict):
            raise RuntimePolicyError("missing [cmb] section")
        if not isinstance(principles, dict):
            raise RuntimePolicyError("missing [principles] section")
        if not isinstance(operations, dict) or not operations:
            raise RuntimePolicyError("missing [operations.*] sections")

        _validate_principles(principles)

        default_friction = _bounded(cmb.get("default_friction"), "default_friction")
        high_threshold = _bounded(
            cmb.get("high_friction_threshold"), "high_friction_threshold"
        )
        critical_threshold = _bounded(cmb.get("critical_threshold"), "critical_threshold")
        if critical_threshold < high_threshold:
            raise RuntimePolicyError(
                "critical_threshold must be greater than or equal to high_friction_threshold"
            )

        rules: dict[str, OperationRule] = {}
        for name, config in operations.items():
            if not isinstance(config, dict):
                raise RuntimePolicyError(f"operations.{name} must be a table")
            controls = config.get("controls", [])
            if isinstance(controls, (str, bytes)) or not isinstance(controls, list):
                raise RuntimePolicyError(f"operations.{name}.controls must be an array")
            rules[name] = OperationRule(
                name=name,
                criticality=_bounded(config.get("criticality"), f"{name}.criticality"),
                controls=tuple(sorted({str(item).strip() for item in controls})),
                reversible=bool(config.get("reversible", False)),
            )

        protocol = str(cmb.get("protocol", "")).strip()
        if protocol not in _SUPPORTED_PROTOCOLS:
            raise RuntimePolicyError(f"unsupported runtime protocol: {protocol or '<missing>'}")

        return cls(
            protocol=protocol,
            default_friction=default_friction,
            high_friction_threshold=high_threshold,
            critical_threshold=critical_threshold,
            operations=rules,
            digest="sha256:" + hashlib.sha256(raw).hexdigest(),
            source=path,
        )


@dataclass(frozen=True, slots=True)
class Assessment:
    operation: str
    allowed: bool
    mode: FrictionMode
    criticality: float
    friction: float
    required_controls: tuple[str, ...]
    satisfied_controls: tuple[str, ...]
    failures: tuple[str, ...]
    policy_digest: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "cmb.runtime-assessment.v1",
            "operation": self.operation,
            "allowed": self.allowed,
            "mode": self.mode.value,
            "criticality": self.criticality,
            "friction": self.friction,
            "required_controls": list(self.required_controls),
            "satisfied_controls": list(self.satisfied_controls),
            "failures": list(self.failures),
            "policy_digest": self.policy_digest,
            "invariants": [
                "PATTERN != PROOF",
                "FIX_COMMITTED != FIX_VERIFIED",
                "CAPABILITY != AUTHORITY",
                "EVIDENCE_REFERENCE != EVIDENCE_VERIFICATION",
                "HUMAN_AGENCY > MACHINE_AUTHORITY",
            ],
        }


def effective_friction(policy: RuntimePolicy, operation: str) -> float:
    rule = policy.operations.get(operation)
    if rule is None:
        return 1.0
    return max(policy.default_friction, rule.criticality)


def required_controls_for(policy: RuntimePolicy, operation: str) -> tuple[str, ...]:
    rule = policy.operations.get(operation)
    if rule is None:
        return ("human_signature", "isolated_verification", "two_party_review")
    friction = effective_friction(policy, operation)
    required = set(rule.controls)
    if friction >= policy.high_friction_threshold:
        required.update(("human_signature", "isolated_verification"))
    if friction >= policy.critical_threshold:
        required.add("two_party_review")
    return tuple(sorted(required))


def assess_operation(
    policy: RuntimePolicy,
    operation: str,
    *,
    evidence: Mapping[str, str] | None = None,
    authorization: AuthorizationToken | None = None,
    public_key_b64: str | None = None,
    project: str = "",
    subject_digest: str = "",
) -> Assessment:
    evidence = evidence or {}
    rule = policy.operations.get(operation)
    if rule is None:
        return Assessment(
            operation=operation,
            allowed=False,
            mode=FrictionMode.HIGH_FRICTION,
            criticality=1.0,
            friction=1.0,
            required_controls=required_controls_for(policy, operation),
            satisfied_controls=(),
            failures=("UNKNOWN_OPERATION_FAIL_CLOSED",),
            policy_digest=policy.digest,
        )

    friction = effective_friction(policy, operation)
    mode = (
        FrictionMode.HIGH_FRICTION
        if friction >= policy.high_friction_threshold
        else FrictionMode.LOW_FRICTION
    )
    required = set(required_controls_for(policy, operation))
    failures: list[str] = []
    satisfied: set[str] = set()

    for control in sorted(required - {"human_signature"}):
        value = evidence.get(control, "").strip()
        if not value:
            failures.append(f"EVIDENCE_REQUIRED:{control}")
        elif not _is_sha256_reference(value):
            failures.append(f"EVIDENCE_REFERENCE_INVALID:{control}")
        else:
            satisfied.add(control)

    if "human_signature" in required:
        if authorization is None:
            failures.append("AUTHORIZATION_REQUIRED")
        elif not public_key_b64:
            failures.append("AUTHORIZATION_PUBLIC_KEY_REQUIRED")
        elif not project:
            failures.append("AUTHORIZATION_PROJECT_REQUIRED")
        elif not subject_digest:
            failures.append("AUTHORIZATION_SUBJECT_DIGEST_REQUIRED")
        else:
            ok, auth_failures = verify_authorization(
                authorization,
                public_key_b64=public_key_b64,
                operation=operation,
                project=project,
                policy_digest=policy.digest,
                subject_digest=subject_digest,
                required_controls=required,
            )
            if ok:
                satisfied.add("human_signature")
            else:
                failures.extend(auth_failures)

    return Assessment(
        operation=operation,
        allowed=not failures,
        mode=mode,
        criticality=rule.criticality,
        friction=friction,
        required_controls=tuple(sorted(required)),
        satisfied_controls=tuple(sorted(satisfied)),
        failures=tuple(dict.fromkeys(failures)),
        policy_digest=policy.digest,
    )


def require_transition(current: VerificationState, target: VerificationState) -> None:
    if target not in _ALLOWED_TRANSITIONS[current]:
        raise RuntimePolicyError(
            f"invalid verification transition: {current.value} -> {target.value}; "
            "verification states may advance only one evidence-bearing step at a time"
        )


def _validate_principles(principles: Mapping[str, Any]) -> None:
    required_false = (
        "pattern_is_proof",
        "profile_is_person",
        "model_is_mind",
        "prediction_is_destiny",
    )
    for key in required_false:
        if principles.get(key) is not False:
            raise RuntimePolicyError(f"{key} must be false")
    if principles.get("human_agency_over_machine_authority") is not True:
        raise RuntimePolicyError("human_agency_over_machine_authority must be true")


def _bounded(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RuntimePolicyError(f"{field} must be numeric")
    result = float(value)
    if not 0.0 <= result <= 1.0:
        raise RuntimePolicyError(f"{field} must be between 0 and 1")
    return result


def _is_sha256_reference(value: str) -> bool:
    """Return True only for a canonical content-addressed evidence reference."""
    if not value.startswith("sha256:"):
        return False
    digest = value[7:]
    return (
        len(digest) == 64
        and digest == digest.lower()
        and all(char in "0123456789abcdef" for char in digest)
    )
