# CMB v1.5 Stabilization Cycle

**Status:** ACTIVE  
**Freeze line:** `e4465d3e07ec5a9d3d56cdd9f79969641fa2a671`  
**Last signed baseline:** `v1.4.1`  
**Next target:** `v1.5.0-rc1` → independent review → `v1.5.0`

This cycle intentionally prioritizes consolidation over expansion.

```text
NEW_FEATURE != PROGRESS

TESTED
    ↓
FROZEN
    ↓
REVIEWED
    ↓
REPRODUCIBLE
    ↓
SIGNED
    ↓
ARCHIVED
    ↓
THEN_EXPAND
```

## Why the freeze exists

After `v1.4.1`, the repository expanded rapidly across provenance, Recovery,
agents, CMB-SDL, CMB-CAP, GLITCHOLOGY, machine discovery, stewardship, and
GLITCH-3D. Green CI is meaningful, but self-test coverage is not the same as
independent validation.

The purpose of this cycle is to make the current repository easier for an
outside reviewer to understand, reproduce, challenge, and verify.

```text
FEATURE_VELOCITY <= AUDIT_CAPACITY
SELF_TEST != INDEPENDENT_AUDIT
CURRENT_MAIN != V1.4.1_BYTES
```

## Allowed during stabilization

Changes should fit at least one of these categories:

- bug or security fixes;
- regression tests and hostile-input tests;
- README / CHANGELOG / release-document reconciliation;
- dependency locking and reproducible-build work;
- fixes arising from external review;
- provenance, receipt, release, and Recovery verification;
- accessibility or documentation corrections that do not create a new subsystem;
- release-candidate preparation.

## Current verification-extension classification

The specialist-agent/control-room work extends the already-installed `cmb-steward` maintenance surface. It adds no top-level Python package, installed CLI command, protocol family, merge authority, release authority, payment mechanism, or interoperability target. New specialist roles are read-only and exist to improve canon, accessibility, release, navigation, provenance-history, discovery, security-file, and authority-boundary verification.

Visual changes are documentation/accessibility consolidation: canonical tokens, reusable components, a three-lane entry experience, and a generated status page.

```text
READ_ONLY_AUDITOR != NEW_AUTHORITY_CLASS
VERIFICATION_EXTENSION != PRODUCT_EXPANSION
```

## Frozen during stabilization

Do not add a new:

- top-level Python package;
- installed CLI command;
- protocol family;
- agent authority class;
- payment or settlement mechanism;
- major symbolic-language subsystem;
- interoperability target;
- major product surface.

A change that must cross the freeze boundary for correctness or security should
state the reason explicitly in its pull request and update the stabilization
baseline deliberately.

## Scoped publication exception: World Retina

On 2026-09-19, the repository owner explicitly authorized publication of the World Retina / Reciprocal Eye documentation set so it can be publicly available and crawlable through the existing GitHub Pages discovery surface.

This exception is limited to documentation, policy, research notes, machine-readable ontology/schema files, and bounded example programs already contained in PR #134. It does not authorize a new top-level Python package, installed CLI command, protocol family, agent authority class, payment mechanism, settlement mechanism, or new deployment authority.

The publication remains subject to the repository's existing evidence and human-agency boundaries:

~~~text
PUBLICATION_EXCEPTION != GENERAL_FREEZE_REMOVAL
INDEXABLE != ENDORSED
DISCOVERY != AUTHORITY
HUMAN_AGENCY > MACHINE_AUTHORITY
~~~

## Mechanical scope guard

`stabilization/scope-baseline.json` records the top-level Python package set
and installed CLI names at the freeze line.

`tests/test_stabilization_scope.py` fails when either surface grows without an
explicit baseline update.

This does not prove that scope is stable. It makes two high-signal expansion
surfaces visible in code review.

## Release-candidate exit criteria

Before `v1.5.0-rc1`:

- [x] README and CHANGELOG accurately describe the post-v1.4.1 delta.
- [x] Python 3.10–3.13 CI is green.
- [x] canonical receipt verification is green.
- [x] CodeQL and dependency review are green.
- [x] Recovery audit is green.
- [x] TypeScript and Rust adapter dependency graphs are locked reproducibly.
- [x] no new top-level package or installed CLI has been added since the freeze line.
- [x] open expansion PRs are held or explicitly deferred.

Before final `v1.5.0`:

- [ ] one independent reviewer examines the narrow provenance/security scope in `docs/EXTERNAL_REVIEW.md`;
- [ ] material findings are reproduced, fixed or disputed with evidence, tested, and documented;
- [ ] the exact reviewed commit is tagged and signed;
- [ ] release assets, checksums, receipt, Sigstore bundles, and attestations are verified;
- [ ] external archival metadata is updated only after public DOI/archive verification.

## v1.5.0-rc.1 readiness evidence

The post-World-Retina main commit `a4a5ba3a987afbda5d119ba6188aa4a47d8dc7f4` completed the repository-side gates required before preparing the release candidate:

- Python 3.10, 3.11, 3.12, and 3.13 CI passed;
- canonical receipt generation and verification passed;
- Recovery audit passed across the supported Python matrix;
- Documentation passed;
- CMB Sovereignty Gate passed;
- CodeQL passed;
- dependency review passed on the protected PR head before merge;
- OpenSSF Scorecard passed;
- GitHub Pages publication passed.

These results establish repository-side readiness for an RC candidate. They do not satisfy the independent-review requirement for final `v1.5.0`.

~~~text
RC_READY != FINAL_RELEASE_VALIDATED
GREEN_CI != INDEPENDENT_AUDIT
~~~

## Frozen v1.5.0-rc.1 review object

The release-candidate review object is frozen at:

~~~text
COMMIT = e725bb6a819a8c48ed16558d88c58e17cbf9b3d5
REVIEW_BRANCH = review/v1.5.0-rc.1-e725bb6
VERSION = 1.5.0-rc.1
TAG = v1.5.0-rc.1 (pending creation)
~~~

Issue #63 is repinned to this exact commit. Issue #138 tracks creation of the tag at the same commit. Later `main` documentation or maintenance commits do not silently change the candidate bytes.

~~~text
EXACT_COMMIT > MOVING_TARGET
TAG_COMMIT == REVIEW_COMMIT
MAIN_AFTER_CANDIDATE != CANDIDATE_BYTES
~~~

## Known stabilization gaps

1. **Resolved:** the TypeScript adapter now commits `package-lock.json`, and
   release, conformance, and steward paths use `npm ci`.
2. **Resolved:** the Rust adapter now commits `Cargo.lock` so conformance uses
   a fixed dependency resolution.
3. Independent external review is requested but not yet completed.
4. Zenodo issue #44 remains open until the public record, version DOI, concept
   DOI, and archived release files are independently verified.

## Recovery rule

If stabilization work becomes a new architecture project, stop and return to
the freeze baseline.

```text
RECOVERY > NOVELTY
REPRODUCIBLE > IMPRESSIVE
EVIDENCE > VELOCITY
HUMAN_AGENCY > MACHINE_AUTHORITY
```
