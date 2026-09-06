from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from cmb_provenance import (
    SchemaValidationError,
    SealError,
    load_receipt,
    save_receipt,
    seal,
    verify,
)
from cmb_provenance.schemas import load_json_strict, validate_receipt
from cmb_provenance.timeutil import normalize_timestamp

FIXTURE_SHA256 = "8247e78df7923748cebc5f6df8a3725d60f018fbf09fc4d03ebce1778020849c"
FIXTURE_MANIFEST_SHA256 = (
    "1ab27ed0962fd55146397cc5dd04dd1eac441745a49df64350a08b7b9fa7f78a"
)
ZERO_COMMIT = "0" * 40
FIXED_TIME = "2000-01-01T00:00:00Z"


def test_deterministic_fixture_hash_and_manifest() -> None:
    receipt = seal(
        "tests/fixtures/deterministic.txt",
        base_dir=".",
        git_commit=ZERO_COMMIT,
        created_at_utc=FIXED_TIME,
    )

    assert receipt.manifest.artifacts[0].sha256 == FIXTURE_SHA256
    assert receipt.manifest_sha256 == FIXTURE_MANIFEST_SHA256
    assert receipt.manifest.git_commit_status == "CALLER_SUPPLIED_UNVERIFIED"
    assert receipt.coverage.paths == ("tests/fixtures/deterministic.txt",)
    assert receipt.coverage.excludes_unlisted is True


def test_seal_sorts_multiple_paths_and_records_exact_coverage(tmp_path: Path) -> None:
    (tmp_path / "z.txt").write_bytes(b"z")
    (tmp_path / "a.txt").write_bytes(b"a")

    receipt = seal(
        ["z.txt", "a.txt"],
        base_dir=tmp_path,
        git_commit=ZERO_COMMIT,
        created_at_utc=FIXED_TIME,
    )

    assert receipt.coverage.paths == ("a.txt", "z.txt")
    assert tuple(item.path for item in receipt.manifest.artifacts) == ("a.txt", "z.txt")


def test_verify_detects_byte_mutation(tmp_path: Path) -> None:
    artifact = tmp_path / "work.txt"
    artifact.write_bytes(b"original")
    receipt = seal(
        artifact.name,
        base_dir=tmp_path,
        git_commit=ZERO_COMMIT,
        created_at_utc=FIXED_TIME,
    )
    assert verify(artifact.name, receipt, base_dir=tmp_path).ok

    artifact.write_bytes(b"mutated")
    result = verify(artifact.name, receipt, base_dir=tmp_path)

    assert not result.ok
    assert {failure.code for failure in result.failures} == {
        "DIGEST_MISMATCH",
        "SIZE_MISMATCH",
    }


def test_verify_rejects_incomplete_and_extra_coverage(tmp_path: Path) -> None:
    for name in ("one.txt", "two.txt", "extra.txt"):
        (tmp_path / name).write_text(name, encoding="utf-8")
    receipt = seal(
        ["one.txt", "two.txt"],
        base_dir=tmp_path,
        git_commit=ZERO_COMMIT,
        created_at_utc=FIXED_TIME,
    )

    result = verify(["one.txt", "extra.txt"], receipt, base_dir=tmp_path)

    assert not result.ok
    assert {failure.code for failure in result.failures} == {
        "MISSING_COVERAGE",
        "UNSEALED_PATH",
    }


def test_receipt_round_trip_is_json_compatible(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.txt"
    artifact.write_text("human agency", encoding="utf-8")
    receipt = seal(
        artifact.name,
        base_dir=tmp_path,
        git_commit=ZERO_COMMIT,
        created_at_utc=FIXED_TIME,
    )

    destination = save_receipt(receipt, tmp_path / "receipt.json")
    loaded = load_receipt(destination)

    assert loaded == receipt
    assert json.loads(destination.read_text(encoding="utf-8")) == receipt.to_dict()


def test_strict_schema_rejects_unknown_fields(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.txt"
    artifact.write_bytes(b"x")
    raw = seal(
        artifact.name,
        base_dir=tmp_path,
        git_commit=ZERO_COMMIT,
        created_at_utc=FIXED_TIME,
    ).to_dict()
    raw["unexpected"] = True

    with pytest.raises(SchemaValidationError, match="unknown"):
        validate_receipt(raw)


def test_strict_schema_rejects_unknown_nested_fields(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.txt"
    artifact.write_bytes(b"x")
    raw = seal(
        artifact.name,
        base_dir=tmp_path,
        git_commit=ZERO_COMMIT,
        created_at_utc=FIXED_TIME,
    ).to_dict()
    raw["manifest"]["artifacts"][0]["unexpected"] = True

    with pytest.raises(SchemaValidationError, match="unknown"):
        validate_receipt(raw)


def test_strict_schema_rejects_invalid_commit_status(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.txt"
    artifact.write_bytes(b"x")
    raw = seal(
        artifact.name,
        base_dir=tmp_path,
        git_commit=ZERO_COMMIT,
        created_at_utc=FIXED_TIME,
    ).to_dict()
    raw["manifest"]["git_commit_status"] = "TRUST_ME"

    with pytest.raises(SchemaValidationError, match="git_commit_status"):
        validate_receipt(raw)


def test_strict_schema_rejects_coverage_drift(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.txt"
    artifact.write_bytes(b"x")
    raw = seal(
        artifact.name,
        base_dir=tmp_path,
        git_commit=ZERO_COMMIT,
        created_at_utc=FIXED_TIME,
    ).to_dict()
    raw["coverage"]["paths"] = ["different.txt"]

    with pytest.raises(SchemaValidationError, match="exactly match"):
        validate_receipt(raw)


def test_strict_json_rejects_duplicate_keys() -> None:
    with pytest.raises(SchemaValidationError, match="Duplicate"):
        load_json_strict('{"schema_version":"one","schema_version":"two"}')


def test_timestamp_normalization() -> None:
    assert normalize_timestamp("2026-09-04T04:30:00-04:00") == "2026-09-04T08:30:00Z"
    assert (
        normalize_timestamp("2026-09-04T08:30:00.120000Z") == "2026-09-04T08:30:00.12Z"
    )
    assert (
        normalize_timestamp("2026-09-04T09:26:28.80233Z")
        == "2026-09-04T09:26:28.80233Z"
    )
    with pytest.raises(SchemaValidationError, match="explicit timezone"):
        normalize_timestamp("2026-09-04T08:30:00")


def test_seal_normalizes_explicit_timestamp(tmp_path: Path) -> None:
    (tmp_path / "a").write_bytes(b"a")
    receipt = seal(
        "a",
        base_dir=tmp_path,
        git_commit=ZERO_COMMIT,
        created_at_utc="2026-09-04T04:30:00-04:00",
    )
    assert receipt.created_at_utc == "2026-09-04T08:30:00Z"


def test_seal_rejects_duplicate_paths(tmp_path: Path) -> None:
    (tmp_path / "a").write_bytes(b"a")
    with pytest.raises(SealError, match="more than once"):
        seal(["a", "a"], base_dir=tmp_path, git_commit=ZERO_COMMIT)


def test_seal_rejects_path_outside_root(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside.txt"
    outside.write_bytes(b"outside")
    try:
        with pytest.raises(SealError, match="outside sealing root"):
            seal(outside, base_dir=tmp_path, git_commit=ZERO_COMMIT)
    finally:
        outside.unlink(missing_ok=True)


@pytest.mark.skipif(
    os.name == "nt", reason="Windows symlink creation requires optional privileges"
)
def test_seal_rejects_symbolic_links(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.write_bytes(b"target")
    link = tmp_path / "link"
    link.symlink_to(target)
    with pytest.raises(SealError, match="symbolic link"):
        seal("link", base_dir=tmp_path, git_commit=ZERO_COMMIT)


@pytest.mark.skipif(shutil.which("git") is None, reason="Git is not installed")
def test_automatic_git_commit_requires_exact_committed_bytes(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(
        ["git", "-C", str(tmp_path), "config", "user.name", "CMB Test"], check=True
    )
    subprocess.run(
        ["git", "-C", str(tmp_path), "config", "user.email", "cmb@example.invalid"],
        check=True,
    )
    artifact = tmp_path / "tracked.txt"
    artifact.write_bytes(b"committed bytes\n")
    subprocess.run(["git", "-C", str(tmp_path), "add", "tracked.txt"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-qm", "fixture"], check=True)

    receipt = seal("tracked.txt", base_dir=tmp_path, created_at_utc=FIXED_TIME)
    assert receipt.manifest.git_commit_status == "VERIFIED_ARTIFACTS_MATCH_COMMIT"

    artifact.write_bytes(b"uncommitted bytes\n")
    with pytest.raises(SealError, match="differs byte-for-byte"):
        seal("tracked.txt", base_dir=tmp_path, created_at_utc=FIXED_TIME)
