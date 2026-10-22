"""Source-level regression audit for the D.N.A. archive reader and glyph registry.

This verifies structure and internal consistency, not accessibility conformance,
external source truth, independent review, search indexing, or live deployment.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GLYPH_NAMES = (
    "ANOMALY_STARE", "NULL_BREATH", "VERIFICATION_CAGE", "DUAL_WITNESS",
    "SIGNAL_DUST", "BURST_SPEECH", "MICROBREAK", "BLUE_ANOMALY",
    "POST_OBSERVATION", "BACKTRACE",
)
PAGES = (
    "docs/ARCHIVE_READING_MAP.md",
    "docs/GLITCHOLOGY_SYMBOL_DICTIONARY.md",
    "docs/EVIDENCE_REVIEW_REGISTER.md",
    "docs/SEARCH_INDEXING_CHECKLIST.md",
    "docs/ARCHIVE_RELEASE_CHECKLIST.md",
    "docs/stylesheets/archive-upgrades.css",
    "docs/index.md",
    "docs/story-universe/index.md",
    "docs/WITNESS_BACKTRACE_PROTOCOL.md",
    "library/glitchology-reader-symbols.v1.json",
    "mkdocs.yml",
)


def check_symbols(data: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["Symbol registry must be a JSON object"]
    if data.get("schema_version") != "cmb.glitchology.reader-symbols.v1":
        errors.append("Reader symbol registry version mismatch")
    if data.get("type") != "authored_symbolic_dictionary":
        errors.append("Symbol meanings must be labeled as authored")
    symbols = data.get("symbols")
    if not isinstance(symbols, list) or len(symbols) != 10:
        return errors + ["Expected exactly ten reader symbols"]
    ids = [item.get("id") for item in symbols if isinstance(item, dict)]
    names = [item.get("name") for item in symbols if isinstance(item, dict)]
    if len(ids) != len(symbols) or len(set(ids)) != len(ids):
        errors.append("Symbol IDs must be unique and nonempty")
    if ids != [f"GLT-{i:04d}" for i in range(27, 37)]:
        errors.append("Symbol IDs must preserve canonical GLT-0027..GLT-0036 order")
    if names != list(GLYPH_NAMES):
        errors.append("Canonical symbol names or order changed")
    for item in symbols:
        if not isinstance(item, dict):
            errors.append("Each symbol must be an object")
        elif any(not isinstance(item.get(key), str) or not item[key].strip()
                 for key in ("id", "name", "class", "glyph", "meaning")):
            errors.append(f"Incomplete symbol: {item.get('id', 'unknown')}")
    return errors


def audit(root: Path) -> list[str]:
    errors = [f"Required file missing: {path}" for path in PAGES
              if not (root / path).is_file()]
    if errors:
        return errors
    read = lambda path: (root / path).read_text(encoding="utf-8")
    config = read("mkdocs.yml")
    home = read("docs/index.md")
    dictionary = read("docs/GLITCHOLOGY_SYMBOL_DICTIONARY.md")
    guide = read("docs/ARCHIVE_READING_MAP.md")
    css = read("docs/stylesheets/archive-upgrades.css")
    for page in (
        "ARCHIVE_READING_MAP.md", "GLITCHOLOGY_SYMBOL_DICTIONARY.md",
        "EVIDENCE_REVIEW_REGISTER.md", "SEARCH_INDEXING_CHECKLIST.md",
        "ARCHIVE_RELEASE_CHECKLIST.md",
    ):
        if f": {page}" not in config:
            errors.append(f"Page absent from MkDocs nav: {page}")
    if "stylesheets/archive-upgrades.css" not in config:
        errors.append("Archive stylesheet absent from MkDocs")
    match = re.search(r'<nav class="cmb-archive-doors"[^>]*>(.*?)</nav>', home, re.S)
    if not match:
        errors.append("Three-door accessible homepage navigation missing")
    else:
        hrefs = re.findall(r'<a\s[^>]*href="([^"]+)"', match.group(1))
        if hrefs != ["ARCHIVE_READING_MAP/", "EVIDENCE_REVIEW_REGISTER/", "DEVELOPERS/"]:
            errors.append(f"Expected exactly three working entry routes, found {hrefs!r}")
    if not re.search(r'class="cmb-archive-pyramid"[^>]*aria-hidden="true"', home):
        errors.append("Decorative pyramid must be hidden from screen readers")
    if "prefers-reduced-motion" not in css or ":focus-visible" not in css:
        errors.append("Archive UI needs reduced-motion and visible focus CSS")
    if "max-width: 780px" not in css:
        errors.append("Archive doors need a responsive mobile layout")
    try:
        data = json.loads(read("library/glitchology-reader-symbols.v1.json"))
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid reader symbol JSON: {exc}")
    else:
        errors.extend(check_symbols(data))
        for item in data.get("symbols", []):
            if isinstance(item, dict) and item.get("id") not in dictionary:
                errors.append(f"Missing symbol in reader dictionary: {item.get('id')}")
    for path in re.findall(r"\]\(([^)]+\.md)(?:#[^)]*)?\)", guide):
        if "://" not in path and not (root / "docs" / path).is_file():
            errors.append(f"Reader map links to missing Markdown: {path}")
    evidence = read("docs/EVIDENCE_REVIEW_REGISTER.md")
    if "SELF_TEST != INDEPENDENT_REVIEW" not in evidence:
        errors.append("Evidence register must disclose its verification limit")
    release = read("docs/ARCHIVE_RELEASE_CHECKLIST.md")
    if "RELEASE_CANDIDATE != SIGNED_RELEASE" not in release:
        errors.append("Release checklist must distinguish candidate from signed release")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    errors = audit(args.root.resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Archive reader/source audit passed (not a live site or independent audit).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
