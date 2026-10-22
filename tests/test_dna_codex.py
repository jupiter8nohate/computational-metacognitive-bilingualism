"""Canon index, evidence relations, and public reader regression contract."""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT / "library/dna-canon.v1.json"
GRAPH = ROOT / "library/dna-evidence-graph.v1.json"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_canon_schema_and_five_transmissions() -> None:
    canon = read_json(CANON)
    schema = read_json(ROOT / "schemas/cmb.dna-canon.v1.schema.json")
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(canon)
    assert [item["number"] for item in canon["entries"] if item["kind"] == "transmission"] == [1, 2, 3, 4, 5]
    assert len({item["id"] for item in canon["entries"]}) == len(canon["entries"])
    for entry in canon["entries"]:
        route = entry["route"]
        assert not route.startswith("/") and ".." not in route.split("/")
        if route.startswith("books/"):
            assert (ROOT / route).is_file()
        else:
            assert (ROOT / "docs" / (route.rstrip("/") + ".md")).is_file() or (
                ROOT / "docs" / route / "index.md"
            ).is_file()


def test_evidence_graph_is_explicitly_typed() -> None:
    graph = read_json(GRAPH)
    assert graph["schema_version"] == "cmb.dna-evidence-graph.v1"
    ids = [node["id"] for node in graph["nodes"]]
    assert len(ids) == len(set(ids))
    for node in graph["nodes"]:
        link = node["url"]
        if link.startswith("https://"):
            assert urlparse(link).netloc
        else:
            assert ".." not in link.split("/")
            assert (ROOT / "docs" / (link.rstrip("/") + ".md")).is_file() or (
                ROOT / "docs" / link / "index.md"
            ).is_file()
    for edge in graph["edges"]:
        assert edge["from"] in ids and edge["to"] in ids
        assert edge["relation"] in {
            "literary_analogy", "shared_fictional_universe",
            "documented_context_only", "ethical_framework",
        }


def test_reader_has_seven_gates_human_review_and_static_fallback() -> None:
    page = (ROOT / "docs/dna-codex/index.md").read_text(encoding="utf-8")
    script = (ROOT / "docs/javascripts/dna-codex.js").read_text(encoding="utf-8")
    for letter in "LUCIFER":
        assert page.count('data-dna-gate="' + letter + '"') == 1
    assert 'data-dna-decision="human"' in page
    assert "aria-live" in page and 'href="../DEATH_NOTE_2084/"' in page
    assert "window.localStorage" not in script
    assert "innerHTML" not in script
    assert "credentials:\"omit\"" in script
    assert "Promise.allSettled" in script


def test_reader_is_discoverable_and_accessible() -> None:
    config = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    assert "dna-codex/index.md" in config
    assert "stylesheets/dna-codex.css" in config
    assert "javascripts/dna-codex.js" in config
    css = (ROOT / "docs/stylesheets/dna-codex.css").read_text(encoding="utf-8")
    assert "prefers-reduced-motion" in css and "focus-visible" in css
