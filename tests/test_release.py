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


def test_canonical_public_artifact_set_is_exact() -> None:
    assert CANONICAL_PUBLIC_ARTIFACTS == (
        "MANIFESTO.md",
        "manifestos/RECLAIMING_THE_PEN_EIGHT_LANGUAGES.md",
        "CMB_Polyglot_Firewall_Specification.md",
        "manifestos/DEMONS_NEED_ATTENTION_DNA.md",
        "manifestos/DNA_PROPHECY_QUESTION_MARK_2030.md",
        "manifestos/DNA_CHICKEN_RUN_MANIFESTO.md",
        "manifestos/CMB_UNCLASSIFIABLE_INDEX.md",
        "manifestos/HARMONI_PERFECT_PLAY_EPISTEMICS.md",
        "manifestos/CMB_Z13_MANIFESTO.md",
        "manifestos/CMB_Z13_LANGUAGE_SPEC.md",
        "library/cmb-z13.registry.json",
        "docs/CREATOR_PROVENANCE.md",
        "library/creator-provenance.json",
        "schemas/cmb.creator-provenance.v1.schema.json",
        "policy/CMB_GLOBAL_ADVOCACY_CHARTER.md",
        "docs/CMB_EDU_KIDS.md",
        "schemas/cmb.edu.v1.schema.json",
        "library/catalog.json",
        "agents/registry.json",
        "agents/agent-card.json",
        "docs/AGENT_DISCOVERY_PROTOCOL.md",
        "schemas/cmb.agent-registry.v1.schema.json",
        "docs/RECOVERY_AND_PRESERVATION.md",
        "machine/recovery-map.json",
        "schemas/cmb.recovery-map.v1.schema.json",
        "datasets/cmb-canonical-corpus/manifest.json",
        "datasets/cmb-canonical-corpus/corpus.jsonl",
        "schemas/cmb.canonical-corpus-manifest.v1.schema.json",
        "schemas/cmb.canonical-corpus-record.v1.schema.json",
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
    assert "cmb-edu --version" in workflow
    assert "cmb-edu validate" in workflow
    assert "cmb-recovery audit" in workflow


def test_ci_generates_and_verifies_canonical_receipt() -> None:
    repository_root = Path(__file__).resolve().parents[1]
    workflow = (
        repository_root / ".github" / "workflows" / "ci.yml"
    ).read_text(encoding="utf-8")

    assert "python scripts/seal_canonical_artifacts.py" in workflow
    assert "--print-json" in workflow


def test_previous_bootstrap_receipt_remains_valid_history() -> None:
    repository_root = Path(__file__).resolve().parents[1]
    receipt = load_receipt(
        repository_root / "receipts" / "canonical-593fd2a6.cmb-receipt.json"
    )

    assert receipt.coverage.paths == (
        "CMB_Polyglot_Firewall_Specification.md",
        "MANIFESTO.md",
        "manifestos/DEMONS_NEED_ATTENTION_DNA.md",
        "policy/CMB_GLOBAL_ADVOCACY_CHARTER.md",
    )
    assert receipt.coverage.excludes_unlisted is True
    assert receipt.manifest_sha256 == (
        "619308c7c322a65b2159679b742e28f61f8558c43cb48dd09229745814043abc"
    )
    artifacts = {artifact.path: artifact for artifact in receipt.manifest.artifacts}
    assert artifacts["policy/CMB_GLOBAL_ADVOCACY_CHARTER.md"].sha256 == (
        "b85e07d891e605854762970ae5fde651f1f559177de2c404225ee430c170b203"
    )


def test_legacy_bootstrap_receipt_remains_valid_history() -> None:
    repository_root = Path(__file__).resolve().parents[1]
    receipt = load_receipt(
        repository_root / "receipts" / "canonical-5139aa72.cmb-receipt.json"
    )

    assert receipt.coverage.paths == (
        "CMB_Polyglot_Firewall_Specification.md",
        "MANIFESTO.md",
        "manifestos/DEMONS_NEED_ATTENTION_DNA.md",
    )
    assert receipt.coverage.excludes_unlisted is True
