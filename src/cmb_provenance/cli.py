"""Console entry point with stable exit codes and safe error rendering."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .c2pa import (
    c2pa_assertion_payload_json,
    save_c2pa_assertion_payload,
    save_c2pa_manifest_definition,
)
from .constants import ANCHOR_TYPES, DEFAULT_LEDGER_NAME, TOOL_VERSION
from .errors import CMBProvenanceError
from .ledger import append_anchor, verify_ledger
from .sealing import load_receipt, save_receipt, seal, verify
from .selftest import run_selftest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cmb-provenance",
        description="Seal explicit artifacts and maintain tamper-evident evidence references.",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {TOOL_VERSION}"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    seal_parser = subparsers.add_parser(
        "seal", help="Create an explicit artifact seal receipt."
    )
    seal_parser.add_argument("paths", nargs="+", type=Path)
    seal_parser.add_argument("--base-dir", type=Path, default=Path.cwd())
    seal_parser.add_argument("--git-commit", help="Full Git commit; defaults to HEAD.")
    seal_parser.add_argument("--created-at", dest="created_at_utc")
    seal_parser.add_argument(
        "--output", type=Path, help="Receipt path; omit to write JSON to stdout."
    )

    verify_parser = subparsers.add_parser(
        "verify", help="Verify files against an exact seal receipt."
    )
    verify_parser.add_argument("paths", nargs="+", type=Path)
    verify_parser.add_argument("--receipt", required=True, type=Path)
    verify_parser.add_argument("--base-dir", type=Path, default=Path.cwd())
    verify_parser.add_argument("--check-git-commit", action="store_true")
    verify_parser.add_argument("--json", action="store_true", dest="json_output")

    anchor_parser = subparsers.add_parser(
        "anchor", help="Append an external reference under a lock."
    )
    anchor_parser.add_argument("--receipt", required=True, type=Path)
    anchor_parser.add_argument(
        "--type", required=True, choices=ANCHOR_TYPES, dest="anchor_type"
    )
    anchor_parser.add_argument("--location", required=True)
    anchor_parser.add_argument("--description", required=True)
    anchor_parser.add_argument("--ledger", type=Path, default=Path(DEFAULT_LEDGER_NAME))
    anchor_parser.add_argument("--external-time", dest="claimed_external_time_utc")
    anchor_parser.add_argument("--time-basis", dest="external_time_basis")
    anchor_parser.add_argument("--lock-timeout", type=float, default=10.0)

    ledger_parser = subparsers.add_parser(
        "ledger-verify", help="Validate every record and chain link."
    )
    ledger_parser.add_argument("--ledger", type=Path, default=Path(DEFAULT_LEDGER_NAME))
    ledger_parser.add_argument("--lock-timeout", type=float, default=10.0)

    c2pa_parser = subparsers.add_parser(
        "export-c2pa-payload",
        help="Export a minimal C2PA-facing payload body from a CMB receipt.",
    )
    c2pa_parser.add_argument("--receipt", required=True, type=Path)
    c2pa_parser.add_argument(
        "--output",
        type=Path,
        help="Destination path; omit to write canonical JSON to stdout.",
    )
    c2pa_parser.add_argument(
        "--include-paths",
        action="store_true",
        help="Include covered artifact paths. Paths are omitted by default.",
    )

    manifest_parser = subparsers.add_parser(
        "build-c2pa-manifest",
        help="Build a C2PA SDK JSON manifest definition around a CMB receipt.",
    )
    manifest_parser.add_argument("--receipt", required=True, type=Path)
    manifest_parser.add_argument("--assertion-label", required=True)
    manifest_parser.add_argument("--output", required=True, type=Path)
    manifest_parser.add_argument("--include-paths", action="store_true")
    manifest_parser.add_argument(
        "--test-example-namespace",
        action="store_true",
        help="Allow com.example/net.example/org.example for local integration tests only.",
    )

    subparsers.add_parser("selftest", help="Run dependency-free Recovery checks.")
    return parser


def _run(args: argparse.Namespace) -> int:
    if args.command == "seal":
        receipt = seal(
            args.paths,
            base_dir=args.base_dir,
            git_commit=args.git_commit,
            created_at_utc=args.created_at_utc,
        )
        if args.output:
            destination = save_receipt(receipt, args.output)
            print(f"SEALED {len(receipt.coverage.paths)} file(s) -> {destination}")
            print(f"manifest_sha256={receipt.manifest_sha256}")
        else:
            print(
                json.dumps(
                    receipt.to_dict(), ensure_ascii=False, indent=2, sort_keys=True
                )
            )
        return 0

    if args.command == "verify":
        result = verify(
            args.paths,
            load_receipt(args.receipt),
            base_dir=args.base_dir,
            check_git_commit=args.check_git_commit,
        )
        if args.json_output:
            print(
                json.dumps(
                    result.to_dict(), ensure_ascii=False, indent=2, sort_keys=True
                )
            )
        elif result.ok:
            print(
                f"VERIFIED {len(result.checked_paths)} file(s) — {result.manifest_sha256}"
            )
        else:
            print("VERIFICATION FAILED", file=sys.stderr)
            for failure in result.failures:
                target = f"{failure.path}: " if failure.path else ""
                print(f"  {target}{failure.code} — {failure.message}", file=sys.stderr)
        return 0 if result.ok else 1

    if args.command == "anchor":
        record = append_anchor(
            args.receipt,
            anchor_type=args.anchor_type,
            location=args.location,
            description=args.description,
            ledger_path=args.ledger,
            claimed_external_time_utc=args.claimed_external_time_utc,
            external_time_basis=args.external_time_basis,
            lock_timeout=args.lock_timeout,
        )
        print(f"APPENDED #{record.sequence} — {record.record_sha256}")
        return 0

    if args.command == "ledger-verify":
        count, tip = verify_ledger(args.ledger, lock_timeout=args.lock_timeout)
        print(f"LEDGER OK — {count} record(s), tip={tip or 'none'}")
        return 0

    if args.command == "export-c2pa-payload":
        receipt = load_receipt(args.receipt)
        if args.output:
            destination = save_c2pa_assertion_payload(
                receipt,
                args.output,
                include_paths=args.include_paths,
            )
            print(f"C2PA-FACING PAYLOAD -> {destination}")
            print("status=adapter_payload_only_not_c2pa_manifest_or_credential")
        else:
            print(
                c2pa_assertion_payload_json(
                    receipt,
                    include_paths=args.include_paths,
                    pretty=False,
                )
            )
        return 0

    if args.command == "build-c2pa-manifest":
        destination = save_c2pa_manifest_definition(
            load_receipt(args.receipt),
            args.output,
            assertion_label=args.assertion_label,
            include_paths=args.include_paths,
            allow_example_namespace=args.test_example_namespace,
        )
        print(f"C2PA MANIFEST DEFINITION -> {destination}")
        print("status=unsigned_definition_requires_external_c2pa_signing_and_binding")
        return 0

    if args.command == "selftest":
        run_selftest()
        print("Self-test passed.")
        return 0

    raise AssertionError(f"Unhandled command: {args.command}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    try:
        return _run(parser.parse_args(argv))
    except (
        CMBProvenanceError,
        OSError,
        UnicodeError,
        ValueError,
        json.JSONDecodeError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
