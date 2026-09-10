import hashlib
from pathlib import Path

import pytest

from cmb_agents.philosophy_evidence import EvidenceError, collect_source_evidence


def test_collects_file_hash_and_excerpt(tmp_path: Path) -> None:
    source = tmp_path / "canon.md"
    source.write_text("PATTERN != PROOF\nHUMAN_AGENCY > MACHINE_AUTHORITY\n", encoding="utf-8")

    records = collect_source_evidence(tmp_path, ["canon.md"])

    assert len(records) == 1
    record = records[0]
    assert record.kind == "file"
    assert record.sha256 == hashlib.sha256(source.read_bytes()).hexdigest()
    assert "PATTERN != PROOF" in record.excerpt
    assert record.files_sampled == 1


def test_collects_directory_sample_deterministically(tmp_path: Path) -> None:
    source_dir = tmp_path / "docs"
    source_dir.mkdir()
    (source_dir / "a.md").write_text("agency", encoding="utf-8")
    (source_dir / "b.txt").write_text("consent", encoding="utf-8")
    (source_dir / "ignored.bin").write_bytes(b"not text evidence")

    first = collect_source_evidence(tmp_path, ["docs"])[0]
    second = collect_source_evidence(tmp_path, ["docs"])[0]

    assert first == second
    assert first.kind == "directory_sample"
    assert first.files_sampled == 2
    assert "[docs/a.md]" in first.excerpt
    assert "[docs/b.txt]" in first.excerpt
    assert "ignored.bin" not in first.excerpt


def test_missing_source_fails_closed_with_evidence_error(tmp_path: Path) -> None:
    with pytest.raises(EvidenceError, match="source path does not exist"):
        collect_source_evidence(tmp_path, ["missing.md"])


def test_absolute_source_path_is_rejected(tmp_path: Path) -> None:
    source = tmp_path / "canon.md"
    source.write_text("agency", encoding="utf-8")

    with pytest.raises(EvidenceError, match="repository-relative"):
        collect_source_evidence(tmp_path, [str(source.resolve())])


def test_parent_escape_is_rejected(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside-cmb-evidence.md"
    outside.write_text("outside", encoding="utf-8")
    try:
        with pytest.raises(EvidenceError, match="escapes repository root"):
            collect_source_evidence(tmp_path, ["../outside-cmb-evidence.md"])
    finally:
        outside.unlink(missing_ok=True)


def test_missing_repo_root_fails_closed(tmp_path: Path) -> None:
    missing_root = tmp_path / "missing-repository"

    with pytest.raises(EvidenceError, match="repository root does not exist"):
        collect_source_evidence(missing_root, ["canon.md"])
