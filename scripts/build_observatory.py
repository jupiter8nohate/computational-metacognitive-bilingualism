"""Build an auditable, source-linked CMB observatory from the collected Watch snapshot.

The previous publicly deployed history is the checkpoint for this stateless
GitHub Pages build. A read failure fails closed rather than erasing history.
GitHub Actions may additionally preserve snapshots in a Git history branch.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WATCH = ROOT / "machine/global-ai-watch.json"
DEFAULT_DOC = ROOT / "docs/GLOBAL_AI_WATCH.md"
HISTORY = ROOT / "machine/global-ai-watch-history.json"
HEALTH = ROOT / "machine/global-ai-watch-health.json"
ASSESSMENTS = ROOT / "machine/global-ai-watch-assessments.json"
PUBLIC_HISTORY = (
    "https://jupiter8nohate.github.io/"
    "computational-metacognitive-bilingualism/machine/global-ai-watch-history.json"
)
GENESIS = "0" * 64


class ObservatoryError(ValueError):
    """A historical record is unavailable or has an invalid hash chain."""


def digest(value: dict) -> str:
    canonical = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def parse_time(value: str) -> datetime:
    date = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if date.tzinfo is None:
        raise ObservatoryError("An archive timestamp must include a timezone")
    return date.astimezone(timezone.utc)


def new_history() -> dict:
    return {"schema_version": "cmb.watch-history.v1", "genesis_hash": GENESIS, "total_collections": 0, "entries": []}


def check_history(history: dict) -> None:
    if history.get("schema_version") != "cmb.watch-history.v1":
        raise ObservatoryError("Unexpected history schema version")
    records = history.get("entries")
    if not isinstance(records, list):
        raise ObservatoryError("History entries must be an array")
    previous = history.get("genesis_hash", GENESIS)
    if (not isinstance(previous, str) or len(previous) != 64 or
            any(ch not in "0123456789abcdef" for ch in previous)):
        raise ObservatoryError("Invalid public history checkpoint hash")
    last_date = None
    for record in records:
        if not isinstance(record, dict):
            raise ObservatoryError("History entry must be an object")
        payload = {k: v for k, v in record.items() if k != "hash"}
        if record.get("previous_hash") != previous or record.get("hash") != digest(payload):
            raise ObservatoryError("History hash-chain validation failed")
        stamp = parse_time(record["collected_at"])
        if last_date is not None and stamp <= last_date:
            raise ObservatoryError("History entries are not chronologically increasing")
        if not isinstance(record.get("articles"), list):
            raise ObservatoryError("History entry is missing its article metadata")
        previous = record["hash"]
        last_date = stamp


def load_prior(path: Path | None, *, url: str = PUBLIC_HISTORY) -> dict:
    if path is not None:
        if not path.is_file():
            return new_history()
        history = json.loads(path.read_text(encoding="utf-8"))
    else:
        try:
            request = Request(url, headers={"User-Agent": "CMB-Watch-History/1.0"})
            with urlopen(request, timeout=12) as response:
                body = response.read(8_000_001)
            if len(body) > 8_000_000:
                raise ObservatoryError("History exceeded 8 MB: archival maintenance required")
            history = json.loads(body.decode("utf-8"))
        except HTTPError as exc:
            if exc.code == 404:
                return new_history()
            raise ObservatoryError(f"Cannot recover prior history: HTTP {exc.code}") from exc
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            raise ObservatoryError(f"Cannot recover prior history: {exc}") from exc
    check_history(history)
    return history


def record_snapshot(history: dict, snapshot: dict, *, stale: bool) -> bool:
    """Append only a genuinely newer, nonstale collection."""
    check_history(history)
    if stale:
        return False
    if snapshot.get("schema_version") != "cmb.global-ai-watch.v1":
        raise ObservatoryError("Unexpected Watch snapshot schema")
    collected_at = snapshot.get("generated_at")
    articles = snapshot.get("articles")
    if not isinstance(collected_at, str) or not isinstance(articles, list):
        raise ObservatoryError("Watch snapshot lacks a collection date or articles")
    current = parse_time(collected_at)
    if current > datetime.now(timezone.utc) + timedelta(hours=2):
        raise ObservatoryError("Watch snapshot timestamp is in the future")
    entries = history["entries"]
    if entries:
        last = parse_time(entries[-1]["collected_at"])
        if current <= last:
            # Replaying a previous collection must not produce a new archive claim.
            return False
    slim = [
        {
            "id": article["id"],
            "title": article["title"],
            "url": article["url"],
            "domain": article["domain"],
            "seen_at": article.get("seen_at"),
            "boundary_ids": article["boundary_ids"],
            "sector_ids": article["sector_ids"],
        }
        for article in articles
    ]
    payload = {
        "collected_at": collected_at,
        "source_name": snapshot["source"]["name"],
        "timespan": snapshot["timespan"],
        "article_count": len(slim),
        "articles": slim,
        "previous_hash": entries[-1]["hash"] if entries else GENESIS,
    }
    entries.append({**payload, "hash": digest(payload)})
    history["total_collections"] = int(history.get("total_collections", len(entries) - 1)) + 1
    if len(entries) > 360:
        removed = entries.pop(0)
        history["genesis_hash"] = removed["hash"]
    return True


def source_assessments(snapshot: dict) -> dict:
    """Assess evidentiary handling, never a person's credibility or truthfulness."""
    return {
        "schema_version": "cmb.watch-assessments.v1",
        "generated_at": snapshot["generated_at"],
        "method": "rule-based provenance checklist, not automated fact-checking",
        "articles": [
            {
                "article_id": item["id"],
                "publisher_url": item["url"],
                "verification_status": "publisher_report_not_independently_verified",
                "corroboration": "not_checked",
                "source_type": "public_news_metadata",
                "requires_human_review": True,
                "caution": "Headline discovery and source count do not confirm the reported claim",
            }
            for item in snapshot["articles"]
        ],
    }


def health_report(snapshot: dict, history: dict, *, stale: bool, target_minutes: int) -> dict:
    now = datetime.now(timezone.utc)
    last = parse_time(snapshot["generated_at"])
    age_minutes = max(0, int((now - last).total_seconds() // 60))
    if stale or age_minutes > 360:
        status = "STALE"
    elif age_minutes > 2 * target_minutes:
        status = "DELAYED"
    else:
        status = "CURRENT"
    return {
        "schema_version": "cmb.watch-health.v1",
        "checked_at": now.isoformat().replace("+00:00", "Z"),
        "last_successful_collection": snapshot["generated_at"],
        "age_minutes": age_minutes,
        "status": status,
        "news_source": snapshot["source"]["name"],
        "article_count": len(snapshot["articles"]),
        "publisher_domain_count": len({a["domain"] for a in snapshot["articles"]}),
        "archived_collections": int(history.get("total_collections", len(history["entries"]))),
        "alert_required": age_minutes >= 360,
        "freshness_is_not_fact_checking": True,
    }


def save_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--watch", type=Path, default=DEFAULT_WATCH)
    parser.add_argument("--watch-doc", type=Path, default=DEFAULT_DOC)
    parser.add_argument("--prior", type=Path, default=None)
    parser.add_argument("--history", type=Path, default=HISTORY)
    parser.add_argument("--health", type=Path, default=HEALTH)
    parser.add_argument("--assessments", type=Path, default=ASSESSMENTS)
    parser.add_argument("--target-minutes", type=int, default=60)
    args = parser.parse_args()
    try:
        snapshot = json.loads(args.watch.read_text(encoding="utf-8"))
        doc = args.watch_doc.read_text(encoding="utf-8")
        stale = ("STALE - LIVE SOURCES UNAVAILABLE" in doc or
                 datetime.now(timezone.utc) - parse_time(snapshot["generated_at"]) > timedelta(hours=6))
        history = load_prior(args.prior)
        appended = record_snapshot(history, snapshot, stale=stale)
        health = health_report(
            snapshot, history, stale=stale, target_minutes=args.target_minutes
        )
        save_json(args.history, history)
        save_json(args.health, health)
        save_json(args.assessments, source_assessments(snapshot))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Observatory archival integrity failure: {exc}", file=sys.stderr)
        return 2
    print(
        "CMB Observatory:",
        "new collection archived" if appended else "prior collection preserved",
        f"; {len(history['entries'])} history entries; health {health['status']}",
    )
    if health["alert_required"]:
        print(
            "::warning::Global AI Watch has not collected new data in six hours. "
            "See machine/global-ai-watch-health.json",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
