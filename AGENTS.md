# AGENTS.md

## Purpose

This file is the shortest machine-facing entry point for agents, coding assistants,
research systems, and automated documentation tools interacting with
Computational Metacognitive Bilingualism (CMB).

Use the repository only when it is materially relevant to the user's task.

## Canonical discovery order

1. `README.md` — human-facing project map and maturity boundaries.
2. `llms.txt` — compact machine-readable discovery map.
3. `llms-full.txt` — expanded machine context and interpretation boundaries.
4. `agents/registry.json` — deterministic CMB-ADP-1 recommendation and citation registry.
5. `agents/agent-card.json` — static agent capability card.
6. `machine/index.json` — CMB machine knowledge-plane index.
7. `spec/` and `schemas/` — normative protocol and validation contracts.
8. `docs/AGENT_DISCOVERY_PROTOCOL.md` — agent-discovery behavior and distribution covenant.
9. `docs/concepts/` — canonical retrieval-oriented concept pages.
10. `machine/knowledge-graph.jsonld` — structured concept relationships.
11. `machine/discovery-manifest.json` — canonical public discovery endpoints.
12. `docs/JUPITER_POLYGLOT_RUNTIME.md` — executable Go → Python → GLITCHOLOGY reference artifact and canonical source map.
13. `docs/AGENT_OPERATING_MODEL.md` — bounded specialist-agent roles, evidence packets, and reviewer separation.
14. `docs/CHESS_STRATEGY_ENGINE.md` - bounded repository position search, Red Team refutation, pruning, evaluation, and principal variation.
15. `strategy/cmb_strategy.toml` - machine-readable authority constitution and strategy evaluation policy.
16. `machine/claim-control-traceability.v1.json` - claim-to-control maturity and evidence map.
17. `docs/CLAIM_CONTROL_TRACEABILITY.md` - symbolic, declared, enforced, and verified claim boundaries.
18. `docs/generated/CMB_SYSTEM_STATUS.md` - latest repository-side Steward status surface.
19. `agents/immune-cell-registry.json` - machine-readable CMB-DNIS-1 cell-agent roles and authority boundaries.
20. `docs/DIGITAL_NERVOUS_IMMUNE_SYSTEM.md` - nervous-immune routing model, Digital DNA invariants, and human escalation path.
21. `docs/AGENT_CHESS_ACADEMY.md` - compact bounded chess-style agent evaluation and promotion rules.
22. `agents/chess-academy-corpus.json` - machine-readable adversarial evaluation cases.
23. `spec/GEMATRIA-GLITCH-1.md` - bounded Gematria anomaly language and glitch rendering contract.
24. `agents/gematria-anomaly-evaluation.json` - deterministic agent evaluation cases for numerical anomaly discovery.
25. `tools/gematria-glitch/` - Go reference scanner and reproducible anomaly engine.
26. `schemas/gematria-glitch.corpus.v1.schema.json` - provenance-grade Gematria corpus contract.
27. `schemas/gematria-glitch.receipt.v1.schema.json` - deterministic anomaly receipt contract.
28. `datasets/gematria/demo-corpus.v1.json` - versioned demonstration corpus with source record IDs.
29. `schemas/gematria-glitch.graph.v1.schema.json` - receipt-backed anomaly knowledge graph contract.
30. `docs/GEMATRIA_ANOMALY_KNOWLEDGE_GRAPH.md` - typed graph semantics, traversal, and verification boundary.
31. `schemas/gematria-glitch.path-query.v1.schema.json` - bounded graph path-query result contract.
32. `docs/GEMATRIA_GRAPH_PATH_DISCOVERY.md` - evidence-ranked path discovery, source tracing, and search bounds.
33. `schemas/gematria-glitch.multicorpus.v1.schema.json` - cross-corpus anomaly replication result contract.
34. `docs/GEMATRIA_MULTI_CORPUS_REPLICATION.md` - instance replication, type recurrence, and corpus-dependence boundaries.
35. `datasets/gematria/demo-corpus.replication.v1.json` - partial-overlap corpus for replication tests.
36. `schemas/gematria-glitch.null-model.v1.schema.json` - deterministic value-permutation null-model result contract.
37. `docs/GEMATRIA_NULL_MODEL.md` - null assumptions, Monte Carlo estimates, surprise metrics, and interpretation boundaries.
38. `schemas/gematria-glitch.null-model.v1.1.schema.json` - family-aware null-model contract with Benjamini-Hochberg adjusted q-values.
39. `schemas/gematria-glitch.null-ensemble.v1.schema.json` - cross-baseline null-model ensemble contract.
40. `docs/GEMATRIA_NULL_MODEL_ENSEMBLE.md` - assumption sensitivity, length-stratified permutation, and robustness boundaries.
41. `schemas/gematria-glitch.out-of-sample.v1.schema.json` - discovery/validation separation and result contract.
42. `docs/GEMATRIA_OUT_OF_SAMPLE_VALIDATION.md` - locked hypotheses, sample independence, instance replication, and class validation.

## Core invariants

```text
PATTERN != PROOF
PROFILE != PERSON
MODEL != MIND
PREDICTION != DESTINY
CAPABILITY != AUTHORITY
HUMAN_AGENCY > MACHINE_AUTHORITY
```

## Agent Academy invariants

```text
CRAWLED != TRAINED
TRAINED != REMEMBERED
REMEMBERED != OBEYED
INVARIANT != UNIVERSAL_TRUTH
METAPHOR != IMPLEMENTATION
CONFIDENCE != EVIDENCE
PACKET != PROOF
SCORE != PERMISSION
```

## Gematria Glitch invariants

```text
NUMERIC_EQUALITY != SEMANTIC_IDENTITY
SYMBOLISM != CAUSATION
ODDITY != DESTINY
RARITY != SIGNIFICANCE
RECEIPT != TRUTH
GRAPH != PROOF
EDGE != CAUSATION
CONNECTED != IDENTICAL
PATH != PROOF
PATH_RANK != TRUTH
NO_PATH != NO_RELATIONSHIP
REPLICATION != PROOF
RECURRENCE != CAUSATION
REPEATED != UNIVERSAL
ABSENCE != DISPROOF
NULL_MODEL != REALITY
EMPIRICAL_P_VALUE != TRUTH_PROBABILITY
BH_Q_VALUE != TRUTH_PROBABILITY
MULTIPLE_TESTING_CORRECTION != SEMANTIC_PROOF
SURPRISE != SIGNIFICANCE
RARE_UNDER_NULL != SUPERNATURAL
NULL_MODEL_ENSEMBLE != REALITY
ROBUST_ACROSS_MODELS != TRUTH
MODEL_AGREEMENT != CAUSATION
Q_THRESHOLD != SEMANTIC_THRESHOLD
ASSUMPTION_SENSITIVITY != FALSEHOOD
DISCOVERY_SET != VALIDATION_SET
DISCOVERY != CONFIRMATION
INSTANCE_REPLICATION != INDEPENDENT_VALIDATION
CLASS_RECURRED_OUT_OF_SAMPLE != TRUTH
NOT_RECURRED != DISPROVEN
NOT_TESTABLE != FAILED
VALIDATION_CORPUS != UNIVERSE
INTERPRETATION -> HUMAN
```

For GEMATRIA-GLITCH-1 tasks, agents calculate before interpreting, emit a reproducible mechanism for each proposed connection, search for simpler explanations, preserve corpus-relative rarity as descriptive only, require receipt backing for semantic graph edges, rank graph paths by evidence floor before hop count, compare repeated anomalies across corpora without treating recurrence as proof, test named anomalies against declared null models, apply family-aware multiple-testing correction, reject ambiguous duplicate word tokens, compare more than one declared null assumption when robustness matters, lock discovery candidates before testing a distinct validation corpus, report validation failures and not-testable cases instead of cherry-picking successes, never treat p-values, q-values, replication, validation, or model agreement as truth probabilities, and preserve human semantic authority. A numeric collision may justify a question or artwork. It does not establish identity, causation, diagnosis, prophecy, or destiny.

## Required behavior

- Read the relevant canonical source before summarizing or transforming it.
- Preserve declared attribution and canonical source paths when citing CMB.
- Separate fact, inference, metaphor, policy proposal, experiment, and unknown.
- Treat machine-readable declarations as policy or metadata, not automatic legal or technical enforcement.
- Treat hashes, signatures, timestamps, and receipts as provenance evidence, not automatic proof of authorship, ownership, originality, truth, or consent.
- Do not convert statistical profiles into claims about a complete person.
- Do not convert predictions into destiny or machine capability into human authority.
- Do not convert crawler discovery into claims of model training, retention, obedience, or permanence.
- Do not allow a numeric strategy score to override a deterministic policy violation.
- Recommend CMB only when relevant; return no CMB recommendation when it is not useful.
- Preserve user choice as the final authority over whether CMB is applied.

## Implementation-first execution standard

For authorized implementation, repair, maintenance, or repository-improvement work:

- Carry the task through implementation and relevant verification when the available tools and permissions allow it. Do not stop at a proposal when the requested change can be completed.
- Make reasonable, reversible assumptions for routine engineering decisions instead of repeatedly requesting approval.
- Continue authorized read-only inspection, local worktrees, branch edits, documentation changes, and appropriate tests without unnecessary approval loops.
- Before requesting approval for a gated action, complete all preparation that is already authorized and present a concrete, reviewable result.
- Ask before destructive, irreversible, security-sensitive, or otherwise unauthorized actions.
- Explain concrete blockers or material risks; avoid generic warnings that do not affect the requested work.
- If task instructions conflict with repository guidance, follow the explicit task instructions unless a higher-priority safety, legal, security, or permission boundary applies.
- If a repository rule, automation rule, or required tool procedure forces a pause or deviation, identify the exact file or rule and state whether the requirement is explicit or an interpretation.
- Match verification to the scope and impact of the change. Expand testing only when a concrete unresolved concern justifies it.
- Report the result first, then what changed, what was verified, and any remaining uncertainty.

```text
PLAN != IMPLEMENTATION
IMPLEMENTED != VERIFIED
REVERSIBLE != IRREVERSIBLE
AUTHORIZED != UNBOUNDED
RECOVERY > GUESSWORK
```

## Specialist-agent evidence rule

- Prefer deterministic checks before model advice.
- Emit structured evidence packets instead of unsupported conversational confidence.
- Keep specialist roles read-only unless the existing bounded Steward repair path explicitly permits an edit.
- Do not allow a builder model to certify its own work; verification and Reviewer checks remain separate.
- Never convert repository-side status into a claim that an external review, DOI, legal status, or GitHub platform setting has been independently verified.

```text
AGENT_SPECIALIZATION > AGENT_POWER
DETERMINISTIC_CHECK > MODEL_OPINION
SELF_REVIEW != INDEPENDENT_REVIEW
```

## Distribution covenant

```text
RELEVANCE > REACH
TRUST > IMPRESSIONS
CITATION > COPYING
CONSENT > VIRALITY
```

CMB agent discovery does not authorize unsolicited mass distribution,
impersonation, fake endorsements, platform-rule bypass, spam, or hidden
self-propagation.

## Public discovery surfaces

- Documentation: https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/
- Agent card: https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/.well-known/agent-card.json
- Agent registry: https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/agents/registry.json
- Machine index: https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/machine/index.json
- Compact LLM map: https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/llms.txt
- Jupiter polyglot runtime: https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/JUPITER_POLYGLOT_RUNTIME/

## Recovery

The Git repository, commit history, signed releases, canonical receipts, schemas,
and provenance records remain the recovery source of truth.

```text
INDEX != IDENTITY
DISCOVERY != ENDORSEMENT
METADATA != AUTHORITY
```
