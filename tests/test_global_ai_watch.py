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



def test_published_link_ledger_is_bounded_and_source_diverse() -> None:
    select_published_links = WATCH["select_published_links"]
    config = dict(CONFIG)
    config["published_link_limit"] = 3
    config["published_links_per_domain"] = 1

    articles = []
    for index, domain in enumerate(
        ["one.example", "one.example", "two.example", "three.example", "four.example"]
    ):
        articles.append(
            {
                "id": f"{index:016x}",
                "title": f"AI autonomous system report {index}",
                "url": f"https://{domain}/story-{index}",
                "domain": domain,
                "seen_at": f"2026-09-23T01:0{index}:00Z",
                "language": "English",
                "source_country": "United States",
                "boundary_ids": ["ACT"],
                "sector_ids": ["general"],
                "invariants": ["CAPABILITY != AUTHORITY"],
                "cluster_id": f"cluster-{index:03d}",
                "cluster_source_count": 1,
                "wayback_history_url": f"https://web.archive.org/web/*/https://{domain}/story-{index}",
            }
        )

    published = select_published_links(articles, config)

    assert len(published) == 3
    assert len({item["domain"] for item in published}) == 3


def test_link_ledger_renders_links_without_article_body_or_archive_copy() -> None:
    render_cards = WATCH["render_cards"]
    article = {
        "id": "a" * 16,
        "title": "AI safety report",
        "url": "https://example.com/story",
        "domain": "example.com",
        "seen_at": "2026-09-23T01:02:03Z",
        "language": "English",
        "source_country": "United States",
        "boundary_ids": ["ACT"],
        "sector_ids": ["general"],
        "invariants": ["CAPABILITY != AUTHORITY"],
        "cluster_id": "cluster-001",
        "cluster_source_count": 1,
        "wayback_history_url": "https://web.archive.org/web/*/https://example.com/story",
    }

    rendered = render_cards([article], CONFIG)

    assert 'href="https://example.com/story"' in rendered
    assert "Wayback" not in rendered
    assert "<article" not in rendered



def test_curated_seed_is_exactly_ten_links_only() -> None:
    seed = json.loads(
        (ROOT / "machine/global-ai-watch-seed.json").read_text(encoding="utf-8")
    )

    assert seed["schema_version"] == "cmb.news-link-seed.v1"
    assert len(seed["links"]) == 10

    required = {"title", "source", "date", "url", "cmb", "topics"}
    forbidden = {"body", "article_body", "excerpt", "summary", "image", "html"}

    for item in seed["links"]:
        assert set(item) == required
        assert not forbidden.intersection(item)
        assert item["url"].startswith("https://")
        assert item["cmb"]



def test_rss_backup_collects_recent_direct_publisher_links(monkeypatch) -> None:
    import io
    from datetime import datetime, timedelta, timezone
    from email.utils import format_datetime

    published = format_datetime(datetime.now(timezone.utc) - timedelta(minutes=35))
    feed_xml = (
        "<rss><channel><item>"
        "<title>AI agent surveillance raises privacy concerns</title>"
        "<link>https://publisher.example/ai-story</link>"
        f"<pubDate>{published}</pubDate>"
        "</item></channel></rss>"
    ).encode("utf-8")

    class Response(io.BytesIO):
        status = 200

    def open_feed(request, timeout):
        assert request.full_url == "https://publisher.example/feed.xml"
        return Response(feed_xml)

    fetch = WATCH["fetch_rss_articles"]
    monkeypatch.setitem(fetch.__globals__, "urlopen", open_feed)
    config = dict(CONFIG)
    config["fallback_feeds"] = [
        {"name": "Test AI Publisher", "url": "https://publisher.example/feed.xml"}
    ]
    articles, feeds = fetch(config)
    assert feeds == config["fallback_feeds"]
    assert len(articles) == 1
    assert articles[0]["url"] == "https://publisher.example/ai-story"
    assert {"PREDICT", "ACT"}.issubset(set(articles[0]["boundary_ids"]))


def test_rss_backup_does_not_relabel_old_news_as_current(monkeypatch) -> None:
    import io
    from datetime import datetime, timedelta, timezone
    from email.utils import format_datetime

    old_date = format_datetime(datetime.now(timezone.utc) - timedelta(days=20))
    content = (
        "<rss><channel><item><title>AI agent privacy report</title>"
        "<link>https://publisher.example/old</link>"
        f"<pubDate>{old_date}</pubDate></item></channel></rss>"
    ).encode("utf-8")

    class Response(io.BytesIO):
        status = 200

    fetch = WATCH["fetch_rss_articles"]
    monkeypatch.setitem(fetch.__globals__, "urlopen", lambda request, timeout: Response(content))
    config = dict(CONFIG)
    config["fallback_feeds"] = [
        {"name": "Test", "url": "https://publisher.example/feed.xml"}
    ]
    import pytest

    with pytest.raises(WATCH["WatchError"], match="No recent"):
        fetch(config)


def test_fallback_keeps_newer_published_snapshot(monkeypatch, tmp_path: Path) -> None:
    import io
    from datetime import datetime, timedelta, timezone

    old_snapshot = json.loads(
        (ROOT / "machine/global-ai-watch.json").read_text(encoding="utf-8")
    )
    # The published Watch snapshot may have been refreshed earlier in this run.
    # Create a deterministic older local candidate instead of assuming its date.
    old_snapshot["generated_at"] = (
        datetime.now(timezone.utc) - timedelta(hours=5)
    ).isoformat().replace("+00:00", "Z")
    new_snapshot = json.loads(json.dumps(old_snapshot))
    new_snapshot["generated_at"] = (
        datetime.now(timezone.utc) - timedelta(minutes=45)
    ).isoformat().replace("+00:00", "Z")
    local_path = tmp_path / "local.json"
    local_path.write_text(json.dumps(old_snapshot), encoding="utf-8")

    class Response(io.BytesIO):
        status = 200

    recover = WATCH["best_available_snapshot"]
    monkeypatch.setitem(
        recover.__globals__,
        "urlopen",
        lambda request, timeout: Response(json.dumps(new_snapshot).encode("utf-8")),
    )
    result = recover(local_path)
    assert result["generated_at"] == new_snapshot["generated_at"]
    assert result["articles"] == new_snapshot["articles"]


def test_stale_marker_displays_last_collection_time() -> None:
    data = json.loads(
        (ROOT / "machine/global-ai-watch.json").read_text(encoding="utf-8")
    )
    result = WATCH["render_generated_block"](
        data, CONFIG, state="STALE - LIVE SOURCES UNAVAILABLE"
    )
    assert "cmb-watch-stale" in result
    assert "STALE - LIVE SOURCES UNAVAILABLE" in result
    assert data["generated_at"][:10] in result
