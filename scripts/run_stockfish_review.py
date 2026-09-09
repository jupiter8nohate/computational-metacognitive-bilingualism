#!/usr/bin/env python3
"""Run the bounded CMB Stockfish Review Council against a Git diff."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from cmb_agents.review_council import ReviewChange, Verdict, render_markdown, review_changes


def _git(args: list[str]) -> str:
    process = subprocess.run(
        ["git", *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=120,
    )
    if process.returncode != 0:
        raise RuntimeError(process.stderr.strip() or "git command failed")
    return process.stdout


def _numstat(base: str, head: str) -> dict[str, tuple[int, int]]:
    stats: dict[str, tuple[int, int]] = {}
    for line in _git(["diff", "--numstat", f"{base}...{head}"]).splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        additions_raw, deletions_raw, path = parts
        additions = int(additions_raw) if additions_raw.isdigit() else 0
        deletions = int(deletions_raw) if deletions_raw.isdigit() else 0
        stats[path] = (additions, deletions)
    return stats


def collect_changes(base: str, head: str) -> tuple[ReviewChange, ...]:
    stats = _numstat(base, head)
    paths = [
        line.strip()
        for line in _git(["diff", "--name-only", f"{base}...{head}"]).splitlines()
        if line.strip()
    ]
    changes: list[ReviewChange] = []
    for path in paths:
        patch = _git(["diff", "--unified=3", f"{base}...{head}", "--", path])
        additions, deletions = stats.get(path, (0, 0))
        changes.append(ReviewChange(path, patch, additions, deletions))
    return tuple(changes)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="Base ref, for example origin/main")
    parser.add_argument("--head", default="HEAD", help="Head ref")
    parser.add_argument("--json", type=Path, default=Path("stockfish-review.json"))
    parser.add_argument("--markdown", type=Path, default=Path("stockfish-review.md"))
    parser.add_argument(
        "--fail-on-request-changes",
        action="store_true",
        help="Return exit code 1 when the bounded council verdict is REQUEST_CHANGES.",
    )
    args = parser.parse_args(argv)

    try:
        changes = collect_changes(args.base, args.head)
        if not changes:
            print("No changed files to review.")
            return 0
        packet = review_changes(changes)
        args.json.write_text(
            json.dumps(packet.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        markdown = render_markdown(packet)
        args.markdown.write_text(markdown, encoding="utf-8")
        print(markdown)
        if args.fail_on_request_changes and packet.verdict is Verdict.REQUEST_CHANGES:
            return 1
        return 0
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as exc:
        print(f"Stockfish review failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
