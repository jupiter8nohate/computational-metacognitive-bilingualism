"""Command-line interface for CMB-EDU."""

from __future__ import annotations

import argparse
import json
import sys

from .fgc import FGCEmojiParser
from .parser import CMBDualBrainParser
from .provenance import build_context_commitment


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cmb-edu",
        description="Compile CMB educational syntax into privacy-first context envelopes.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    dual = subparsers.add_parser("parse", help="Parse Dual-Brain CMB syntax.")
    dual.add_argument("stream")
    dual.add_argument("--commitment", action="store_true")

    fgc = subparsers.add_parser("parse-fgc", help="Parse FGC emoji learning syntax.")
    fgc.add_argument("stream")
    fgc.add_argument("--commitment", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "parse":
            envelope = CMBDualBrainParser().parse_envelope(args.stream)
        else:
            envelope = FGCEmojiParser().parse_envelope(args.stream)

        output = (
            build_context_commitment(envelope)
            if args.commitment
            else envelope.to_dict()
        )
        print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except ValueError as exc:
        print(f"cmb-edu: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
