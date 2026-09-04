# MCP integration

CMB includes an **optional** Model Context Protocol adapter for the existing
CMB-ADP-1 agent service.

The adapter targets the official MCP **2026-07-28** protocol generation through
the stable Python SDK 2.x line. It reuses the existing CMB recommendation,
citation, summary, knowledge-graph, and distribution-boundary functions rather
than creating a second semantic implementation.

## Install

~~~bash
python -m pip install -e ".[mcp]"
cmb-mcp
~~~

The command serves MCP over stdio, which is the local-host transport.

## Tools

The adapter exposes:

~~~text
cmb_recommend
cmb_cite
cmb_summary
cmb_graph
cmb_distribution_boundary
~~~

It also exposes the canonical CMB agent registry as:

~~~text
cmb://registry
~~~

## Architecture

~~~text
CMB-ADP-1 service
      |
      +-- recommend()
      +-- citation_for()
      +-- summary_for()
      +-- knowledge_graph()
      +-- distribution policy
      |
      v
official MCP Python SDK
      |
      v
cmb-mcp
~~~

There is one semantic engine. MCP is an interoperability surface.

## Standards boundary

The adapter uses the official SDK, but CMB does not claim that the existence of
an adapter is certification, endorsement, or independent protocol audit.

~~~text
SDK_USAGE != CERTIFICATION
DISCOVERY != ENDORSEMENT
TOOL_ACCESS != MACHINE_AUTHORITY
RECOMMENDATION != AUTHORITY
~~~

A production remote deployment still needs appropriate transport security,
authentication/authorization, rate limiting, logging, and operational controls.
