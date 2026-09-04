"""Release artifact definitions and checksum support shared by tests and automation."""

from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path

CANONICAL_PUBLIC_ARTIFACTS: tuple[str, ...] = (
    "MANIFESTO.md",
    "CMB_Polyglot_Firewall_Specification.md",
    "manifestos/DEMONS_NEED_ATTENTION_DNA.md",
)


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            result.update(chunk)
    return result.hexdigest()


def build_checksums(directory: Path, output: Path) -> list[Path]:
    directory = directory.resolve(strict=True)
    output = output.resolve(strict=False)
    if output.parent != directory:
        raise ValueError(
            "Checksum output must be directly inside the release directory."
        )
    files = sorted(
        (path for path in directory.iterdir() if path.is_file() and path != output),
        key=lambda path: path.name,
    )
    if not files:
        raise ValueError(f"No release files found in {directory}.")
    if any("\n" in path.name or "\r" in path.name for path in files):
        raise ValueError("Release filenames must not contain newlines.")

    rendered = "".join(f"{digest(path)}  {path.name}\n" for path in files)
    temporary_name: str | None = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=".SHA256SUMS.", dir=directory
        )
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(rendered)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, output)
        temporary_name = None
    finally:
        if temporary_name:
            Path(temporary_name).unlink(missing_ok=True)
    return files
