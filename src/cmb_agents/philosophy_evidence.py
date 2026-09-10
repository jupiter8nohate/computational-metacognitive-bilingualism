"""Bounded source-evidence loader for the CMB 333 Philosophy Swarm.

The loader resolves declared repository sources, prevents path escape, hashes source
material, and captures small text excerpts for internal proposal grounding.

SOURCE_PATH != EVIDENCE
HASH != TRUTH
EXCERPT != WHOLE_SOURCE
MODEL_OUTPUT != EVIDENCE
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Final, Sequence

MAX_FILE_BYTES: Final[int] = 64 * 1024
MAX_EXCERPT_CHARS: Final[int] = 3000
MAX_DIRECTORY_FILES: Final[int] = 8
_DIRECTORY_EXTENSIONS: Final[frozenset[str]] = frozenset(
    {".md", ".txt", ".py", ".json", ".toml", ".yaml", ".yml"}
)


class EvidenceError(RuntimeError):
    """Raised when declared evidence cannot be safely resolved."""


@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    path: str
    kind: str
    sha256: str
    excerpt: str
    bytes_sampled: int
    files_sampled: int

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _safe_resolve(root: Path, relative_path: str) -> Path:
    if not relative_path or Path(relative_path).is_absolute():
        raise EvidenceError(f"source path must be repository-relative: {relative_path!r}")

    root_resolved = root.resolve(strict=True)
    candidate = (root_resolved / relative_path).resolve(strict=True)
    try:
        candidate.relative_to(root_resolved)
    except ValueError as exc:
        raise EvidenceError(f"source path escapes repository root: {relative_path}") from exc
    return candidate


def _read_sample(path: Path) -> tuple[bytes, str]:
    with path.open("rb") as handle:
        sample = handle.read(MAX_FILE_BYTES)
    return sample, sample.decode("utf-8", errors="replace")[:MAX_EXCERPT_CHARS]


def _file_record(root: Path, relative_path: str, path: Path) -> EvidenceRecord:
    data = path.read_bytes()
    sample, excerpt = _read_sample(path)
    return EvidenceRecord(
        path=relative_path,
        kind="file",
        sha256=hashlib.sha256(data).hexdigest(),
        excerpt=excerpt,
        bytes_sampled=len(sample),
        files_sampled=1,
    )


def _directory_record(root: Path, relative_path: str, path: Path) -> EvidenceRecord:
    candidates = sorted(
        child
        for child in path.rglob("*")
        if child.is_file() and child.suffix.lower() in _DIRECTORY_EXTENSIONS
    )[:MAX_DIRECTORY_FILES]
    if not candidates:
        raise EvidenceError(f"source directory contains no bounded text evidence: {relative_path}")

    digest = hashlib.sha256()
    excerpts: list[str] = []
    bytes_sampled = 0
    root_resolved = root.resolve(strict=True)

    for child in candidates:
        child_relative = child.relative_to(root_resolved).as_posix()
        data = child.read_bytes()
        sample, excerpt = _read_sample(child)
        child_digest = hashlib.sha256(data).hexdigest()
        digest.update(child_relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(child_digest.encode("ascii"))
        digest.update(b"\n")
        bytes_sampled += len(sample)
        excerpts.append(f"[{child_relative}]\n{excerpt}")

    return EvidenceRecord(
        path=relative_path,
        kind="directory_sample",
        sha256=digest.hexdigest(),
        excerpt="\n\n".join(excerpts)[: MAX_EXCERPT_CHARS * 2],
        bytes_sampled=bytes_sampled,
        files_sampled=len(candidates),
    )


def collect_source_evidence(
    repo_root: Path,
    source_paths: Sequence[str],
) -> tuple[EvidenceRecord, ...]:
    """Resolve, hash, and sample each declared source inside ``repo_root``."""

    root = repo_root.resolve(strict=True)
    if not root.is_dir():
        raise EvidenceError(f"repository root is not a directory: {root}")

    records: list[EvidenceRecord] = []
    for relative_path in source_paths:
        path = _safe_resolve(root, relative_path)
        if path.is_file():
            records.append(_file_record(root, relative_path, path))
        elif path.is_dir():
            records.append(_directory_record(root, relative_path, path))
        else:
            raise EvidenceError(f"source is neither file nor directory: {relative_path}")
    return tuple(records)
