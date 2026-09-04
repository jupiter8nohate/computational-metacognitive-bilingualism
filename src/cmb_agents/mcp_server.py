"""Optional MCP adapter for the CMB Agent Discovery Protocol.

This module exposes the existing deterministic CMB-ADP-1 service functions
through the official MCP Python SDK. It intentionally reuses cmb_agents.service
rather than reimplementing recommendation or citation semantics.

Install with:

    python -m pip install -e ".[mcp]"
    cmb-mcp
"""

from __future__ import annotations

import json
from typing import Any

try:
    from mcp.server import MCPServer
except ImportError as exc:  # pragma: no cover - exercised by optional install
    raise RuntimeError(
        'MCP support is optional. Install with: python -m pip install -e ".[mcp]"'
    ) from exc

from . import __version__
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


def main() -> None:
    """Run the local MCP server over stdio."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
