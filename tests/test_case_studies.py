from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "cmb.case-study.v1.schema.json"
RECORD_PATH = ROOT / "research" / "case-studies" / "2026-09-04_GOOGLE_GENERATIVE_MISCLASSIFICATION.json"
REPORT_PATH = ROOT / "research" / "case-studies" / "2026-09-04_GOOGLE_GENERATIVE_MISCLASSIFICATION.md"
EXPECTED_SCREENSHOT_SHA256 = "20b31021bea08e7fa1387ee57ed3fbeafefd6470a0474ba166586d0ccaa3697d"


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_case_study_schema_is_valid_and_record_conforms() -> None:
    schema = _load_json(SCHEMA_PATH)
    record = _load_json(RECORD_PATH)

    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(record)


def test_case_study_preserves_screenshot_fingerprint_across_formats() -> None:
    record = _load_json(RECORD_PATH)
    report = REPORT_PATH.read_text(encoding="utf-8")

    evidence = record["evidence"]
    assert isinstance(evidence, list)
    screenshot = next(item for item in evidence if item["id"] == "source-screenshot")

    assert screenshot["sha256"] == EXPECTED_SCREENSHOT_SHA256
    assert EXPECTED_SCREENSHOT_SHA256 in report
    assert screenshot["public_copy"] is False


def test_case_study_keeps_disputed_claims_evidence_bounded() -> None:
    record = _load_json(RECORD_PATH)
    claims = record["claims"]
    assert isinstance(claims, list)

    disputed = {
        claim["status"]
        for claim in claims
        if claim["id"] != "cryptic-symbolic-material-exists"
    }
    assert disputed <= {
        "not_established",
        "not_verified",
        "unsupported_by_available_evidence",
    }
    assert all(claim["evidence_boundary"] for claim in claims)


def test_case_study_is_explicitly_revisable() -> None:
    record = _load_json(RECORD_PATH)
    revision_policy = record["revision_policy"]

    assert revision_policy["open_to_revision"] is True
    assert len(revision_policy["triggers"]) >= 1
