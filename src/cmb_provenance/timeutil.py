"""Strict ISO-8601 parsing and canonical UTC rendering."""

from __future__ import annotations

import re
from datetime import datetime, timezone

from .errors import SchemaValidationError

_TIMESTAMP_RE = re.compile(
    r"^(?P<datetime>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})"
    r"(?P<fraction>\.\d{1,6})?(?P<timezone>Z|[+-]\d{2}:\d{2})$"
)


def normalize_timestamp(value: str) -> str:
    """Return an aware ISO-8601 timestamp normalized to UTC with a ``Z`` suffix."""

    match = _TIMESTAMP_RE.fullmatch(value) if isinstance(value, str) else None
    if match is None:
        raise SchemaValidationError(
            "Timestamp must use ISO-8601 date-time syntax with seconds and an explicit timezone."
        )
    fraction = match.group("fraction")
    padded_fraction = f".{fraction[1:].ljust(6, '0')}" if fraction is not None else ""
    zone = "+00:00" if match.group("timezone") == "Z" else match.group("timezone")
    candidate = f"{match.group('datetime')}{padded_fraction}{zone}"
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise SchemaValidationError(f"Invalid timestamp {value!r}: {exc}") from exc
    if parsed.tzinfo is None:
        raise SchemaValidationError("Timestamp must include a timezone.")

    normalized = parsed.astimezone(timezone.utc).isoformat(timespec="microseconds")
    main, offset = normalized.rsplit("+", 1)
    if "." in main:
        main = main.rstrip("0").rstrip(".")
    return f"{main}Z" if offset == "00:00" else normalized


def utc_now_iso() -> str:
    return normalize_timestamp(
        datetime.now(timezone.utc).isoformat(timespec="microseconds")
    )
