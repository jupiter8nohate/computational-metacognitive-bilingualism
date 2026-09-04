#!/usr/bin/env python3
"""Verify that generic c2patool output contains the exact CMB adapter payload."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterator


def walk(value: Any) -> Iterator[Any]:
    yield value
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--expected-payload", required=True, type=Path)
    parser.add_argument("--assertion-label", required=True)
    args = parser.parse_args()

    report = json.loads(args.report.read_text(encoding="utf-8"))
    expected = json.loads(args.expected_payload.read_text(encoding="utf-8"))

    values = list(walk(report))
    if args.assertion_label not in values:
        raise SystemExit(
            f"C2PA report does not expose assertion label {args.assertion_label!r}."
        )

    if not any(value == expected for value in values if isinstance(value, dict)):
        raise SystemExit("C2PA report does not contain the exact CMB assertion payload.")

    rendered = json.dumps(report, sort_keys=True)
    if "cmb.c2pa-assertion-payload.v1" not in rendered:
        raise SystemExit("CMB payload schema marker missing from C2PA report.")

    print("C2PA round-trip verified: generic reader recovered exact CMB payload.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
