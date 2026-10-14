"""Refresh the public CMB Global AI Watch from GDELT DOC 2.0 metadata.

The collector stores headlines, source metadata, direct source URLs, and CMB
classification labels. It does not copy article bodies and it does not treat a
headline, cluster, or GDELT match as independent confirmation of a claim.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "machine/global-ai-watch-config.json"
DEFAULT_DOC = ROOT / "docs/GLOBAL_AI_WATCH.md"
DEFAULT_JSON = ROOT / "machine/global-ai-watch.json"
START_MARKER = "<!-- CMB_GLOBAL_AI_WATCH_GENERATED_START -->"
END_MARKER = "<!-- CMB_GLOBAL_AI_WATCH_GENERATED_END -->"
PUBLIC_SNAPSHOT = "https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/machine/global-ai-watch.json"
USER_AGENT = (
    "CMB-Global-AI-Watch/1.0 "
    "(+https://github.com/jupiter8nohate/computational-metacognitive-bilingualism)"
)
TRACKING_KEYS = {
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
    "ref",
    "ref_src",
}
STOPWORDS = {
    "about",
    "after",
    "against",
    "artificial",
    "before",
    "being",
    "could",
    "from",
    "have",
    "into",
    "machine",
    "more",
    "news",
    "over",
    "said",
    "says",
    "that",
    "their",
    "this",
    "through",
    "using",
    "with",
    "would",
}


class WatchError(RuntimeError):
    """Raised when the watch snapshot cannot be produced safely."""


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WatchError(f"Cannot read JSON from {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise WatchError(f"Expected a JSON object in {path}")
    return value


def normalized_url(raw: str) -> str | None:
    try:
        parsed = urlsplit(raw.strip())
    except ValueError:
        return None
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        return None

    cleaned_query = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        lower = key.lower()
        if lower.startswith("utm_") or lower in TRACKING_KEYS:
            continue
        cleaned_query.append((key, value))

    path = parsed.path or "/"
    return urlunsplit(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            path,
            urlencode(cleaned_query, doseq=True),
            "",
        )
    )


def parse_seen_date(value: object) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    raw = value.strip()
    for fmt in ("%Y%m%dT%H%M%SZ", "%Y%m%d%H%M%S", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            dt = datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
            return dt.isoformat().replace("+00:00", "Z")
        except ValueError:
            continue
    return None


def contains_term(text: str, term: str) -> bool:
    return term.casefold() in text.casefold()


def classify(title: str, config: dict[str, Any]) -> tuple[list[str], list[str], list[str]]:
    boundary_ids: list[str] = []
    invariants: list[str] = []
    sector_ids: list[str] = []

    for boundary in config.get("boundaries", []):
        terms = boundary.get("terms", [])
        if any(contains_term(title, str(term)) for term in terms):
            boundary_id = str(boundary["id"])
            boundary_ids.append(boundary_id)
            for invariant in boundary.get("invariants", []):
                invariant_text = str(invariant)
                if invariant_text not in invariants:
                    invariants.append(invariant_text)

    for sector in config.get("sectors", []):
        terms = sector.get("terms", [])
        if any(contains_term(title, str(term)) for term in terms):
            sector_ids.append(str(sector["id"]))

    if not sector_ids:
        sector_ids = ["general"]

    return boundary_ids, sector_ids, invariants


def title_tokens(title: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", title.casefold())
        if len(token) > 2 and token not in STOPWORDS
    }


def jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def cluster_articles(articles: list[dict[str, Any]], threshold: float = 0.55) -> None:
    clusters: list[dict[str, Any]] = []

    for article in articles:
        tokens = title_tokens(article["title"])
        best_index: int | None = None
        best_score = 0.0

        for index, cluster in enumerate(clusters):
            score = jaccard(tokens, cluster["anchor_tokens"])
            if score > best_score:
                best_index = index
                best_score = score

        if best_index is not None and best_score >= threshold:
            clusters[best_index]["articles"].append(article)
            article["cluster_id"] = clusters[best_index]["id"]
        else:
            cluster_id = f"cluster-{len(clusters) + 1:03d}"
            clusters.append(
                {
                    "id": cluster_id,
                    "anchor_tokens": tokens,
                    "articles": [article],
                }
            )
            article["cluster_id"] = cluster_id

    for cluster in clusters:
        source_count = len({item["domain"] for item in cluster["articles"]})
        for article in cluster["articles"]:
            article["cluster_source_count"] = max(1, source_count)


def normalize_articles(payload: dict[str, Any], config: dict[str, Any]) -> list[dict[str, Any]]:
    raw_articles = payload.get("articles", [])
    if not isinstance(raw_articles, list):
        raise WatchError("GDELT response does not contain an articles array")

    seen_urls: set[str] = set()
    articles: list[dict[str, Any]] = []
    archive_base = str(config["source"]["archive_history_base"])

    for raw in raw_articles:
        if not isinstance(raw, dict):
            continue
        title = str(raw.get("title") or "").strip()
        source_url = str(raw.get("url") or "").strip()
        normalized = normalized_url(source_url)
        if not title or normalized is None or normalized in seen_urls:
            continue

        boundary_ids, sector_ids, invariants = classify(title, config)
        if not boundary_ids:
            continue

        seen_urls.add(normalized)
        domain = str(raw.get("domain") or urlsplit(normalized).netloc).strip()
        if not domain:
            domain = urlsplit(normalized).netloc

        article = {
            "id": hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16],
            "title": title,
            "url": source_url,
            "domain": domain,
            "seen_at": parse_seen_date(raw.get("seendate")),
            "language": str(raw["language"]).strip() if raw.get("language") else None,
            "source_country": (
                str(raw["sourcecountry"]).strip() if raw.get("sourcecountry") else None
            ),
            "boundary_ids": boundary_ids,
            "sector_ids": sector_ids,
            "invariants": invariants,
            "cluster_id": "",
            "cluster_source_count": 1,
            "wayback_history_url": archive_base + source_url,
        }
        articles.append(article)

    articles.sort(key=lambda item: item["seen_at"] or "", reverse=True)
    cluster_articles(articles)
    return articles



def select_published_links(
    articles: list[dict[str, Any]],
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    """Select a small, diverse link ledger from the analyzed metadata sample."""
    limit = max(1, int(config.get("published_link_limit", 24)))
    per_domain = max(1, int(config.get("published_links_per_domain", 2)))
    domain_counts: dict[str, int] = {}
    selected: list[dict[str, Any]] = []

    ranked = sorted(
        articles,
        key=lambda item: (
            len(item["boundary_ids"]),
            item["cluster_source_count"],
            len(item["sector_ids"]),
            item["seen_at"] or "",
        ),
        reverse=True,
    )

    for article in ranked:
        domain = article["domain"]
        if domain_counts.get(domain, 0) >= per_domain:
            continue
        selected.append(article)
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
        if len(selected) >= limit:
            break

    selected.sort(key=lambda item: item["seen_at"] or "", reverse=True)
    return selected


def gdelt_url(config: dict[str, Any]) -> str:
    params = {
        "query": config["query"],
        "mode": "artlist",
        "format": "json",
        "maxrecords": int(config.get("max_records", 100)),
        "timespan": config.get("timespan", "24h"),
        "sort": "datedesc",
    }
    return str(config["source"]["endpoint"]) + "?" + urlencode(params)


def fetch_gdelt(config: dict[str, Any], *, timeout: float = 20.0, attempts: int = 3) -> dict[str, Any]:
    target = gdelt_url(config)
    last_error: Exception | None = None

    for attempt in range(1, attempts + 1):
        request = Request(
            target,
            headers={
                "Accept": "application/json",
                "User-Agent": USER_AGENT,
            },
        )
        try:
            with urlopen(request, timeout=timeout) as response:
                if response.status != 200:
                    raise WatchError(f"GDELT returned HTTP {response.status}")
                body = response.read()
            payload = json.loads(body.decode("utf-8"))
            if not isinstance(payload, dict):
                raise WatchError("GDELT returned a non-object JSON payload")
            return payload
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, WatchError) as exc:
            last_error = exc
            if attempt < attempts:
                time.sleep(1.5 * attempt)

    raise WatchError(f"GDELT fetch failed after {attempts} attempts: {last_error}")


def fetch_rss_articles(
    config: dict[str, Any], *, timeout: float = 12.0
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Use direct publisher RSS headlines when GDELT is rate-limited.

    Only recent, source-linked metadata is retained; we never copy article bodies.
    Every feed is optional, so a single publisher outage cannot stop the watch.
    """
    now = datetime.now(timezone.utc)
    max_age = timedelta(hours=int(config.get("fallback_max_age_hours", 120)))
    samples: list[dict[str, Any]] = []
    active_feeds: list[dict[str, str]] = []
    failures: list[str] = []

    for feed in config.get("fallback_feeds", []):
        name, url = str(feed["name"]), str(feed["url"])
        if urlsplit(url).scheme != "https":
            failures.append(f"{name}: non-HTTPS feed")
            continue
        request = Request(
            url,
            headers={
                "Accept": "application/rss+xml, application/xml, text/xml",
                "User-Agent": USER_AGENT,
            },
        )
        try:
            with urlopen(request, timeout=timeout) as response:
                if response.status != 200:
                    raise WatchError(f"HTTP {response.status}")
                xml_bytes = response.read(2_000_001)
            if len(xml_bytes) > 2_000_000:
                raise WatchError("RSS feed exceeds 2 MB")
            document = ET.fromstring(xml_bytes)
            candidates = document.findall("./channel/item")
            if not candidates:
                raise WatchError("RSS contains no channel items")
        except (OSError, ValueError, ET.ParseError, WatchError) as exc:
            failures.append(f"{name}: {exc}")
            continue

        valid_count = 0
        for item in candidates:
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            raw_date = (item.findtext("pubDate") or "").strip()
            if not title or normalized_url(link) is None or not raw_date:
                continue
            try:
                published = parsedate_to_datetime(raw_date)
            except (ValueError, TypeError, IndexError):
                continue
            if published.tzinfo is None:
                published = published.replace(tzinfo=timezone.utc)
            published = published.astimezone(timezone.utc)
            if not (now - max_age <= published <= now + timedelta(hours=2)):
                continue
            samples.append(
                {
                    "title": title,
                    "url": link,
                    "domain": urlsplit(link).netloc,
                    "seendate": published.strftime("%Y%m%dT%H%M%SZ"),
                    "language": "English",
                    "sourcecountry": None,
                }
            )
            valid_count += 1
        if valid_count:
            active_feeds.append({"name": name, "url": url})

    articles = normalize_articles({"articles": samples}, config)
    if not articles:
        raise WatchError(
            "No recent, CMB-relevant RSS headlines available; "
            + ("; ".join(failures) if failures else "feeds returned no matching headlines")
        )
    return articles, active_feeds


def snapshot_date(data: dict[str, Any]) -> datetime | None:
    raw = data.get("generated_at")
    if not isinstance(raw, str):
        return None
    try:
        value = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    if value.tzinfo is None:
        return None
    return value.astimezone(timezone.utc)


def usable_snapshot(data: dict[str, Any]) -> bool:
    """Reject malformed or future-dated published fallback metadata."""
    when = snapshot_date(data)
    if (
        data.get("schema_version") != "cmb.global-ai-watch.v1"
        or when is None
        or when > datetime.now(timezone.utc) + timedelta(hours=2)
    ):
        return False
    articles = data.get("articles")
    if not isinstance(articles, list) or not articles:
        return False
    if data.get("article_count") != len(articles):
        return False
    return all(
        isinstance(article, dict)
        and isinstance(article.get("title"), str)
        and isinstance(article.get("url"), str)
        and normalized_url(article["url"]) is not None
        and isinstance(article.get("boundary_ids"), list)
        and isinstance(article.get("domain"), str)
        for article in articles
    )


def best_available_snapshot(local_path: Path, *, timeout: float = 8.0) -> dict[str, Any]:
    """Preserve the newest valid deployed snapshot across stateless Actions runs."""
    local = load_json(local_path)
    selected = local if usable_snapshot(local) else None
    try:
        request = Request(PUBLIC_SNAPSHOT, headers={"User-Agent": USER_AGENT})
        with urlopen(request, timeout=timeout) as response:
            if response.status != 200:
                raise WatchError(f"Prior snapshot returned HTTP {response.status}")
            body = response.read(2_000_001)
        if len(body) > 2_000_000:
            raise WatchError("Prior snapshot is larger than 2 MB")
        public = json.loads(body.decode("utf-8"))
        if (
            isinstance(public, dict)
            and usable_snapshot(public)
            and (selected is None or snapshot_date(public) > snapshot_date(selected))
        ):
            selected = public
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, WatchError):
        pass
    if selected is None:
        raise WatchError("No valid previous Global AI Watch snapshot is available")
    return selected


def snapshot(config: dict[str, Any], articles: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "cmb.global-ai-watch.v1",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": {
            "name": str(config["source"]["name"]),
            "endpoint": str(config["source"]["endpoint"]),
            "documentation": str(config["source"]["documentation"]),
        },
        "query": str(config["query"]),
        "timespan": str(config["timespan"]),
        "article_count": len(articles),
        "domain_count": len({article["domain"] for article in articles}),
        "country_count": len(
            {
                article["source_country"]
                for article in articles
                if article["source_country"]
            }
        ),
        "interpretation_boundaries": list(config["interpretation_boundaries"]),
        "articles": articles,
    }


def human_seen(value: str | None) -> str:
    if not value:
        return "time unavailable"
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value
    return dt.strftime("%Y-%m-%d %H:%M UTC")


def render_cards(articles: list[dict[str, Any]], config: dict[str, Any]) -> str:
    """Render only outbound news links and minimal CMB metadata."""
    if not articles:
        return '<p class="cmb-watch-empty">No relevant links matched this snapshot.</p>'

    boundary_labels = {
        str(item["id"]): str(item["label"]) for item in config.get("boundaries", [])
    }
    rows: list[str] = []

    for article in articles:
        title = html.escape(article["title"])
        url = html.escape(article["url"], quote=True)
        domain = html.escape(article["domain"])
        boundary_text = " + ".join(
            boundary_labels.get(item, item) for item in article["boundary_ids"]
        )
        seen = human_seen(article["seen_at"])
        rows.append(
            "<li>"
            f'<a href="{url}" rel="noopener noreferrer">{title}</a>'
            f' <small>{domain} · {html.escape(seen)} · {html.escape(boundary_text)}</small>'
            "</li>"
        )

    return '<ul class="cmb-news-links">\n' + "\n".join(rows) + "\n</ul>"

def render_generated_block(
    data: dict[str, Any], config: dict[str, Any], *, state: str = "LIVE"
) -> str:
    articles = data["articles"]
    generated = human_seen(data["generated_at"])
    return "\n\n".join(
        [
            (
                '<div id="cmb-watch-status" class="cmb-watch-status">'
                f"{html.escape(state)} // last collected {generated} // {len(articles)} outbound sources"
                "</div>"
            ),
            render_cards(articles, config),
            (
                '<p class="cmb-watch-method-note">'
                "<strong>Publication rule:</strong> the analysis step may inspect a larger "
                "metadata sample in memory, but this page publishes only a bounded set of "
                "source links. No article body, image, excerpt, or copied archive is stored."
                "</p>"
            ),
        ]
    )

def replace_generated_section(document: str, generated: str) -> str:
    if START_MARKER not in document or END_MARKER not in document:
        raise WatchError("Global AI Watch document is missing generated-section markers")
    before, remainder = document.split(START_MARKER, 1)
    _, after = remainder.split(END_MARKER, 1)
    return (
        before
        + START_MARKER
        + "\n\n"
        + generated.rstrip()
        + "\n\n"
        + END_MARKER
        + after
    )


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-doc", type=Path, default=DEFAULT_DOC)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument(
        "--fixture",
        type=Path,
        help="Read a saved GDELT JSON response instead of using the network.",
    )
    parser.add_argument(
        "--allow-stale",
        action="store_true",
        help="Preserve the checked-in snapshot when the external GDELT fetch is unavailable.",
    )
    args = parser.parse_args()

    try:
        config = load_json(args.config)
        effective_config = config
        state = "LIVE GDELT"
        try:
            payload = load_json(args.fixture) if args.fixture else fetch_gdelt(
                config, timeout=12.0, attempts=2
            )
            articles = normalize_articles(payload, config)
            if not articles:
                raise WatchError("GDELT returned no qualifying AI headlines")
        except WatchError as gdelt_error:
            if args.fixture is not None:
                raise
            try:
                articles, active_feeds = fetch_rss_articles(config)
                effective_config = dict(config)
                effective_config["source"] = {
                    "name": "Direct publisher RSS fallback: "
                    + ", ".join(feed["name"] for feed in active_feeds),
                    "endpoint": active_feeds[0]["url"],
                    "documentation": "https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/GLOBAL_AI_WATCH/",
                }
                effective_config["query"] = "Recent publisher RSS headlines classified by explicit CMB terms"
                effective_config["timespan"] = str(config.get("fallback_max_age_hours", 120)) + "h"
                state = "LIVE RSS BACKUP"
                print(
                    "Global AI Watch: GDELT unavailable; publishing direct RSS "
                    f"headlines instead: {gdelt_error}",
                    file=sys.stderr,
                )
            except WatchError as rss_error:
                if not args.allow_stale:
                    raise WatchError(
                        f"GDELT and RSS failed: {gdelt_error}; {rss_error}"
                    ) from rss_error
                data = best_available_snapshot(args.output_json)
                document = args.output_doc.read_text(encoding="utf-8")
                updated_document = replace_generated_section(
                    document,
                    render_generated_block(
                        data, config, state="STALE - LIVE SOURCES UNAVAILABLE"
                    ),
                )
                atomic_write(args.output_json, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
                atomic_write(args.output_doc, updated_document)
                print(
                    "::warning::Global AI Watch publishing a clearly labeled stale "
                    f"snapshot; GDELT: {gdelt_error}; RSS: {rss_error}",
                    file=sys.stderr,
                )
                return 0

        published_links = select_published_links(articles, config)
        data = snapshot(effective_config, published_links)
        document = args.output_doc.read_text(encoding="utf-8")
        updated_document = replace_generated_section(
            document, render_generated_block(data, config, state=state)
        )
        atomic_write(args.output_json, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        atomic_write(args.output_doc, updated_document)
    except (OSError, WatchError, KeyError, TypeError, ValueError) as exc:
        print(f"Global AI Watch refresh failed: {exc}", file=sys.stderr)
        return 2

    print(
        "Global AI Watch refreshed: "
        f"{data['article_count']} published links, "
        f"{data['domain_count']} domains, "
        f"{data['country_count']} source countries."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
