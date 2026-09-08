# CMB Claim-to-Control Traceability

## Purpose

CMB separates philosophical language from executable guarantees.

A principle can be meaningful before software enforces it, but the repository must not describe every meaningful principle as an implemented security control.

```text
SYMBOLIC
  -> DECLARED
  -> ENFORCED
  -> VERIFIED
```

The canonical machine-readable record is:

```text
machine/claim-control-traceability.v1.json
```

The deterministic validator is:

```text
python -m cmb_agents.claim_control --manifest machine/claim-control-traceability.v1.json
```

## Maturity levels

| Level | Meaning |
| --- | --- |
| SYMBOLIC | A philosophical or architectural principle. No technical enforcement is claimed. |
| DECLARED | The principle is explicitly represented in repository policy or documentation. |
| ENFORCED | Deterministic runtime or validation code rejects states that violate the declared boundary. |
| VERIFIED | The enforcement path is linked to executable tests as repository-side evidence. |

A claim cannot be marked VERIFIED unless it has both an enforcement control and a test control.

## Current examples

```text
PATTERN != PROOF
PROFILE != PERSON
MODEL != MIND
PREDICTION != DESTINY
RISK_SCORE != INTENT
MACHINE_CAN_PROPOSE != MACHINE_CAN_MERGE
HUMAN_AGENCY > MACHINE_AUTHORITY
```

These are mapped to the strategy constitution, deterministic validators, and tests in the traceability manifest.

Two useful principles remain intentionally symbolic until separate infrastructure exists:

```text
SENSATION != AUTHORITY
OBSERVATION != UNDERSTANDING
```

They are not described as network isolation, consent enforcement, copyright determination, or proof about machine consciousness.

## Fail-closed drift detection

Every control contains a repository-relative path and an exact textual anchor.

The validator fails when:

- a referenced file disappears;
- a control anchor disappears;
- a VERIFIED claim loses its test;
- an ENFORCED or VERIFIED claim loses deterministic enforcement;
- a control path attempts to escape the repository;
- duplicate claim identifiers or expressions appear.

This turns documentation drift into a CI-visible defect.

## Evidence boundary

```text
DECLARED_POLICY != TECHNICAL_ENFORCEMENT
TECHNICAL_ENFORCEMENT != LEGAL_ENFORCEABILITY
TEST_PASS != CORRECTNESS
GREEN_CI != INDEPENDENT_AUDIT
```

Repository-side verification means the declared control is present and its linked tests pass. It does not prove universal correctness, legal compliance, subjective understanding, human intent, or future safety.

## Recovery rule

```text
CLAIM
  -> TRACE
  -> CONTROL
  -> TEST
  -> CI
  -> HUMAN REVIEW

EVIDENCE > ELOQUENCE
PATTERN != PROOF
```
