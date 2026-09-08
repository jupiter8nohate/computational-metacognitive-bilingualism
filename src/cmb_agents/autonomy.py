"""Deterministic autonomy arbiter for bounded CMB repository agents.

The arbiter sits between strategy selection and mutation. It does not generate edits,
execute model-provided commands, merge pull requests, publish releases, or change
repository authority. Its only job is to decide whether the existing Steward may
attempt a bounded repair for a concrete repository failure.

POSITION -> STRATEGY -> AUTONOMY_ARBITER -> STEWARD -> VERIFY -> DRAFT_PR -> HUMAN

SCORE != PERMISSION
AGENT_CAN_PROPOSE != AGENT_CAN_MERGE
HUMAN_AGENCY > MACHINE_AUTHORITY
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Final

from cmb_agents.strategy import StrategyError, is_autonomous_target, load_policy

SCHEMA_VERSION: Final[str] = "cmb.autonomy-decision.v1"

BOUNDARIES: Final[tuple[str, ...]] = (
    "PATTERN != PROOF",
    "CONFIDENCE != EVIDENCE",
    "SCORE != PERMISSION",
    "SELF_REVIEW != INDEPENDENT_REVIEW",
    "AGENT_CAN_PROPOSE != AGENT_CAN_MERGE",
    "CAPABILITY != AUTHORITY",
    "HUMAN_AGENCY > MACHINE_AUTHORITY",
)


class AutonomyError(RuntimeError):
    """Raised when an autonomy input or authority invariant is invalid."""


@dataclass(frozen=True, slots=True)
class Decision:
    schema_version: str
    verdict: str
    should_repair: bool
    requires_human: bool
    selected_move_id: str | None
    selected_move_title: str | None
    selected_move_action: str | None
    selected_move_score: float | None
    reasons: tuple[str, ...]
    target_paths: tuple[str, ...] = ()
    boundaries: tuple[str, ...] = field(default=BOUNDARIES)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["reasons"] = list(self.reasons)
        payload["target_paths"] = list(self.target_paths)
        payload["boundaries"] = list(self.boundaries)
        return payload


def _load_json_object(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AutonomyError(f"cannot load JSON object from {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise AutonomyError(f"{path} must contain a JSON object")
    return data


def _selected_move(strategy_report: dict[str, Any]) -> dict[str, Any] | None:
    move_id = strategy_report.get("selected_move_id")
    if move_id is None:
        return None
    if not isinstance(move_id, str) or not move_id.strip():
        raise AutonomyError("selected_move_id must be a non-empty string or null")

    evaluated = strategy_report.get("evaluated_moves", [])
    if not isinstance(evaluated, list):
        raise AutonomyError("evaluated_moves must be a list")

    for item in evaluated:
        if not isinstance(item, dict):
            continue
        candidate = item.get("candidate")
        if isinstance(candidate, dict) and candidate.get("move_id") == move_id:
            return item

    raise AutonomyError(f"selected move {move_id!r} is missing from evaluated_moves")


def decide(
    audit: dict[str, Any],
    strategy_report: dict[str, Any],
    policy: dict[str, Any],
) -> Decision:
    authority = policy.get("authority", {})
    recovery = policy.get("recovery", {})
    moves_policy = policy.get("moves", {})

    if authority.get("machine_may_open_draft_pr") is not True:
        raise AutonomyError("policy must explicitly permit draft pull request proposals")
    if authority.get("human_final_authority") is not True:
        raise AutonomyError("policy must preserve human final authority")
    if recovery.get("draft_pr_only") is not True:
        raise AutonomyError("recovery policy must remain draft-pr-only")
    if recovery.get("require_reversible_patch") is not True:
        raise AutonomyError("recovery policy must require reversible patches")
    if recovery.get("require_verification_after_change") is not True:
        raise AutonomyError("recovery policy must require post-change verification")

    allowed_actions_raw = moves_policy.get("allowed_actions", [])
    if not isinstance(allowed_actions_raw, list):
        raise AutonomyError("moves.allowed_actions must be a list")
    allowed_actions = {str(value) for value in allowed_actions_raw}

    selected = _selected_move(strategy_report)
    selected_id = strategy_report.get("selected_move_id")
    selected_title = strategy_report.get("selected_move_title")
    selected_action = strategy_report.get("selected_move_action")
    report_requires_human = bool(strategy_report.get("selected_move_requires_human"))

    audit_ok = audit.get("ok")
    if audit_ok is not True and audit_ok is not False:
        raise AutonomyError("audit.ok must be boolean")

    if selected is None:
        if audit_ok:
            return Decision(
                schema_version=SCHEMA_VERSION,
                verdict="PRESERVE_POSITION",
                should_repair=False,
                requires_human=False,
                selected_move_id=None,
                selected_move_title=None,
                selected_move_action=None,
                selected_move_score=None,
                reasons=("Deterministic audit is clean and no legal move was selected.",),
            )
        return Decision(
            schema_version=SCHEMA_VERSION,
            verdict="HUMAN_REVIEW",
            should_repair=False,
            requires_human=True,
            selected_move_id=None,
            selected_move_title=None,
            selected_move_action=None,
            selected_move_score=None,
            reasons=("Audit contains concrete failures but strategy selected no safe autonomous move.",),
        )

    candidate = selected.get("candidate")
    refutation = selected.get("refutation")
    if not isinstance(candidate, dict) or not isinstance(refutation, dict):
        raise AutonomyError("selected evaluated move must contain candidate and refutation objects")

    nested_action = candidate.get("action")
    if not isinstance(nested_action, str) or not nested_action:
        raise AutonomyError("selected candidate action must be a non-empty string")
    if selected_action != nested_action:
        raise AutonomyError("selected_move_action disagrees with selected candidate")
    if nested_action not in allowed_actions:
        raise AutonomyError(f"selected action is not allowed by policy: {nested_action}")

    score_raw = selected.get("score")
    if not isinstance(score_raw, (int, float)):
        raise AutonomyError("selected move score must be numeric")
    score = float(score_raw)

    target_paths_raw = candidate.get("target_paths", [])
    if not isinstance(target_paths_raw, list):
        raise AutonomyError("selected candidate target_paths must be a list")
    target_paths = tuple(str(path) for path in target_paths_raw)

    reasons: list[str] = []
    nested_requires_human = bool(candidate.get("requires_human")) or bool(
        refutation.get("requires_human")
    )
    requires_human = report_requires_human or nested_requires_human

    if bool(selected.get("pruned")):
        reasons.append("Selected move is marked pruned and cannot execute autonomously.")
        requires_human = True

    if refutation.get("survives") is not True:
        reasons.append("Red Team refutation did not permit the move.")
        requires_human = True

    if requires_human:
        reasons.append("The selected move crosses a human review boundary.")
        return Decision(
            schema_version=SCHEMA_VERSION,
            verdict="HUMAN_REVIEW",
            should_repair=False,
            requires_human=True,
            selected_move_id=str(selected_id),
            selected_move_title=str(selected_title) if selected_title is not None else None,
            selected_move_action=nested_action,
            selected_move_score=score,
            reasons=tuple(reasons),
            target_paths=target_paths,
        )

    if nested_action != "autonomous_repair":
        verdict = "PRESERVE_POSITION" if nested_action == "preserve_position" else "HUMAN_REVIEW"
        human = verdict == "HUMAN_REVIEW"
        reasons.append(f"Selected action {nested_action!r} is not an autonomous repair action.")
        return Decision(
            schema_version=SCHEMA_VERSION,
            verdict=verdict,
            should_repair=False,
            requires_human=human,
            selected_move_id=str(selected_id),
            selected_move_title=str(selected_title) if selected_title is not None else None,
            selected_move_action=nested_action,
            selected_move_score=score,
            reasons=tuple(reasons),
            target_paths=target_paths,
        )

    if audit_ok:
        return Decision(
            schema_version=SCHEMA_VERSION,
            verdict="PRESERVE_POSITION",
            should_repair=False,
            requires_human=False,
            selected_move_id=str(selected_id),
            selected_move_title=str(selected_title) if selected_title is not None else None,
            selected_move_action=nested_action,
            selected_move_score=score,
            reasons=("Audit is clean, so no autonomous mutation is justified.",),
            target_paths=target_paths,
        )

    if candidate.get("reversible") is not True:
        reasons.append("Autonomous repair candidate is not explicitly reversible.")

    unsafe_targets = tuple(path for path in target_paths if not is_autonomous_target(path))
    if unsafe_targets:
        reasons.append(
            "Autonomous repair targets protected paths: " + ", ".join(sorted(unsafe_targets))
        )

    gains = candidate.get("gains")
    if not isinstance(gains, dict):
        raise AutonomyError("selected candidate gains must be an object")
    authority_gain = gains.get("human_authority_preservation")
    if not isinstance(authority_gain, (int, float)) or float(authority_gain) < 1.0:
        reasons.append("Human authority preservation is below the hard autonomy threshold.")

    if reasons:
        return Decision(
            schema_version=SCHEMA_VERSION,
            verdict="HUMAN_REVIEW",
            should_repair=False,
            requires_human=True,
            selected_move_id=str(selected_id),
            selected_move_title=str(selected_title) if selected_title is not None else None,
            selected_move_action=nested_action,
            selected_move_score=score,
            reasons=tuple(reasons),
            target_paths=target_paths,
        )

    return Decision(
        schema_version=SCHEMA_VERSION,
        verdict="PROPOSE_REPAIR",
        should_repair=True,
        requires_human=False,
        selected_move_id=str(selected_id),
        selected_move_title=str(selected_title) if selected_title is not None else None,
        selected_move_action=nested_action,
        selected_move_score=score,
        reasons=(
            "Concrete audit failure exists.",
            "Strategy selected a reversible autonomous repair.",
            "Red Team did not refute the move.",
            "All target paths remain inside the bounded Steward mutation envelope.",
            "Human merge authority remains intact.",
        ),
        target_paths=target_paths,
    )


def _write_summary(path: Path, decision: Decision) -> None:
    score = "n/a" if decision.selected_move_score is None else f"{decision.selected_move_score:.4f}"
    targets = ", ".join(decision.target_paths) if decision.target_paths else "none"
    reasons = "\n".join(f"- {reason}" for reason in decision.reasons)
    boundaries = "\n".join(f"- `{item}`" for item in decision.boundaries)
    path.write_text(
        "\n".join(
            (
                "## CMB Autonomy Arbiter",
                "",
                f"- Verdict: **{decision.verdict}**",
                f"- Repair permitted: **{str(decision.should_repair).lower()}**",
                f"- Human review required: **{str(decision.requires_human).lower()}**",
                f"- Selected move: `{decision.selected_move_id or 'none'}`",
                f"- Selected action: `{decision.selected_move_action or 'none'}`",
                f"- Position score: `{score}`",
                f"- Targets: `{targets}`",
                "",
                "### Reasons",
                reasons,
                "",
                "### Authority boundaries",
                boundaries,
                "",
            )
        ),
        encoding="utf-8",
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bounded CMB autonomy arbiter")
    subparsers = parser.add_subparsers(dest="command", required=True)

    decide_parser = subparsers.add_parser("decide", help="decide whether Steward repair is legal")
    decide_parser.add_argument("--audit", type=Path, required=True)
    decide_parser.add_argument("--strategy-report", type=Path, required=True)
    decide_parser.add_argument("--policy", type=Path, required=True)
    decide_parser.add_argument("--output", type=Path, required=True)
    decide_parser.add_argument("--summary", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command != "decide":
            raise AutonomyError(f"unsupported command: {args.command}")

        audit = _load_json_object(args.audit)
        strategy_report = _load_json_object(args.strategy_report)
        try:
            policy = load_policy(args.policy)
        except StrategyError as exc:
            raise AutonomyError(str(exc)) from exc

        decision = decide(audit, strategy_report, policy)
        args.output.write_text(
            json.dumps(decision.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        _write_summary(args.summary, decision)
    except AutonomyError as exc:
        parser.error(str(exc))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
