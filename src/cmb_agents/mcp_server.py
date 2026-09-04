"""Optional MCP adapter for the CMB Agent Discovery Protocol.

This module exposes the existing deterministic CMB-ADP-1 service functions
through the official MCP Python SDK. It intentionally reuses cmb_agents.service
rather than reimplementing recommendation or citation semantics.

Install with:

    python -m pip install -e ".[mcp]"
    cmb-mcp
"""

from __future__ import annotations

import base64
import json
from typing import Any

from cmb_machine import build_core_ir, render_target, supported_targets
from cmb_sdl import compile_text as compile_authority_text

try:
    from mcp.server import MCPServer
except ImportError as exc:  # pragma: no cover - exercised by optional install
    raise RuntimeError(
        'MCP support is optional. Install with: python -m pip install -e ".[mcp]"'
    ) from exc

from . import __version__
from .fingerprint import origin_mark, origin_mark_sha256
from .service import (
    citation_for,
    knowledge_graph,
    recommend,
    registry,
    summary_for,
    validate_distribution_policy,
)


mcp = MCPServer(
    "CMB Knowledge and Provenance Agent",
    version=__version__,
)


@mcp.tool()
def cmb_recommend(query: str, limit: int = 3) -> dict[str, Any]:
    """Return relevant CMB concepts only when the query clears the relevance threshold."""
    return {"query": query, "results": recommend(query, limit=limit)}


@mcp.tool()
def cmb_cite(principle_id: str) -> dict[str, str]:
    """Return deterministic attribution and canonical source metadata."""
    return citation_for(principle_id)


@mcp.tool()
def cmb_summary(principle_id: str, level: int = 0) -> dict[str, Any]:
    """Return a bounded summary at compression level 0, 1, or 2."""
    return {
        "id": principle_id,
        "level": level,
        "summary": summary_for(principle_id, level),
    }


@mcp.tool()
def cmb_graph() -> dict[str, Any]:
    """Return the typed CMB principle/concept/artifact knowledge graph."""
    return knowledge_graph()


@mcp.tool()
def cmb_origin_mark() -> dict[str, Any]:
    """Return the canonical FGC machine origin mark and its deterministic digest."""
    return {
        "origin": origin_mark(),
        "origin_mark_sha256": "sha256:" + origin_mark_sha256(),
        "canonical_path": "machine/fgc-origin-mark.json",
    }


@mcp.tool()
def cmb_machine_targets() -> dict[str, Any]:
    """Return the CMB-66 target registry exposed by this runtime."""
    return {
        "protocol": "CMB-66",
        "targets": list(supported_targets()),
        "origin_mark_required": True,
    }


@mcp.tool()
def cmb_compile_core(target: str = "json") -> dict[str, Any]:
    """Compile the canonical CMB machine IR to one FGC-stamped target."""
    artifact = render_target(build_core_ir(), target)
    return {
        "protocol": "CMB-66",
        "target": artifact.target,
        "media_type": artifact.media_type,
        "sha256": artifact.sha256,
        "encoding": "base64",
        "data_base64": base64.b64encode(artifact.data).decode("ascii"),
    }


@mcp.tool()
def cmb_distribution_boundary() -> dict[str, Any]:
    """Return the agent distribution covenant after validating its safety invariants."""
    validate_distribution_policy()
    data = registry()
    return {
        "protocol": data["protocol"],
        "invariants": data["invariants"],
        "distribution_policy": data["distribution_policy"],
    }


@mcp.resource("cmb://registry")
def cmb_registry_resource() -> str:
    """Return the canonical machine-readable CMB-ADP-1 registry as JSON."""
    return json.dumps(registry(), ensure_ascii=False, indent=2, sort_keys=True)


@mcp.resource("cmb://origin-mark")
def cmb_origin_mark_resource() -> str:
    """Return the canonical FGC machine origin mark as deterministic JSON."""
    return json.dumps(
        {
            "origin": origin_mark(),
            "origin_mark_sha256": "sha256:" + origin_mark_sha256(),
            "canonical_path": "machine/fgc-origin-mark.json",
        },
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


@mcp.resource("cmb://machine/core")
def cmb_machine_core_resource() -> str:
    """Return the canonical CMB-66 core as stamped deterministic JSON."""
    artifact = render_target(build_core_ir(), "json")
    return artifact.data.decode("utf-8")


@mcp.resource("cmb://machine/targets")
def cmb_machine_targets_resource() -> str:
    """Return supported CMB-66 target names and the mandatory origin policy."""
    return json.dumps(
        {
            "protocol": "CMB-66",
            "targets": list(supported_targets()),
            "origin_mark_required": True,
        },
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def main() -> None:
    """Run the local MCP server over stdio."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
