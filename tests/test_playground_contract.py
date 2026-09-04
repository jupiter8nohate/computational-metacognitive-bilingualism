from __future__ import annotations

import json
from pathlib import Path

from cmb_provenance.boundary import BoundaryCode

ROOT = Path(__file__).resolve().parents[1]
PLAYGROUND = ROOT / "docs" / "playground" / "index.html"
REGISTRY = ROOT / "library" / "cmb-z13.registry.json"


def test_playground_contains_every_canonical_z13_lens() -> None:
    html = PLAYGROUND.read_text(encoding="utf-8")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

    for entry in registry["archetypes"]:
        encoded = json.dumps(
            [
                entry["glyph"],
                entry["sign"],
                entry["software_language"],
                entry["operator"],
                entry["function"],
            ],
            ensure_ascii=False,
            separators=(",", ":"),
        )
        assert encoded in html


def test_playground_contains_every_boundary_rejection_code() -> None:
    html = PLAYGROUND.read_text(encoding="utf-8")

    for code in BoundaryCode:
        assert code.value in html


def test_playground_preserves_human_final_authority() -> None:
    html = PLAYGROUND.read_text(encoding="utf-8")
    assert '"HUMAN_FINAL"' in html
    assert "HUMAN_AGENCY &gt; MACHINE_AUTHORITY" in html
