"""Locked, strict, tamper-evident ledger for public evidence references."""

from __future__ import annotations

import hmac
import os
import stat
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any

from .canonical import canonical_json_bytes, sha256_bytes
from .constants import (
    ANCHOR_SCHEMA_VERSION,
    ANCHOR_TYPES,
    DEFAULT_LEDGER_NAME,
    UNVERIFIED_REFERENCE_STATUS,
)
from .errors import LedgerError, SchemaValidationError
from .locking import FileLock
from .schemas import load_json_strict, validate_anchor_record
from .sealing import ReceiptInput, coerce_receipt
from .timeutil import normalize_timestamp, utc_now_iso


@dataclass(frozen=True, slots=True)
class AnchorRecord:
    schema_version: str
    sequence: int
    anchor_type: str
    description: str
    location: str
    manifest_sha256: str
    local_recorded_at_utc: str
    claimed_external_time_utc: str | None
    external_time_basis: str | None
    verification_status: str
    previous_record_sha256: str | None
    record_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _record_from_dict(raw: dict[str, Any]) -> AnchorRecord:
    try:
        validate_anchor_record(raw)
        record = AnchorRecord(**raw)
    except (SchemaValidationError, TypeError) as exc:
        raise LedgerError(str(exc)) from exc
    expected = compute_record_sha256(record)
    if not hmac.compare_digest(expected, record.record_sha256):
        raise LedgerError(
            f"Anchor record {record.sequence} failed its SHA-256 integrity check."
        )
    return record


def compute_record_sha256(record: AnchorRecord) -> str:
    payload = record.to_dict()
    payload.pop("record_sha256")
    return sha256_bytes(canonical_json_bytes(payload))


def _load_unlocked(path: Path) -> list[AnchorRecord]:
    try:
        if path.is_symlink():
            raise LedgerError(f"Refusing to read symbolic-link ledger: {path}")
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
        flags |= getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(path, flags)
    except FileNotFoundError:
        return []
    except LedgerError:
        raise
    except OSError as exc:
        raise LedgerError(f"Unable to open ledger {path}: {exc}") from exc

    try:
        with os.fdopen(descriptor, "rb") as handle:
            before = os.fstat(handle.fileno())
            if not stat.S_ISREG(before.st_mode):
                raise LedgerError(f"Ledger is not a regular file: {path}")
            if before.st_size > 128 * 1024 * 1024:
                raise LedgerError(f"Ledger exceeds the 128 MiB safety limit: {path}")
            encoded = handle.read()
            after = os.fstat(handle.fileno())
        identity_before = (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_mtime_ns,
        )
        identity_after = (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
        )
        if identity_before != identity_after:
            raise LedgerError(f"Ledger changed while it was being read: {path}")
        if encoded and not encoded.endswith(b"\n"):
            raise LedgerError(
                f"Refusing to read: existing ledger does not end with a newline: {path}"
            )
        lines = encoded.decode("utf-8").splitlines()
    except LedgerError:
        raise
    except (OSError, UnicodeError) as exc:
        raise LedgerError(f"Unable to read ledger {path}: {exc}") from exc

    records: list[AnchorRecord] = []
    previous_hash: str | None = None
    for line_number, line in enumerate(lines, start=1):
        if not line:
            raise LedgerError(f"Blank line detected at ledger line {line_number}.")
        try:
            raw = load_json_strict(line)
            if not isinstance(raw, dict):
                raise SchemaValidationError("Anchor record must be a JSON object.")
            record = _record_from_dict(raw)
        except (SchemaValidationError, LedgerError) as exc:
            raise LedgerError(
                f"Invalid anchor record at line {line_number}: {exc}"
            ) from exc

        expected_sequence = len(records) + 1
        if record.sequence != expected_sequence:
            raise LedgerError(
                f"Sequence break at line {line_number}: expected {expected_sequence}, got {record.sequence}."
            )
        if record.previous_record_sha256 != previous_hash:
            raise LedgerError(f"Hash-chain break at line {line_number}.")
        records.append(record)
        previous_hash = record.record_sha256
    return records


def _append_unlocked(path: Path, record: AnchorRecord) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        if path.is_symlink():
            raise LedgerError(f"Refusing to append symbolic-link ledger: {path}")
        flags = os.O_RDWR | os.O_APPEND | os.O_CREAT
        flags |= getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(path, flags, 0o600)
        encoded = canonical_json_bytes(record.to_dict()) + b"\n"
        with os.fdopen(descriptor, "r+b", buffering=0) as handle:
            current = os.fstat(handle.fileno())
            if not stat.S_ISREG(current.st_mode):
                raise LedgerError(f"Ledger is not a regular file: {path}")
            if current.st_size:
                handle.seek(-1, os.SEEK_END)
                if handle.read(1) != b"\n":
                    raise LedgerError(
                        f"Refusing to append: existing ledger does not end with a newline: {path}"
                    )
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        if os.name != "nt":
            directory_fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
    except LedgerError:
        raise
    except OSError as exc:
        raise LedgerError(f"Unable to append ledger {path}: {exc}") from exc


def load_ledger(
    path: str | os.PathLike[str] = DEFAULT_LEDGER_NAME,
    *,
    lock_timeout: float = 10.0,
) -> list[AnchorRecord]:
    ledger_path = Path(path)
    with FileLock(ledger_path, timeout=lock_timeout):
        return _load_unlocked(ledger_path)


def verify_ledger(
    path: str | os.PathLike[str] = DEFAULT_LEDGER_NAME,
    *,
    lock_timeout: float = 10.0,
) -> tuple[int, str | None]:
    records = load_ledger(path, lock_timeout=lock_timeout)
    return len(records), records[-1].record_sha256 if records else None


def append_anchor(
    receipt: ReceiptInput,
    *,
    anchor_type: str,
    location: str,
    description: str,
    ledger_path: str | os.PathLike[str] = DEFAULT_LEDGER_NAME,
    claimed_external_time_utc: str | None = None,
    external_time_basis: str | None = None,
    local_recorded_at_utc: str | None = None,
    lock_timeout: float = 10.0,
) -> AnchorRecord:
    """Validate the receipt, lock the whole read-modify-append operation, and append."""

    sealed = coerce_receipt(receipt)
    if anchor_type not in ANCHOR_TYPES:
        raise LedgerError(f"anchor_type must be one of {ANCHOR_TYPES}.")
    location = location.strip()
    description = description.strip()
    if not location or not description:
        raise LedgerError("location and description must not be empty.")
    if (claimed_external_time_utc is None) != (external_time_basis is None):
        raise LedgerError(
            "claimed_external_time_utc and external_time_basis must both be supplied or both omitted."
        )
    claimed = (
        normalize_timestamp(claimed_external_time_utc)
        if claimed_external_time_utc
        else None
    )
    basis = external_time_basis.strip() if external_time_basis is not None else None
    recorded = (
        normalize_timestamp(local_recorded_at_utc)
        if local_recorded_at_utc
        else utc_now_iso()
    )

    path = Path(ledger_path)
    with FileLock(path, timeout=lock_timeout):
        records = _load_unlocked(path)
        provisional = AnchorRecord(
            schema_version=ANCHOR_SCHEMA_VERSION,
            sequence=len(records) + 1,
            anchor_type=anchor_type,
            description=description,
            location=location,
            manifest_sha256=sealed.manifest_sha256,
            local_recorded_at_utc=recorded,
            claimed_external_time_utc=claimed,
            external_time_basis=basis,
            verification_status=UNVERIFIED_REFERENCE_STATUS,
            previous_record_sha256=records[-1].record_sha256 if records else None,
            record_sha256="0" * 64,
        )
        finalized = replace(
            provisional, record_sha256=compute_record_sha256(provisional)
        )
        _record_from_dict(finalized.to_dict())
        _append_unlocked(path, finalized)
        return finalized
