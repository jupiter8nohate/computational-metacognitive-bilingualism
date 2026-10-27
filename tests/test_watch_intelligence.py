"""Regression tests for the evidence-bounded Watch intelligence layer."""
from __future__ import annotations

import copy
import json
import runpy
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
MODULE = runpy.run_path(str(ROOT / "scripts/build_watch_intelligence.py"))
BUILD = MODULE["build_intelligence"]


def fixture():
    articles = [
        {
            "id": "b" * 16,
            "title": "Court reviews police AI facial recognition and privacy complaint",
            "url": "https://example.org/ai?utm_source=test",
            "domain": "example.org",
            "seen_at": "2026-10-26T08:00:00Z",
            "language": "English",
            "source_country": None,
            "boundary_ids": ["PREDICT", "ACT"],
            "sector_ids": ["justice_policing", "privacy_surveillance"],
            "cluster_id": "cluster-001",
            "wayback_history_url": "https://web.archive.org/web/*/https://example.org/ai",
        },
        {
            "id": "a" * 16,
            "title": "Robot vendor launches AI agent",
            "url": "https://example.net/robots",
            "domain": "example.net",
            "seen_at": "2026-10-26T09:00:00Z",
            "language": None,
            "source_country": "United Kingdom",
            "boundary_ids": ["ACT"],
            "sector_ids": ["general"],
            "cluster_id": "cluster-002",
            "wayback_history_url": "https://web.archive.org/web/*/https://example.net/robots",
        },
    ]
    snapshot = {"schema_version": "cmb.global-ai-watch.v1",
                "generated_at": "2026-10-26T10:00:00Z", "article_count": len(articles), "articles": articles}
    assessments = {"schema_version": "cmb.watch-assessments.v1",
                   "generated_at": snapshot["generated_at"],
                   "articles": [{"article_id": "b" * 16, "traceability_grade": "SOURCE_DOMAIN_CONSISTENT"}]}
    health = {"schema_version": "cmb.watch-health.v1", "checked_at": "2026-10-26T11:00:00Z",
              "last_successful_collection": snapshot["generated_at"], "status": "CURRENT"}
    history = {"schema_version": "cmb.watch-history.v1", "entries": [
        {"collected_at": "2026-10-26T01:00:00Z", "article_count": 2,
         "articles": [{"url": "https://example.org/ai"}, {"url": "https://example.net/robots"}]},
        {"collected_at": "2026-10-26T02:00:00Z", "article_count": 2,
         "articles": [{"url": "https://example.org/ai"}, {"url": "https://example.net/robots"}]},
    ]}
    return snapshot, assessments, health, history


def test_metadata_triage_is_not_fact_check_or_risk_score():
    payload = BUILD(*fixture())
    assert len(payload["dossiers"]) == 2
    first, second = payload["dossiers"]
    assert first["triage_priority"] == "REVIEW_FIRST"
    assert first["rights_lenses"] == ["privacy_consent", "due_process"]
    assert first["legal_watch_candidate"]
    assert first["claim_verification"] == "NOT_INDEPENDENTLY_CHECKED"
    assert first["independent_corroboration"] == "NOT_CHECKED"
    assert first["reported_incident_status"] == "NOT_ESTABLISHED_FROM_HEADLINE"
    assert "Who authorized" in " ".join(first["review_questions"])
    assert second["triage_priority"] == "ROUTINE_REVIEW"
    assert second["traceability_grade"] == "NOT_ASSESSED"
    assert payload["coverage"]["distinct_publisher_domains"] == 2


def test_dossiers_deterministic_and_tied_to_urls():
    record = fixture()
    assert BUILD(*record) == BUILD(*copy.deepcopy(record))
    assert BUILD(*record)["dossiers"][0]["dossier_id"].startswith("watch-")


def test_history_does_not_misstate_repeated_links_as_independent_events():
    payload = BUILD(*fixture())
    day = payload["history"][0]
    assert day == {"day": "2026-10-26", "collections": 2,
                   "observed_links": 4, "distinct_links_within_day": 2}


def test_mismatched_snapshots_fail_closed():
    watch, assessments, health, history = fixture()
    health["last_successful_collection"] = "2026-10-25T00:00:00Z"
    with pytest.raises(ValueError, match="same collection"):
        BUILD(watch, assessments, health, history)
    health["last_successful_collection"] = watch["generated_at"]
    assessments["generated_at"] = None
    with pytest.raises(ValueError, match="same collection"):
        BUILD(watch, assessments, health, history)


def test_source_country_is_not_interpreted_as_event_location():
    payload = BUILD(*fixture())
    assert payload["coverage"]["source_countries"] == {
        "United Kingdom": 1, "unspecified": 1}
    assert "SOURCE_COUNTRY != INCIDENT_LOCATION" in payload["boundaries"]


def test_bad_url_fails_closed():
    watch, assessments, health, history = fixture()
    watch["articles"][0]["url"] = "javascript:alert(1)"
    with pytest.raises(ValueError, match="Invalid source URL"):
        BUILD(watch, assessments, health, history)


def test_output_validates_against_public_schema():
    schema = json.loads((ROOT / "schemas/cmb.watch-intelligence.v1.schema.json").read_text())
    Draft202012Validator.check_schema(schema)
    errors = list(Draft202012Validator(schema).iter_errors(BUILD(*fixture())))
    assert not errors, [error.message for error in errors]


def test_committed_watch_seed_is_not_misrepresented_as_current():
    seed = json.loads((ROOT / "machine/global-ai-watch.json").read_text())
    assert seed["generated_at"] < "2026-10-27T00:00:00Z"
    assert "HEADLINE != INCIDENT_PROOF" in BUILD(*fixture())["boundaries"]
