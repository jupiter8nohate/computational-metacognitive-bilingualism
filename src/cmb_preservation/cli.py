"""Command-line interface for CMB preservation and Recovery auditing."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .audit import AuditError, audit_repository


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cmb-recovery",
        description="Audit CMB Recovery declarations and canonical corpus integrity.",
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root.")
    parser.add_argument(
        "command",
        choices=("audit", "status"),
        nargs="?",
        default="audit",
        help="audit validates all preservation metadata; status prints the same result as JSON.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = audit_repository(args.root)
    except (AuditError, OSError) as exc:
        print(f"cmb-recovery: {exc}", file=sys.stderr)
        return 1

    if args.command == "status":
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
        print(
            "CMB Recovery audit OK: "
            f"{result['corpus_records']} corpus records, "
            f"{result['evidence_paths_checked']} evidence paths, "
            f"sha256={result['corpus_sha256']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
