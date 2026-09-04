#!/usr/bin/env python3
"""Create deterministic SHA-256 checksum lines for release files."""

from __future__ import annotations

import argparse
from pathlib import Path

from cmb_provenance.release import build_checksums


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", nargs="?", type=Path, default=Path("dist"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or args.directory / "SHA256SUMS"
    files = build_checksums(args.directory, output)
    print(f"Wrote {output} for {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
