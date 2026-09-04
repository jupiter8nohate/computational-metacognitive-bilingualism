from __future__ import annotations

import json
from pathlib import Path

import pytest

from cmb_provenance.z13 import (
    Z13ParseError,
    Z13ValidationError,
    explain_statement,
    iter_lenses,
    parse_statement,
)
from cmb_provenance.z13_cli import main


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "library" / "cmb-z13.registry.json"
SCHEMA = ROOT / "schemas" / "cmb.z13.ast.v1.schema.json"


def test_parse_native_statement_to_ast() -> None:
    statement = parse_statement("♍::GO -> VERIFY[claim] => EVIDENCE_REQUIRED;")
    assert statement.sign == "Virgo"
    assert statement.language == "Go"
    assert statement.operator == "PRECISION"
    assert statement.operation == "VERIFY"
    assert statement.guardian_mode == "The Verification Sentinel"
    assert statement.to_dict()["human_authority_final"] is True


def test_parser_accepts_documented_language_alias() -> None:
    statement = parse_statement(
        "♈::CPP -> REQUEST[action] => HUMAN_AUTHORIZATION_REQUIRED;"
    )
    assert statement.language == "C++"
    assert statement.operator == "ACTION"


def test_parser_rejects_glyph_language_mismatch() -> None:
    with pytest.raises(Z13ValidationError, match="requires Go"):
        parse_statement("♍::PYTHON -> VERIFY[claim] => EVIDENCE_REQUIRED;")


def test_parser_requires_complete_statement() -> None:
    with pytest.raises(Z13ParseError, match="Expected"):
        parse_statement("♍::GO -> VERIFY[claim] => EVIDENCE_REQUIRED")


def test_runtime_mapping_matches_machine_registry() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    registered = {
        entry["glyph"]: (
            entry["sign"],
            entry["software_language"],
            entry["operator"],
            entry["function"],
            entry["guardian_name"],
        )
        for entry in registry["archetypes"]
    }
    runtime = {
        lens.glyph: (
            lens.sign,
            lens.language,
            lens.operator,
            lens.function,
            lens.guardian_mode,
        )
        for lens in iter_lenses()
    }
    assert runtime == registered


def test_ast_schema_freezes_human_authority_boundary() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert schema["additionalProperties"] is False
    assert schema["properties"]["schema_version"]["const"] == "cmb.z13.ast.v1"
    assert schema["properties"]["registry_version"]["const"] == "1.1.0"
    assert schema["properties"]["human_authority_final"]["const"] is True


def test_explain_keeps_human_boundary() -> None:
    explanation = explain_statement(
        parse_statement("♏::PROLOG -> INFER[pattern] => HYPOTHESIS;")
    )
    assert "The Forensic Oracle" in explanation
    assert "HUMAN_AGENCY > MACHINE_AUTHORITY" in explanation


def test_cli_parse_and_validate(capsys) -> None:
    code = main(["parse", "♊::TYPESCRIPT -> TRANSLATE[meaning] => representation;"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["sign"] == "Gemini"
    assert payload["operator"] == "BILINGUALISM"

    code = main(["validate", "⛎::LISP -> INSPECT[rule] => META_REVIEW;"])
    assert code == 0
    assert "HUMAN_DECISION_BOUNDARY" in capsys.readouterr().out


def test_cli_export_json(tmp_path: Path) -> None:
    output = tmp_path / "statement.json"
    code = main([
        "export-json",
        "♐::JULIA -> DISCOVER[hypothesis] => POSSIBILITY;",
        "--output",
        str(output),
    ])
    assert code == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["sign"] == "Sagittarius"
    assert payload["result"] == "POSSIBILITY"
