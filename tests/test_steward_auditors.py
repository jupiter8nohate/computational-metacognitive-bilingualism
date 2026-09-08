from __future__ import annotations

import json
from pathlib import Path

from cmb_agents.immune_system import DIGITAL_DNA
from cmb_agents.auditors import (
    AgentAudit,
    EvidencePacket,
    audit_accessibility,
    audit_canon,
    audit_librarian,
    audit_dnis,
    review_packets,
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_canon_auditor_detects_public_mirror_drift(tmp_path: Path) -> None:
    glyph = {
        "id": "backtrace",
        "name": "Backtrace",
        "glyph": "‹—",
        "definition": "Trace toward source.",
        "human_semantics": "Trace the claim backward.",
        "machine_semantics": "BACKTRACE_TO_PROVENANCE",
    }
    source = {"glyphs": [glyph]}
    _write(tmp_path / "src/cmb_glitch8/glyphs.v1.json", json.dumps(source))
    _write(tmp_path / "library/glitch8.glyphs.v1.json", json.dumps(source))
    _write(tmp_path / "books/GLITCH8_GLYPH_REFERENCE.md", "# Backtrace\n")

    assert audit_canon(tmp_path).ok

    _write(tmp_path / "library/glitch8.glyphs.v1.json", json.dumps({"glyphs": []}))
    result = audit_canon(tmp_path)
    assert not result.ok
    assert result.packet.observed["mirror_matches"] is False


def test_librarian_rejects_missing_navigation_target(tmp_path: Path) -> None:
    _write(tmp_path / "docs/index.md", "# Home\n")
    _write(tmp_path / "mkdocs.yml", "nav:\n  - Home: index.md\n")
    assert audit_librarian(tmp_path).ok

    _write(tmp_path / "mkdocs.yml", "nav:\n  - Missing: missing.md\n")
    result = audit_librarian(tmp_path)
    assert not result.ok
    assert result.packet.observed["missing_nav_targets"] == ["missing.md"]


def test_accessibility_auditor_requires_front_door_safeguards(tmp_path: Path) -> None:
    _write(tmp_path / "docs/index.md", '<img src="hero.svg" alt="CMB hero">\n')
    _write(tmp_path / "README.md", "# CMB\n")
    _write(tmp_path / "docs/SEARCH_FOR_TRUTH.md", "# Search\n")
    _write(
        tmp_path / "docs/stylesheets/accessibility.css",
        ".x:focus-visible { outline: 2px solid; }\n"
        "@media (prefers-reduced-motion: reduce) { .x { transition: none; } }\n",
    )

    assert audit_accessibility(tmp_path).ok

    _write(tmp_path / "docs/index.md", '<img src="hero.svg">\n')
    assert not audit_accessibility(tmp_path).ok


def test_reviewer_rejects_authority_escalation() -> None:
    packet = EvidencePacket(
        agent="UNSAFE",
        task="authority_test",
        observed={},
        evidence=("test",),
        confidence=1.0,
        recommended_action="reject",
        authority="merge",
        severity="error",
    )
    audit = AgentAudit(name="UNSAFE", ok=True, summary="unsafe", packet=packet)

    result = review_packets((audit,))
    assert not result.ok
    assert result.packet.observed["unsafe_authority_packets"] == ["UNSAFE"]


def test_evidence_packet_serializes_tuple_evidence_as_list() -> None:
    packet = EvidencePacket(
        agent="CANON",
        task="test",
        observed={"ok": True},
        evidence=("a", "b"),
        confidence=0.75,
        recommended_action="none",
    )
    payload = packet.to_dict()
    assert payload["evidence"] == ["a", "b"]
    assert payload["authority"] == "read_only"


def test_dnis_auditor_detects_digital_dna_drift(tmp_path: Path) -> None:
    cells = [
        {"id": name}
        for name in (
            "RECEPTOR_CELL",
            "DENDRITIC_CELL",
            "POSITION_CELL",
            "CHAPERONE_CELL",
            "T_CELL_POLICY_GATE",
            "REFLEX_CELL",
            "MACROPHAGE_RECOVERY",
            "CORTEX_LIAISON",
            "B_CELL_PROVENANCE",
            "MEMORY_CELL",
        )
    ]
    registry = {
        "protocol": "CMB-DNIS-1",
        "digital_dna": list(DIGITAL_DNA),
        "cells": cells,
    }
    _write(tmp_path / "agents/immune-cell-registry.json", json.dumps(registry))

    assert audit_dnis(tmp_path).ok

    registry["digital_dna"] = ["PATTERN == PROOF"]
    _write(tmp_path / "agents/immune-cell-registry.json", json.dumps(registry))
    result = audit_dnis(tmp_path)
    assert not result.ok
    assert result.packet.observed["digital_dna_matches_runtime"] is False
