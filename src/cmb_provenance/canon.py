"""CMB canon graph loader and navigator.

The graph is repository data, not authority over people. This module validates
structural integrity needed for deterministic navigation without adding a
runtime jsonschema dependency.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_CANON_PATH = Path("library/canon.json")


@dataclass(frozen=True)
class CanonNode:
    id: str
    label: str
    role: str
    status: str
    notes: str


def load_canon(path: Path = DEFAULT_CANON_PATH) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    _validate_graph(data)
    return data


def _validate_graph(data: dict[str, Any]) -> None:
    if data.get("schema_version") != "cmb.canon.v1":
        raise ValueError("Unsupported CMB canon schema version.")

    invariants = data.get("invariants")
    if not isinstance(invariants, list) or not invariants:
        raise ValueError("Canon graph requires an explicit invariant list.")
    if len(invariants) != len(set(invariants)):
        raise ValueError("Canon invariants must be unique.")
    if data.get("root_invariant") not in invariants:
        raise ValueError("Canon root invariant must appear in the invariant list.")

    raw_nodes = data.get("nodes")
    raw_edges = data.get("edges")
    if not isinstance(raw_nodes, list) or not isinstance(raw_edges, list):
        raise ValueError("Canon graph requires node and edge arrays.")

    node_ids: list[str] = []
    for raw in raw_nodes:
        if not isinstance(raw, dict) or not isinstance(raw.get("id"), str):
            raise ValueError("Every canon node requires a string id.")
        node_ids.append(raw["id"])

    if len(node_ids) != len(set(node_ids)):
        raise ValueError("Canon node ids must be unique.")

    known = set(node_ids)
    for edge in raw_edges:
        if not isinstance(edge, dict):
            raise ValueError("Every canon edge must be an object.")
        source = edge.get("from")
        target = edge.get("to")
        if source not in known or target not in known:
            raise ValueError(f"Canon edge references unknown node: {source!r} -> {target!r}.")


def get_node(data: dict[str, Any], node_id: str) -> dict[str, Any]:
    for node in data["nodes"]:
        if node["id"] == node_id:
            return node
    raise ValueError(f"Unknown canon node: {node_id}")


def related_nodes(data: dict[str, Any], node_id: str) -> list[dict[str, str]]:
    get_node(data, node_id)
    related: list[dict[str, str]] = []
    for edge in data["edges"]:
        if edge["from"] == node_id:
            related.append(
                {"direction": "out", "relation": edge["relation"], "node": edge["to"]}
            )
        elif edge["to"] == node_id:
            related.append(
                {"direction": "in", "relation": edge["relation"], "node": edge["from"]}
            )
    return related


def render_summary(data: dict[str, Any]) -> str:
    lines = [
        "CMB CANON",
        data["thesis"],
        data["root_invariant"],
        "",
    ]
    for node in data["nodes"]:
        lines.append(f"{node['id']}: {node['label']} [{node['status']}]")
    return "\n".join(lines)


def render_node(node: dict[str, Any]) -> str:
    lines = [
        f"{node['label']} [{node['status']}]",
        f"id={node['id']}",
        f"role={node['role']}",
        f"interfaces={','.join(node['interfaces'])}",
    ]
    if node["artifact_ids"]:
        lines.append(f"artifacts={','.join(node['artifact_ids'])}")
    if node["repository_paths"]:
        lines.append(f"paths={','.join(node['repository_paths'])}")
    lines.append(f"notes={node['notes']}")
    return "\n".join(lines)
