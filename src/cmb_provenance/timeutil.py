"""Strict ISO-8601 parsing and canonical UTC rendering."""

from __future__ import annotations

import re
from datetime import datetime, timezone

from .errors import SchemaValidationError

_TIMESTAMP_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})$"
)


def normalize_timestamp(value: str) -> str:
    """Return an aware ISO-8601 timestamp normalized to UTC with a ``Z`` suffix."""

    if not isinstance(value, str) or not _TIMESTAMP_RE.fullmatch(value):
        raise SchemaValidationError(
            "Timestamp must use ISO-8601 date-time syntax with seconds and an explicit timezone."
        )
    candidate = f"{value[:-1]}+00:00" if value.endswith("Z") else value
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
