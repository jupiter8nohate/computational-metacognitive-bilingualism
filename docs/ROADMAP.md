# CMB engineering roadmap

The project has enough conceptual surface area. The next gains come from publishing, testing, outside review, and adoption.

## P0 ✦ first signed release

Publish the first GitHub release through the existing tag-triggered workflow.

Release acceptance criteria:

- Python 3.10–3.13 pass;
- canonical receipt passes;
- distributions build and reinstall;
- SHA256SUMS is generated;
- Sigstore bundles are produced;
- GitHub attestations are produced;
- release assets are published from the exact tag.

Until that happens, release automation is evidence of readiness, not evidence of a completed release.

## P0 ✦ one independent reviewer

Issue #5 is the primary outside-validation gate.

The project wants one serious security/provenance review before seeking broad endorsement.

## P1 ✦ repository hardening

Completed in-repository controls include:

- SECURITY.md
- CONTRIBUTING.md
- CODEOWNERS
- Dependabot
- CodeQL
- dependency review
- OpenSSF Scorecard
- explicit threat model

Platform-side controls still require repository settings:

- Dependency Graph;
- private vulnerability reporting;
- branch protections described in [Repository settings](REPOSITORY_SETTINGS.md).

## P1 ✦ interactive human/machine front door

Implemented:

- zero-dependency browser playground;
- local SHA-256 demonstration;
- CMB-Z13 symbolic projection;
- explicit policy-boundary evaluation;
- no external JavaScript analytics or dependencies.

Remaining deployment step: enable GitHub Pages or another reviewed static host.

## P1 ✦ explicit boundary contract

Implemented:

- Python reference evaluator;
- versioned `cmb.boundary-event.v1` JSON contract;
- shared language-neutral conformance fixtures;
- TypeScript/Express reference adapter;
- Rust/Actix Web reference adapter;
- Go standard-library reference adapter with strict JSON parsing;
- hosted polyglot conformance workflow.

Next boundary work:

- extend shared invalid-input fixtures across every language adapter;
- add authenticated provenance for the upstream facts feeding a boundary event;
- avoid behavioral inference as a substitute for explicit application state.

## P1 ✦ machine interoperability

Implemented:

- root `llms.txt` and `llms-full.txt` discovery entry points;
- CMB-ADP-1 static registry and local HTTP service;
- optional MCP adapter using the official Python SDK 2.x line;
- normative `CMB-CORE-1` and protocol-versioning rules.

Next interoperability work:

- add an authenticated Streamable HTTP deployment profile for MCP;
- add official conformance/smoke tests for every published machine interface;
- evaluate A2A only after a concrete interoperability use case exists;
- keep one canonical semantic engine rather than duplicating ranking logic.

## P1 ✦ research falsifiability

Implemented:

- explicit software, provenance, educational, accessibility, policy, and
  historical-novelty falsification criteria in `research/FALSIFIABILITY.md`.

Next research work:

- convert strong empirical claims into preregisterable study questions;
- seek independent replication or critique before using validation language.

## P1 ✦ CMB-Z13 executable notation

The experimental reference parser supports:

```text
cmb-z13 parse
cmb-z13 validate
cmb-z13 explain
cmb-z13 export-json
```

Next parser work should focus on versioned grammar, multi-statement documents, conformance fixtures, and falsifiable behavior rather than adding more symbolic categories.

## P2 ✦ production C2PA identity decision

Before production entity-specific assertions:

- establish a domain-controlled namespace;
- choose an appropriate signing/certificate strategy;
- complete external review;
- decide whether formal C2PA conformance is appropriate.

## P2 ✦ documentation publishing

The repository includes a buildable MkDocs site and browser playground. Enable GitHub Pages only after the repository owner reviews the public information architecture and desired domain.

## Rule for future expansion

```text
NEW_FEATURE
    -> PRIOR_ART
    -> CLEAR_DELTA
    -> TEST
    -> DOCUMENT
    -> EXTERNAL_CRITIQUE
```

Do not add a new universe when an existing component can be made more interoperable, testable, or understandable.
