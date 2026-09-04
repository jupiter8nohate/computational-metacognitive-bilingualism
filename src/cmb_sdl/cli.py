"""Command-line interface for CMB Sovereign Delegation Language."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .compiler import compile_text, validate_delegation
from .model import SDLValidationError


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cmb-sdl")
    sub = parser.add_subparsers(dest="command", required=True)

    compile_parser = sub.add_parser(
        "compile",
        help="Compile CMB-SDL into deterministic Authority IR.",
    )
    compile_parser.add_argument("input", type=Path)
    compile_parser.add_argument("--output", type=Path)

    delegation = sub.add_parser(
        "check-delegation",
        help="Verify that child Authority IR cannot exceed parent authority.",
    )
    delegation.add_argument("parent", type=Path)
    delegation.add_argument("child", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "compile":
            ir = compile_text(args.input.read_text(encoding="utf-8"))
            rendered = json.dumps(ir, indent=2, sort_keys=True) + "\n"
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(rendered, encoding="utf-8")
            else:
                print(rendered, end="")
            return 0

        parent = json.loads(args.parent.read_text(encoding="utf-8"))
        child = json.loads(args.child.read_text(encoding="utf-8"))
        validate_delegation(parent, child)
        print("CMB_SDL_DELEGATION_OK")
        return 0
    except (OSError, json.JSONDecodeError, SDLValidationError) as exc:
        print(f"CMB_SDL_ERROR: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
