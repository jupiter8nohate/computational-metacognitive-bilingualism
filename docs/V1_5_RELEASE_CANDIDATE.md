# CMB v1.5 Release Candidate Brief

| Field | Value |
| --- | --- |
| Latest published signed release | `v1.4.1` |
| Candidate source and tool version | `1.5.0-rc.2` |
| Candidate tag | `v1.5.0-rc.2` |
| Exact commit and review branch | [Review ticket #63](https://github.com/jupiter8nohate/computational-metacognitive-bilingualism/issues/63) |
| Tag and signed assets | [Publication ticket #138](https://github.com/jupiter8nohate/computational-metacognitive-bilingualism/issues/138) |
| Final target | `v1.5.0` |

This document is the short technical handoff for the v1.5 release candidate.
It is deliberately narrower than the full CMB universe.

The unpublished `rc.1` review commit `e725bb6a819a8c48ed16558d88c58e17cbf9b3d5` pinned a Zstandard dependency affected by [RUSTSEC-2026-0391](https://rustsec.org/advisories/RUSTSEC-2026-0391.html). The `rc.2` source includes the subsequent Actix remediation and its regression check.

## Candidate purpose

v1.5 is a consolidation release for the large post-v1.4.1 development delta.
Its primary goal is to make the current implementation reproducible,
reviewable, and accurately bounded before further feature expansion.

```text
FEATURE_VELOCITY <= AUDIT_CAPACITY
SELF_TEST != INDEPENDENT_AUDIT
REPRODUCIBLE > IMPRESSIVE
```

## Major post-v1.4.1 additions

The candidate includes, among other already-implemented work:

- CMB-RECOVERY-1 and the canonical recovery/retrieval corpus;
- Public Stewardship Incubation machine-readable status;
- canonical Err ⃝or⃟⃤ GLITCHOLOGY naming and living-language registry work;
- the executable Go → Python → GLITCHOLOGY reference runtime;
- GLT-0037–GLT-0046 composite protocols;
- GLITCH-IR v1 / GLT-8101 eight-language semantic conformance;
- bounded CMB Steward agents with draft-PR-only authority;
- GLITCH-3D-1 spatial semantics and runtime;
- machine discovery and documentation hardening;
- explicit v1.5 stabilization/scope controls;
- committed npm and Cargo lockfiles with locked CI/release installation;
- the World Retina / Reciprocal Eye publication set, including the 57-chapter story, PRE-2084 bridge, Two Loops, Ten Civic Forks, public policy/research surfaces, machine ontology/schema, and bounded example programs;
- canonical GitHub Pages discovery for World Retina through sitemap, robots policy, machine/LLM discovery surfaces, public gateway URLs, and deployment-time IndexNow notification.

This list is a release narrative, not a claim that every experimental subsystem
has become a stable public compatibility promise.

## Stable review target

The first independent technical review remains intentionally narrow:

```text
src/cmb_provenance/
scripts/seal_canonical_artifacts.py
scripts/build_checksums.py
.github/workflows/ci.yml
.github/workflows/release.yml
tests/
RELEASE.md
docs/C2PA_INTEROPERABILITY.md
docs/THREAT_MODEL.md
SECURITY.md
```

The reviewer is not required to audit every manifesto, symbolic language,
educational experiment, or research subsystem.

## Candidate gates

Record the following evidence for the exact `rc.2` tree in [issue #138](https://github.com/jupiter8nohate/computational-metacognitive-bilingualism/issues/138) before tagging.

- synchronized package, tool and citation versions;
- successful Python 3.10–3.13 tests, canonical receipt, Recovery audit and CodeQL;
- passing dependency review and a passing Actix Zstandard regression check;
- passing locked TypeScript and Rust tests, Go boundary conformance, and GLT-8101 conformance.

## Review-target repin

[Issue #63](https://github.com/jupiter8nohate/computational-metacognitive-bilingualism/issues/63) records the exact `rc.2` candidate commit and its review branch. A reviewer can verify the commit directly even as `main` advances.

~~~text
OLD_REVIEW_TARGET != CURRENT_CANDIDATE_TREE
EXACT_COMMIT > MOVING_TARGET
~~~

## RC publication state

The `v1.5.0-rc.2` tag must point to the exact candidate commit in [issue #138](https://github.com/jupiter8nohate/computational-metacognitive-bilingualism/issues/138). The tag workflow publishes a signed prerelease after its gates succeed.

~~~text
TAG_COMMIT == REVIEW_COMMIT
MAIN_AFTER_CANDIDATE != CANDIDATE_BYTES
RC != FINAL_RELEASE
~~~

## Final v1.5.0 gate

The candidate is the exact tree for independent review. Python build tooling normalizes `1.5.0-rc.2` to `1.5.0rc2` in wheel and sdist metadata. The CMB tool and receipt record the SemVer form `1.5.0-rc.2`.

Before final `v1.5.0`:

- [ ] issue #63 records one independent review against the exact candidate commit;
- [ ] material findings are reproduced;
- [ ] fixes or evidence-backed disputes are recorded;
- [ ] behavior changes receive regression coverage;
- [ ] remaining uncertainty is documented;
- [ ] final version metadata is synchronized;
- [ ] signed release assets, checksums, receipt, Sigstore bundles, and GitHub attestations are verified;
- [ ] archive/DOI metadata is recorded only after the public record resolves and the archived files are checked.

## Evidence boundaries

```text
GREEN_CI != INDEPENDENT_AUDIT
HASH != AUTHORSHIP
SIGNATURE != ORIGINALITY
REVIEW != CERTIFICATION
INTEROPERABILITY != CONFORMANCE_CERTIFICATION
RELEASE_CANDIDATE != FINAL_RELEASE
```

## Recovery

If a candidate change introduces another major subsystem, return it to a later
feature cycle instead of expanding v1.5.

```text
RECOVERY > NOVELTY
THEN_EXPAND
```
