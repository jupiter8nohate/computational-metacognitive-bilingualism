"""Regression tests for reader architecture and negative cases."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from audit_evolution import audit


def test_canonical_upgrade_audit() -> None:
    assert audit(ROOT) == []


def test_gates_cannot_be_claimed_independently_reviewed() -> None:
    """The checked-in crosswalk must not silently certify its own claims."""
    data = json.loads((ROOT / "library/cmb-gate-claims.v1.json").read_text(encoding="utf-8"))
    assert len(data["entries"]) == 7
    assert all(e["review_status"] == "pending" for e in data["entries"])
    assert all(e["independently_reviewed"] is False for e in data["entries"])


def test_missing_source_is_reported() -> None:
    """A truncated checkout fails closed instead of reporting a green audit."""
    with tempfile.TemporaryDirectory() as directory:
        assert any("Missing" in error for error in audit(Path(directory)))
