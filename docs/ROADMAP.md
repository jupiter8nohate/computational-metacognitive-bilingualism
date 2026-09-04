# CMB engineering roadmap

The project has enough conceptual surface area. The next gains come from publishing, testing, outside review, and adoption.

## P0 — first signed release

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

## P0 — one independent reviewer

Issue #5 is the primary outside-validation gate.

The project wants one serious security/provenance review before seeking broad endorsement.

## P1 — repository hardening

- SECURITY.md
- CONTRIBUTING.md
- CODEOWNERS
- Dependabot
- CodeQL
- dependency review
- OpenSSF Scorecard
- explicit threat model

## P1 — CMB-Z13 executable notation

The experimental reference parser now supports:

```text
cmb-z13 parse
cmb-z13 validate
cmb-z13 explain
cmb-z13 export-json
```

Next parser work should focus on versioned grammar, multi-statement documents, conformance fixtures, and falsifiable behavior rather than adding more symbolic categories.

## P2 — production C2PA identity decision

Before production entity-specific assertions:

- establish a domain-controlled namespace;
- choose an appropriate signing/certificate strategy;
- complete external review;
- decide whether formal C2PA conformance is appropriate.

## P2 — documentation publishing

The repository now includes a buildable MkDocs site. Enable GitHub Pages only after the repository owner reviews the public information architecture and desired domain.

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
