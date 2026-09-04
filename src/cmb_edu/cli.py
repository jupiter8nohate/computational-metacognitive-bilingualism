"""Command-line interface for the experimental CMB-EDU learning layer."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from . import __version__
from .fgc import FGCEmojiParser
from .parser import CMBDualBrainParser, CMBParseError


def _add_source_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("source", nargs="?", help="One CMB-EDU Dual-Brain stream.")
    parser.add_argument("--file", type=Path, help="Read one CMB-EDU stream from a UTF-8 file.")


def _read_source(args: argparse.Namespace) -> str:
    if args.source and args.file:
        raise CMBParseError("Provide either SOURCE or --file, not both.")
    if args.file:
        return args.file.read_text(encoding="utf-8")
    if args.source:
        return args.source
    raise CMBParseError("A CMB-EDU SOURCE or --file is required.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cmb-edu",
        description=(
            "Parse and validate privacy-first CMB educational context streams. "
            "Human declarations remain distinct from machine inference."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__} experimental",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    parse_cmd = subparsers.add_parser(
        "parse",
        help="Parse one stream and print the Metacognitive Context Envelope.",
    )
    _add_source_arguments(parse_cmd)

    fgc_cmd = subparsers.add_parser(
        "parse-fgc",
        help="Parse one Flamingoglyph Code learning stream into a CMB-EDU envelope.",
    )
    _add_source_arguments(fgc_cmd)

    validate_cmd = subparsers.add_parser(
        "validate",
        help="Validate one stream against the CMB-EDU grammar and sovereignty policy.",
    )
    _add_source_arguments(validate_cmd)

    export_cmd = subparsers.add_parser(
        "export-json",
        help="Write one parsed Metacognitive Context Envelope to JSON.",
    )
    _add_source_arguments(export_cmd)
    export_cmd.add_argument("--output", required=True, type=Path)

    return parser


def _run(args: argparse.Namespace) -> int:
    source = _read_source(args)
    if args.command == "parse-fgc":
        envelope = FGCEmojiParser().parse_stream(source)
    else:
        envelope = CMBDualBrainParser().parse_stream(source)

    if args.command == "validate":
        boundary = envelope["sovereignty_gate"]["declared_invariant"]
        print(f"VALID cmb.edu.v1 boundary={boundary} authority=HUMAN_FINAL")
        return 0

    encoded = json.dumps(envelope, ensure_ascii=False, indent=2, sort_keys=True)
    if args.command in {"parse", "parse-fgc"}:
        print(encoded)
        return 0

    if args.command == "export-json":
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded + "\n", encoding="utf-8")
        print(f"CMB-EDU envelope -> {args.output}")
        return 0

    raise AssertionError(f"Unhandled command: {args.command}")


def main(argv: Sequence[str] | None = None) -> int:
    try:
        return _run(build_parser().parse_args(argv))
    except (CMBParseError, OSError, UnicodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
