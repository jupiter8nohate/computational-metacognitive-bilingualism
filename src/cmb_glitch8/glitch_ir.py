"""Reference GLITCH-IR v1 semantic evaluator."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

GLITCH_IR_SCHEMA_VERSION: Final[str] = "glitch-ir.v1"
GLITCH_IR_PROTOCOL: Final[str] = "GLITCH-IR"
GLITCH_IR_PROTOCOL_VERSION: Final[str] = "1.0.0"


class GlitchIRError(ValueError):
    """Raised when a GLITCH-IR vector is malformed."""


@dataclass(frozen=True, slots=True)
class GlitchIRResult:
    vector_id: str
    protocol_version: str
    verdict: str
    operator: str
    state: str

    def canonical_line(self) -> str:
        return "|".join(
            (
                self.vector_id,
                self.protocol_version,
                self.verdict,
                self.operator,
                self.state,
            )
        ) + "\n"


_REQUIRED_ROOT = {
    "schema_version",
    "protocol",
    "protocol_version",
    "vector_id",
    "registry_id",
    "canonical_name",
    "claim",
    "human_review",
    "expected_result",
    "invariants",
}


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise GlitchIRError(f"{field} must be a non-empty string")
    return value


def validate_vector(vector: dict[str, Any]) -> None:
    if set(vector) != _REQUIRED_ROOT:
        missing = sorted(_REQUIRED_ROOT - set(vector))
        extra = sorted(set(vector) - _REQUIRED_ROOT)
        raise GlitchIRError(f"invalid root fields: missing={missing}, extra={extra}")

    if vector["schema_version"] != GLITCH_IR_SCHEMA_VERSION:
        raise GlitchIRError("unsupported GLITCH-IR schema version")
    if vector["protocol"] != GLITCH_IR_PROTOCOL:
        raise GlitchIRError("unsupported GLITCH-IR protocol")
    if vector["protocol_version"] != GLITCH_IR_PROTOCOL_VERSION:
        raise GlitchIRError("unsupported GLITCH-IR protocol version")

    _require_string(vector["vector_id"], "vector_id")
    _require_string(vector["registry_id"], "registry_id")
    _require_string(vector["canonical_name"], "canonical_name")

    claim = vector["claim"]
    if not isinstance(claim, dict) or set(claim) != {
        "verification_label",
        "evidence",
        "source",
    }:
        raise GlitchIRError("claim must contain only verification_label, evidence, and source")

    if claim["verification_label"] not in {"PRESENT", "ABSENT"}:
        raise GlitchIRError("invalid verification_label")
    if claim["evidence"] not in {"PRESENT", "ABSENT", "UNKNOWN"}:
        raise GlitchIRError("invalid evidence state")
    if claim["source"] not in {"KNOWN", "UNKNOWN"}:
        raise GlitchIRError("invalid source state")

    expected = vector["expected_result"]
    if not isinstance(expected, dict) or set(expected) != {"verdict", "operator", "state"}:
        raise GlitchIRError("expected_result must contain verdict, operator, and state")

    for field in ("verdict", "operator", "state"):
        _require_string(expected[field], f"expected_result.{field}")

    invariants = vector["invariants"]
    if (
        not isinstance(invariants, list)
        or not invariants
        or any(not isinstance(value, str) or not value for value in invariants)
        or len(set(invariants)) != len(invariants)
    ):
        raise GlitchIRError("invariants must be a non-empty unique string list")


def load_vector(path: Path | str) -> dict[str, Any]:
    source = Path(path)
    try:
        value = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise GlitchIRError(f"cannot read GLITCH-IR vector {source}: {exc}") from exc
    if not isinstance(value, dict):
        raise GlitchIRError("GLITCH-IR vector root must be an object")
    validate_vector(value)
    return value


def evaluate_vector(vector: dict[str, Any]) -> GlitchIRResult:
    validate_vector(vector)
    claim = vector["claim"]

    if claim["verification_label"] == "PRESENT" and claim["evidence"] != "PRESENT":
        verdict, operator, state = "BACKTRACE", "GLT-0036", "CONTESTED"
    elif claim["source"] == "UNKNOWN":
        verdict, operator, state = "BACKTRACE", "GLT-0036", "CONTESTED"
    else:
        verdict, operator, state = "ACCEPT", "NONE", "ACCEPTED"

    return GlitchIRResult(
        vector_id=vector["vector_id"],
        protocol_version=vector["protocol_version"],
        verdict=verdict,
        operator=operator,
        state=state,
    )


def assert_expected_result(vector: dict[str, Any], result: GlitchIRResult) -> None:
    expected = vector["expected_result"]
    actual = {
        "verdict": result.verdict,
        "operator": result.operator,
        "state": result.state,
    }
    if actual != expected:
        raise GlitchIRError(f"semantic drift: expected={expected}, actual={actual}")
