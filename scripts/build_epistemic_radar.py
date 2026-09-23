"""Build the CMB Epistemic Radar from current and baseline GDELT samples.

This script performs transparent, deterministic comparison over public news
metadata. It does not fact-check article content and it never treats a pattern,
cluster, discrepancy flag, or vocabulary spike as proof.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from update_global_ai_watch import (
    WatchError,
    fetch_gdelt,
    load_json,
    normalize_articles,
)


ROOT = Path(__file__).resolve().parents[1]
WATCH_CONFIG = ROOT / "machine/global-ai-watch-config.json"
RADAR_CONFIG = ROOT / "machine/cmb-epistemic-radar-config.json"
DEFAULT_OUTPUT_JSON = ROOT / "machine/cmb-epistemic-radar.json"
DEFAULT_OUTPUT_DOC = ROOT / "docs/CMB_EPISTEMIC_RADAR.md"
START_MARKER = "<!-- CMB_EPISTEMIC_RADAR_GENERATED_START -->"
END_MARKER = "<!-- CMB_EPISTEMIC_RADAR_GENERATED_END -->"

WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9+'-]{2,}")
NUMBER_RE = re.compile(r"(?<![A-Za-z])(?:[$£€])?\d+(?:\.\d+)?%?")
VOCAB_STOPWORDS = {
    "about", "after", "again", "against", "agent", "agents", "ahead", "amid",
    "among", "artificial", "because", "before", "being", "between", "could",
    "from", "generative", "have", "into", "intelligence", "machine", "model",
    "models", "more", "news", "over", "report", "reports", "said", "says",
    "system", "systems", "that", "their", "this", "through", "using", "with",
    "would", "year", "years", "your", "ai",
}


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def count_matches(titles: list[str], terms: list[str]) -> int:
    lowered = [title.casefold() for title in titles]
    return sum(
        1
        for title in lowered
        if any(term.casefold() in title for term in terms)
    )


def technology_signals(
    current: list[dict[str, Any]],
    baseline: list[dict[str, Any]],
    radar_config: dict[str, Any],
) -> list[dict[str, Any]]:
    current_titles = [item["title"] for item in current]
    baseline_titles = [item["title"] for item in baseline]
    output: list[dict[str, Any]] = []

    for signal in radar_config.get("technology_signals", []):
        terms = [str(term) for term in signal.get("terms", [])]
        current_mentions = count_matches(current_titles, terms)
        baseline_mentions = count_matches(baseline_titles, terms)
        concentration = (
            current_mentions / baseline_mentions if baseline_mentions else 0.0
        )
        concentration = max(0.0, min(1.0, concentration))

        status = "not_observed"
        if current_mentions:
            status = "observed"
        if current_mentions >= 2 and concentration >= 0.5:
            status = "concentrated_now"

        output.append(
            {
                "id": str(signal["id"]),
                "label": str(signal["label"]),
                "current_mentions": current_mentions,
                "baseline_mentions": baseline_mentions,
                "current_concentration": round(concentration, 4),
                "status": status,
            }
        )

    output.sort(
        key=lambda item: (
            item["status"] == "concentrated_now",
            item["current_mentions"],
            item["current_concentration"],
        ),
        reverse=True,
    )
    return output


def vocabulary_counts(articles: list[dict[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for article in articles:
        seen_in_title: set[str] = set()
        for match in WORD_RE.findall(article["title"]):
            term = match.casefold().strip("'-+")
            if len(term) < 4 or term in VOCAB_STOPWORDS:
                continue
            if term in seen_in_title:
                continue
            seen_in_title.add(term)
            counts[term] += 1
    return counts


def emerging_vocabulary(
    current: list[dict[str, Any]],
    baseline: list[dict[str, Any]],
    limit: int = 20,
) -> list[dict[str, Any]]:
    current_counts = vocabulary_counts(current)
    baseline_counts = vocabulary_counts(baseline)
    candidates: list[dict[str, Any]] = []

    for term, current_mentions in current_counts.items():
        baseline_mentions = baseline_counts.get(term, 0)
        if current_mentions < 2 or baseline_mentions < 1:
            continue
        concentration = current_mentions / baseline_mentions
        if concentration < 0.5:
            continue
        candidates.append(
            {
                "term": term,
                "current_mentions": current_mentions,
                "baseline_mentions": baseline_mentions,
                "current_concentration": round(min(1.0, concentration), 4),
            }
        )

    candidates.sort(
        key=lambda item: (
            item["current_concentration"],
            item["current_mentions"],
            -item["baseline_mentions"],
            item["term"],
        ),
        reverse=True,
    )
    return candidates[:limit]


def cue_present(title: str, cues: list[str]) -> bool:
    lowered = title.casefold()
    return any(cue.casefold() in lowered for cue in cues)


def extract_numbers(title: str) -> set[str]:
    values = set(NUMBER_RE.findall(title))
    filtered: set[str] = set()
    for value in values:
        digits = re.sub(r"[^0-9.]", "", value)
        try:
            numeric = float(digits)
        except ValueError:
            continue
        if 1900 <= numeric <= 2100 and value.isdigit():
            continue
        filtered.add(value)
    return filtered


def cluster_discrepancies(
    articles: list[dict[str, Any]],
    radar_config: dict[str, Any],
) -> list[dict[str, str]]:
    domains = {item["domain"] for item in articles}
    if len(domains) < 2 or len(articles) < 2:
        return []

    discrepancies: list[dict[str, str]] = []

    for axis in radar_config.get("contradiction_axes", []):
        left_hits = [
            item for item in articles
            if cue_present(item["title"], [str(x) for x in axis["left"]])
        ]
        right_hits = [
            item for item in articles
            if cue_present(item["title"], [str(x) for x in axis["right"]])
        ]
        if not left_hits or not right_hits:
            continue
        if not any(
            left["domain"] != right["domain"]
            for left in left_hits
            for right in right_hits
        ):
            continue

        discrepancies.append(
            {
                "type": "opposition_language",
                "label": str(axis["id"]),
                "details": (
                    "Related headlines contain opposing cue sets across "
                    "different source domains. Human comparison is required."
                ),
            }
        )

    number_sets = [
        (item["domain"], extract_numbers(item["title"]))
        for item in articles
    ]
    distinct_numbers = set().union(*(numbers for _, numbers in number_sets))
    domains_with_numbers = {
        domain for domain, numbers in number_sets if numbers
    }
    if len(distinct_numbers) >= 2 and len(domains_with_numbers) >= 2:
        discrepancies.append(
            {
                "type": "numeric_variation",
                "label": "headline_numbers_differ",
                "details": (
                    "Related headlines contain different numeric values across "
                    "multiple source domains. The values may refer to different "
                    "quantities, so this is a review prompt rather than a contradiction."
                ),
            }
        )

    return discrepancies


def review_questions(boundaries: set[str], radar_config: dict[str, Any]) -> list[str]:
    lessons = radar_config.get("lessons", {})
    questions: list[str] = []
    for boundary in ("PREDICT", "GENERATE", "ACT"):
        if boundary not in boundaries:
            continue
        lesson = lessons.get(boundary, {})
        question = str(lesson.get("question", "")).strip()
        check = str(lesson.get("check", "")).strip()
        if question:
            questions.append(question)
        if check:
            questions.append("Verification check: " + check)
    return questions


def build_clusters(
    current: list[dict[str, Any]],
    radar_config: dict[str, Any],
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for article in current:
        grouped[article["cluster_id"]].append(article)

    output: list[dict[str, Any]] = []
    high_terms = [str(x) for x in radar_config.get("high_consequence_terms", [])]

    for cluster_id, articles in grouped.items():
        boundaries = {
            boundary
            for article in articles
            for boundary in article["boundary_ids"]
        }
        sectors = {
            sector
            for article in articles
            for sector in article["sector_ids"]
        }
        title_blob = " ".join(item["title"] for item in articles).casefold()
        high_consequence = [
            term for term in high_terms if term.casefold() in title_blob
        ]
        discrepancies = cluster_discrepancies(articles, radar_config)

        flags: list[str] = []
        source_count = len({item["domain"] for item in articles})
        if source_count == 1:
            flags.append("single_source_cluster")
        else:
            flags.append("multi_source_cluster")
        if high_consequence:
            flags.append("high_consequence_context")
        if discrepancies:
            flags.append("cross_source_review_needed")
        if "ACT" in boundaries:
            flags.append("machine_to_action_boundary")
        if {"PREDICT", "ACT"} <= boundaries:
            flags.append("prediction_to_action_chain")
        if {"GENERATE", "ACT"} <= boundaries:
            flags.append("generation_to_action_chain")

        output.append(
            {
                "id": cluster_id,
                "article_ids": [item["id"] for item in articles],
                "source_count": source_count,
                "boundary_ids": sorted(boundaries),
                "sector_ids": sorted(sectors),
                "high_consequence_terms": high_consequence,
                "discrepancies": discrepancies,
                "review_questions": review_questions(boundaries, radar_config),
                "attention_flags": flags,
            }
        )

    output.sort(
        key=lambda cluster: (
            bool(cluster["discrepancies"]),
            bool(cluster["high_consequence_terms"]),
            cluster["source_count"],
            len(cluster["article_ids"]),
        ),
        reverse=True,
    )
    return output


def boundary_counts(current: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"PREDICT": 0, "GENERATE": 0, "ACT": 0}
    for article in current:
        for boundary in article["boundary_ids"]:
            if boundary in counts:
                counts[boundary] += 1
    return counts


def build_snapshot(
    current: list[dict[str, Any]],
    baseline: list[dict[str, Any]],
    watch_config: dict[str, Any],
    radar_config: dict[str, Any],
) -> dict[str, Any]:
    clusters = build_clusters(current, radar_config)
    signals = technology_signals(current, baseline, radar_config)
    observed_signals = [
        item for item in signals if item["status"] != "not_observed"
    ]

    return {
        "schema_version": "cmb.epistemic-radar.v1",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "current_timespan": str(radar_config["current_timespan"]),
        "baseline_timespan": str(radar_config["baseline_timespan"]),
        "source": {
            "name": str(watch_config["source"]["name"]),
            "endpoint": str(watch_config["source"]["endpoint"]),
        },
        "epistemic_boundaries": list(radar_config["epistemic_boundaries"]),
        "summary": {
            "current_story_count": len(current),
            "current_domain_count": len({item["domain"] for item in current}),
            "cluster_count": len(clusters),
            "discrepancy_cluster_count": sum(
                1 for item in clusters if item["discrepancies"]
            ),
            "high_consequence_cluster_count": sum(
                1 for item in clusters if item["high_consequence_terms"]
            ),
            "technology_signal_count": len(observed_signals),
        },
        "boundary_counts": boundary_counts(current),
        "technology_signals": signals,
        "emerging_vocabulary": emerging_vocabulary(current, baseline),
        "clusters": clusters,
    }


def title_for_cluster(
    cluster: dict[str, Any],
    article_lookup: dict[str, dict[str, Any]],
) -> str:
    for article_id in cluster["article_ids"]:
        article = article_lookup.get(article_id)
        if article:
            return article["title"]
    return cluster["id"]


def render_signal_chips(signals: list[dict[str, Any]], limit: int = 8) -> str:
    visible = [item for item in signals if item["status"] != "not_observed"][:limit]
    if not visible:
        return '<div class="cmb-watch-empty">No configured technology families were observed in this sample.</div>'

    rows = []
    for item in visible:
        label = html.escape(item["label"])
        rows.append(
            '<div class="cmb-radar-signal">'
            f"<strong>{label}</strong>"
            f"<span>{item['current_mentions']} current / {item['baseline_mentions']} baseline sample mentions</span>"
            f"<code>{item['status']}</code>"
            "</div>"
        )
    return '<div class="cmb-radar-signals">' + "".join(rows) + "</div>"


def render_vocab(items: list[dict[str, Any]], limit: int = 10) -> str:
    if not items:
        return '<p>No concentrated vocabulary candidates met the current threshold.</p>'
    chips = []
    for item in items[:limit]:
        chips.append(
            '<span class="cmb-radar-vocab">'
            + html.escape(item["term"])
            + f" <small>{item['current_mentions']}/{item['baseline_mentions']}</small>"
            + "</span>"
        )
    return '<div class="cmb-radar-vocab-list">' + "".join(chips) + "</div>"


def render_clusters(
    clusters: list[dict[str, Any]],
    current: list[dict[str, Any]],
    limit: int = 8,
) -> str:
    article_lookup = {item["id"]: item for item in current}
    interesting = [
        cluster for cluster in clusters
        if cluster["discrepancies"]
        or cluster["high_consequence_terms"]
        or "prediction_to_action_chain" in cluster["attention_flags"]
        or "generation_to_action_chain" in cluster["attention_flags"]
    ][:limit]

    if not interesting:
        return '<div class="cmb-watch-empty">No clusters met the current review-prompt threshold.</div>'

    cards: list[str] = []
    for cluster in interesting:
        title = html.escape(title_for_cluster(cluster, article_lookup))
        flags = " · ".join(cluster["attention_flags"])
        boundaries = " + ".join(cluster["boundary_ids"]) or "unclassified"
        discrepancy_text = (
            "; ".join(
                f"{item['label']}: {item['details']}"
                for item in cluster["discrepancies"]
            )
            if cluster["discrepancies"]
            else "No cross-source discrepancy rule fired."
        )
        questions = "".join(
            f"<li>{html.escape(question)}</li>"
            for question in cluster["review_questions"]
        )

        source_links: list[str] = []
        for article_id in cluster["article_ids"][:5]:
            article = article_lookup.get(article_id)
            if not article:
                continue
            source_links.append(
                '<li><a rel="noopener noreferrer" href="'
                + html.escape(article["url"], quote=True)
                + '">'
                + html.escape(article["domain"])
                + "</a></li>"
            )

        cards.append(
            '<article class="cmb-radar-card">'
            f'<div class="cmb-news-card__signal">{html.escape(boundaries)}</div>'
            f"<h3>{title}</h3>"
            f'<p><strong>Review flags:</strong> {html.escape(flags)}</p>'
            f'<p><strong>Discrepancy layer:</strong> {html.escape(discrepancy_text)}</p>'
            "<details><summary>Teach mode: questions to ask</summary>"
            f"<ul>{questions}</ul></details>"
            "<details><summary>Open source coverage</summary>"
            f"<ul>{''.join(source_links)}</ul></details>"
            "</article>"
        )

    return '<div class="cmb-radar-grid">' + "".join(cards) + "</div>"


def render_generated(
    snapshot: dict[str, Any],
    current: list[dict[str, Any]],
    radar_config: dict[str, Any],
) -> str:
    summary = snapshot["summary"]
    generated = snapshot["generated_at"].replace("T", " ").replace("Z", " UTC")
    counts = snapshot["boundary_counts"]

    return "\n\n".join(
        [
            (
                '<div class="cmb-radar-status">'
                f"RADAR SAMPLE // {html.escape(generated)} // "
                f"PREDICT={counts.get('PREDICT', 0)} · "
                f"GENERATE={counts.get('GENERATE', 0)} · "
                f"ACT={counts.get('ACT', 0)}"
                "</div>"
            ),
            "\n".join(
                [
                    '<div class="cmb-watch-metrics">',
                    f'<div><strong>{summary["current_story_count"]}</strong><span>current stories</span></div>',
                    f'<div><strong>{summary["cluster_count"]}</strong><span>story clusters</span></div>',
                    f'<div><strong>{summary["discrepancy_cluster_count"]}</strong><span>discrepancy flags</span></div>',
                    f'<div><strong>{summary["technology_signal_count"]}</strong><span>technology signals</span></div>',
                    "</div>",
                ]
            ),
            "### Technology signals\n\n" + render_signal_chips(snapshot["technology_signals"], int(radar_config.get("published_signal_limit", 8))),
            (
                "### Emerging vocabulary candidates\n\n"
                + render_vocab(snapshot["emerging_vocabulary"], int(radar_config.get("published_vocabulary_limit", 10)))
                + "\n\n"
                "<p class=\"cmb-watch-method-note\">"
                "These are concentration signals in finite GDELT samples, not proof that a term is new, important, or technically novel."
                "</p>"
            ),
            "### Human-review clusters\n\n" + render_clusters(snapshot["clusters"], current, int(radar_config.get("published_cluster_limit", 8))),
        ]
    )


def replace_generated(document: str, generated: str) -> str:
    if START_MARKER not in document or END_MARKER not in document:
        raise WatchError("Epistemic Radar document is missing generated markers")
    before, rest = document.split(START_MARKER, 1)
    _, after = rest.split(END_MARKER, 1)
    return (
        before
        + START_MARKER
        + "\n\n"
        + generated.rstrip()
        + "\n\n"
        + END_MARKER
        + after
    )


def fetch_sample(
    watch_config: dict[str, Any],
    timespan: str,
    max_records: int,
    fixture: Path | None,
) -> list[dict[str, Any]]:
    config = deepcopy(watch_config)
    config["timespan"] = timespan
    config["max_records"] = max_records
    payload = load_json(fixture) if fixture else fetch_gdelt(config)
    return normalize_articles(payload, config)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--watch-config", type=Path, default=WATCH_CONFIG)
    parser.add_argument("--radar-config", type=Path, default=RADAR_CONFIG)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-doc", type=Path, default=DEFAULT_OUTPUT_DOC)
    parser.add_argument("--current-fixture", type=Path)
    parser.add_argument("--baseline-fixture", type=Path)
    args = parser.parse_args()

    try:
        watch_config = load_json(args.watch_config)
        radar_config = load_json(args.radar_config)
        current = fetch_sample(
            watch_config,
            str(radar_config["current_timespan"]),
            int(radar_config["max_records"]),
            args.current_fixture,
        )
        baseline = fetch_sample(
            watch_config,
            str(radar_config["baseline_timespan"]),
            int(radar_config["max_records"]),
            args.baseline_fixture,
        )
        snapshot = build_snapshot(current, baseline, watch_config, radar_config)
        document = args.output_doc.read_text(encoding="utf-8")
        updated = replace_generated(document, render_generated(snapshot, current, radar_config))
        write_atomic(
            args.output_json,
            json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n",
        )
        write_atomic(args.output_doc, updated)
    except (OSError, WatchError, KeyError, TypeError, ValueError) as exc:
        print(f"Epistemic Radar build failed: {exc}", file=sys.stderr)
        return 2

    print(
        "Epistemic Radar built: "
        f"{snapshot['summary']['current_story_count']} current stories, "
        f"{snapshot['summary']['cluster_count']} clusters, "
        f"{snapshot['summary']['discrepancy_cluster_count']} discrepancy prompts."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
