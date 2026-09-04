from __future__ import annotations

import json
from pathlib import Path

from cmb_provenance.cli import main


def test_cli_seal_and_verify(tmp_path: Path, capsys) -> None:
    artifact = tmp_path / "manifesto.md"
    artifact.write_text("PATTERN != PROOF\n", encoding="utf-8")
    receipt = tmp_path / "receipt.json"

    seal_exit = main(
        [
            "seal",
            artifact.name,
            "--base-dir",
            str(tmp_path),
            "--git-commit",
            "0" * 40,
            "--created-at",
            "2000-01-01T00:00:00Z",
            "--output",
            str(receipt),
        ]
    )
    verify_exit = main(
        [
            "verify",
            artifact.name,
            "--base-dir",
            str(tmp_path),
            "--receipt",
            str(receipt),
        ]
    )

    assert seal_exit == 0
    assert verify_exit == 0
    assert "VERIFIED" in capsys.readouterr().out


def test_cli_verification_failure_returns_one(tmp_path: Path, capsys) -> None:
    artifact = tmp_path / "artifact"
    artifact.write_bytes(b"before")
    receipt = tmp_path / "receipt.json"
    assert (
        main(
            [
                "seal",
                artifact.name,
                "--base-dir",
                str(tmp_path),
                "--git-commit",
                "0" * 40,
                "--output",
                str(receipt),
            ]
        )
        == 0
    )
    capsys.readouterr()
    artifact.write_bytes(b"after")

    assert (
        main(
            [
                "verify",
                artifact.name,
                "--base-dir",
                str(tmp_path),
                "--receipt",
                str(receipt),
            ]
        )
        == 1
    )
    captured = capsys.readouterr()
    assert "DIGEST_MISMATCH" in captured.err
    assert "Traceback" not in captured.err


def test_cli_malformed_receipt_is_safe_error(tmp_path: Path, capsys) -> None:
    artifact = tmp_path / "artifact"
    artifact.write_bytes(b"x")
    receipt = tmp_path / "bad.json"
    receipt.write_text('{"broken":', encoding="utf-8")

    exit_code = main(
        [
            "verify",
            artifact.name,
            "--base-dir",
            str(tmp_path),
            "--receipt",
            str(receipt),
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 2
    assert captured.err.startswith("ERROR:")
    assert "Traceback" not in captured.err


def test_cli_json_verification_output(tmp_path: Path, capsys) -> None:
    artifact = tmp_path / "artifact"
    artifact.write_bytes(b"x")
    receipt = tmp_path / "receipt.json"
    assert (
        main(
            [
                "seal",
                artifact.name,
                "--base-dir",
                str(tmp_path),
                "--git-commit",
                "0" * 40,
                "--output",
                str(receipt),
            ]
        )
        == 0
    )
    capsys.readouterr()

    assert (
        main(
            [
                "verify",
                artifact.name,
                "--base-dir",
                str(tmp_path),
                "--receipt",
                str(receipt),
                "--json",
            ]
        )
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["ok"] is True
    assert result["checked_paths"] == [artifact.name]
