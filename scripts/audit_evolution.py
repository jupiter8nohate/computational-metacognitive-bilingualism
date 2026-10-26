"""Independent, dependency-free source audit for the ten-upgrade CMB branch.

Checks local structure and editorial constraints, not rendered WCAG compliance,
live search indexing, legal conclusions or independently verified sources.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NINE = (
    "DEATH_NOTE_2084",
    "DEATH_NOTE_2084_FALSE_LIGHT",
    "DEATH_NOTE_2084_HOUSE_OF_A_MILLION_DOORS",
    "DEATH_NOTE_2084_LEDGER_OF_INVISIBLE_CELLS",
    "DEATH_NOTE_2084_CHILD_WHO_REFUSED_THE_UPDATE",
    "DEATH_NOTE_2084_LEDGER_OF_INVISIBLE_YEARS",
    "DEATH_NOTE_2084_POST_GROUND_BASELINE",
    "DEATH_NOTE_2084_WITNESS_IN_LIGHTHOUSE",
    "DEATH_NOTE_2084_STATION_SEVEN",
)
LETTERS = "LUCIFER"
NAMES = ("ANOMALY_STARE", "NULL_BREATH", "VERIFICATION_CAGE", "DUAL_WITNESS",
         "SIGNAL_DUST", "BURST_SPEECH", "MICROBREAK", "BLUE_ANOMALY",
         "POST_OBSERVATION", "BACKTRACE")


def audit(root: Path = ROOT) -> list[str]:
    errors: list[str] = []

    def load(path: str) -> str:
        target = root / path
        if not target.is_file():
            errors.append(f"Missing {path}")
            return ""
        return target.read_text(encoding="utf-8")

    def json_file(path: str) -> dict:
        content = load(path)
        try:
            data = json.loads(content)
            if not isinstance(data, dict):
                raise ValueError("Expected object")
            return data
        except (ValueError, json.JSONDecodeError) as exc:
            errors.append(f"Invalid JSON in {path}: {exc}")
            return {}

    home = load("docs/index.md")
    reader = load("docs/2084/index.md")
    codex = load("docs/dna-codex/index.md")
    css = load("docs/stylesheets/evolution.css")
    js = load("docs/javascripts/evolution-reader.js")
    config = load("mkdocs.yml")
    bio = load("docs/JUPITER_HUDSON_BIOGRAPHY.md")
    review = load("docs/EVOLUTION_RELEASE_NOTES.md")
    glyphs = json_file("library/glitchology-reader-symbols.v1.json")
    ledger = json_file("library/cmb-gate-claims.v1.json")
    schema = json_file("schemas/cmb.gate-claim-ledger.v1.schema.json")
    dictionary = load("docs/GLITCHOLOGY_SYMBOL_DICTIONARY.md")

    gateway = re.search(r'<nav id="cmb-evolution-gates"[^>]*>(.*?)</nav>', home, re.S)
    routes = re.findall(r'<a class="cmb-evolution__link" href="([^"]+)"', gateway.group(1)) if gateway else []
    if routes != ["2084/", "concepts/what-is-cmb/", "GLITCHOLOGY_SYMBOL_DICTIONARY/", "EVIDENCE_REVIEW_REGISTER/"]:
        errors.append("Four-gateway navigation missing or out of order")
    if 'stylesheets/evolution.css' not in config or 'javascripts/evolution-reader.js' not in config:
        errors.append("Evolution assets not registered in MkDocs")
    for requirement in ("prefers-reduced-motion", ":focus-visible", "max-width: 780px"):
        if requirement not in css:
            errors.append(f"Visual accessibility marker missing: {requirement}")
    if "localStorage" in js or "sendBeacon" in js:
        errors.append("Reader must not track or retain completed choices")
    if len(re.findall(r'data-chapter="\d+"', reader)) != 9 or len(re.findall(r'data-era="sequel"', reader)) != 4:
        errors.append("Canonical nine-transmission reader or sequel distinction missing")
    seo_specs = load("scripts/enrich_search_metadata.py")
    for route in NINE:
        if f'"{route}/": PageSpec(' not in seo_specs:
            errors.append(f"SEO page registry missing canonical route: {route}")
        if f'../{route}/' not in reader or not (root / "docs" / f"{route}.md").is_file():
            errors.append(f"Missing canonical transmission route: {route}")
        if route not in js:
            errors.append(f"JS previous/next navigation missing: {route}")
    if "Fiction is not evidence" not in codex:
        errors.append("Seven Gates source boundary missing")
    if len(re.findall(r'data-dna-gate="[LUCIFER]"', codex)) != 7:
        errors.append("Expected exactly seven fictional gates")
    if not schema or schema.get("$id", "").split("/")[-1] != "cmb.gate-claim-ledger.v1.schema.json":
        errors.append("Gate ledger schema absent or malformed")
    if ledger.get("schema_version") != "cmb.gate-claim-ledger.v1":
        errors.append("Gate ledger version mismatch")
    entries = ledger.get("entries", [])
    if not isinstance(entries, list) or len(entries) != 7:
        errors.append("Expected exactly seven gate claim records")
    else:
        if [entry.get("gate") for entry in entries if isinstance(entry, dict)] != list(LETTERS):
            errors.append("Seven letters must retain LUCIFER order")
        for entry in entries:
            if not isinstance(entry, dict):
                errors.append("Invalid gate record")
                continue
            if entry.get("independently_reviewed") is not False or entry.get("review_status") != "pending":
                errors.append(f"Unverified gate claim marked reviewed: {entry.get('gate')}")
            for key in ("fiction_route", "context_route"):
                route = entry.get(key, "")
                if not re.fullmatch(r"(?:[A-Za-z0-9_-]+/)+", route):
                    errors.append(f"Unsafe route for {entry.get('gate')}: {key}")
                    continue
                doc = root / "docs" / (route.rstrip("/") + ".md")
                index = root / "docs" / route / "index.md"
                if not (doc.is_file() or index.is_file()):
                    errors.append(f"Missing gate context target: {route}")
    symbols = glyphs.get("symbols", [])
    if len(symbols) != 10 or glyphs.get("schema_version") != "cmb.glitchology.reader-symbols.v1":
        errors.append("Canonical reader symbols missing")
    else:
        if [s.get("id") for s in symbols] != [f"GLT-{i:04d}" for i in range(27, 37)]:
            errors.append("Canonical glyph IDs changed")
        if [s.get("name") for s in symbols] != list(NAMES):
            errors.append("Canonical glyph names changed")
        for s in symbols:
            if not all(str(s.get(k, "")).strip() for k in ("id", "glyph", "name", "meaning")):
                errors.append(f"Empty glyph entry {s.get('id')}")
            if s.get("id") not in dictionary or s.get("name") not in dictionary:
                errors.append(f"Dictionary drift for {s.get('id')}")
    for required in ("Creator declarations", "Independent secondary", "Source classification"):
        if required not in bio:
            errors.append(f"Biography source boundary missing: {required}")
    for required in ("freeze-boundary exceptions", "SELF_TEST != INDEPENDENT_AUDIT", "PUBLISHED != INDEXED"):
        if required not in review:
            errors.append(f"Release review boundary missing: {required}")
    return errors


def main() -> int:
    errors = audit()
    for error in errors:
        print("ERROR:", error, file=sys.stderr)
    if errors:
        return 1
    print("Evolution source audit passed: four portals, nine chapters, seven gates, ten glyphs, evidence and release boundaries.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
