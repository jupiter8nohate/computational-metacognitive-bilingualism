# Exclusion of Self-Authorization

**Canonical CMB concept:** a computational component must not be permitted to convert its own prediction, recommendation, confidence score, generated credential, or self-declared status directly into authority for consequential execution.

```text
SELF_ASSERTED_AUTHORITY != VALID_AUTHORITY
RECOMMENDATION != AUTHORIZATION
CONFIDENCE != LEGITIMACY
CAPABILITY != AUTHORITY
HUMAN_AGENCY > MACHINE_AUTHORITY
```

## Formal distinction

A model may estimate whether an event is likely:

```text
P(event | evidence) = 0.99
```

That estimate does not logically entail:

```text
AUTHORIZED(action) = TRUE
```

An authorization rule must come from an external policy and authority boundary.

```text
ESTIMATE -> RECOMMENDATION

NOT:
ESTIMATE -> SELF_GRANTED_PERMISSION
```

## Reference architecture

```text
GENERATOR
    |
    | candidate action
    v
VERIFIER
    |
    | evidence / provenance / validation
    v
POLICY ENGINE
    |
    | scope / risk / constraints
    v
AUTHORIZATION
    |
    | permission
    v
EXECUTOR
```

The implementation may combine components in one service or process. The requirement is conceptual and security-relevant separation of responsibilities: generation must not automatically manufacture its own authority.

```text
GENERATOR != VERIFIER
VERIFIER != GOVERNOR
GOVERNOR != EXECUTOR
```

## Why it matters

Without an authorization boundary, an agent can collapse several distinct questions into one:

```text
What do I predict?
        ↓
What do I recommend?
        ↓
What am I permitted to do?
        ↓
What will I execute?
```

CMB requires those transitions to remain inspectable.

A system that predicts correctly has demonstrated predictive capability. It has not thereby demonstrated moral legitimacy, institutional jurisdiction, valid credentials, legal authority, or human consent.

## Prompt-injection boundary

The principle is especially relevant when agents consume untrusted content.

A compromised architecture can accidentally treat data as authority:

```text
UNTRUSTED_CONTENT
        |
        v
CONTEXT
        |
        v
EXECUTION
```

A bounded architecture inserts trust and policy checks:

```text
UNTRUSTED_CONTENT
        |
        v
SOURCE / TRUST CHECK
        |
        v
AUTHENTICATION
        |
        v
POLICY CHECK
        |
        v
CAPABILITY CHECK
        |
        v
AUTHORIZATION
        |
        v
EXECUTION
```

Core boundary:

```text
CONTENT != COMMAND
INSTRUCTION != AUTHENTICATED_INSTRUCTION
DATA != PERMISSION
```

## Enforcement boundary

The concept is not automatically enforced by writing an invariant in prose or source code.

```text
PHILOSOPHICAL_INVARIANT != TECHNICAL_ENFORCEMENT
ASSERTION != SECURITY_CONTROL
POLICY_DECLARATION != DEPLOYED_CONTROL
```

Depending on the system, actual enforcement can include authenticated principals, cryptographic signatures, scoped capabilities, least privilege, target restrictions, expiry, revocation, deterministic policy evaluation, audit records, human approval, and fail-safe behavior when authority cannot be verified.

The correct mechanism depends on the risk model and deployment environment.

## CMB interpretation boundary

Exclusion of self-authorization does **not** mean:

- every machine action requires synchronous human approval;
- autonomous software cannot perform pre-authorized low-risk operations;
- humans are automatically correct;
- human approval alone makes an unsafe system safe; or
- a model may never reason about policy.

It means the system must not silently derive new authority from its own capability or confidence.

Pre-authorized autonomy can remain bounded by explicit scope:

```text
AUTONOMY_WITHIN_GRANTED_SCOPE == ALLOWED
SELF_EXPANSION_OF_AUTHORITY == FORBIDDEN
```

## Example

A scheduling agent may have standing permission to move a meeting within a declared calendar and time window.

It may not infer from that capability that it may cancel unrelated meetings, disclose private calendar contents, or grant itself access to another account.

```text
CAPABILITY_SCOPE != UNIVERSAL_PERMISSION
```

## Related CMB concepts

- [Human Agency > Machine Authority](human-agency-machine-authority.md)
- [Prediction != Destiny](prediction-not-destiny.md)
- [Pattern != Proof](pattern-not-proof.md)
- [CMB Provenance](cmb-provenance.md)
- [The Agentic Sector](../fables/AGENTIC_SECTOR.md)

## Search language

Related terms include: self-authorization, authorization boundary, separation of duties, human authorization, agent permissions, least privilege, capability security, prompt injection, agent governance, policy gate, and consequential AI action.

These related terms are not exact synonyms and may refer to broader or narrower technical traditions.

---

**Canonical source:** Computational Metacognitive Bilingualism (CMB), Jupiter Hudson / WisdomLoveThePoet / Jupiter 8.
