"""Command-line interface for CMB Capability Authorization Passport."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

from cmb_policy.authorization import write_keypair
from cmb_sdl import compile_text

from .credential import (
    CapabilityError,
    issue_capability,
    load_credential,
    public_key_fingerprint,
    vc_projection,
    verify_capability,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cmb-cap")
    sub = parser.add_subparsers(dest="command", required=True)

    keygen = sub.add_parser("keygen", help="Generate a local Ed25519 keypair.")
    keygen.add_argument("--private-key", type=Path, required=True)
    keygen.add_argument("--public-key", type=Path, required=True)

    issue_sdl = sub.add_parser(
        "issue-sdl",
        help="Compile CMB-SDL and issue a signed CMB-CAP credential.",
    )
    issue_sdl.add_argument("input", type=Path)
    issue_sdl.add_argument("--private-key", type=Path, required=True)
    issue_sdl.add_argument("--parent", type=Path)
    issue_sdl.add_argument("--output", type=Path, required=True)

    issue_ir = sub.add_parser(
        "issue-ir",
        help="Issue a signed CMB-CAP credential from Authority IR JSON.",
    )
    issue_ir.add_argument("input", type=Path)
    issue_ir.add_argument("--private-key", type=Path, required=True)
    issue_ir.add_argument("--parent", type=Path)
    issue_ir.add_argument("--output", type=Path, required=True)

    verify = sub.add_parser(
        "verify",
        help="Verify a CMB-CAP signature, expiry, authority, key pin, and lineage.",
    )
    verify.add_argument("credential", type=Path)
    verify.add_argument("--public-key", type=Path)
    verify.add_argument("--parent", type=Path)

    export_vc = sub.add_parser(
        "export-vc",
        help="Export a W3C VC 2.0-shaped projection without claiming DI conformance.",
    )
    export_vc.add_argument("credential", type=Path)
    export_vc.add_argument("--public-key", type=Path)
    export_vc.add_argument("--parent", type=Path)
    export_vc.add_argument("--output", type=Path)
    return parser


def _read_key(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def _write_json(payload: dict[str, Any], output: Path | None) -> None:
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if output is None:
        print(encoded, end="")
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(encoded, encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "keygen":
            write_keypair(args.private_key, args.public_key)
            print("CMB_CAP_KEYPAIR_CREATED")
            return 0

        if args.command in {"issue-sdl", "issue-ir"}:
            if args.command == "issue-sdl":
                authority = compile_text(args.input.read_text(encoding="utf-8"))
            else:
                authority = json.loads(args.input.read_text(encoding="utf-8"))
            if not isinstance(authority, dict):
                raise CapabilityError("Authority IR must be a JSON object.")
            parent = load_credential(args.parent) if args.parent else None
            credential = issue_capability(
                authority,
                private_key_b64=_read_key(args.private_key),
                parent_credential=parent,
            )
            _write_json(credential, args.output)
            print("CMB_CAP_ISSUED")
            return 0

        if args.command == "verify":
            credential = load_credential(args.credential)
            parent = load_credential(args.parent) if args.parent else None
            expected = (
                public_key_fingerprint(_read_key(args.public_key))
                if args.public_key
                else None
            )
            ok, failures = verify_capability(
                credential,
                expected_key_fingerprint=expected,
                parent_credential=parent,
            )
            print(
                json.dumps(
                    {"valid": ok, "failures": list(failures)},
                    sort_keys=True,
                )
            )
            return 0 if ok else 3

        credential = load_credential(args.credential)
        parent = load_credential(args.parent) if args.parent else None
        expected = (
            public_key_fingerprint(_read_key(args.public_key))
            if args.public_key
            else None
        )
        ok, failures = verify_capability(
            credential,
            expected_key_fingerprint=expected,
            parent_credential=parent,
        )
        if not ok:
            raise CapabilityError(
                "Refusing VC projection of unverified credential: "
                + ", ".join(failures)
            )
        _write_json(vc_projection(credential), args.output)
        return 0
    except (OSError, json.JSONDecodeError, CapabilityError, ValueError) as exc:
        print(f"CMB_CAP_ERROR: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
