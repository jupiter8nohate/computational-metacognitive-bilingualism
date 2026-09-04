# CMB engineering roadmap

The project has enough conceptual surface area. The next gains come from publishing, testing, outside review, and adoption.

## P0 ✦ signed release — completed

The signed-release gate is operational. Version `v1.4.1` was published through the tag-triggered GitHub Actions workflow with release artifacts, `SHA256SUMS`, a CMB source receipt, and Sigstore bundles.

The remaining release rule is temporal rather than architectural:

```text
PUBLISHED_RELEASE != CURRENT_MAIN
POST_RELEASE_CHANGE != SEALED_BY_OLDER_TAG
```

Any canonical artifact changed after `v1.4.1` must wait for a later version-matching signed release before those new bytes are covered by that release receipt.

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

Deployment status: GitHub Pages is live at the canonical project URL. Future work should improve information architecture, retrieval quality, and measurement rather than re-solving deployment.

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

## P1 ✦ structured case-study evidence

Implemented:

- human-readable case-study reports in `research/case-studies/`;
- `cmb.case-study.v1` JSON Schema;
- machine-readable evidence records;
- screenshot SHA-256 fingerprint preservation without republishing the source image;
- CI validation that the structured record, human report, and evidence digest remain synchronized;
- public Pages discovery for the case-study front door and structured JSON.

Next research work:

- add new cases only when they contribute independent evidence rather than repeating the same example;
- preserve explicit revision triggers and negative findings;
- seek independent reproduction or critique of high-value cases.

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

## P2 ✦ documentation publishing — live

The MkDocs site and browser playground are deployed on GitHub Pages. The next documentation gains come from keeping the public site synchronized with the repository, exposing structured research records, improving retrieval paths, and measuring actual search/index performance.

```text
PUBLISHED != INDEXED
INDEXED != RETRIEVED
RETRIEVED != ADOPTED
```

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
