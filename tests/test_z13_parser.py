from __future__ import annotations

import json
from pathlib import Path

import pytest

from cmb_provenance.z13 import (
    Z13_AST_SCHEMA_VERSION,
    Z13Error,
    canonical_lenses,
    explain_z13_statement,
    parse_z13_statement,
)
from cmb_provenance.z13_cli import main

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "library" / "cmb-z13.registry.json"
SCHEMA = ROOT / "schemas" / "cmb.z13.ast.v1.schema.json"


@pytest.mark.parametrize(
    ("source", "sign", "language", "operator", "operation"),
    [
        ("♍::GO -> VERIFY[claim] => EVIDENCE_REQUIRED;", "Virgo", "Go", "PRECISION", "VERIFY"),
        ("♊::TYPESCRIPT -> TRANSLATE[human_meaning] => machine_representation;", "Gemini", "TypeScript", "BILINGUALISM", "TRANSLATE"),
        ("♏::PROLOG -> INFER[pattern] => HYPOTHESIS;", "Scorpio", "Prolog", "INFERENCE", "INFER"),
        ("⛎::LISP -> INSPECT[rule] => META(rule);", "Ophiuchus", "Common Lisp", "METACOGNITION", "INSPECT"),
        ("♈::CPP -> REQUEST[action] => HUMAN_CONSENT_REQUIRED;", "Aries", "C++", "ACTION", "REQUEST"),
    ],
)
def test_parse_canonical_examples(source: str, sign: str, language: str, operator: str, operation: str) -> None:
    statement = parse_z13_statement(source)
    assert statement.sign == sign
    assert statement.language == language
    assert statement.canonical_operator == operator
    assert statement.operation == operation
    assert statement.authority == "HUMAN_FINAL"
    assert statement.to_dict()["schema_version"] == Z13_AST_SCHEMA_VERSION


def test_parser_rejects_language_mapping_drift() -> None:
    with pytest.raises(Z13Error, match="canonically mapped"):
        parse_z13_statement("♍::PYTHON -> VERIFY[claim] => EVIDENCE_REQUIRED;")


def test_parser_rejects_unknown_operation_for_lens() -> None:
    with pytest.raises(Z13Error, match="does not define operation"):
        parse_z13_statement("♍::GO -> INFER[claim] => HYPOTHESIS;")


def test_parser_mapping_matches_machine_registry() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    expected = {
        entry["sign"]: (
            entry["glyph"],
            entry["software_language"],
            entry["operator"],
            entry["function"],
            entry["guardian_name"],
            entry["guardian_team"],
        )
        for entry in registry["archetypes"]
    }
    actual = {
        lens.sign: (
            lens.glyph,
            lens.language,
            lens.canonical_operator,
            lens.canonical_function,
            lens.guardian_name,
            lens.guardian_team,
        )
        for lens in canonical_lenses()
    }
    assert actual == expected


def test_ast_schema_freezes_human_authority_boundary() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert schema["additionalProperties"] is False
    assert schema["properties"]["authority"]["const"] == "HUMAN_FINAL"


def test_explanation_preserves_human_authority() -> None:
    explanation = explain_z13_statement(parse_z13_statement("♍::GO -> VERIFY[claim] => EVIDENCE_REQUIRED;"))
    assert "Verification Sentinel" in explanation
    assert "Human authority remains final." in explanation


def test_cli_parse_and_validate(capsys) -> None:
    source = "♏::PROLOG -> INFER[pattern] => HYPOTHESIS;"
    assert main(["validate", source]) == 0
    assert "VALID ♏ Scorpio/Prolog" in capsys.readouterr().out
    assert main(["parse", source]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["sign"] == "Scorpio"
    assert payload["authority"] == "HUMAN_FINAL"


def test_cli_export_json(tmp_path: Path) -> None:
    output = tmp_path / "statement.json"
    assert main(["export-json", "♍::GO -> VERIFY[claim] => EVIDENCE_REQUIRED;", "--output", str(output)]) == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["canonical_operator"] == "PRECISION"
