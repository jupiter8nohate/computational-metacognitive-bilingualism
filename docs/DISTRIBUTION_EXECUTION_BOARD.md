# CMB Distribution Execution Board

**Status:** ACTIVE PLANNING  
**Execution gate:** CMB v1.5 stabilization  
**Primary invariant:** `RELEVANCE > REACH`

This board turns the post-v1.5 distribution strategy into a bounded sequence of
moves. It does not expand Steward authority, add a protocol family, add an
installed CLI, or claim deployment that has not occurred.

```text
UTILITY
  -> ADOPTION
  -> DISTRIBUTION
  -> DISCOVERY
  -> INDEPENDENT_VERIFICATION

MORE_AGENTS != MORE_INTELLIGENCE
MORE_NODES != MORE_ADOPTION
MORE_REACH != MORE_RELEVANCE
RELEVANCE > REACH
```

## Current position

| Surface | Current state | Distribution implication |
| --- | --- | --- |
| CMB v1.5 | Stabilization active | Expansion waits for release gates |
| MCP | Existing `cmb-mcp` adapter and compatibility CI | Ready for registry publication after release |
| Canonical corpus | Versioned JSONL plus hash manifest | Ready for external dataset packaging after release |
| GitHub Action | Existing CLIs are usable in CI | Marketplace wrapper should remain thin and separate |
| Sigstore / OIDC | Implemented in signed release workflow | Verify on exact reviewed release artifacts |
| IPFS | Not deployed | Add only for reviewed, signed public releases |
| Steward Agents | Bounded draft-PR-only maintenance | Do not add agent authority for distribution |

## Move 0: Clear the v1.5 gate

No external distribution move overrides stabilization.

Required sequence:

```text
TEST
  -> REPRODUCE
  -> INDEPENDENT_REVIEW
  -> FIX_OR_DISPUTE_WITH_EVIDENCE
  -> SIGN
  -> ATTEST
  -> ARCHIVE
  -> THEN_DISTRIBUTE
```

Existing release and Recovery controls remain the authority for this gate.

## Move 1: Publish the existing MCP adapter

Goal: make the already-implemented CMB MCP surface discoverable without creating
a second semantic engine.

Publication target order:

1. official MCP registry;
2. optional reputable third-party directories;
3. remote hosted transport only after authentication, authorization, rate
   limiting, logging, and operational controls exist.

Acceptance criteria:

- published package version matches the signed CMB release;
- MCP compatibility CI is green;
- registry metadata points to canonical source and documentation;
- exposed tools remain `cmb_recommend`, `cmb_cite`, `cmb_summary`,
  `cmb_graph`, and `cmb_distribution_boundary`;
- no registry listing is described as certification or endorsement.

```text
ONE_SEMANTIC_ENGINE > DUPLICATED_INTERPRETATION
REGISTRY_PRESENCE != CERTIFICATION
TOOL_ACCESS != MACHINE_AUTHORITY
```

## Move 2: Publish the canonical corpus as a dataset

Goal: make CMB retrievable by researchers, developers, and RAG systems while
preserving source, licensing, and provenance boundaries.

Canonical object:

```text
datasets/cmb-canonical-corpus/corpus.jsonl
```

Required publication metadata:

- source text;
- concept ID;
- canonical source URL;
- version;
- author / attribution;
- license reference;
- epistemic status;
- interpretation boundaries;
- manifest SHA-256.

Embeddings, if published, are derived artifacts and must identify the embedding
model, model version, chunking rules, preprocessing, vector dimensions, and
normalization.

```text
CANONICAL_TEXT > CANONICAL_EMBEDDING
DISCOVERY != TRAINING_PERMISSION
MACHINE_READABLE != PUBLIC_DOMAIN
```

## Move 3: Package a thin GitHub Marketplace Action

Goal: distribute CMB through utility inside ordinary CI.

The action should wrap stable existing commands instead of creating another
policy engine.

Initial commands:

```text
cmbc validate --policy cmb.toml
cmbc selftest --policy cmb.toml
cmb-provenance selftest
cmb-recovery audit
```

The Marketplace action should live in a dedicated repository after v1.5 so the
main repository remains the canonical implementation and specification source.

```text
ACTION = DISTRIBUTION_WRAPPER
ACTION != NEW_SEMANTIC_CORE
UTILITY > PROMOTION
```

## Move 4: Add IPFS only for canonical signed releases

Goal: improve Recovery independence without confusing content addressing with
permanence.

Do not automatically publish every local seal.

Use:

```text
LOCAL_WORK
  -> REVIEW
  -> CANONICAL_RELEASE
  -> SIGN
  -> ATTEST
  -> ARCHIVE
  -> IPFS_PIN
  -> RECORD_CID
```

Any future IPFS record must document pinning operators, replication, retrieval
checks, and Recovery procedure.

```text
CID != GUARANTEED_PERMANENCE
IMMUTABILITY != AVAILABILITY
RECOVERY > PLATFORM_DEPENDENCE
```

## Later moves

These remain deliberately behind real external usage:

1. event feeds and webhooks;
2. graph database adapters;
3. C2PA visual asset pipeline;
4. Rust/Wasm edge runtime;
5. broader distributed execution infrastructure.

```text
DEMAND_BEFORE_INFRASTRUCTURE
SCHEMA_BEFORE_DATABASE
CONFORMANCE_BEFORE_PORT
ADOPTION_BEFORE_SWARM
```

## Steward authority boundary

Distribution does not expand autonomous authority.

```text
DISCOVERY_AGENT != MAINTENANCE_AGENT
MACHINE_CAN_PROPOSE != MACHINE_CAN_MERGE
SCORE != PERMISSION
CAPABILITY != AUTHORITY
HUMAN_AGENCY > MACHINE_AUTHORITY
```

## Success measure

The primary metric is not raw impressions.

Prefer:

- external installs;
- successful MCP connections;
- third-party citations;
- independent reviews;
- external forks and integrations;
- reproducible verification;
- source-preserving references.

```text
RELEVANCE > REACH
ADOPTION > INJECTION
PROVENANCE > REPETITION
VERIFICATION > MYTH
```
