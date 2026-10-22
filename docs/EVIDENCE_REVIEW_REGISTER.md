# WITNESS://BACKTRACE | Evidence Review Register

**Status: EDITORIAL PROCEDURE, NOT EXTERNAL VALIDATION.**

This register complements the existing [ten-record evidence dataset](https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/datasets/2084-witness-evidence.v1.json) and the [WITNESS://BACKTRACE protocol](WITNESS_BACKTRACE_PROTOCOL.md). A structural CI pass does not mean any current source link or claim has been independently reviewed.

## Claim categories

| Category | Rule |
| --- | --- |
| DOCUMENTED_CONTEXT | A narrow statement supported by an inspectable primary source |
| INTERPRETATION | An author's extrapolation, commentary or contested conclusion |
| FICTION | A fictional event, character, technology, or 2084 institution |
| UNKNOWN | An unresolved source, event, or causal link needing further work |

Do not convert **INTERPRETATION** into **DOCUMENTED_CONTEXT** because a statement is repeated, stylized, or marked VERIFIED.

## Human review entry template

Copy this table into a pull request when challenging or updating a source; **do not fill in verification results without performing the review**.

| Field | Entry |
| --- | --- |
| Evidence ID | `01` through `10` |
| Claim quoted/paraphrased | Exact narrow claim under examination |
| Source title + URL | Direct HTTPS source |
| Source owner, jurisdiction and publication date | Identify, or state unknown |
| Date reviewed (UTC) | Actual inspection date |
| Status | documented / context_dependent / research / unresolved |
| Support | Supported / partially supported / unsupported |
| Counterevidence and limitations | Required |
| Correction / PR link | Record amendment and discussion |
| Human reviewer | Named reviewer, no automated reviewer impersonation |

## Existing ten-source queue

**IDs 01-10 are awaiting an independently documented source-by-source recheck in this register.** The JSON registry's existing evidence_status values characterize narrow claims, not a completed 2026-10-22 external audit.

1. Behavioral tracking and data brokerage
2. Predictive credit and worker assessment
3. Emotion inference and algorithmic hiring
4. Workplace language monitoring
5. Identity authorization and SSO dependency
6. Remote proctoring and accessibility
7. Consumer reporting and linked decisions
8. Software-mediated repair restrictions
9. Face matching and false identifications
10. Graph models for connected financial risk

## Correction protocol

Submit one reviewable PR updating both the evidence JSON and relevant prose. Preserve counterevidence; do not silently overwrite a prior finding. Give affected claims an explicit status of unknown if available source material is insufficient. Document source removals, corrected dates, and legal-case posture accurately.

```text
SOURCE_FOUND != CLAIM_PROVEN
SELF_TEST != INDEPENDENT_REVIEW
FICTION != ALLEGATION
PATTERN != PROOF
```
