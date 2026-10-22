"""Create a deterministic SHA-256 manifest for the D.N.A. story reading edition.

Does not sign, publish, archive externally, or modify canonical source.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILES = (
    "docs/ARCHIVE_READING_MAP.md",
    "docs/story-universe/index.md",
    "docs/story-universe/continuity.md",
    "docs/DEATH_NOTE_2084.md",
    "docs/DEATH_NOTE_2084_FALSE_LIGHT.md",
    "docs/DEATH_NOTE_2084_HOUSE_OF_A_MILLION_DOORS.md",
    "docs/DEATH_NOTE_2084_LEDGER_OF_INVISIBLE_CELLS.md",
    "docs/DEATH_NOTE_2084_CHILD_WHO_REFUSED_THE_UPDATE.md",
    "docs/DEATH_NOTE_2084_LEDGER_OF_INVISIBLE_YEARS.md",
    "docs/DEATH_NOTE_2084_POST_GROUND_BASELINE.md",
    "docs/DEATH_NOTE_2084_WITNESS_IN_LIGHTHOUSE.md",
    "docs/DEATH_NOTE_2084_STATION_SEVEN.md",
    "docs/GLITCHOLOGY_SYMBOL_DICTIONARY.md",
    "library/glitchology-reader-symbols.v1.json",
    "docs/EVIDENCE_REVIEW_REGISTER.md",
)


def create_manifest(root: Path, paths: tuple[str, ...] = SOURCE_FILES) -> dict:
    base = root.resolve(strict=True)
    records = []
    for name in sorted(set(paths)):
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"Unsafe archive path: {name}")
        path = (base / relative).resolve(strict=True)
        if not path.is_relative_to(base) or not path.is_file():
            raise ValueError(f"Archive source must be a regular file within root: {name}")
        data = path.read_bytes()
        records.append({"path": relative.as_posix(), "bytes": len(data),
                        "sha256": hashlib.sha256(data).hexdigest()})
    return {"schema_version": "cmb.dna-reader-archive.v1",
            "archive_type": "unsigned_source_inventory",
            "creator": "Jupiter Hudson / WisdomLoveThePoet / Jupiter 8",
            "digest_algorithm": "sha256",
            "claim_boundary": "Hashing does not attest authorship, license ownership, timestamp, or publication.",
            "files": records}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, help="Optional output JSON path")
    args = parser.parse_args()
    try:
        manifest = create_manifest(args.root)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    payload = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
        print(f"Unsigned reader archive manifest written to {args.output}")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
