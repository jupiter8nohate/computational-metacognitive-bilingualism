"""Deterministic tests for the CMB Global AI Watch collector."""

from __future__ import annotations

import json
from pathlib import Path
import runpy
from urllib.parse import parse_qs, urlsplit


ROOT = Path(__file__).resolve().parents[1]
WATCH = runpy.run_path(str(ROOT / "scripts/update_global_ai_watch.py"))
CONFIG = json.loads(
    (ROOT / "machine/global-ai-watch-config.json").read_text(encoding="utf-8")
)


def test_tracking_parameters_do_not_create_duplicate_story_ids() -> None:
    normalized_url = WATCH["normalized_url"]

    first = normalized_url("https://example.com/story?id=7&utm_source=test&fbclid=abc")
    second = normalized_url("https://example.com/story?fbclid=other&id=7")

    assert first == "https://example.com/story?id=7"
    assert second == "https://example.com/story?id=7"


def test_classification_maps_headlines_to_explicit_cmb_boundaries() -> None:
    classify = WATCH["classify"]

    boundaries, sectors, invariants = classify(
        "Military AI intelligence report triggers autonomous targeting review",
        CONFIG,
    )

    assert "PREDICT" in boundaries
    assert "ACT" in boundaries
    assert "military_security" in sectors
    assert "PATTERN != PROOF" in invariants
    assert "CAPABILITY != AUTHORITY" in invariants


def test_normalizer_skips_unclassified_items_and_deduplicates() -> None:
    normalize_articles = WATCH["normalize_articles"]
    payload = {
        "articles": [
            {
                "title": "Election deepfake spreads AI-generated misinformation",
                "url": "https://news.example/a?utm_source=feed",
                "domain": "news.example",
                "seendate": "20260923T010203Z",
                "language": "English",
                "sourcecountry": "United States",
            },
            {
                "title": "Election deepfake spreads AI-generated misinformation",
                "url": "https://news.example/a?utm_source=other",
                "domain": "news.example",
                "seendate": "20260923T010204Z",
                "language": "English",
                "sourcecountry": "United States",
            },
            {
                "title": "Local football club wins final",
                "url": "https://sport.example/final",
                "domain": "sport.example",
                "seendate": "20260923T010205Z",
                "language": "English",
                "sourcecountry": "United Kingdom",
            },
        ]
    }

    articles = normalize_articles(payload, CONFIG)

    assert len(articles) == 1
    assert articles[0]["boundary_ids"] == ["GENERATE"]
    assert "elections_information" in articles[0]["sector_ids"]
    assert articles[0]["id"]
    assert articles[0]["wayback_history_url"].startswith("https://web.archive.org/web/*/")


def test_headline_clustering_counts_distinct_source_domains() -> None:
    cluster_articles = WATCH["cluster_articles"]
    articles = [
        {
            "title": "AI deepfake election video triggers investigation",
            "domain": "one.example",
        },
        {
            "title": "AI deepfake election video triggers new investigation",
            "domain": "two.example",
        },
    ]

    cluster_articles(articles)

    assert articles[0]["cluster_id"] == articles[1]["cluster_id"]
    assert articles[0]["cluster_source_count"] == 2
    assert articles[1]["cluster_source_count"] == 2


def test_rendering_escapes_untrusted_headline_html() -> None:
    render_cards = WATCH["render_cards"]
    article = {
        "title": "<script>alert(1)</script> AI deepfake",
        "url": "https://example.com/story",
        "domain": "example.com",
        "seen_at": "2026-09-23T01:02:03Z",
        "language": "English",
        "source_country": "United States",
        "boundary_ids": ["GENERATE"],
        "sector_ids": ["elections_information"],
        "invariants": ["GENERATED != VERIFIED"],
        "cluster_id": "cluster-001",
        "cluster_source_count": 1,
        "wayback_history_url": "https://web.archive.org/web/*/https://example.com/story",
    }

    rendered = render_cards([article], CONFIG)

    assert "<script>" not in rendered
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in rendered


def test_gdelt_url_uses_bounded_article_list_query() -> None:
    gdelt_url = WATCH["gdelt_url"]
    parsed = urlsplit(gdelt_url(CONFIG))
    params = parse_qs(parsed.query)

    assert parsed.scheme == "https"
    assert params["mode"] == ["artlist"]
    assert params["format"] == ["json"]
    assert params["timespan"] == [CONFIG["timespan"]]
    assert int(params["maxrecords"][0]) <= 250


def test_generated_section_replacement_preserves_authored_text() -> None:
    replace_generated_section = WATCH["replace_generated_section"]
    start = WATCH["START_MARKER"]
    end = WATCH["END_MARKER"]
    document = f"# Watch\n\nBefore\n\n{start}\nold\n{end}\n\nAfter\n"

    updated = replace_generated_section(document, "new snapshot")

    assert updated.startswith("# Watch\n\nBefore")
    assert "new snapshot" in updated
    assert "old" not in updated
    assert updated.rstrip().endswith("After")
