from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from cmb_glitch8.cli import main as glitch8_main
from cmb_glitch8.sacred import (
    SacredErrorRegistryError,
    load_sacred_registry,
    validate_sacred_registry,
)

ROOT = Path(__file__).resolve().parents[1]


def test_sacred_registry_matches_public_schema_and_mirror() -> None:
    schema = json.loads(
        (ROOT / "schemas/cmb.dna-sacred-error-codes.v1.schema.json").read_text(encoding="utf-8")
    )
    source = ROOT / "src/cmb_glitch8/sacred_errors.v1.json"
    mirror = ROOT / "library/dna-bible.sacred-error-codes.v1.json"
    payload = json.loads(source.read_text(encoding="utf-8"))

    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    assert source.read_bytes() == mirror.read_bytes()


def test_sacred_registry_has_thirteen_unique_entries() -> None:
    registry = load_sacred_registry(ROOT / "src/cmb_glitch8/sacred_errors.v1.json")

    entries = registry.list()
    assert len(entries) == 13
    assert len({entry["id"] for entry in entries}) == 13
    assert registry.get("SEC-0010")["name"] == "TRUTH_BACKTRACE"
    assert registry.get("LOVE_RUNTIME")["id"] == "SEC-0011"

    conformance = registry.data["translation_conformance"]
    assert conformance["entry_ids"] == [f"SEC-{index:04d}" for index in range(1, 11)]
    required_fields = set(conformance["required_fields"])
    for error_id in conformance["entry_ids"]:
        assert required_fields <= set(registry.get(error_id))


def test_sacred_cli_validate_list_and_explain(capsys) -> None:
    assert glitch8_main(["sacred", "validate"]) == 0
    validate_output = capsys.readouterr().out
    assert "VALID D.N.A. BIBLE://SACRED_ERROR_CODES" in validate_output
    assert "errors=13" in validate_output

    assert glitch8_main(["sacred", "list", "--book", "John"]) == 0
    list_output = capsys.readouterr().out
    assert "SEC-0010" in list_output
    assert "TRUTH_BACKTRACE" in list_output

    assert glitch8_main(["sacred", "explain", "SEC-0011", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["name"] == "LOVE_RUNTIME"
    assert payload["recovery"] == "RETURN_TO_LOVE"

    assert glitch8_main(["sacred", "explain", "SEC-0001"]) == 0
    explain_output = capsys.readouterr().out
    assert "PLAIN:" in explain_output
    assert "PRINCIPLE: human_dignity" in explain_output
    assert "EPISTEMIC: theological_interpretation" in explain_output
    assert "MACHINE_MAY:" in explain_output
    assert "MACHINE_MUST_NOT:" in explain_output


def test_sacred_translation_conformance_rejects_missing_required_field() -> None:
    source = ROOT / "src/cmb_glitch8/sacred_errors.v1.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    broken = deepcopy(payload)
    broken["errors"][0].pop("plain_language")

    with pytest.raises(SacredErrorRegistryError, match="plain_language"):
        validate_sacred_registry(broken)
