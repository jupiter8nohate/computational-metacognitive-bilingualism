"""Deterministic claim-to-control traceability validation for CMB.

The validator keeps philosophical language separate from executable enforcement.

SYMBOLIC -> DECLARED -> ENFORCED -> VERIFIED

A VERIFIED claim must point to an enforcement control and a test control.
A stale file path or missing anchor fails validation.

PATTERN != PROOF
TEST_PASS != CORRECTNESS
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Final

SCHEMA_VERSION: Final[str] = "cmb.claim-control.v1"
MATURITIES: Final[tuple[str, ...]] = ("symbolic", "declared", "enforced", "verified")
CONTROL_KINDS: Final[set[str]] = {"doc", "policy", "validator", "runtime", "test", "workflow"}
ENFORCEMENT_KINDS: Final[set[str]] = {"validator", "runtime"}


class ClaimControlError(RuntimeError):
    """Raised when a claim-to-control manifest is invalid or stale."""


def _safe_relative_path(raw: Any) -> Path:
    value = str(raw)
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ClaimControlError(f"unsafe control path: {value!r}")
    normalized = candidate.as_posix().lstrip("./")
    if not normalized:
        raise ClaimControlError("control path must not be empty")
    return Path(normalized)


def _require_text(mapping: dict[str, Any], key: str, context: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ClaimControlError(f"{context}.{key} must be a non-empty string")
    return value.strip()


def _validate_control(control: Any, *, root: Path, context: str) -> str:
    if not isinstance(control, dict):
        raise ClaimControlError(f"{context} must be an object")

    kind = _require_text(control, "kind", context)
    if kind not in CONTROL_KINDS:
        raise ClaimControlError(f"{context}.kind is unsupported: {kind}")

    relative_path = _safe_relative_path(control.get("path"))
    anchor = _require_text(control, "anchor", context)
    target = root / relative_path

    if not target.is_file():
        raise ClaimControlError(f"{context} references missing file: {relative_path.as_posix()}")

    content = target.read_text(encoding="utf-8")
    if anchor not in content:
        raise ClaimControlError(
            f"{context} anchor not found in {relative_path.as_posix()}: {anchor!r}"
        )
    return kind


def validate_manifest(data: Any, *, root: Path | None = None) -> dict[str, Any]:
    """Validate structure, maturity semantics, file references, and anchors."""
    root = (root or Path.cwd()).resolve()
    if not isinstance(data, dict):
        raise ClaimControlError("manifest must be a JSON object")
    if data.get("schema_version") != SCHEMA_VERSION:
        raise ClaimControlError(f"schema_version must equal {SCHEMA_VERSION!r}")

    claims = data.get("claims")
    if not isinstance(claims, list) or not claims:
        raise ClaimControlError("claims must be a non-empty array")

    seen_ids: set[str] = set()
    seen_expressions: set[str] = set()
    counts: Counter[str] = Counter()

    for index, claim in enumerate(claims):
        context = f"claims[{index}]"
        if not isinstance(claim, dict):
            raise ClaimControlError(f"{context} must be an object")

        claim_id = _require_text(claim, "claim_id", context)
        expression = _require_text(claim, "expression", context)
        maturity = _require_text(claim, "maturity", context)
        _require_text(claim, "meaning", context)

        if claim_id in seen_ids:
            raise ClaimControlError(f"duplicate claim_id: {claim_id}")
        if expression in seen_expressions:
            raise ClaimControlError(f"duplicate claim expression: {expression}")
        if maturity not in MATURITIES:
            raise ClaimControlError(f"{context}.maturity is unsupported: {maturity}")

        seen_ids.add(claim_id)
        seen_expressions.add(expression)
        counts[maturity] += 1

        controls = claim.get("controls", [])
        if not isinstance(controls, list):
            raise ClaimControlError(f"{context}.controls must be an array")

        kinds = {
            _validate_control(control, root=root, context=f"{context}.controls[{control_index}]")
            for control_index, control in enumerate(controls)
        }

        if maturity in {"declared", "enforced", "verified"} and not ({"policy", "doc"} & kinds):
            raise ClaimControlError(
                f"{claim_id} is {maturity} but has no policy or documentation declaration"
            )
        if maturity in {"enforced", "verified"} and not (ENFORCEMENT_KINDS & kinds):
            raise ClaimControlError(
                f"{claim_id} is {maturity} but has no runtime or validator enforcement"
            )
        if maturity == "verified" and "test" not in kinds:
            raise ClaimControlError(f"{claim_id} is verified but has no test control")

    return {
        "schema_version": SCHEMA_VERSION,
        "claim_count": len(claims),
        "maturity_counts": {name: counts.get(name, 0) for name in MATURITIES},
    }


def validate_manifest_file(path: Path, *, root: Path | None = None) -> dict[str, Any]:
    resolved_path = path.resolve()
    if root is None:
        root = resolved_path.parent.parent if resolved_path.parent.name == "machine" else Path.cwd()
    root = root.resolve()
    try:
        data = json.loads(resolved_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ClaimControlError(f"unable to read claim-control manifest: {exc}") from exc
    return validate_manifest(data, root=root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("machine/claim-control-traceability.v1.json"),
    )
    args = parser.parse_args(argv)

    try:
        summary = validate_manifest_file(args.manifest)
    except ClaimControlError as exc:
        print(f"CMB claim-control gate failed: {exc}")
        return 1

    counts = summary["maturity_counts"]
    print(
        "CMB claim-control gate passed: "
        f"{summary['claim_count']} claims "
        f"(symbolic={counts['symbolic']}, declared={counts['declared']}, "
        f"enforced={counts['enforced']}, verified={counts['verified']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
