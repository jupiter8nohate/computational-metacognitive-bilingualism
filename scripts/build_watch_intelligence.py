"""Explainable, metadata-only research dossiers for the CMB Global AI Watch.

A published headline is a lead for human investigation, never a verified incident.
No article body, personal profile, model-based truth score or hidden API is used.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]

RIGHTS_RULES: dict[str, tuple[str, ...]] = {
    "accessibility_disability": ("disability", "disabled", "autism", "autistic", "accessibility", "accommodation"),
    "privacy_consent": ("privacy", "surveillance", "consent", "tracking", "biometric", "face recognition", "facial recognition"),
    "equal_treatment": ("bias", "discrimination", "civil rights", "racial", "unfair", "employment screening"),
    "due_process": ("court", "police", "arrest", "appeal", "prison", "judge", "trial", "sentencing"),
    "children_safety": ("children", "child", "teen", "minors", "school", "student"),
}
LEGAL_TERMS = ("court", "judge", "law", "regulation", "legislation", "bill", "statute", "enforcement",
               "lawsuit", "justice", "judiciary", "compliance", "guidance", "regulator", "attorney general")
AUTHORITY_QUESTIONS = {
    "PREDICT": "What evidence supports the classification, and can the affected person contest it?",
    "GENERATE": "Can the generated claim or media be traced to a primary source?",
    "ACT": "Who authorized the machine-assisted action, and can a human stop or reverse it?",
}
SENSITIVE_SECTORS = {
    "military_security", "justice_policing", "healthcare", "children_wellbeing",
    "workplace_civil_rights", "privacy_surveillance",
}


def words_match(title: str, terms: tuple[str, ...]) -> bool:
    lowered = title.casefold()
    return any(re.search(r"(?<!\w)" + re.escape(term.casefold()) + r"(?!\w)", lowered) for term in terms)


def aggregate_history(history: dict[str, Any]) -> list[dict[str, Any]]:
    """Show collected links by day, not incidents or independent stories.

    A daily distinct-URL count is only unique within that day, not across days.
    """
    days: dict[str, dict[str, Any]] = defaultdict(lambda: {"collections": 0, "observed_links": 0, "urls": set()})
    for entry in history.get("entries", []):
        if not isinstance(entry, dict) or not isinstance(entry.get("collected_at"), str):
            continue
        day = entry["collected_at"][:10]
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day):
            continue
        bucket = days[day]
        bucket["collections"] += 1
        bucket["observed_links"] += max(0, int(entry.get("article_count", 0)))
        for article in entry.get("articles", []):
            if isinstance(article, dict) and isinstance(article.get("url"), str):
                bucket["urls"].add(article["url"])
    return [
        {
            "day": day,
            "collections": bucket["collections"],
            "observed_links": bucket["observed_links"],
            "distinct_links_within_day": len(bucket["urls"]),
        }
        for day, bucket in sorted(days.items())[-30:]
    ]


def build_intelligence(
    snapshot: dict[str, Any],
    assessments: dict[str, Any],
    health: dict[str, Any],
    history: dict[str, Any],
) -> dict[str, Any]:
    if snapshot.get("schema_version") != "cmb.global-ai-watch.v1":
        raise ValueError("Incompatible Watch snapshot")
    if assessments.get("schema_version") != "cmb.watch-assessments.v1":
        raise ValueError("Incompatible source assessments")
    if health.get("schema_version") != "cmb.watch-health.v1":
        raise ValueError("Incompatible health report")
    if history.get("schema_version") != "cmb.watch-history.v1":
        raise ValueError("Incompatible history")
    if snapshot.get("generated_at") != assessments.get("generated_at"):
        raise ValueError("Assessments and Watch snapshot must describe the same collection")
    if health.get("last_successful_collection") != snapshot.get("generated_at"):
        raise ValueError("Health and Watch snapshot must describe the same collection")
    if snapshot.get("article_count") != len(snapshot.get("articles", [])):
        raise ValueError("Watch article count is inconsistent")

    assessed = {item["article_id"]: item for item in assessments.get("articles", [])
                if isinstance(item, dict) and isinstance(item.get("article_id"), str)}
    dossiers: list[dict[str, Any]] = []
    rights_counter: Counter[str] = Counter()
    priority_counter: Counter[str] = Counter()
    languages: Counter[str] = Counter()
    countries: Counter[str] = Counter()
    domains: set[str] = set()

    for article in snapshot["articles"]:
        article_id = article["id"]
        title = article["title"]
        url = article["url"]
        parts = urlsplit(url)
        if parts.scheme not in ("http", "https") or not parts.netloc:
            raise ValueError("Invalid source URL")
        boundaries = list(article.get("boundary_ids", []))
        sectors = list(article.get("sector_ids", []))
        rights = [key for key, terms in RIGHTS_RULES.items() if words_match(title, terms)]
        rights_counter.update(rights)
        legal_watch = words_match(title, LEGAL_TERMS)
        # Triage priority is a review workload signal, not a risk or accuracy score.
        triggers = []
        if set(sectors) & SENSITIVE_SECTORS:
            triggers.append("sensitive_sector")
        if len(set(boundaries)) >= 2:
            triggers.append("multiple_machine_boundaries")
        if rights:
            triggers.append("potential_rights_implications")
        if legal_watch:
            triggers.append("legal_process_mentioned")
        priority = "REVIEW_FIRST" if len(triggers) >= 2 else "ROUTINE_REVIEW"
        priority_counter[priority] += 1

        source = assessed.get(article_id, {})
        traceability = source.get("traceability_grade", "NOT_ASSESSED")
        # A single source, a wire syndication and a shared press release are not corroboration.
        domain = article.get("domain", parts.netloc)
        domains.add(domain)
        languages[str(article.get("language") or "unspecified")] += 1
        countries[str(article.get("source_country") or "unspecified")] += 1
        questions = [AUTHORITY_QUESTIONS[b] for b in ("PREDICT", "GENERATE", "ACT") if b in boundaries]
        if rights:
            questions.append("Which people might be affected, and what accessible appeal or remedy exists?")
        if legal_watch:
            questions.append("Which primary legal instrument or court record supports the reported development?")
        if not questions:
            questions.append("Which primary evidence would establish what happened?")

        dossiers.append({
            "dossier_id": "watch-" + hashlib.sha256(url.encode("utf-8")).hexdigest()[:16],
            "article_id": article_id,
            "title": title,
            "url": url,
            "publisher_domain": domain,
            "seen_at": article.get("seen_at"),
            "language": article.get("language"),
            "source_country": article.get("source_country"),
            "cluster_id": article.get("cluster_id"),
            "boundary_ids": boundaries,
            "sector_ids": sectors,
            "rights_lenses": rights,
            "legal_watch_candidate": legal_watch,
            "triage_priority": priority,
            "triage_reasons": triggers,
            "traceability_grade": traceability,
            "claim_verification": "NOT_INDEPENDENTLY_CHECKED",
            "correction_status": "NOT_CHECKED",
            "independent_corroboration": "NOT_CHECKED",
            "reported_incident_status": "NOT_ESTABLISHED_FROM_HEADLINE",
            "review_questions": questions,
            "source_links": [{"type": "publisher", "url": url},
                             {"type": "archive_lookup", "url": article.get("wayback_history_url", "")}],
        })

    return {
        "schema_version": "cmb.watch-intelligence.v1",
        "snapshot_generated_at": snapshot["generated_at"],
        "health_checked_at": health.get("checked_at"),
        "collection_status": health.get("status", "UNKNOWN"),
        "method": "Explainable headline/metadata rules for human review, not automatic fact checking",
        "boundaries": [
            "HEADLINE != INCIDENT_PROOF",
            "TRIAGE_PRIORITY != SEVERITY",
            "SOURCE_DOMAIN != INDEPENDENT_CORROBORATION",
            "NEWS_REPORT != VERIFIED_FACT",
            "SOURCE_COUNTRY != INCIDENT_LOCATION",
            "PATTERN != PROOF",
            "HUMAN_AGENCY > MACHINE_AUTHORITY",
        ],
        "coverage": {
            "published_links": len(dossiers),
            "distinct_publisher_domains": len(domains),
            "languages": dict(sorted(languages.items())),
            "source_countries": dict(sorted(countries.items())),
            "rights_lenses": dict(sorted(rights_counter.items())),
            "triage_priorities": dict(sorted(priority_counter.items())),
        },
        "history": aggregate_history(history),
        "dossiers": dossiers,
    }


def save_atomic(output: Path, payload: dict[str, Any]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=output.parent,
                                     prefix=output.name + ".", delete=False) as stream:
        tmp = Path(stream.name)
        json.dump(payload, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")
    try:
        os.replace(tmp, output)
    finally:
        tmp.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--watch", type=Path, default=ROOT / "machine/global-ai-watch.json")
    parser.add_argument("--assessments", type=Path, default=ROOT / "machine/global-ai-watch-assessments.json")
    parser.add_argument("--health", type=Path, default=ROOT / "machine/global-ai-watch-health.json")
    parser.add_argument("--history", type=Path, default=ROOT / "machine/global-ai-watch-history.json")
    parser.add_argument("--output", type=Path, default=ROOT / "machine/global-ai-watch-intelligence.json")
    args = parser.parse_args()
    try:
        def read(path: Path) -> dict[str, Any]:
            return json.loads(path.read_text(encoding="utf-8"))
        payload = build_intelligence(read(args.watch), read(args.assessments),
                                     read(args.health), read(args.history))
        save_atomic(args.output, payload)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(2, "Watch intelligence build failed: " + str(exc) + "\n")
    print("Global AI Watch dossiers: " + str(len(payload["dossiers"]))
          + "; status: " + payload["collection_status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
