# D.N.A. Bible™ | Release, Attestation and Recovery Checklist

**Scope:** Documentation, reader tools, provenance and human review within the v1.5 stabilization contract. Not a signed release or independent certification by this document's existence.

## Automated gates

- [ ] Site builds through `python scripts/build_docs.py`.
- [ ] Archive experience audit passes `python scripts/verify_archive_experience.py`.
- [ ] Symbol registry IDs and canon references validate.
- [ ] Source-to-HTML links, images and static assets validate.
- [ ] Accessibility and reduced-motion checks pass their documented scope.
- [ ] Existing provenance and Recovery test suites pass.
- [ ] No unsupported protocol/CLI/package surface added.

## Human and external gates

- [ ] Review each claim in [Evidence Review Register](EVIDENCE_REVIEW_REGISTER.md).
- [ ] Perform real screen-reader and keyboard-only browsing on published pages.
- [ ] Inspect Pages URLs after merge and note actual status.
- [ ] Complete independent provenance audit (open release issue).
- [ ] Create and publicly verify signed release candidate tag at **the frozen candidate commit**, not an incidental newer `main` SHA.
- [ ] Complete reproducibility and dependency review; publish observed results.
- [ ] Archive a signed release on an independent host (e.g. Zenodo) and verify any public DOI before reporting it.
- [ ] Record exported canonical files, SHA-256, tag/commit, title, creator, license and recovery instructions.
- [ ] Test restoration of a copy independent of GitHub Pages.

## Recovery contract

A future export manifest should be deterministic and source-path-preserving. An SHA-256 digest detects modification of archived bytes; it does not establish original human authorship, license ownership, permanent availability, or legal enforceability.

The [existing Recovery architecture](RECOVERY_AND_PRESERVATION.md), `machine/recovery-map.json`, and canonical-corpus tooling remain authoritative for technical artifacts. This checklist does not replace or silently regenerate their signed records.

```text
RELEASE_CANDIDATE != SIGNED_RELEASE
SELF_TEST != INDEPENDENT_REVIEW
HASH != AUTHORSHIP_JUDGMENT
CID != GUARANTEED_AVAILABILITY
RECOVERY > SINGLE_PLATFORM_DEPENDENCE
```
