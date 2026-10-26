# ♃ D.N.A. Bible™ | Ten-Upgrade Evolution Review

**Status:** Proposed review-branch improvements; NOT a live release, completed independent audit, signed release, DOI, or confirmed external search indexing.

**Origin:** Jupiter Hudson / WisdomLoveThePoet / Jupiter 8. The changes extend the existing MkDocs/GLITCHOLOGY/2084 infrastructure and preserve the source literary canon.

## Coverage map

| Upgrade | Implementation | Verification |
| --- | --- | --- |
| Four gateways | Home adds four accessible permanent reading paths | Evolution structural audit, browser smoke |
| Red and gold design | Responsive evolution.css layer | Reduced-motion, contrast and focus checks |
| Nine-transmission reading | Canonical ordered reader with per-page ephemeral checkboxes and progressive previous/next links | Browser smoke and static fallback |
| Search discoverability | Existing SEO generator and site-integrity tests remain authoritative; added canonical-route and page-spec checks | Source audit and strict MkDocs build |
| Canonical symbols | Existing v1 symbol JSON remains authoritative; dictionary consistency gets additional checks | Ten IDs, names and sequence validation |
| Seven Gates | Existing interactive Codex gains explicit research crosswalk | Seven buttons and seven labeled context entries |
| Evidence traceability | New machine-readable fiction-to-context crosswalk, all entries pending human review | Typed records with status and limitations |
| Author provenance | Biography gains a structured verified-vs-declared reading guide | Existing source boundary remains visible |
| Browser coverage | Chromium screenshot, navigation and axe-core checks | Optional dedicated PR workflow |
| Release discipline | Proposal stays on a review branch; no direct main edits or regenerated signed release | External review and DOI gates remain open |

## Stabilization boundary

README.md declares the v1.5 feature freeze. The interactive reader and new visual layer are **freeze-boundary exceptions proposed for review** under this pull request, not changes already accepted into a frozen release candidate. No protocol schema used for signatures, production API, or published signed tag is replaced. Maintainers should first decide whether these UX exceptions belong in a later release cycle.

## Required acceptance checks

1. Run `python scripts/audit_evolution.py` and `python scripts/verify_archive_experience.py`.
2. Run `python scripts/build_docs.py` and existing search and link audits.
3. Inspect the optional Playwright/axe-core output in desktop and mobile layouts; test keyboard navigation and at least one screen reader manually.
4. Review claimed context and counterevidence before any ledger record becomes marked independently reviewed.
5. Review commit tree, PR discussion, package dependencies, and any freeze-boundary exceptions before merge.
6. Keep the v1.5 release candidate immutable. Do not claim a later commit is covered by its older release receipt.
7. Verify any future signed tags and DOI externally, including a restoration test.

```text
PUBLISHED != INDEXED
FICTION != EVIDENCE
SELF_TEST != INDEPENDENT_AUDIT
HASH != AUTHORSHIP_PROOF
HUMAN_AGENCY > MACHINE_AUTHORITY
```
