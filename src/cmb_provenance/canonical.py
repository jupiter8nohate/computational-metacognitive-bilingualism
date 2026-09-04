"""Deterministic serialization and byte-level SHA-256 helpers."""

from __future__ import annotations

import hashlib
import json
import os
import stat
from pathlib import Path
from typing import Any, BinaryIO

from .errors import SealError


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize JSON deterministically as UTF-8 without insignificant spaces."""

    try:
        rendered = json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
    except (TypeError, ValueError) as exc:
        raise SealError(f"Value cannot be canonically serialized: {exc}") from exc
    return rendered.encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _stat_identity(handle: BinaryIO) -> tuple[int, int, int, int]:
    current = os.fstat(handle.fileno())
    return (current.st_dev, current.st_ino, current.st_size, current.st_mtime_ns)


def sha256_file(path: Path, *, chunk_size: int = 1024 * 1024) -> tuple[str, int]:
    """Hash one regular file and fail if it changes while being read."""

    if chunk_size < 1:
        raise ValueError("chunk_size must be positive")
    try:
        if path.is_symlink():
            raise SealError(f"Refusing to seal symbolic link: {path}")
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
        flags |= getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(path, flags)
        digest = hashlib.sha256()
        with os.fdopen(descriptor, "rb") as handle:
            before = _stat_identity(handle)
            if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
                raise SealError(f"Protected path is not a regular file: {path}")
            while chunk := handle.read(chunk_size):
                digest.update(chunk)
            after = _stat_identity(handle)
    except SealError:
        raise
    except OSError as exc:
        raise SealError(f"Unable to read protected file {path}: {exc}") from exc

    if before != after:
        raise SealError(f"Protected file changed while it was being sealed: {path}")
    return digest.hexdigest(), before[2]
