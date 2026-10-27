"""Regression gate for the emergency Actix zstd advisory remediation.

The Actix HTTP zstd feature must stay off until a Cargo-resolved graph uses
a compatible patched release. Brotli and gzip support must remain enabled.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def test_actix_lock_excludes_vulnerable_zstd_chain():
    adapter = ROOT / "adapters" / "rust-actix"
    manifest = (adapter / "Cargo.toml").read_text(encoding="utf-8")
    lockfile = (adapter / "Cargo.lock").read_text(encoding="utf-8")
    assert '"compress-gzip"' in manifest
    assert '"compress-brotli"' in manifest
    assert '"compress-zstd"' not in manifest
    assert not re.search(r'^name = "(?:zstd|zstd-safe|zstd-sys)"$', lockfile, re.M)
