"""Command-line reference implementation for CMB-Z13."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .z13 import Z13Error, Z13_SPEC_VERSION, explain_z13_statement, parse_z13_statement


def _add_source_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("source", nargs="?", help="One CMB-Z13 statement.")
    parser.add_argument("--file", type=Path, help="Read one CMB-Z13 statement from a file.")


def _read_source(args: argparse.Namespace) -> str:
    if args.source and args.file:
        raise Z13Error("Provide either SOURCE or --file, not both.")
    if args.file:
        return args.file.read_text(encoding="utf-8")
    if args.source:
        return args.source
    raise Z13Error("A CMB-Z13 SOURCE or --file is required.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cmb-z13",
        description="Parse, validate, explain, and export CMB-Z13 symbolic notation.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {Z13_SPEC_VERSION} experimental-reference",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command, help_text in (
        ("parse", "Parse one statement and print its deterministic AST."),
        ("validate", "Validate one statement against the canonical 13-lens mapping."),
        ("explain", "Explain one valid statement in plain language."),
        ("export-json", "Write one parsed AST to a JSON file."),
    ):
        sub = subparsers.add_parser(command, help=help_text)
        _add_source_arguments(sub)
        if command == "export-json":
            sub.add_argument("--output", required=True, type=Path)
    return parser


def _run(args: argparse.Namespace) -> int:
    statement = parse_z13_statement(_read_source(args))
    if args.command == "validate":
        print(f"VALID {statement.glyph} {statement.sign}/{statement.language} operation={statement.operation}")
        return 0
    if args.command == "explain":
        print(explain_z13_statement(statement))
        return 0

    encoded = json.dumps(statement.to_dict(), ensure_ascii=False, indent=2, sort_keys=True)
    if args.command == "parse":
        print(encoded)
        return 0
    if args.command == "export-json":
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded + "\n", encoding="utf-8")
        print(f"CMB-Z13 AST -> {args.output}")
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
