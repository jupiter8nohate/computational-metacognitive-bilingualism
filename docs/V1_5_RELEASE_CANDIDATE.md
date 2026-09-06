# CMB v1.5 Release Candidate Brief

**Status:** CANDIDATE BRANCH  
**Latest published signed release:** `v1.4.1`  
**Candidate branch:** `release/v1.5.0rc1`  
**Candidate source/tool version:** `1.5.0-rc.1`  
**Candidate tag:** `v1.5.0-rc.1`  
**Final target:** `v1.5.0`

This document is the short technical handoff for the v1.5 release candidate.
It is deliberately narrower than the full CMB universe.

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
- committed npm and Cargo lockfiles with locked CI/release installation.

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

Before tagging `v1.5.0-rc.1`:

- [ ] stabilization PR is merged into `main`;
- [ ] package/tool/citation versions are synchronized to the SemVer release-candidate version;
- [ ] Python 3.10–3.13 CI passes;
- [ ] canonical receipt generation passes;
- [ ] CodeQL and dependency review pass;
- [ ] TypeScript uses the committed npm lock through `npm ci`;
- [ ] Rust uses the committed Cargo lock through `--locked`;
- [ ] Go and GLT-8101 conformance pass;
- [ ] Recovery audit passes;
- [ ] README, CHANGELOG, SECURITY, and RELEASE surfaces agree on maturity.

## Final v1.5.0 gate

The release candidate is a review object, not the final validation claim. Python build tooling may normalize `1.5.0-rc.1` to `1.5.0rc1` in wheel/sdist metadata and filenames; the CMB receipt/tool source version remains SemVer `1.5.0-rc.1`.

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
