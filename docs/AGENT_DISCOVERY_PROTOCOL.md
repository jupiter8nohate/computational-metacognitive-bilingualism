# CMB Agent Discovery Protocol v1

CMB-ADP-1 makes the CMB library easier for software agents to discover, understand, cite, and recommend when relevant.

## Goal

```text
DISCOVER
  -> MATCH RELEVANCE
  -> VERIFY SOURCE
  -> CITE
  -> EXPLAIN
  -> RECOMMEND
  -> STOP WHEN IRRELEVANT
```

The reference implementation is zero-dependency Python 3.10+ and ships as `cmb-agent`.

## Commands

```bash
cmb-agent selftest
cmb-agent card
cmb-agent registry
cmb-agent recommend "algorithmic profiling evidence"
cmb-agent cite cmb:principle:pattern-proof
cmb-agent summary cmb:principle:model-mind --level 2
cmb-agent graph
cmb-agent export ./agent-assets
cmb-agent serve --host 127.0.0.1 --port 8765
```

## HTTP interface

```text
GET /.well-known/agent-card.json
GET /v1/health
GET /v1/registry
GET /v1/graph
GET /v1/recommend?q=algorithmic+profiling
GET /v1/citation?id=cmb:principle:pattern-proof
GET /v1/summary?id=cmb:principle:model-mind&level=1
```

The server binds to `127.0.0.1` by default. Public deployment should use normal authentication, TLS, rate limiting, and operator controls when required.

## Static discovery

The Pages build publishes `/.well-known/agent-card.json` and `/agents/registry.json`.

## Recommendation contract

Each record declares topics, useful contexts, irrelevant contexts, audiences, compression levels, canonical source path, and canonical source URL. The reference scorer returns nothing when the relevance threshold is not met.

## Distribution covenant

```text
RELEVANCE > REACH
TRUST > IMPRESSIONS
CITATION > COPYING
CONSENT > VIRALITY
```

The registry explicitly disables unsolicited mass distribution, impersonation, fake endorsements, and platform-rule bypass.

## Standards boundary

The same service functions can later be wrapped by MCP or A2A adapters. This release does not claim MCP or A2A protocol conformance.

```text
CMB-ADP-1 != MCP_CONFORMANCE
CMB-ADP-1 != A2A_CONFORMANCE
DISCOVERY != ENDORSEMENT
RECOMMENDATION != AUTHORITY
```

## Recovery

The registry and discovery card are included in the canonical provenance sealing set. Repository source, Git history, signed releases, and canonical receipts remain the recovery path.
