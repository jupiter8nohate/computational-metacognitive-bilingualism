"""Console interface for the CMB-Z13 reference parser."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .z13 import Z13Error, explain_statement, parse_statement


def _json_text(statement_text: str) -> str:
    statement = parse_statement(statement_text)
    return json.dumps(
        statement.to_dict(),
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cmb-z13",
        description="Parse and validate CMB-Z13 symbolic statements.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command, help_text in (
        ("parse", "Parse one CMB-Z13 statement and emit its AST as JSON."),
        ("validate", "Validate one CMB-Z13 statement."),
        ("explain", "Explain one CMB-Z13 statement in human-readable form."),
        ("export-json", "Write one CMB-Z13 AST to a JSON file."),
    ):
        sub = subparsers.add_parser(command, help=help_text)
        sub.add_argument("statement")
        if command == "export-json":
            sub.add_argument("--output", required=True, type=Path)

    return parser


def _run(args: argparse.Namespace) -> int:
    if args.command == "parse":
        print(_json_text(args.statement))
        return 0

    if args.command == "validate":
        statement = parse_statement(args.statement)
        print(
            f"VALID {statement.glyph} {statement.sign} "
            f"-> {statement.operator} -> HUMAN_DECISION_BOUNDARY"
        )
        return 0

    if args.command == "explain":
        print(explain_statement(parse_statement(args.statement)))
        return 0

    if args.command == "export-json":
        destination: Path = args.output
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(_json_text(args.statement) + "\n", encoding="utf-8")
        print(f"CMB-Z13 AST -> {destination}")
        return 0

    raise AssertionError(f"Unhandled command: {args.command}")


def main(argv: Sequence[str] | None = None) -> int:
    try:
        return _run(build_parser().parse_args(argv))
    except (Z13Error, OSError, UnicodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
