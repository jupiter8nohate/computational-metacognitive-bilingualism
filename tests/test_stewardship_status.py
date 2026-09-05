from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from cmb_glitch8.payments import GLITCH402_DEPLOYMENT_STATUS


ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = ROOT / "machine" / "stewardship-status.json"
SCHEMA_PATH = ROOT / "schemas" / "cmb.stewardship-status.v1.schema.json"


def _status() -> dict[str, object]:
    return json.loads(STATUS_PATH.read_text(encoding="utf-8"))


def test_stewardship_status_matches_strict_schema() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(_status())


def test_incubation_financial_boundaries_fail_closed() -> None:
    status = _status()

    assert status["project_status"] == "public-stewardship-incubation"
    assert status["legal_entity_formed"] is False
    assert status["tax_exempt_status_claimed"] is False
    assert status["active_fundraising"] is False
    assert status["donations_accepted"] is False
    assert status["paid_access"] is False
    assert status["production_settlement"] is False
    assert status["production_payee_configured"] is False
    assert status["investment_token_issued"] is False
    assert status["treasury_exists"] is False


def test_machine_status_matches_glitch402_runtime_status() -> None:
    status = _status()
    glitch402 = status["glitch402"]

    assert glitch402["deployment_status"] == GLITCH402_DEPLOYMENT_STATUS
    assert glitch402["research_only"] is True


def test_incubation_has_no_github_funding_surface() -> None:
    assert not (ROOT / ".github" / "FUNDING.yml").exists()


def test_status_documents_and_blueprint_resolve() -> None:
    status = _status()

    assert (ROOT / status["human_status_document"]).is_file()
    assert (ROOT / status["future_foundation_blueprint"]).is_file()
