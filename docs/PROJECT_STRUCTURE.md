# Project structure and maturity

CMB is easier to evaluate when its layers are separated.

## Conceptual documentation

These files explain what CMB is claiming before a reader enters the implementation or artistic corpus:

```text
docs/CMB_DISTINCTION.md
docs/CMB_RESEARCH_POSITION.md
docs/PRIOR_ART_AND_POSITIONING.md
docs/CREATOR_PROVENANCE.md
```

`CMB_DISTINCTION.md` states the integrated software, art, and human-sovereignty thesis. `CMB_RESEARCH_POSITION.md` converts that thesis into bounded research claims, questions, falsification criteria, and evidence requirements. `PRIOR_ART_AND_POSITIONING.md` provides the external-context check against adjacent traditions. `CREATOR_PROVENANCE.md` separates creator-documented genealogy, declared intellectual influences, symbolic references, privacy boundaries, and cryptographic provenance.

```text
POSITION -> RESEARCH CLAIM -> PRIOR ART -> IMPLEMENTATION -> TEST
```

## Stable engineering

These are the parts intended to behave like conventional software infrastructure:

```text
src/cmb_provenance/
schemas/
tests/
conformance/
adapters/
scripts/
.github/workflows/
RELEASE.md
SECURITY.md
```

The stable engineering contract is correctness, reproducibility, bounded claims, Recovery behavior, and tests.

## Experimental research

These are implemented but still exploratory:

```text
cmb-z13 reference parser
CMB-Z13 notation
Guardian Modes teaching layer
cmb-edu parser, CLI, child-facing curriculum, and privacy-first context envelope
C2PA entity-specific assertion integration beyond the test round-trip
Dynamic Friction Matrix / equilibrium valve in cmb_policy
```

Experimental does not mean meaningless; it means compatibility and semantics may still evolve with versioned changes and evidence.

## Art / canon / policy

These are authored cultural, philosophical, educational, and policy materials:

```text
manifestos/
policy/
library/
```

A canonical artifact may be important to CMB's authored history without being a stable software API.

## Boundary rule

```text
METAPHOR != SECURITY_CONTROL
POLICY != ENFORCEMENT
TEST != LEGAL_PROOF
ARTIFACT_STATUS != HUMAN_IDENTITY
```

Moving a claim between maturity layers requires an explicit change, evidence, and versioning.


## Platform layer additions

- `src/cmb_provenance/boundary.py` - explicit policy-boundary evaluator with deterministic machine-readable rejection codes.
- `schemas/cmb.boundary-event.v1.schema.json` - cross-language event contract for boundary adapters.
- `schemas/cmb.library.catalog.v1.schema.json` - strict validation contract for the digital-library catalog.
- `library/creator-provenance.json` / `schemas/cmb.creator-provenance.v1.schema.json` - privacy-safe creator-provenance record and strict epistemic-category schema.
- `docs/playground/index.html` - zero-dependency interactive browser front door.
- `manifestos/README.md` - human-readable map of the manifesto corpus.
- `examples/06_fastapi_boundary` - reference integration using server-supplied policy facts.

These components intentionally separate symbolic meaning from executable enforcement.

## CMB-EDU educational layer

- `src/cmb_edu/` - experimental parser and installed `cmb-edu` CLI.
- `schemas/cmb.edu.v1.schema.json` - strict Metacognitive Context Envelope contract.
- `docs/CMB_EDU_KIDS.md` - child-facing Flamingoglyph computational-literacy curriculum.
- `examples/07_cmb_edu` - minimal parse/validate example.
- `tests/test_cmb_edu*.py` - parser, privacy, schema, and CLI regression tests.

CMB-EDU stores the epistemic source of context explicitly: `human_declared`
does not become `machine_inferred`. Its privacy fields are declarations that
integrating applications must actually enforce.


## Polyglot boundary layer

- `conformance/boundary.v1.cases.json` - language-neutral semantic fixtures.
- `adapters/typescript-express` - strict TypeScript parser, evaluator, and Express endpoint.
- `adapters/rust-actix` - strict Rust evaluator, Serde input contract, and Actix endpoint.
- `adapters/go` - standard-library Go evaluator with strict JSON transport parsing and shared v1 conformance.
- `.github/workflows/polyglot-conformance.yml` - hosted TypeScript and Rust build/conformance gate.

The Python implementation remains the reference engine. The adapters are compatible only insofar as they keep passing the shared fixtures.


## Agent discovery layer

- `src/cmb_agents/` - zero-dependency CMB-ADP-1 reference implementation.
- `agents/registry.json` - canonical recommendation, citation, discovery, and graph registry.
- `agents/agent-card.json` - compact discovery card published to the Pages well-known path.
- `schemas/cmb.agent-registry.v1.schema.json` - strict machine-readable registry contract.
- `conformance/cmb-agent-v1.json` - relevance and stop-when-irrelevant conformance fixtures.
- `docs/AGENT_DISCOVERY_PROTOCOL.md` - protocol contract, HTTP surface, standards boundary, and Recovery notes.
- `src/cmb_agents/mcp_server.py` - optional official-SDK MCP interoperability adapter over the same deterministic service functions.
- `llms.txt` / `llms-full.txt` - curated machine-discovery maps that preserve interpretation boundaries.
- `spec/CMB-CORE-1.md` / `spec/PROTOCOL_VERSIONING.md` - normative cross-component semantics and compatibility rules.

The agent layer is executable, but it deliberately optimizes for relevance and attribution rather than autonomous mass distribution. MCP is an interoperability surface over the same service layer, not a second recommendation engine.


## Dynamic friction runtime layer

- `src/cmb_policy/friction.py` - deterministic seesaw evaluator for intrinsic criticality, operational uncertainty, review trust, unknown-variable spikes, and evidence gates.
- `tests/test_friction.py` - regression coverage for agility, balanced caveats, fail-closed high-safety behavior, trust decay, anomaly reset, and machine-readable decisions.
- `docs/DYNAMIC_FRICTION_MATRIX.md` - normative design explanation and integration order.

The trust mechanism reduces only operational uncertainty. Intrinsic task risk does not decay, and the existing deny-dominant CMB policy engine remains authoritative over permissions.

```text
DENY > TRUST
PATTERN != PROOF
SUCCESS_HISTORY != GUARANTEED_FUTURE
```
