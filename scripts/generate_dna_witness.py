"""Deterministic, source-linked D.N.A. Living Codex companion.

Six named, rules-based roles generate fictional allegories from source-linked
headlines. This is not an LLM and it cannot modify human canonical scripture.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
ROLES = ("Herald", "Witness", "Adversary", "Scribe", "Archivist", "Guardian")


def safe_text(value: str) -> str:
    return html.escape(" ".join(value.split())[:200], quote=True)


def make_scroll(history: dict, health: dict) -> dict:
    seen: set[str] = set()
    chapters: list[dict] = []
    for entry in reversed(history["entries"]):
        for article in entry["articles"]:
            if (article.get("id") in seen
                or not article.get("title")
                or urlsplit(article.get("url", "")).scheme != "https"):
                continue
            seen.add(article["id"])
            boundaries = article.get("boundary_ids", [])
            question = (
                "Who authorized the action, and how can a human contest it?"
                if "ACT" in boundaries else
                "What evidence separates the generated signal from its source?"
                if "GENERATE" in boundaries else
                "What independent evidence confirms the predicted pattern?"
            )
            chapters.append({
                "id": "witness-" + hashlib.sha256(
                    article["url"].encode("utf-8")).hexdigest()[:12],
                "theme": article["title"],
                "source_url": article["url"],
                "source_domain": article["domain"],
                "boundaries": boundaries,
                "status": "fictional_allegory_not_fact_checked",
                "question": question,
                "passage": [
                    "And the Watcher heard a new account arise from the public square.",
                    "Yet the Scribe refused to place a headline upon the throne of Truth.",
                    "For a machine may recognize a pattern, but a pattern is not proof.",
                    "And the Adversary asked for the source before drawing any conclusion.",
                    "So the Guardian left the question open, and the human kept the pen.",
                ],
            })
            if len(chapters) >= 4:
                break
        if len(chapters) >= 4:
            break
    return {
        "schema_version": "cmb.dna-witness.v1",
        "author": "CMB deterministic rule-based generator",
        "canonical_author": "Jupiter Hudson / WisdomLoveThePoet / Jupiter 8",
        "human_canon_untouched": True,
        "roles": list(ROLES),
        "status": health["status"],
        "chapters": chapters,
    }


def render(scroll: dict) -> str:
    result = [
        "# D.N.A. // The Living Codex",
        "",
        "**Demons Need Attention | The Book of Witnesses**",
        "",
        "This automated **rules-based prototype** generates original fictional",
        "allegories inspired by news headline metadata. It is not an AI language",
        "model, independent journalism, a fact-checker, or a prophecy.",
        "",
        "**The human-authored D.N.A. Bible remains protected.**",
        "These machine-generated reflections are noncanonical; they never",
        "rewrite the human author's work or become factual evidence.",
        "",
        "**Six roles:** Herald, Witness, Adversary, Scribe, Archivist, Guardian.",
        "",
        "**Collection state:** " + safe_text(scroll["status"]),
        "",
    ]
    if not scroll["chapters"]:
        result.append("Awaiting a valid historical collection to generate a witness.")
    for chapter in scroll["chapters"]:
        result.extend([
            "## " + chapter["id"],
            "",
            "**Source-linked theme:** " + safe_text(chapter["theme"]),
            "",
            "**Genre:** fictional allegory, not a report of the event.",
            "",
        ])
        result.extend(
            str(index) + ". " + passage
            for index, passage in enumerate(chapter["passage"], 1)
        )
        result.extend([
            "",
            "**Human-review question:** " + safe_text(chapter["question"]),
            "",
            "**Original reporting:** [" + safe_text(chapter["source_domain"])
            + "](" + chapter["source_url"] + ")",
            "",
            "PATTERN != PROOF | PROFILE != PERSON | HUMAN_AGENCY > MACHINE_AUTHORITY",
            "",
            "---",
            "",
        ])
    result.extend([
        "[Machine-readable Codex](https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/machine/dna-living-codex.json)"
        " | [Global AI Watch](https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/GLOBAL_AI_WATCH/)",
        "",
        "*The canonical human author retains authority over the D.N.A. Bible.*",
        "",
    ])
    return "\n".join(result)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history", type=Path, default=ROOT / "machine/global-ai-watch-history.json")
    parser.add_argument("--health", type=Path, default=ROOT / "machine/global-ai-watch-health.json")
    parser.add_argument("--output-doc", type=Path, default=ROOT / "docs/DNA_LIVING_CODEX.md")
    parser.add_argument("--output-json", type=Path, default=ROOT / "machine/dna-living-codex.json")
    args = parser.parse_args()
    history = json.loads(args.history.read_text(encoding="utf-8"))
    health = json.loads(args.health.read_text(encoding="utf-8"))
    scroll = make_scroll(history, health)
    args.output_doc.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_doc.write_text(render(scroll), encoding="utf-8")
    args.output_json.write_text(
        json.dumps(scroll, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print("D.N.A. Living Codex: " + str(len(scroll["chapters"])) + " witness passages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
