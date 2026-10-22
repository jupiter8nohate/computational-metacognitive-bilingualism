"""Deterministic source-map audit for the 2084 Evidence Ledger.

This is a documentation consistency test. It does not make network requests,
verify the truth of a linked source, or grant authority to automated judgments.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "datasets/2084-witness-evidence.v1.json"
LEDGER = ROOT / "docs/DEATH_NOTE_2084_EVIDENCE_LEDGER.md"
EXPECTED_IDS = tuple(f"{number:02d}" for number in range(1, 11))
STATUSES = {"documented", "context_dependent", "research"}
SOURCE_TYPES = {
    "agency_report", "agency_case", "agency_guidance",
    "legal_text", "technical_standard", "research", "vendor_documentation",
}
FIELDS = {"id", "mechanism", "evidence_status", "supported_claim", "limitation", "sources"}


def validate(data: object, ledger: str) -> list[str]:
    """Return specific, stable failures instead of merely accepting valid JSON."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["Registry must be a JSON object."]
    if data.get("schema_version") != "cmb.2084-witness.v1":
        errors.append("Unexpected schema_version.")
    if data.get("story_is_fictional") is not True:
        errors.append("Fiction boundary must explicitly be true.")
    if not isinstance(data.get("scope_note"), str) or len(data["scope_note"].strip()) < 70:
        errors.append("Missing substantive epistemic scope note.")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(data.get("as_of", ""))):
        errors.append("as_of must be an ISO date.")
    entries = data.get("entries")
    if not isinstance(entries, list) or len(entries) != 10:
        return errors + ["Registry must contain exactly ten entries."]
    found: list[str] = []
    for index, entry in enumerate(entries, 1):
        label = f"entry {index}"
        if not isinstance(entry, dict):
            errors.append(f"{label} must be an object.")
            continue
        missing = FIELDS - entry.keys()
        if missing:
            errors.append(f"{label}: missing {', '.join(sorted(missing))}.")
            continue
        identifier = entry["id"]
        if not isinstance(identifier, str) or not re.fullmatch(r"\d{2}", identifier):
            errors.append(f"{label}: ID must be two digits.")
            continue
        found.append(identifier)
        if entry["evidence_status"] not in STATUSES:
            errors.append(f"{identifier}: invalid evidence_status.")
        for field in ("mechanism", "supported_claim", "limitation"):
            value = entry[field]
            if not isinstance(value, str) or len(value.strip()) < 25:
                errors.append(f"{identifier}: missing meaningful {field}.")
        if f"| **{identifier}** |" not in ledger:
            errors.append(f"{identifier}: missing corresponding ledger table row.")
        sources = entry["sources"]
        if not isinstance(sources, list) or not sources:
            errors.append(f"{identifier}: requires at least one source.")
            continue
        for offset, source in enumerate(sources, 1):
            key = f"{identifier} source {offset}"
            if not isinstance(source, dict):
                errors.append(f"{key}: source must be an object.")
                continue
            if source.get("source_type") not in SOURCE_TYPES:
                errors.append(f"{key}: invalid source_type.")
            if not isinstance(source.get("title"), str) or not source["title"].strip():
                errors.append(f"{key}: missing title.")
            url = source.get("url")
            if not isinstance(url, str):
                errors.append(f"{key}: missing URL.")
                continue
            parsed = urlsplit(url)
            if (
                parsed.scheme != "https"
                or not parsed.netloc
                or parsed.username is not None
                or parsed.password is not None
                or parsed.fragment
            ):
                errors.append(f"{key}: unsafe or malformed HTTPS URL.")
            elif url not in ledger:
                errors.append(f"{key}: URL is not cited in the canonical evidence ledger.")
    if tuple(found) != EXPECTED_IDS:
        errors.append("Entries must have unique sequential IDs 01 through 10.")
    if "do not" not in ledger.lower() and "does not" not in ledger.lower():
        errors.append("Ledger lacks a visible claim-limitation statement.")
    return errors


def audit(registry_path: Path = REGISTRY, ledger_path: Path = LEDGER) -> list[str]:
    try:
        payload = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"Could not read registry: {exc}"]
    try:
        story = ledger_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [f"Could not read canonical ledger: {exc}"]
    return validate(payload, story)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--ledger", type=Path, default=LEDGER)
    args = parser.parse_args()
    issues = audit(args.registry, args.ledger)
    if issues:
        for issue in issues:
            print(f"FAIL: {issue}")
        return 1
    print("PASS: 10 scoped claims, source URLs, identifiers, and fiction boundaries.")
    print("NOTE: Source truth, HTTP status, and publication deployment are not verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
