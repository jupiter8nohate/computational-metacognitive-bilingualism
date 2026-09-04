from __future__ import annotations

import json
from pathlib import Path

from cmb_provenance import (
    C2PA_ASSERTION_PAYLOAD_SCHEMA_VERSION,
    build_c2pa_manifest_definition,
    c2pa_assertion_payload_bytes,
    load_receipt,
    to_c2pa_assertion_payload,
    validate_c2pa_assertion_label,
)
from cmb_provenance.errors import SealError
from cmb_provenance.cli import main

FIXTURES = Path(__file__).parent / "fixtures"
RECEIPT = FIXTURES / "c2pa_receipt.json"
EXPECTED = FIXTURES / "c2pa_payload.expected.json"
SCHEMA = Path(__file__).parents[1] / "schemas" / "cmb.c2pa-assertion-payload.v1.schema.json"


def test_adapter_matches_deterministic_fixture() -> None:
    receipt = load_receipt(RECEIPT)
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))

    first = to_c2pa_assertion_payload(receipt)
    second = to_c2pa_assertion_payload(receipt)

    assert first == expected
    assert second == expected
    assert c2pa_assertion_payload_bytes(receipt) == c2pa_assertion_payload_bytes(receipt)
    assert b"example.txt" not in c2pa_assertion_payload_bytes(receipt)


def test_adapter_includes_paths_only_when_explicitly_requested() -> None:
    receipt = load_receipt(RECEIPT)

    default_payload = to_c2pa_assertion_payload(receipt)
    path_payload = to_c2pa_assertion_payload(receipt, include_paths=True)

    assert default_payload["coverage"]["paths_included"] is False
    assert default_payload["coverage"]["paths"] == []
    assert path_payload["coverage"]["paths_included"] is True
    assert path_payload["coverage"]["paths"] == ["example.txt"]


def test_payload_keeps_c2pa_nonconformance_boundary_explicit() -> None:
    payload = to_c2pa_assertion_payload(load_receipt(RECEIPT))

    assert payload["schema_version"] == C2PA_ASSERTION_PAYLOAD_SCHEMA_VERSION
    assert payload["c2pa_status"] == {
        "payload_is_c2pa_manifest": False,
        "payload_is_content_credential": False,
        "project_claims_c2pa_conformance": False,
        "requires_external_c2pa_tooling": True,
    }
    assert payload["evidence_boundary"]["integrity_is_authorship"] is False
    assert payload["evidence_boundary"]["assertion_is_truth"] is False


def test_json_schema_is_strict_about_boundary_fields() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    assert schema["additionalProperties"] is False
    assert schema["properties"]["schema_version"]["const"] == "cmb.c2pa-assertion-payload.v1"
    assert (
        schema["properties"]["c2pa_status"]["properties"][
            "project_claims_c2pa_conformance"
        ]["const"]
        is False
    )
    assert (
        schema["properties"]["evidence_boundary"]["properties"][
            "integrity_is_authorship"
        ]["const"]
        is False
    )


def test_cli_exports_privacy_minimized_payload(tmp_path: Path, capsys) -> None:
    output = tmp_path / "payload.json"

    exit_code = main(
        [
            "export-c2pa-payload",
            "--receipt",
            str(RECEIPT),
            "--output",
            str(output),
        ]
    )

    assert exit_code == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["coverage"]["paths"] == []
    captured = capsys.readouterr()
    assert "adapter_payload_only_not_c2pa_manifest_or_credential" in captured.out


def test_cli_include_paths_is_opt_in(capsys) -> None:
    exit_code = main(
        [
            "export-c2pa-payload",
            "--receipt",
            str(RECEIPT),
            "--include-paths",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["coverage"]["paths"] == ["example.txt"]



def test_manifest_definition_wraps_payload_without_claiming_conformance() -> None:
    receipt = load_receipt(RECEIPT)
    manifest = build_c2pa_manifest_definition(
        receipt,
        assertion_label="com.example.cmb_provenance",
        allow_example_namespace=True,
    )

    assert manifest["claim_generator_info"][0]["name"] == "cmb-provenance"
    assertion = manifest["assertions"][0]
    assert assertion["label"] == "com.example.cmb_provenance"
    assert assertion["kind"] == "Json"
    assert assertion["created"] is True
    assert assertion["data"] == to_c2pa_assertion_payload(receipt)


def test_production_manifest_rejects_reserved_example_namespace() -> None:
    try:
        validate_c2pa_assertion_label("com.example.cmb_provenance")
    except SealError as exc:
        assert "reserved for documentation and tests" in str(exc)
    else:
        raise AssertionError("reserved example namespace should be rejected")


def test_manifest_label_rejects_reserved_c2pa_namespace() -> None:
    try:
        validate_c2pa_assertion_label("c2pa.cmb.provenance")
    except SealError as exc:
        assert "Reserved C2PA/standards namespaces" in str(exc)
    else:
        raise AssertionError("c2pa namespace should be rejected")


def test_cli_builds_test_manifest_definition(tmp_path: Path, capsys) -> None:
    output = tmp_path / "manifest.json"
    exit_code = main(
        [
            "build-c2pa-manifest",
            "--receipt",
            str(RECEIPT),
            "--assertion-label",
            "com.example.cmb_provenance",
            "--test-example-namespace",
            "--output",
            str(output),
        ]
    )

    assert exit_code == 0
    manifest = json.loads(output.read_text(encoding="utf-8"))
    assert manifest["assertions"][0]["label"] == "com.example.cmb_provenance"
    assert (
        manifest["assertions"][0]["data"]["c2pa_status"]["project_claims_c2pa_conformance"]
        is False
    )
    assert "requires_external_c2pa_signing_and_binding" in capsys.readouterr().out
