"""Offline integrity and correctness tests for the expanded CMB Observatory."""
from __future__ import annotations

import hashlib
import json
import runpy
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
OBS = runpy.run_path(str(ROOT / "scripts/build_observatory.py"))
RADAR = runpy.run_path(str(ROOT / "scripts/build_epistemic_radar.py"))
CODEX = runpy.run_path(str(ROOT / "scripts/generate_dna_witness.py"))


def sample(when: datetime | None = None, *, source: str = "Sample RSS") -> dict:
    now = when or datetime.now(timezone.utc).replace(microsecond=0)
    return {
        "schema_version": "cmb.global-ai-watch.v1",
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "source": {"name": source, "endpoint": "https://sample.example/rss"},
        "timespan": "72h",
        "articles": [
            {
                "id": "a" * 16,
                "title": "AI agent privacy investigation",
                "url": "https://example.org/news/1",
                "domain": "example.org",
                "seen_at": now.isoformat().replace("+00:00", "Z"),
                "boundary_ids": ["ACT"],
                "sector_ids": ["privacy_surveillance"],
            }
        ],
    }


def test_history_is_append_only_and_hash_linked() -> None:
    history = OBS["new_history"]()
    first = sample(datetime.now(timezone.utc) - timedelta(days=2))
    second = sample(datetime.now(timezone.utc) - timedelta(days=1))
    assert OBS["record_snapshot"](history, first, stale=False)
    assert OBS["record_snapshot"](history, second, stale=False)
    assert not OBS["record_snapshot"](history, second, stale=False)
    OBS["check_history"](history)
    assert len(history["entries"]) == 2
    assert history["entries"][1]["previous_hash"] == history["entries"][0]["hash"]
    history["entries"][0]["articles"][0]["title"] = "tampered"
    with pytest.raises(OBS["ObservatoryError"], match="hash-chain"):
        OBS["check_history"](history)


def test_stale_snapshot_does_not_extend_archive() -> None:
    history = OBS["new_history"]()
    assert not OBS["record_snapshot"](history, sample(), stale=True)
    assert history["entries"] == []


def test_replay_older_collection_cannot_replace_newer_one() -> None:
    history = OBS["new_history"]()
    fresh = sample()
    assert OBS["record_snapshot"](history, fresh, stale=False)
    assert not OBS["record_snapshot"](
        history, sample(datetime.now(timezone.utc) - timedelta(days=3)), stale=False
    )


def test_health_alert_requires_six_hours_of_staleness() -> None:
    snap = sample(datetime.now(timezone.utc) - timedelta(hours=8))
    health = OBS["health_report"](snap, OBS["new_history"](), stale=False, target_minutes=60)
    assert health["status"] == "STALE"
    assert health["alert_required"] is True
    assert health["age_minutes"] >= 360


def test_evidence_grades_never_pretend_to_fact_check() -> None:
    grades = OBS["source_assessments"](sample())
    grade = grades["articles"][0]
    assert grade["requires_human_review"]
    assert grade["corroboration"] == "not_checked"
    assert grade["verification_status"] == "publisher_report_not_independently_verified"


def test_historical_comparison_requires_distinct_matching_source_and_window() -> None:
    current = sample()
    history = OBS["new_history"]()
    assert RADAR["comparable_historical_baseline"](current, history) is None
    OBS["record_snapshot"](
        history, sample(datetime.now(timezone.utc) - timedelta(days=2)), stale=False
    )
    selected = RADAR["comparable_historical_baseline"](current, history)
    assert selected and selected[0]["url"] == "https://example.org/news/1"
    changed_source = sample(source="Different feed")
    assert RADAR["comparable_historical_baseline"](changed_source, history) is None
    changed_window = sample()
    changed_window["timespan"] = "24h"
    assert RADAR["comparable_historical_baseline"](changed_window, history) is None


def test_living_codex_is_noncanonical_and_links_source() -> None:
    history = OBS["new_history"]()
    OBS["record_snapshot"](history, sample(), stale=False)
    health = OBS["health_report"](sample(), history, stale=False, target_minutes=60)
    scroll = CODEX["make_scroll"](history, health)
    assert scroll["human_canon_untouched"]
    assert len(scroll["roles"]) == 6
    assert scroll["chapters"][0]["status"] == "fictional_allegory_not_fact_checked"
    body = CODEX["render"](scroll)
    assert "https://example.org/news/1" in body
    assert "not an AI language" in body
    assert "human-authored D.N.A. Bible" in body


def test_public_dashboard_escapes_headlines_without_innerhtml() -> None:
    js = (ROOT / "docs/javascripts/watch-dashboard.js").read_text(encoding="utf-8")
    assert "textContent" in js
    assert "innerHTML" not in js
    assert 'cache: "no-store"' in js


def test_placeholder_history_is_valid() -> None:
    history = json.loads(
        (ROOT / "machine/global-ai-watch-history.json").read_text(encoding="utf-8")
    )
    OBS["check_history"](history)
