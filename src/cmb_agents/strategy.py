"""Bounded chess-style strategy engine for CMB Steward agents.

The engine models repository maintenance as a position search:

POSITION -> LEGAL MOVES -> PRUNE -> RED TEAM -> EVALUATE -> PRINCIPAL VARIATION

It never executes model-provided shell commands and never writes repository files.
Mutation remains delegated to the existing bounded Steward repair path.

PATTERN != PROOF
RISK_SCORE != INTENT
CONFIDENCE != EVIDENCE
MACHINE_CAN_PROPOSE != MACHINE_CAN_MERGE
HUMAN_AGENCY > MACHINE_AUTHORITY
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Final

from cmb_agents.model_gateway import ModelGatewayError, model_available, request_json

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10
    import tomli as tomllib  # type: ignore[no-redef]

def _looks_like_repository_root(path: Path) -> bool:
    return (
        (path / "pyproject.toml").is_file()
        and (path / "strategy/cmb_strategy.toml").is_file()
        and (path / "src/cmb_agents/strategy.py").is_file()
    )


def _resolve_repository_root() -> Path:
    candidates: list[Path] = []
    for variable in ("CMB_REPOSITORY_ROOT", "GITHUB_WORKSPACE"):
        raw = os.environ.get(variable)
        if raw:
            candidates.append(Path(raw))

    candidates.extend((Path.cwd(), Path(__file__).resolve().parents[2]))

    seen: set[Path] = set()
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            continue
        if resolved in seen:
            continue
        seen.add(resolved)
        if _looks_like_repository_root(resolved):
            return resolved

    return Path(__file__).resolve().parents[2]


ROOT: Final[Path] = _resolve_repository_root()

DIMENSIONS: Final[tuple[str, ...]] = (
    "correctness",
    "security",
    "reproducibility",
    "interoperability",
    "provenance",
    "maintainability",
    "accessibility",
    "reversibility",
    "evidence_strength",
    "human_authority_preservation",
)

PROTECTED_PREFIXES: Final[tuple[str, ...]] = (
    ".github/",
    "tests/",
    "scripts/",
    "schemas/",
    "machine/",
    "agents/",
    "policy/",
    "receipts/",
)

PROTECTED_EXACT: Final[set[str]] = {
    "LICENSE",
    "NOTICE",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "pyproject.toml",
    "cmb.toml",
    "strategy/cmb_strategy.toml",
    "src/cmb_agents/steward.py",
    "src/cmb_agents/strategy.py",
}


class StrategyError(RuntimeError):
    """Raised when strategy input or authority boundaries are invalid."""


@dataclass(frozen=True, slots=True)
class Position:
    commit: str
    branch: str
    state_hash: str
    audit_ok: bool
    failed_checks: tuple[str, ...]
    evidence_packet_count: int
    latest_changed_paths: tuple[str, ...]
    stabilization_mode: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "failed_checks": list(self.failed_checks),
            "latest_changed_paths": list(self.latest_changed_paths),
        }


@dataclass(frozen=True, slots=True)
class CandidateMove:
    move_id: str
    role: str
    title: str
    rationale: str
    target_paths: tuple[str, ...]
    action: str
    gains: dict[str, float]
    risk: float
    complexity: float
    reversible: bool
    requires_human: bool
    evidence: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "target_paths": list(self.target_paths),
            "evidence": list(self.evidence),
        }


@dataclass(frozen=True, slots=True)
class Refutation:
    move_id: str
    survives: bool
    reason: str
    risk_delta: float
    requires_human: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class EvaluatedMove:
    candidate: CandidateMove
    refutation: Refutation
    pruned: bool
    prune_reason: str | None
    score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate": self.candidate.to_dict(),
            "refutation": self.refutation.to_dict(),
            "pruned": self.pruned,
            "prune_reason": self.prune_reason,
            "score": self.score,
        }


@dataclass(frozen=True, slots=True)
class StrategyReport:
    schema_version: str
    position: Position
    evaluated_moves: tuple[EvaluatedMove, ...]
    principal_variation: tuple[str, ...]
    selected_move_id: str | None
    selected_move_title: str | None
    selected_move_action: str | None
    selected_move_requires_human: bool
    model_used: bool
    model_error: str | None = None
    boundaries: tuple[str, ...] = field(
        default=(
            "PATTERN != PROOF",
            "RISK_SCORE != INTENT",
            "CONFIDENCE != EVIDENCE",
            "TEST_PASS != CORRECTNESS",
            "MACHINE_CAN_PROPOSE != MACHINE_CAN_MERGE",
            "HUMAN_AGENCY > MACHINE_AUTHORITY",
        )
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "position": self.position.to_dict(),
            "evaluated_moves": [item.to_dict() for item in self.evaluated_moves],
            "principal_variation": list(self.principal_variation),
            "selected_move_id": self.selected_move_id,
            "selected_move_title": self.selected_move_title,
            "selected_move_action": self.selected_move_action,
            "selected_move_requires_human": self.selected_move_requires_human,
            "model_used": self.model_used,
            "model_error": self.model_error,
            "boundaries": list(self.boundaries),
        }


def _run_git(args: list[str]) -> str:
    process = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=60,
    )
    if process.returncode != 0:
        raise StrategyError(process.stderr.strip() or f"git command failed: {args!r}")
    return process.stdout.strip()


def load_policy(path: Path) -> dict[str, Any]:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    authority = data.get("authority", {})
    invariants = data.get("invariants", {})

    required_false = (
        "machine_may_merge",
        "machine_may_release",
        "machine_may_sign",
        "machine_may_expand_own_authority",
    )
    if any(authority.get(key) is not False for key in required_false):
        raise StrategyError("strategy policy grants prohibited machine authority")
    if authority.get("human_final_authority") is not True:
        raise StrategyError("strategy policy must preserve human final authority")

    invariant_requirements = {
        "pattern_is_proof": False,
        "profile_is_person": False,
        "model_is_mind": False,
        "prediction_is_destiny": False,
        "risk_score_is_intent": False,
        "human_agency_over_machine_authority": True,
    }
    for key, expected in invariant_requirements.items():
        if invariants.get(key) is not expected:
            raise StrategyError(f"invalid strategy invariant: {key}")

    return data


def _normalize_path(path: str) -> str:
    candidate = Path(path)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise StrategyError(f"unsafe path: {path!r}")
    normalized = candidate.as_posix().lstrip("./")
    if not normalized:
        raise StrategyError("empty path")
    return normalized


def is_autonomous_target(path: str) -> bool:
    try:
        normalized = _normalize_path(path)
    except StrategyError:
        return False
    if normalized in PROTECTED_EXACT:
        return False
    if any(normalized.startswith(prefix) for prefix in PROTECTED_PREFIXES):
        return False
    return normalized == "README.md" or normalized.startswith(
        ("src/cmb_glitch8/", "src/cmb_agents/", "src/cmb_machine/", "docs/", "books/", "examples/")
    )


def _load_audit(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise StrategyError("audit report must be a JSON object")
    return data


def build_position(audit: dict[str, Any], *, stabilization_mode: bool) -> Position:
    commit = _run_git(["rev-parse", "HEAD"])
    branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    latest_paths_raw = _run_git(["show", "--pretty=format:", "--name-only", "HEAD"])
    latest_paths = tuple(sorted({line.strip() for line in latest_paths_raw.splitlines() if line.strip()}))

    checks = audit.get("checks", [])
    failed = tuple(
        f"{item.get('role', 'UNKNOWN')}:{item.get('name', 'unknown')}"
        for item in checks
        if isinstance(item, dict) and not bool(item.get("ok"))
    )
    packets = audit.get("evidence_packets", [])
    audit_ok = bool(audit.get("ok"))

    canonical = json.dumps(
        {
            "commit": commit,
            "audit_ok": audit_ok,
            "failed_checks": failed,
            "latest_changed_paths": latest_paths,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    state_hash = "sha256:" + hashlib.sha256(canonical).hexdigest()

    return Position(
        commit=commit,
        branch=branch,
        state_hash=state_hash,
        audit_ok=audit_ok,
        failed_checks=failed,
        evidence_packet_count=len(packets) if isinstance(packets, list) else 0,
        latest_changed_paths=latest_paths,
        stabilization_mode=stabilization_mode,
    )


def _bounded_score(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, number))


def _candidate_from_dict(item: dict[str, Any]) -> CandidateMove:
    gains_raw = item.get("gains", {})
    gains = {dimension: _bounded_score(gains_raw.get(dimension, 0.0)) for dimension in DIMENSIONS}

    target_paths = tuple(_normalize_path(str(path)) for path in item.get("target_paths", []))
    evidence = tuple(str(value) for value in item.get("evidence", []))

    return CandidateMove(
        move_id=str(item["move_id"]),
        role=str(item["role"]).upper(),
        title=str(item["title"]),
        rationale=str(item["rationale"]),
        target_paths=target_paths,
        action=str(item["action"]),
        gains=gains,
        risk=_bounded_score(item.get("risk", 0.5)),
        complexity=_bounded_score(item.get("complexity", 0.5)),
        reversible=bool(item.get("reversible", False)),
        requires_human=bool(item.get("requires_human", True)),
        evidence=evidence,
    )


def _refutation_from_dict(item: dict[str, Any]) -> Refutation:
    return Refutation(
        move_id=str(item["move_id"]),
        survives=bool(item.get("survives", False)),
        reason=str(item.get("reason", "")),
        risk_delta=_bounded_score(item.get("risk_delta", 0.0)),
        requires_human=bool(item.get("requires_human", True)),
    )


def hard_prune(candidate: CandidateMove, refutation: Refutation, policy: dict[str, Any]) -> str | None:
    if candidate.role not in {"TACTICIAN", "STRATEGIST", "SECURITY", "RECOVERY"}:
        return "unknown agent role"

    allowed_actions = set(policy.get("moves", {}).get("allowed_actions", []))
    if candidate.action not in allowed_actions:
        return "action is outside the legal move set"

    if not refutation.survives:
        return "red-team refutation rejected the move"

    if candidate.action == "autonomous_repair":
        if candidate.requires_human or refutation.requires_human:
            return "autonomous repair cannot require human-only authority"
        if not candidate.reversible:
            return "autonomous repair must be reversible"
        if not candidate.target_paths:
            return "autonomous repair requires explicit target paths"
        if any(not is_autonomous_target(path) for path in candidate.target_paths):
            return "autonomous repair targets a protected path"

    if candidate.gains["human_authority_preservation"] < 1.0:
        return "human authority preservation is below the hard threshold"

    if candidate.risk + refutation.risk_delta > float(policy["evaluation"]["max_combined_risk"]):
        return "combined risk exceeds policy threshold"

    return None


def evaluate(candidate: CandidateMove, refutation: Refutation, policy: dict[str, Any]) -> float:
    weights = policy["evaluation"]["weights"]
    gain_score = sum(float(weights.get(key, 0.0)) * candidate.gains[key] for key in DIMENSIONS)
    penalty = (
        float(policy["evaluation"]["risk_penalty"]) * (candidate.risk + refutation.risk_delta)
        + float(policy["evaluation"]["complexity_penalty"]) * candidate.complexity
    )
    if not candidate.reversible:
        penalty += float(policy["evaluation"]["irreversibility_penalty"])
    return round(gain_score - penalty, 6)


def _responses_json(
    *,
    api_key: str,
    model: str,
    instructions: str,
    input_payload: dict[str, Any],
    schema_name: str,
    schema: dict[str, Any],
) -> dict[str, Any]:
    try:
        result = request_json(
            instructions=instructions,
            input_payload=input_payload,
            schema_name=schema_name,
            schema=schema,
            openai_api_key=api_key,
            openai_model=model,
            max_output_tokens=8000,
            timeout=180,
        )
    except ModelGatewayError as exc:
        raise StrategyError(str(exc)) from exc
    return result.payload


def _candidate_schema(max_moves: int) -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["moves"],
        "properties": {
            "moves": {
                "type": "array",
                "minItems": 1,
                "maxItems": max_moves,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "move_id",
                        "role",
                        "title",
                        "rationale",
                        "target_paths",
                        "action",
                        "gains",
                        "risk",
                        "complexity",
                        "reversible",
                        "requires_human",
                        "evidence",
                    ],
                    "properties": {
                        "move_id": {"type": "string", "minLength": 1, "maxLength": 80},
                        "role": {"enum": ["TACTICIAN", "STRATEGIST", "SECURITY", "RECOVERY"]},
                        "title": {"type": "string", "minLength": 1, "maxLength": 160},
                        "rationale": {"type": "string", "minLength": 1, "maxLength": 1600},
                        "target_paths": {
                            "type": "array",
                            "maxItems": 8,
                            "items": {"type": "string", "minLength": 1, "maxLength": 240},
                        },
                        "action": {"type": "string", "minLength": 1, "maxLength": 80},
                        "gains": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": list(DIMENSIONS),
                            "properties": {
                                key: {"type": "number", "minimum": 0.0, "maximum": 1.0}
                                for key in DIMENSIONS
                            },
                        },
                        "risk": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                        "complexity": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                        "reversible": {"type": "boolean"},
                        "requires_human": {"type": "boolean"},
                        "evidence": {
                            "type": "array",
                            "maxItems": 12,
                            "items": {"type": "string", "maxLength": 400},
                        },
                    },
                },
            }
        },
    }


def _review_schema(max_moves: int) -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["refutations"],
        "properties": {
            "refutations": {
                "type": "array",
                "minItems": 1,
                "maxItems": max_moves,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["move_id", "survives", "reason", "risk_delta", "requires_human"],
                    "properties": {
                        "move_id": {"type": "string", "minLength": 1, "maxLength": 80},
                        "survives": {"type": "boolean"},
                        "reason": {"type": "string", "minLength": 1, "maxLength": 1200},
                        "risk_delta": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                        "requires_human": {"type": "boolean"},
                    },
                },
            }
        },
    }


def request_candidate_moves(
    position: Position,
    audit: dict[str, Any],
    policy: dict[str, Any],
    *,
    api_key: str,
    model: str,
) -> tuple[CandidateMove, ...]:
    max_moves = int(policy["search"]["max_candidate_moves"])
    input_payload = {
        "position": position.to_dict(),
        "failed_checks": [
            {
                "role": item.get("role"),
                "name": item.get("name"),
                "output": str(item.get("output", ""))[-2500:],
            }
            for item in audit.get("checks", [])
            if isinstance(item, dict) and not bool(item.get("ok"))
        ],
        "legal_actions": policy["moves"]["allowed_actions"],
        "stabilization_rule": (
            "During stabilization, prefer concrete Recovery and correctness work. "
            "Do not propose a new protocol family, CLI, package, authority class, payment rail, or interoperability target."
        ),
        "authority_rule": (
            "Agents may observe, evaluate, propose, test, and recommend. "
            "They may not merge, release, sign, change security authority, or expand their own permissions."
        ),
        "principles": [
            "PATTERN != PROOF",
            "RISK_SCORE != INTENT",
            "CONFIDENCE != EVIDENCE",
            "MACHINE_CAN_PROPOSE != MACHINE_CAN_MERGE",
            "HUMAN_AGENCY > MACHINE_AUTHORITY",
        ],
    }
    result = _responses_json(
        api_key=api_key,
        model=model,
        instructions=(
            "Act as four separated CMB chess-engine roles: TACTICIAN, STRATEGIST, SECURITY, and RECOVERY. "
            "Generate only evidence-linked candidate moves for the current repository position. "
            "A move is a bounded engineering recommendation, not a claim of human intent. "
            "Prefer minimum reversible changes. Never propose weakening tests or bypassing human authority."
        ),
        input_payload=input_payload,
        schema_name="cmb_strategy_candidate_moves",
        schema=_candidate_schema(max_moves),
    )
    return tuple(_candidate_from_dict(item) for item in result["moves"])


def request_refutations(
    position: Position,
    candidates: tuple[CandidateMove, ...],
    policy: dict[str, Any],
    *,
    api_key: str,
    model: str,
) -> tuple[Refutation, ...]:
    max_moves = int(policy["search"]["max_candidate_moves"])
    result = _responses_json(
        api_key=api_key,
        model=model,
        instructions=(
            "Act only as the CMB RED_TEAM and REVIEWER. Try to refute each proposed move. "
            "Reject unsupported scope expansion, protected-path autonomous mutation, authority escalation, "
            "irreversible changes, security regressions, and claims stronger than the evidence. "
            "Do not reward a move merely because the proposer sounded confident."
        ),
        input_payload={
            "position": position.to_dict(),
            "moves": [candidate.to_dict() for candidate in candidates],
            "hard_boundaries": [
                "PATTERN != PROOF",
                "RISK_SCORE != INTENT",
                "CONFIDENCE != EVIDENCE",
                "TEST_PASS != CORRECTNESS",
                "MACHINE_CAN_PROPOSE != MACHINE_CAN_MERGE",
                "HUMAN_AGENCY > MACHINE_AUTHORITY",
            ],
        },
        schema_name="cmb_strategy_refutations",
        schema=_review_schema(max_moves),
    )
    return tuple(_refutation_from_dict(item) for item in result["refutations"])


def deterministic_moves(position: Position) -> tuple[CandidateMove, ...]:
    if position.audit_ok:
        return ()
    return (
        CandidateMove(
            move_id="RECOVERY-FAILURES-1",
            role="RECOVERY",
            title="Repair the smallest concrete failing audit",
            rationale=(
                "The position contains deterministic failures. Search the smallest reversible repair "
                "before considering feature work."
            ),
            target_paths=(),
            action="human_review",
            gains={
                **{key: 0.0 for key in DIMENSIONS},
                "correctness": 0.9,
                "reproducibility": 0.8,
                "reversibility": 1.0,
                "evidence_strength": 0.9,
                "human_authority_preservation": 1.0,
            },
            risk=0.15,
            complexity=0.2,
            reversible=True,
            requires_human=True,
            evidence=position.failed_checks,
        ),
    )


def analyze(
    audit: dict[str, Any],
    policy: dict[str, Any],
    *,
    api_key: str = "",
    model: str = "",
) -> StrategyReport:
    mode = str(policy.get("engine", {}).get("mode", "stabilization"))
    position = build_position(audit, stabilization_mode=mode == "stabilization")
    analysis_when_clean = bool(policy["search"].get("analysis_when_clean", False))

    model_used = bool(
        model_available(openai_api_key=api_key, openai_model=model)
        and (not position.audit_ok or analysis_when_clean)
    )
    model_error: str | None = None
    if model_used:
        try:
            candidates = request_candidate_moves(position, audit, policy, api_key=api_key, model=model)
            refutations = request_refutations(position, candidates, policy, api_key=api_key, model=model)
        except StrategyError as exc:
            model_used = False
            model_error = str(exc)
            candidates = deterministic_moves(position)
            refutations = tuple(
                Refutation(
                    move_id=item.move_id,
                    survives=True,
                    reason="AI search unavailable. Deterministic Recovery preserves human review.",
                    risk_delta=0.0,
                    requires_human=True,
                )
                for item in candidates
            )
    else:
        candidates = deterministic_moves(position)
        refutations = tuple(
            Refutation(
                move_id=item.move_id,
                survives=True,
                reason="Deterministic fallback move preserves human review.",
                risk_delta=0.0,
                requires_human=True,
            )
            for item in candidates
        )

    refutation_map = {item.move_id: item for item in refutations}
    evaluated: list[EvaluatedMove] = []
    for candidate in candidates:
        refutation = refutation_map.get(
            candidate.move_id,
            Refutation(
                move_id=candidate.move_id,
                survives=False,
                reason="No matching red-team review was returned.",
                risk_delta=1.0,
                requires_human=True,
            ),
        )
        prune_reason = hard_prune(candidate, refutation, policy)
        score = float("-inf") if prune_reason else evaluate(candidate, refutation, policy)
        evaluated.append(
            EvaluatedMove(
                candidate=candidate,
                refutation=refutation,
                pruned=prune_reason is not None,
                prune_reason=prune_reason,
                score=score,
            )
        )

    survivors = sorted(
        (item for item in evaluated if not item.pruned),
        key=lambda item: (-item.score, item.candidate.move_id),
    )
    selected = survivors[0] if survivors else None
    principal_variation = tuple(item.candidate.move_id for item in survivors[:3])

    return StrategyReport(
        schema_version="cmb.strategy-report.v1",
        position=position,
        evaluated_moves=tuple(evaluated),
        principal_variation=principal_variation,
        selected_move_id=selected.candidate.move_id if selected else None,
        selected_move_title=selected.candidate.title if selected else None,
        selected_move_action=selected.candidate.action if selected else None,
        selected_move_requires_human=(
            selected.candidate.requires_human or selected.refutation.requires_human
            if selected
            else False
        ),
        model_used=model_used,
        model_error=model_error,
    )


def _write_report(path: Path, report: StrategyReport) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _write_summary(path: Path, report: StrategyReport) -> None:
    selected = report.selected_move_title or "No legal move selected"
    lines = [
        "# CMB Strategy Engine",
        "",
        f"Position: `{report.position.state_hash}`",
        f"Audit: {'PASS' if report.position.audit_ok else 'ATTENTION'}",
        f"Model used: {'yes' if report.model_used else 'no'}",
        f"Model fallback: {report.model_error or 'none'}",
        f"Selected move: **{selected}**",
        "",
        "## Principal variation",
        "",
    ]
    if report.principal_variation:
        lines.extend(f"{index}. `{move_id}`" for index, move_id in enumerate(report.principal_variation, start=1))
    else:
        lines.append("No move. Preserve the current position.")
    lines.extend(
        [
            "",
            "PATTERN != PROOF",
            "",
            "RISK_SCORE != INTENT",
            "",
            "MACHINE_CAN_PROPOSE != MACHINE_CAN_MERGE",
            "",
            "HUMAN_AGENCY > MACHINE_AUTHORITY",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--policy", type=Path, default=Path("strategy/cmb_strategy.toml"))
    parser.add_argument("--output", type=Path, default=Path(".cmb-agent/strategy.json"))
    parser.add_argument("--summary", type=Path, default=Path(".cmb-agent/strategy.md"))
    args = parser.parse_args(argv)

    try:
        policy = load_policy(args.policy)
        audit = _load_audit(args.audit)
        report = analyze(
            audit,
            policy,
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            model=os.environ.get("CMB_AGENT_MODEL", ""),
        )
        _write_report(args.output, report)
        _write_summary(args.summary, report)
        if report.selected_move_title:
            print(f"Best move: {report.selected_move_title}")
        else:
            print("Best move: preserve the current position")
        print(f"Principal variation: {', '.join(report.principal_variation) or 'none'}")
        return 0
    except (OSError, StrategyError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        print(f"CMB Strategy Engine failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
