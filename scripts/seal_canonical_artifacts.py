#!/usr/bin/env python3
"""Seal and verify the canonical public CMB artifact set."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cmb_provenance import save_receipt, seal, verify
from cmb_provenance.release import CANONICAL_PUBLIC_ARTIFACTS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path.cwd(),
        help="Repository root containing the canonical artifacts.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Destination for the canonical receipt JSON.",
    )
    parser.add_argument(
        "--print-json",
        action="store_true",
        help="Print the validated receipt JSON after writing it.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    base_dir = args.base_dir.resolve(strict=True)
    output = args.output
    if not output.is_absolute():
        output = base_dir / output

    receipt = seal(CANONICAL_PUBLIC_ARTIFACTS, base_dir=base_dir)
    save_receipt(receipt, output)

    verification = verify(
        CANONICAL_PUBLIC_ARTIFACTS,
        receipt,
        base_dir=base_dir,
        check_git_commit=True,
    )
    if not verification.ok:
        details = "; ".join(
            f"{failure.code}: {failure.path}: {failure.message}"
            for failure in verification.failures
        )
        raise RuntimeError(f"Canonical receipt verification failed: {details}")

    print(f"sealed_commit={receipt.manifest.git_commit}")
    print(f"git_commit_status={receipt.manifest.git_commit_status}")
    print(f"manifest_sha256={receipt.manifest_sha256}")
    print("coverage=" + ",".join(receipt.coverage.paths))

    if args.print_json:
        print("---BEGIN_CMB_RECEIPT---")
        print(json.dumps(receipt.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))
        print("---END_CMB_RECEIPT---")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
