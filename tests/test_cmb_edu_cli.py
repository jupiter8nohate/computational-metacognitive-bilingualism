from __future__ import annotations

import json
from pathlib import Path

from cmb_edu.cli import main


SOURCE = (
    '♌::CREATIVE -> STATE[confident || overstimulated] '
    '=> GENERATE("dragon_story") -> PROFILE_NOT_PERSON;'
)


def test_cli_validate(capsys) -> None:
    assert main(["validate", SOURCE]) == 0
    out = capsys.readouterr().out
    assert "VALID cmb.edu.v1" in out
    assert "authority=HUMAN_FINAL" in out


def test_cli_parse(capsys) -> None:
    assert main(["parse", SOURCE]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["context"]["source"] == "human_declared"
    assert payload["context"]["machine_inferred"] is False
    assert payload["privacy"]["training_permission"] is False


def test_cli_export_json(tmp_path: Path) -> None:
    output = tmp_path / "edu.json"
    assert main(["export-json", SOURCE, "--output", str(output)]) == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["schema"] == "cmb.edu.v1"
    assert payload["privacy"]["persistence"] == "ephemeral"


def test_cli_rejects_invalid_stream(capsys) -> None:
    assert main(["validate", "PROFILE = PERSON"]) == 2
    assert "ERROR:" in capsys.readouterr().err
