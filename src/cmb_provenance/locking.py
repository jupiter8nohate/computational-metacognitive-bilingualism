"""Cross-platform exclusive file locking for complete ledger operations."""

from __future__ import annotations

import errno
import os
import time
from pathlib import Path
from types import TracebackType
from typing import BinaryIO

from .errors import LedgerError, LockTimeoutError

if os.name == "nt":  # pragma: no cover - exercised by the Windows CI runner when added
    import msvcrt
else:
    import fcntl


class FileLock:
    """Hold an OS-level exclusive lock on a stable sibling lock file."""

    def __init__(
        self, target: Path, *, timeout: float = 10.0, poll_interval: float = 0.05
    ) -> None:
        if timeout < 0:
            raise ValueError("timeout must be non-negative")
        if poll_interval <= 0:
            raise ValueError("poll_interval must be positive")
        self.target = Path(target)
        self.lock_path = self.target.with_name(f"{self.target.name}.lock")
        self.timeout = timeout
        self.poll_interval = poll_interval
        self._handle: BinaryIO | None = None

    def __enter__(self) -> FileLock:
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        flags = os.O_RDWR | os.O_CREAT
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        try:
            descriptor = os.open(self.lock_path, flags, 0o600)
            self._handle = os.fdopen(descriptor, "r+b", buffering=0)
            if (
                os.name == "nt" and os.fstat(descriptor).st_size == 0
            ):  # pragma: no cover
                self._handle.write(b"\0")
                self._handle.flush()
        except OSError as exc:
            raise LedgerError(
                f"Unable to open ledger lock {self.lock_path}: {exc}"
            ) from exc

        deadline = time.monotonic() + self.timeout
        while True:
            try:
                self._acquire_nonblocking()
                return self
            except (BlockingIOError, OSError) as exc:
                if isinstance(exc, OSError) and exc.errno not in {
                    errno.EACCES,
                    errno.EAGAIN,
                    errno.EDEADLK,
                }:
                    self._close()
                    raise LedgerError(
                        f"Unable to acquire ledger lock {self.lock_path}: {exc}"
                    ) from exc
                if time.monotonic() >= deadline:
                    self._close()
                    raise LockTimeoutError(
                        f"Timed out after {self.timeout:g}s waiting for ledger lock {self.lock_path}."
                    ) from exc
                time.sleep(self.poll_interval)

    def _acquire_nonblocking(self) -> None:
        if self._handle is None:
            raise LedgerError("Ledger lock handle is not open.")
        if os.name == "nt":  # pragma: no cover
            self._handle.seek(0)
            msvcrt.locking(self._handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            fcntl.flock(self._handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

    def _release(self) -> None:
        if self._handle is None:
            return
        if os.name == "nt":  # pragma: no cover
            self._handle.seek(0)
            msvcrt.locking(self._handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            fcntl.flock(self._handle.fileno(), fcntl.LOCK_UN)

    def _close(self) -> None:
        if self._handle is not None:
            self._handle.close()
            self._handle = None

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        try:
            self._release()
        finally:
            self._close()
