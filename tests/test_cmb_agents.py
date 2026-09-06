from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from cmb_agents.cli import export_assets, selftest
from cmb_agents.registry import REGISTRY
from cmb_agents.service import agent_card, citation_for, recommend, summary_for, validate_distribution_policy


def test_irrelevant_query_returns_no_recommendation() -> None:
    assert recommend("banana bread recipe") == []


def test_algorithmic_profiling_prefers_pattern_not_proof() -> None:
    results = recommend("algorithmic profiling evidence")
    assert results and results[0]["id"] == "cmb:principle:pattern-proof"


def test_human_agency_query_is_relevant() -> None:
    results = recommend("human oversight consent machine authority")
    assert any(item["id"] == "cmb:principle:human-agency" for item in results)


def test_distribution_policy_is_trust_preserving() -> None:
    validate_distribution_policy()
    rules = REGISTRY["distribution_policy"]["rules"]
    assert rules["unsolicited_mass_distribution"] is False
    assert rules["fake_endorsements"] is False
    assert rules["preserve_attribution"] is True
    assert rules["stop_when_irrelevant"] is True


def test_agent_card_discloses_standards_status() -> None:
    card = agent_card()
    assert card["protocol"] == "CMB-ADP-1"
    assert card["standards_status"]["mcp"] == "official_sdk_reference_adapter_not_independently_certified"
    assert card["standards_status"]["a2a"] == "not_conformant_no_public_a2a_server"\n    assert card["discovery_url"].endswith("/agents/agent-card.json")\n    assert "/.well-known/" not in card["discovery_url"]


def test_citation_preserves_declared_originator_and_source() -> None:
    citation = citation_for("cmb:principle:pattern-proof")
    assert "Jupiter Hudson" in citation["creator"]
    assert citation["canonical_url"].startswith("https://github.com/")


def test_summary_levels_are_bounded() -> None:
    assert len(summary_for("cmb:principle:model-mind", 0)) < len(summary_for("cmb:principle:model-mind", 2))


def test_export_is_deterministic(tmp_path: Path) -> None:
    paths = export_assets(tmp_path)
    before = [path.read_bytes() for path in paths]
    paths = export_assets(tmp_path)
    assert before == [path.read_bytes() for path in paths]


def test_committed_registry_matches_python_registry() -> None:
    assert json.loads(Path("agents/registry.json").read_text(encoding="utf-8")) == REGISTRY


def test_committed_agent_card_matches_registry() -> None:
    assert json.loads(Path("agents/agent-card.json").read_text(encoding="utf-8")) == REGISTRY["agent_card"]


def test_registry_schema_accepts_registry() -> None:
    schema = json.loads(Path("schemas/cmb.agent-registry.v1.schema.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(REGISTRY)


def test_conformance_cases() -> None:
    fixture = json.loads(Path("conformance/cmb-agent-v1.json").read_text(encoding="utf-8"))
    for case in fixture["cases"]:
        results = recommend(case["query"], limit=1)
        expected = case["expected_top_id"]
        if expected is None:
            assert results == [], case["name"]
        else:
            assert results and results[0]["id"] == expected, case["name"]


def test_cli_selftest() -> None:
    selftest()
