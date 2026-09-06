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
- [ ] Python 3.10–3.13 CI is green.
- [ ] canonical receipt verification is green.
- [ ] CodeQL and dependency review are green.
- [ ] Recovery audit is green.
- [x] TypeScript and Rust adapter dependency graphs are locked reproducibly.
- [x] no new top-level package or installed CLI has been added since the freeze line.
- [x] open expansion PRs are held or explicitly deferred.

Before final `v1.5.0`:

- [ ] one independent reviewer examines the narrow provenance/security scope in `docs/EXTERNAL_REVIEW.md`;
- [ ] material findings are reproduced, fixed or disputed with evidence, tested, and documented;
- [ ] the exact reviewed commit is tagged and signed;
- [ ] release assets, checksums, receipt, Sigstore bundles, and attestations are verified;
- [ ] external archival metadata is updated only after public DOI/archive verification.

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
