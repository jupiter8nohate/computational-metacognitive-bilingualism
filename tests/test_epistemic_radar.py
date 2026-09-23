"""Deterministic tests for the CMB Epistemic Radar."""

from __future__ import annotations

import json
from pathlib import Path
import runpy

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
RADAR = runpy.run_path(str(ROOT / "scripts/build_epistemic_radar.py"))
WATCH_CONFIG = json.loads(
    (ROOT / "machine/global-ai-watch-config.json").read_text(encoding="utf-8")
)
RADAR_CONFIG = json.loads(
    (ROOT / "machine/cmb-epistemic-radar-config.json").read_text(encoding="utf-8")
)
RADAR_SCHEMA = json.loads(
    (ROOT / "schemas/cmb.epistemic-radar.v1.schema.json").read_text(encoding="utf-8")
)


def article(
    *,
    article_id: str,
    title: str,
    domain: str,
    cluster_id: str = "cluster-001",
    boundaries: list[str] | None = None,
    sectors: list[str] | None = None,
) -> dict[str, object]:
    return {
        "id": article_id,
        "title": title,
        "url": f"https://{domain}/{article_id}",
        "domain": domain,
        "seen_at": "2026-09-23T01:00:00Z",
        "language": "English",
        "source_country": "United States",
        "boundary_ids": boundaries or ["ACT"],
        "sector_ids": sectors or ["general"],
        "invariants": ["CAPABILITY != AUTHORITY"],
        "cluster_id": cluster_id,
        "cluster_source_count": 1,
        "wayback_history_url": f"https://web.archive.org/web/*/https://{domain}/{article_id}",
    }


def test_discrepancy_flag_requires_related_multi_source_opposition() -> None:
    cluster_discrepancies = RADAR["cluster_discrepancies"]
    items = [
        article(
            article_id="a" * 16,
            title="Regulator approved autonomous AI deployment",
            domain="one.example",
        ),
        article(
            article_id="b" * 16,
            title="Regulator blocked autonomous AI deployment",
            domain="two.example",
        ),
    ]

    flags = cluster_discrepancies(items, RADAR_CONFIG)

    assert any(
        flag["type"] == "opposition_language"
        and flag["label"] == "permission_status"
        for flag in flags
    )


def test_same_domain_opposition_is_not_cross_source_discrepancy() -> None:
    cluster_discrepancies = RADAR["cluster_discrepancies"]
    items = [
        article(
            article_id="a" * 16,
            title="Company approved autonomous AI deployment",
            domain="one.example",
        ),
        article(
            article_id="b" * 16,
            title="Company blocked autonomous AI deployment",
            domain="one.example",
        ),
    ]

    assert cluster_discrepancies(items, RADAR_CONFIG) == []


def test_emerging_vocabulary_is_a_concentration_signal_not_novelty_claim() -> None:
    emerging_vocabulary = RADAR["emerging_vocabulary"]
    current = [
        article(
            article_id="a" * 16,
            title="Neuromorphic accelerator enters AI laboratory",
            domain="one.example",
        ),
        article(
            article_id="b" * 16,
            title="Neuromorphic processor expands AI research",
            domain="two.example",
        ),
    ]
    baseline = current + [
        article(
            article_id="c" * 16,
            title="Older neuromorphic computing research continues",
            domain="three.example",
        ),
    ]

    candidates = emerging_vocabulary(current, baseline)

    neuromorphic = next(item for item in candidates if item["term"] == "neuromorphic")
    assert neuromorphic["current_mentions"] == 2
    assert neuromorphic["baseline_mentions"] == 3
    assert 0 < neuromorphic["current_concentration"] <= 1


def test_high_consequence_prediction_to_action_chain_generates_review_prompts() -> None:
    build_clusters = RADAR["build_clusters"]
    current = [
        article(
            article_id="a" * 16,
            title="Military AI intelligence prediction triggers autonomous drone review",
            domain="one.example",
            boundaries=["PREDICT", "ACT"],
            sectors=["military_security"],
        ),
        article(
            article_id="b" * 16,
            title="Military AI intelligence prediction triggers drone review",
            domain="two.example",
            boundaries=["PREDICT", "ACT"],
            sectors=["military_security"],
        ),
    ]

    clusters = build_clusters(current, RADAR_CONFIG)

    assert len(clusters) == 1
    cluster = clusters[0]
    assert "high_consequence_context" in cluster["attention_flags"]
    assert "prediction_to_action_chain" in cluster["attention_flags"]
    assert "military" in cluster["high_consequence_terms"]
    assert any("What evidence produced" in q for q in cluster["review_questions"])
    assert any("Who authorized" in q for q in cluster["review_questions"])


def test_snapshot_conforms_to_public_json_schema() -> None:
    build_snapshot = RADAR["build_snapshot"]
    current = [
        article(
            article_id="a" * 16,
            title="AI deepfake voice used in fraud investigation",
            domain="one.example",
            boundaries=["GENERATE", "ACT"],
            sectors=["cybercrime"],
        )
    ]
    baseline = list(current)

    snapshot = build_snapshot(current, baseline, WATCH_CONFIG, RADAR_CONFIG)

    Draft202012Validator(RADAR_SCHEMA).validate(snapshot)
    assert snapshot["summary"]["current_story_count"] == 1
    assert snapshot["boundary_counts"]["GENERATE"] == 1
    assert snapshot["boundary_counts"]["ACT"] == 1


def test_radar_rendering_escapes_untrusted_headline_html() -> None:
    render_clusters = RADAR["render_clusters"]
    current = [
        article(
            article_id="a" * 16,
            title="<img src=x onerror=alert(1)> military AI weapon review",
            domain="one.example",
            boundaries=["ACT"],
            sectors=["military_security"],
        )
    ]
    clusters = RADAR["build_clusters"](current, RADAR_CONFIG)

    rendered = render_clusters(clusters, current)

    assert "<img src=x" not in rendered
    assert "&lt;img src=x onerror=alert(1)&gt;" in rendered
