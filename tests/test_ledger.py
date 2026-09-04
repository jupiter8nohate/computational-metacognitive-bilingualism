from __future__ import annotations

import json
import multiprocessing
import os
from pathlib import Path

import pytest

from cmb_provenance import (
    LedgerError,
    LockTimeoutError,
    append_anchor,
    load_ledger,
    save_receipt,
    seal,
)
from cmb_provenance.locking import FileLock

ZERO_COMMIT = "0" * 40
FIXED_TIME = "2000-01-01T00:00:00Z"


def _make_receipt(tmp_path: Path):
    artifact = tmp_path / "artifact.txt"
    artifact.write_bytes(b"artifact")
    return seal(
        artifact.name,
        base_dir=tmp_path,
        git_commit=ZERO_COMMIT,
        created_at_utc=FIXED_TIME,
    )


def _append_worker(receipt_path: str, ledger_path: str, worker_number: int) -> None:
    append_anchor(
        receipt_path,
        anchor_type="other",
        location=f"worker://{worker_number}",
        description=f"concurrent writer {worker_number}",
        ledger_path=ledger_path,
        lock_timeout=20,
    )


def test_anchor_round_trip_and_hash_chain(tmp_path: Path) -> None:
    receipt = _make_receipt(tmp_path)
    ledger = tmp_path / "anchors.jsonl"
    first = append_anchor(
        receipt,
        anchor_type="other",
        location="test://one",
        description="first reference",
        ledger_path=ledger,
        local_recorded_at_utc="2000-01-01T00:00:01Z",
    )
    second = append_anchor(
        receipt,
        anchor_type="public_post",
        location="https://example.test/post",
        description="second reference",
        ledger_path=ledger,
        claimed_external_time_utc="2000-01-01T01:00:02+01:00",
        external_time_basis="displayed by source",
        local_recorded_at_utc="2000-01-01T00:00:03Z",
    )

    loaded = load_ledger(ledger)

    assert [record.sequence for record in loaded] == [1, 2]
    assert second.previous_record_sha256 == first.record_sha256
    assert loaded[1].claimed_external_time_utc == "2000-01-01T00:00:02Z"


def test_corrupted_record_is_detected(tmp_path: Path) -> None:
    receipt = _make_receipt(tmp_path)
    ledger = tmp_path / "anchors.jsonl"
    append_anchor(
        receipt,
        anchor_type="other",
        location="test://original",
        description="reference",
        ledger_path=ledger,
    )
    ledger.write_text(
        ledger.read_text(encoding="utf-8").replace("test://original", "test://corrupt"),
        encoding="utf-8",
    )

    with pytest.raises(LedgerError, match="integrity"):
        load_ledger(ledger)


def test_unknown_record_field_is_rejected(tmp_path: Path) -> None:
    receipt = _make_receipt(tmp_path)
    ledger = tmp_path / "anchors.jsonl"
    append_anchor(
        receipt,
        anchor_type="other",
        location="test://one",
        description="reference",
        ledger_path=ledger,
    )
    raw = json.loads(ledger.read_text(encoding="utf-8"))
    raw["unexpected"] = "schema drift"
    ledger.write_text(json.dumps(raw, separators=(",", ":")) + "\n", encoding="utf-8")

    with pytest.raises(LedgerError, match="unknown"):
        load_ledger(ledger)


def test_missing_final_newline_refuses_append(tmp_path: Path) -> None:
    receipt = _make_receipt(tmp_path)
    ledger = tmp_path / "anchors.jsonl"
    first = append_anchor(
        receipt,
        anchor_type="other",
        location="test://one",
        description="reference",
        ledger_path=ledger,
    )
    ledger.write_bytes(ledger.read_bytes().rstrip(b"\n"))

    with pytest.raises(LedgerError, match="does not end with a newline"):
        append_anchor(
            receipt,
            anchor_type="other",
            location="test://two",
            description="reference two",
            ledger_path=ledger,
        )
    assert first.sequence == 1


def test_lock_timeout_is_bounded(tmp_path: Path) -> None:
    ledger = tmp_path / "anchors.jsonl"
    with FileLock(ledger, timeout=1):
        with pytest.raises(LockTimeoutError, match="Timed out"):
            with FileLock(ledger, timeout=0.05, poll_interval=0.01):
                pass


def test_concurrent_writers_preserve_every_record(tmp_path: Path) -> None:
    receipt_path = save_receipt(_make_receipt(tmp_path), tmp_path / "receipt.json")
    ledger = tmp_path / "anchors.jsonl"
    context = multiprocessing.get_context("spawn")
    processes = [
        context.Process(
            target=_append_worker, args=(str(receipt_path), str(ledger), number)
        )
        for number in range(8)
    ]

    for process in processes:
        process.start()
    for process in processes:
        process.join(timeout=30)
        assert process.exitcode == 0

    records = load_ledger(ledger)
    assert len(records) == 8
    assert [record.sequence for record in records] == list(range(1, 9))
    assert len({record.location for record in records}) == 8


@pytest.mark.skipif(
    os.name == "nt", reason="Windows symlink creation requires optional privileges"
)
def test_symbolic_link_ledger_is_rejected(tmp_path: Path) -> None:
    receipt = _make_receipt(tmp_path)
    target = tmp_path / "target.jsonl"
    target.write_bytes(b"")
    ledger = tmp_path / "anchors.jsonl"
    ledger.symlink_to(target)

    with pytest.raises(LedgerError, match="symbolic-link"):
        append_anchor(
            receipt,
            anchor_type="other",
            location="test://one",
            description="reference",
            ledger_path=ledger,
        )
