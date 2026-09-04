from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from cmb_provenance.release import build_checksums


def test_release_checksums_are_sorted_and_repeatable(tmp_path: Path) -> None:
    (tmp_path / "z.whl").write_bytes(b"z")
    (tmp_path / "a.tar.gz").write_bytes(b"a")
    output = tmp_path / "SHA256SUMS"

    files = build_checksums(tmp_path, output)
    first = output.read_text(encoding="utf-8")
    build_checksums(tmp_path, output)

    assert [path.name for path in files] == ["a.tar.gz", "z.whl"]
    assert first == output.read_text(encoding="utf-8")
    assert first.splitlines() == [
        f"{hashlib.sha256(b'a').hexdigest()}  a.tar.gz",
        f"{hashlib.sha256(b'z').hexdigest()}  z.whl",
    ]


def test_release_checksums_require_artifacts(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="No release files"):
        build_checksums(tmp_path, tmp_path / "SHA256SUMS")
