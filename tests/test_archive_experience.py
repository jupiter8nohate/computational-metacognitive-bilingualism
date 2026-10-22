"""Regression tests for the ten-part archive upgrade."""
from __future__ import annotations

import copy
import hashlib
import json
import runpy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
AUDIT = runpy.run_path(str(ROOT / "scripts/verify_archive_experience.py"))
EXPORT = runpy.run_path(str(ROOT / "scripts/export_reader_archive.py"))


def test_archive_source_consistency() -> None:
    assert AUDIT["audit"](ROOT) == []


def test_symbol_registry_fails_on_duplicate_or_relabelled_id() -> None:
    data = json.loads((ROOT / "library/glitchology-reader-symbols.v1.json").read_text(encoding="utf-8"))
    assert AUDIT["check_symbols"](data) == []
    duplicate = copy.deepcopy(data)
    duplicate["symbols"][1]["id"] = duplicate["symbols"][0]["id"]
    assert any("IDs must" in message for message in AUDIT["check_symbols"](duplicate))
    renamed = copy.deepcopy(data)
    renamed["symbols"][0]["name"] = "MAGICAL_PROOF"
    assert any("names or order" in message for message in AUDIT["check_symbols"](renamed))


def test_archive_manifest_is_deterministic_and_hashes_exact_bytes(tmp_path: Path) -> None:
    source = tmp_path / "novel.md"
    source.write_text("Jupiter 8\nPATTERN != PROOF\n", encoding="utf-8")
    first = EXPORT["create_manifest"](tmp_path, ("novel.md",))
    second = EXPORT["create_manifest"](tmp_path, ("novel.md",))
    assert first == second
    assert first["archive_type"] == "unsigned_source_inventory"
    assert first["files"][0]["sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()
    source.write_text("A different ending\n", encoding="utf-8")
    third = EXPORT["create_manifest"](tmp_path, ("novel.md",))
    assert third["files"][0]["sha256"] != first["files"][0]["sha256"]


@pytest.mark.parametrize("unsafe", ["../escape.md", "/tmp/not-in-archive.txt"])
def test_archive_manifest_rejects_path_escape(tmp_path: Path, unsafe: str) -> None:
    with pytest.raises((ValueError, OSError)):
        EXPORT["create_manifest"](tmp_path, (unsafe,))


def test_archive_manifest_rejects_symlink_escape(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside-dna-secret.txt"
    outside.write_text("not archive content", encoding="utf-8")
    link = tmp_path / "link.txt"
    link.symlink_to(outside)
    with pytest.raises(ValueError, match="within root"):
        EXPORT["create_manifest"](tmp_path, ("link.txt",))
