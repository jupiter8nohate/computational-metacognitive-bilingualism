from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from cmb_preservation import audit_repository
from cmb_preservation.cli import main as recovery_main

ROOT = Path(__file__).resolve().parents[1]


def _json(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_recovery_map_matches_schema_and_refuses_false_permanence_claims() -> None:
    schema = _json("schemas/cmb.recovery-map.v1.schema.json")
    recovery = _json("machine/recovery-map.json")
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(recovery)

    claims = recovery["claims"]
    assert claims["permanence_guaranteed"] is False
    assert claims["availability_guaranteed"] is False
    assert claims["blockchain_used"] is False
    assert claims["dna_storage_deployed"] is False


def test_corpus_manifest_and_every_record_match_public_schemas() -> None:
    manifest_schema = _json("schemas/cmb.canonical-corpus-manifest.v1.schema.json")
    record_schema = _json("schemas/cmb.canonical-corpus-record.v1.schema.json")
    manifest = _json("datasets/cmb-canonical-corpus/manifest.json")

    Draft202012Validator.check_schema(manifest_schema)
    Draft202012Validator.check_schema(record_schema)
    Draft202012Validator(manifest_schema).validate(manifest)

    corpus_path = ROOT / manifest["corpus_file"]
    data = corpus_path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == manifest["sha256"]

    records = [json.loads(line) for line in data.decode("utf-8").splitlines() if line.strip()]
    assert len(records) == manifest["record_count"]
    assert len({record["id"] for record in records}) == len(records)
    validator = Draft202012Validator(record_schema)
    for record in records:
        validator.validate(record)


def test_repository_preservation_audit_is_green() -> None:
    result = audit_repository(ROOT)
    assert result["ok"] is True
    assert result["corpus_records"] == 8
    assert result["permanence_guaranteed"] is False
    assert result["availability_guaranteed"] is False


def test_recovery_cli_status_is_machine_readable(capsys) -> None:
    assert recovery_main(["--root", str(ROOT), "status"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["corpus_records"] == 8
    assert payload["permanence_guaranteed"] is False
    assert payload["availability_guaranteed"] is False
