from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from cmb_provenance import load_receipt
from cmb_provenance.release import CANONICAL_PUBLIC_ARTIFACTS, build_checksums


def test_release_checksums_are_sorted_and_repeatable(tmp_path: Path) -> None:
    (tmp_path / "z.whl").write_bytes(b"z")
    (tmp_path / "a.tar.gz").write_bytes(b"a")
    output = tmp_path / "SHA256SUMS"

    files = build_checksums(tmp_path, output)
    first = output.read_text(encoding="utf-8")
    build_checksums(tmp_path, output)

    assert [path.name for path in files] == ["a.tar.gz", "z.whl"]
    assert first == output.read_text(encoding="utf-8")
    assert first.splitlines() == [
        f"{hashlib.sha256(b'a').hexdigest()}  a.tar.gz",
        f"{hashlib.sha256(b'z').hexdigest()}  z.whl",
    ]


def test_release_checksums_require_artifacts(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="No release files"):
        build_checksums(tmp_path, tmp_path / "SHA256SUMS")


def test_canonical_public_artifact_set_is_exact_and_includes_dna() -> None:
    assert CANONICAL_PUBLIC_ARTIFACTS == (
        "MANIFESTO.md",
        "CMB_Polyglot_Firewall_Specification.md",
        "manifestos/DEMONS_NEED_ATTENTION_DNA.md",
    )


def test_canonical_public_artifacts_exist_in_repository() -> None:
    repository_root = Path(__file__).resolve().parents[1]
    missing = [
        path
        for path in CANONICAL_PUBLIC_ARTIFACTS
        if not (repository_root / path).is_file()
    ]
    assert missing == []


def test_release_workflow_uses_canonical_sealing_script() -> None:
    repository_root = Path(__file__).resolve().parents[1]
    workflow = (
        repository_root / ".github" / "workflows" / "release.yml"
    ).read_text(encoding="utf-8")

    assert "python scripts/seal_canonical_artifacts.py" in workflow
    assert "--output dist/cmb-source.cmb-receipt.json" in workflow


def test_ci_generates_and_verifies_canonical_receipt() -> None:
    repository_root = Path(__file__).resolve().parents[1]
    workflow = (
        repository_root / ".github" / "workflows" / "ci.yml"
    ).read_text(encoding="utf-8")

    assert "python scripts/seal_canonical_artifacts.py" in workflow
    assert "--print-json" in workflow


def test_checked_in_bootstrap_receipt_covers_dna() -> None:
    repository_root = Path(__file__).resolve().parents[1]
    receipt = load_receipt(
        repository_root / "receipts" / "canonical-5139aa72.cmb-receipt.json"
    )

    assert receipt.coverage.paths == tuple(sorted(CANONICAL_PUBLIC_ARTIFACTS))
    assert receipt.coverage.excludes_unlisted is True
    assert "manifestos/DEMONS_NEED_ATTENTION_DNA.md" in receipt.coverage.paths
