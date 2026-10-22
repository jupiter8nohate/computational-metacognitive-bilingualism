"""Regression tests for the bounded DEATH NOTE 2084 witness ledger."""

from __future__ import annotations

import copy
import json
import runpy
from pathlib import Path

MODULE = runpy.run_path(
    str(Path(__file__).resolve().parents[1] / "scripts/verify_2084_evidence.py")
)
validate = MODULE["validate"]
audit = MODULE["audit"]
REGISTRY = MODULE["REGISTRY"]
LEDGER = MODULE["LEDGER"]


def fixture() -> tuple[dict, str]:
    return (
        json.loads(REGISTRY.read_text(encoding="utf-8")),
        LEDGER.read_text(encoding="utf-8"),
    )


def test_current_registry_matches_the_canonical_publication() -> None:
    assert audit() == []


def test_duplicate_or_out_of_order_claim_ids_fail() -> None:
    data, text = fixture()
    data["entries"][9]["id"] = "09"
    assert any("unique sequential IDs" in issue for issue in validate(data, text))


def test_claim_must_not_be_marked_as_automatically_verified() -> None:
    data, text = fixture()
    data["entries"][0]["evidence_status"] = "absolute_proof"
    assert any("invalid evidence_status" in issue for issue in validate(data, text))


def test_fiction_boundary_cannot_be_switched_off() -> None:
    data, text = fixture()
    data["story_is_fictional"] = False
    assert any("Fiction boundary" in issue for issue in validate(data, text))


def test_unreferenced_source_fails() -> None:
    data, text = fixture()
    data["entries"][0]["sources"][0]["url"] = "https://example.org/unreviewed-source"
    assert any("not cited" in issue for issue in validate(data, text))


def test_non_https_source_fails() -> None:
    data, text = fixture()
    data["entries"][0]["sources"][0]["url"] = "http://example.org/unreviewed-source"
    assert any("malformed HTTPS" in issue for issue in validate(data, text))


def test_unlisted_claim_cannot_pass_as_published() -> None:
    data, text = fixture()
    modified = text.replace("| **10** |", "| **XX** |", 1)
    assert any("missing corresponding ledger table row" in issue for issue in validate(data, modified))


def test_missing_limitation_is_rejected() -> None:
    data, text = fixture()
    data = copy.deepcopy(data)
    data["entries"][4]["limitation"] = ""
    assert any("missing meaningful limitation" in issue for issue in validate(data, text))
