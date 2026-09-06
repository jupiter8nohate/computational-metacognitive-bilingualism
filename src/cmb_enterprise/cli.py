"""Command-line interface for the CMB enterprise composition layer."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Sequence

from cmb_cap.credential import CapabilityError
from cmb_provenance.errors import CMBProvenanceError
from cmb_provenance.sealing import save_receipt, seal

from .report import build_trust_report


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cmb-enterprise",
        description=(
            "Compose CMB artifact integrity and enterprise authority into a "
            "machine-readable trust report."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    verify_parser = sub.add_parser("verify", help="Generate an enterprise trust report.")
    verify_parser.add_argument("paths", nargs="+", type=Path)
    verify_parser.add_argument("--receipt", required=True, type=Path)
    verify_parser.add_argument("--base-dir", type=Path, default=Path.cwd())
    verify_parser.add_argument("--check-git-commit", action="store_true")
    verify_parser.add_argument("--credential", type=Path)
    verify_parser.add_argument("--public-key", type=Path)
    verify_parser.add_argument("--parent", type=Path)
    verify_parser.add_argument("--require-authority", action="store_true")
    verify_parser.add_argument("--output", type=Path)

    sub.add_parser("selftest", help="Run deterministic integrity/deny Recovery checks.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "selftest":
            _selftest()
            print("CMB_ENTERPRISE_SELFTEST_OK")
            return 0

        if args.public_key is not None and args.credential is None:
            raise ValueError("--public-key requires --credential")
        if args.parent is not None and args.credential is None:
            raise ValueError("--parent requires --credential")
        if args.require_authority and (
            args.credential is None or args.public_key is None
        ):
            raise ValueError(
                "--require-authority requires both --credential and --public-key"
            )

        report = build_trust_report(
            args.paths,
            receipt=args.receipt,
            base_dir=args.base_dir,
            check_git_commit=args.check_git_commit,
            credential=args.credential,
            public_key=args.public_key,
            parent_credential=args.parent,
            require_authority=args.require_authority,
        )
        encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if args.output is None:
            print(encoded, end="")
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(encoded, encoding="utf-8")
            print(f"CMB_ENTERPRISE_REPORT -> {args.output}")
            print(f"decision={report['decision']}")

        return 0 if report["decision"] != "DENY" else 3
    except (CMBProvenanceError, CapabilityError, OSError, ValueError) as exc:
        print(f"CMB_ENTERPRISE_ERROR: {exc}")
        return 2


def _selftest() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        asset = root / "asset.txt"
        receipt_path = root / "receipt.json"
        asset.write_text("human authority\n", encoding="utf-8")
        save_receipt(
            seal(
                [asset],
                base_dir=root,
                git_commit="0" * 40,
                created_at_utc="2026-09-05T00:00:00Z",
            ),
            receipt_path,
        )

        clean = build_trust_report(
            [asset],
            receipt=receipt_path,
            base_dir=root,
        )
        if clean["decision"] != "HUMAN_REVIEW":
            raise ValueError("selftest expected unsigned integrity-only review state")
        if clean["artifact_integrity"]["status"] != "PASS":
            raise ValueError("selftest expected clean artifact integrity")

        asset.write_text("tampered\n", encoding="utf-8")
        tampered = build_trust_report(
            [asset],
            receipt=receipt_path,
            base_dir=root,
        )
        if tampered["decision"] != "DENY":
            raise ValueError("selftest expected tampered artifact to deny")


if __name__ == "__main__":
    raise SystemExit(main())
