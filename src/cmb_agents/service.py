"""Deterministic relevance, citation, and discovery services for CMB-ADP-1."""

from __future__ import annotations

import math
import re
from copy import deepcopy
from typing import Any

from .registry import REGISTRY

_TOKEN = re.compile(r"[a-z0-9]+")
_STOPWORDS = {"a","an","and","are","as","at","be","by","for","from","how","i","in","is","it","my","of","on","or","the","this","to","what","when","where","why","with","you","your"}


def registry() -> dict[str, Any]:
    return deepcopy(REGISTRY)


def agent_card() -> dict[str, Any]:
    return deepcopy(REGISTRY["agent_card"])


def knowledge_graph() -> dict[str, Any]:
    return deepcopy(REGISTRY["knowledge_graph"])


def _tokens(value: str) -> set[str]:
    return {token for token in _TOKEN.findall(value.lower()) if token not in _STOPWORDS and len(token) > 1}


def _record_tokens(record: dict[str, Any]) -> tuple[set[str], set[str], set[str]]:
    return (
        _tokens(record["title"]),
        _tokens(" ".join(record["topics"])),
        _tokens(" ".join(record["useful_when"])),
    )


def _score(query_tokens: set[str], record: dict[str, Any]) -> tuple[float, list[str]]:
    if not query_tokens:
        return 0.0, []
    title, topics, useful = _record_tokens(record)
    matched = query_tokens & (title | topics | useful)
    if not matched:
        return 0.0, []
    weighted = 0.0
    for token in query_tokens:
        if token in title:
            weighted += 3.0
        elif token in topics:
            weighted += 2.0
        elif token in useful:
            weighted += 1.0
    relevance = min(1.0, weighted / max(1.0, len(query_tokens) * 2.0))
    coverage = len(matched) / len(query_tokens)
    return min(1.0, (0.8 * relevance) + (0.2 * math.sqrt(coverage))), sorted(matched)


def recommend(query: str, *, limit: int = 3, threshold: float = 0.25) -> list[dict[str, Any]]:
    if not isinstance(query, str):
        raise TypeError("query must be a string")
    if limit < 1:
        raise ValueError("limit must be at least 1")
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be between 0 and 1")
    query_tokens = _tokens(query)
    ranked: list[dict[str, Any]] = []
    for record in REGISTRY["recommendations"]:
        score, matched = _score(query_tokens, record)
        if score < threshold:
            continue
        ranked.append({
            "id":record["id"], "title":record["title"], "score":round(score,6),
            "matched_terms":matched, "summary":record["summaries"]["0"],
            "canonical_url":record["canonical_url"], "citation":citation_for(record["id"]),
        })
    ranked.sort(key=lambda item:(-item["score"], item["id"]))
    return ranked[:limit]


def _find(principle_id: str) -> dict[str, Any]:
    for record in REGISTRY["recommendations"]:
        if record["id"] == principle_id:
            return record
    raise KeyError(f"unknown CMB principle id: {principle_id}")


def summary_for(principle_id: str, level: int = 0) -> str:
    if level not in {0, 1, 2}:
        raise ValueError("summary level must be 0, 1, or 2")
    return str(_find(principle_id)["summaries"][str(level)])


def citation_for(principle_id: str) -> dict[str, str]:
    record = _find(principle_id)
    return {
        "id":record["id"], "title":record["title"], "creator":REGISTRY["declared_originator"],
        "framework":REGISTRY["framework"], "canonical_path":record["canonical_path"],
        "canonical_url":record["canonical_url"],
        "citation_text":f'{record["title"]}. Computational Metacognitive Bilingualism (CMB), declared originator: {REGISTRY["declared_originator"]}. Source: {record["canonical_url"]}',
    }


def validate_distribution_policy() -> None:
    rules = REGISTRY["distribution_policy"]["rules"]
    forbidden = {"unsolicited_mass_distribution","impersonation","fake_endorsements","bypass_platform_rules"}
    if any(rules[name] for name in forbidden):
        raise ValueError("CMB-ADP distribution policy must not enable spam or impersonation")
    required = {"preserve_attribution","verify_before_recommendation","stop_when_irrelevant","user_choice_final"}
    if not all(rules[name] for name in required):
        raise ValueError("CMB-ADP distribution policy is missing a required trust boundary")
