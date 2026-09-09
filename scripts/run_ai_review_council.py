#!/usr/bin/env python3
"""Run model-assisted CMB review specialists over a Git diff."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from cmb_agents.ai_review_council import run_ai_council
from cmb_agents.model_gateway import model_available
from run_stockfish_review import collect_changes


def _render(results: tuple[dict[str, object], ...]) -> str:
    lines = [
        "# CMB AI Review Council",
        "",
        "AI findings are advisory and must be checked against repository evidence.",
        "",
    ]
    for result in results:
        agent = str(result.get("agent", "UNKNOWN"))
        verdict = str(result.get("verdict", "HUMAN_REVIEW"))
        confidence = float(result.get("confidence", 0.0))
        summary = str(result.get("summary", ""))
        truncated = bool(result.get("input_truncated", False))
        provider = str(result.get("model_provider", "unknown"))
        model_name = str(result.get("model", "unknown"))
        lines.extend([
            f"## {agent}",
            "",
            f"Verdict: **{verdict}**  ",
            f"Confidence: **{confidence:.3f}**  ",
            f"Input truncated: **{str(truncated).lower()}**",
            f"Provider: **{provider}**",
            f"Model: **{model_name}**",
            "",
            summary,
            "",
        ])
        findings = result.get("findings", [])
        if isinstance(findings, list) and findings:
            for finding in findings:
                if not isinstance(finding, dict):
                    continue
                lines.append(
                    f"- **{str(finding.get('severity', 'info')).upper()}** "
                    f"`{finding.get('path', '')}`: {finding.get('message', '')}"
                )
            lines.append("")
    lines.extend([
        "MODEL_OPINION != EVIDENCE  ",
        "AI_REVIEW != HUMAN_APPROVAL  ",
        "HUMAN_AGENCY > MACHINE_AUTHORITY",
        "",
    ])
    return "\n".join(lines)


def _render_unavailable(message: str) -> str:
    return "\n".join([
        "# CMB AI Review Council",
        "",
        "Status: **UNAVAILABLE**",
        "",
        message,
        "",
        "The deterministic review remains authoritative for this workflow run.",
        "",
        "MODEL_ADVICE != POLICY  ",
        "AI_REVIEW != HUMAN_APPROVAL  ",
        "",
    ])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--json", type=Path, default=Path("ai-review-council.json"))
    parser.add_argument("--markdown", type=Path, default=Path("ai-review-council.md"))
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return nonzero when the optional AI council is unavailable.",
    )
    args = parser.parse_args(argv)

    api_key = os.environ.get("OPENAI_API_KEY", "")
    model = os.environ.get("CMB_AGENT_MODEL", "")
    copilot_token = os.environ.get("CMB_COPILOT_TOKEN", "")
    copilot_model = os.environ.get("CMB_COPILOT_MODEL", "")
    if not model_available(
        openai_api_key=api_key,
        openai_model=model,
        copilot_token=copilot_token,
    ):
        message = "AI review skipped because no model provider is available."
        args.markdown.write_text(_render_unavailable(message), encoding="utf-8")
        print(message)
        return 1 if args.strict else 0

    try:
        changes = collect_changes(args.base, args.head)
        if not changes:
            message = "No changed files to review."
            args.markdown.write_text(_render_unavailable(message), encoding="utf-8")
            print(message)
            return 0
        results = run_ai_council(
            changes,
            api_key=api_key,
            model=model,
            copilot_token=copilot_token,
            copilot_model=copilot_model,
        )
        args.json.write_text(
            json.dumps(results, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        markdown = _render(results)
        args.markdown.write_text(markdown, encoding="utf-8")
        print(markdown)
        return 0
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        message = f"AI review council unavailable: {str(exc)[:1200]}"
        args.markdown.write_text(_render_unavailable(message), encoding="utf-8")
        print(message, file=sys.stderr)
        return 1 if args.strict else 0


if __name__ == "__main__":
    raise SystemExit(main())
