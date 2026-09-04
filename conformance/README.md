# CMB Boundary Conformance

This directory is the language-neutral semantic contract for CMB boundary implementations.

`boundary.v1.cases.json` contains valid `cmb.boundary-event.v1` inputs and the expected policy outcome. Every supported implementation should run these exact cases.

## Contract

Implementations must preserve:

```text
AI_INVOLVED && !AI_DISCLOSED
    -> AI_DISCLOSURE_REQUIRED

CONSEQUENTIAL_DECISION && !HUMAN_REVIEW_AVAILABLE
    -> HUMAN_REVIEW_REQUIRED

PROFILE_TREATED_AS_PERSON
    -> PROFILE_IS_NOT_PERSON

PREDICTION_TREATED_AS_DESTINY
    -> PREDICTION_IS_NOT_DESTINY

CONSENT_REQUIRED && !CONSENT_PRESENT
    -> CONSENT_REQUIRED

AUTHORITY = HUMAN_FINAL
```

Violation order is part of v1 conformance so logs, tests, and adapters remain deterministic.

## Boundary

The fixtures contain explicit application facts. They are not examples of behavioral inference and do not authorize software to infer identity, diagnosis, mental state, intent, or moral status from human expression.

A new rule requires a new reviewed contract version or a backwards-compatible extension with explicit versioning. Do not silently reinterpret v1.
