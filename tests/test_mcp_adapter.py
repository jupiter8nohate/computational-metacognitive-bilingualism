from __future__ import annotations

import anyio
import pytest

pytest.importorskip("mcp")

from mcp import Client

from cmb_agents.mcp_server import mcp


def test_mcp_server_lists_and_calls_cmb_tools() -> None:
    async def exercise() -> None:
        async with Client(mcp) as client:
            tools = await client.list_tools()
            names = {tool.name for tool in tools.tools}

            assert {
                "cmb_recommend",
                "cmb_cite",
                "cmb_summary",
                "cmb_graph",
                "cmb_distribution_boundary",
            } <= names

            result = await client.call_tool(
                "cmb_recommend",
                {"query": "algorithmic profiling evidence", "limit": 1},
            )
            assert result.content

    anyio.run(exercise)
