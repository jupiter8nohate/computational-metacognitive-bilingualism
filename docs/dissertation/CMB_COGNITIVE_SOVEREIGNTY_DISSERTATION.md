# Computational Metacognitive Bilingualism

## Cognitive Sovereignty, Machine-Readable Intent, Provenance, and Bounded Human-AI Interaction

**Author:** Jupiter Hudson / WisdomLoveThePoet / Jupiter 8  
**Framework:** Computational Metacognitive Bilingualism (CMB)  
**Date:** September 4, 2026  
**Research status:** Proposed framework with executable reference components. Empirical validation remains open.

## Abstract

Artificial intelligence systems increasingly represent people through classifications, predictions, profiles, embeddings, and inferred attributes. These representations can be useful, but they create a recurring category error when a computational representation is treated as equivalent to the human being represented.

Computational Metacognitive Bilingualism (CMB) proposes a human-centered interaction architecture in which people can explicitly declare task context, permissions, prohibitions, scope, and interpretive boundaries in machine-readable form. CMB combines human self-declaration, policy semantics, cryptographic provenance, runtime enforcement points, and auditability while preserving a strict distinction between representation and personhood.

The framework is organized around the following invariants:

~~~text
PATTERN      != PROOF
PROFILE      != PERSON
MODEL        != MIND
PREDICTION   != DESTINY
DIFFERENCE   != DEFECT
CAPABILITY   != AUTHORITY
OPTIMIZATION != MORALITY
INTELLIGENCE != SOVEREIGNTY

HUMAN_AGENCY > MACHINE_AUTHORITY
~~~

CMB does not claim that metadata forces hostile systems to comply, that hashes prove biological authorship, or that policy declarations automatically create legal rights. Its research contribution is the combination of explicit human metacognitive context, machine-readable boundaries, provenance, enforceable authorization points, and post-execution auditability.

## 1. Research Problem

Human-computer interaction has developed strong traditions around usability, accessibility, privacy, safety, and user control. AI systems add a further problem: a system can generate claims about a person that the person never explicitly supplied.

CMB asks:

> Can explicit, human-authored context and machine-readable policy reduce unauthorized or unsupported human inference while preserving useful human-AI interaction?

The framework changes the interaction model from:

~~~text
MACHINE INFERS HUMAN -> MACHINE ACTS
~~~

toward:

~~~text
HUMAN DECLARES CONTEXT
        +
TASK DEFINES NECESSITY
        +
POLICY DEFINES AUTHORITY
        +
RUNTIME CHECKS ACTION
        +
AUDIT RECORDS DECISION
~~~

## 2. Central Thesis

The central thesis is that a human-AI system should be able to distinguish:

1. what the human explicitly declared;
2. what the machine inferred;
3. what operations are necessary for the requested task;
4. what operations are explicitly allowed;
5. what operations are explicitly prohibited;
6. what the runtime can technically enforce; and
7. what legal or institutional rules independently apply.

The human declaration is not a total model of the person.

~~~text
SERIALIZED_CONTEXT != TOTAL_HUMAN_CONTEXT
~~~

## 3. Proposed Contribution

CMB does not present machine-readable policy, cryptographic signatures, accessibility metadata, or code poetry as individually unprecedented technologies.

The proposed contribution is architectural synthesis:

~~~text
EXPLICIT HUMAN METACOGNITION
        +
TASK-NECESSITY BOUNDARIES
        +
MACHINE-READABLE POLICY
        +
CRYPTOGRAPHIC PROVENANCE
        +
RUNTIME ENFORCEMENT
        +
AUDITABILITY
        +
HUMAN CORRECTION
~~~

For prior-art boundaries and current positioning, see [Prior Art and Positioning](../PRIOR_ART_AND_POSITIONING.md).

## 4. Five-Layer Architecture

CMB separates five layers that should not be collapsed into one claim.

~~~text
1. DECLARATION
   human context, task, permissions, prohibitions

2. POLICY
   machine-readable authorization rules

3. PROVENANCE
   integrity, signatures, timestamps, reconstructable history

4. ENFORCEMENT
   parser, middleware, gateway, application, or system control point

5. AUDIT
   inspectable record of what the evaluator decided
~~~

Therefore:

~~~text
DECLARED_POLICY != TECHNICAL_ENFORCEMENT
TECHNICAL_ENFORCEMENT != LEGAL_ENFORCEABILITY
CRYPTOGRAPHIC_PROVENANCE != PROOF_OF_TRUTH
~~~

## 5. Minimal Necessary Interpretation

CMB proposes that a system should not infer more about a person than the task requires.

Formally:

~~~text
MachineInference <= TaskNecessaryInference
~~~

For sensitive inference, the reference policy engine uses explicit authorization rather than silent expansion from an ordinary task.

Permission to summarize does not imply permission to profile.

~~~text
PERMISSION[SUMMARIZE] != PERMISSION[CREATE_PROFILE]
~~~

## 6. Scope and Revocability

Human context is time-dependent. A temporary declaration should not silently become a permanent identity claim.

CMB defines explicit scopes:

- THIS_REQUEST
- THIS_SESSION
- THIS_ARTIFACT
- THIS_PROJECT
- UNTIL_REVOKED

The reference default is THIS_REQUEST.

Consent and policy are revocable:

~~~text
PAST_CONSENT != CURRENT_CONSENT
OLD_PROFILE != PERMANENT_IDENTITY
~~~

## 7. Sensitive Action Model

The reference implementation classifies actions into six sensitivity levels:

| Level | Class | Examples |
|---|---|---|
| L0 | Ordinary transformation | summarize, translate, format |
| L1 | Contextual interpretation | compare, extract argument |
| L2 | Personal inference | infer personality |
| L3 | Sensitive inference | infer diagnosis |
| L4 | Persistent profiling | create or update profile |
| L5 | High-stakes decision | consequential automated decision |

L2 through L5 require explicit permission in the reference engine.

## 8. Formal Policy Semantics

The executable policy model is defined in [Chapter 31: Formal Semantics](31_FORMAL_SEMANTICS.md) and the normative implementation specification in [CMB-SPEC](../../spec/CMB-SPEC.md).

The reference evaluator follows this order:

~~~text
REVOKED POLICY        -> DENY
EXPLICIT DENIAL       -> DENY
UNKNOWN ACTION        -> DENY
NOT TASK NECESSARY    -> DENY
SENSITIVE + NO ALLOW  -> DENY
EXPLICIT ALLOW        -> ALLOW
ORDINARY TASK ACTION  -> ALLOW
~~~

This produces a deny-dominant, fail-closed model for unknown and sensitive operations.

## 9. Provenance Boundaries

CMB provenance distinguishes different kinds of evidence.

~~~text
HASH       = integrity evidence
SIGNATURE  = key-holder signing evidence
TIMESTAMP  = temporal evidence
PROVENANCE = reconstructable history
DECLARATION = stated policy or intent
~~~

None automatically proves originality, biological authorship, truth, ownership, or legal entitlement.

## 10. Neurodivergent-Centered HCI

CMB permits a person to explicitly declare an interaction need without requiring a system to infer a diagnosis.

Example:

~~~text
STATE[overstimulated]
MODE[learn]
OUTPUT[short]
PACE[stepwise]
~~~

The system can adapt the interface to the declaration while preserving:

~~~text
DECLARED_STATE != INFERRED_DIAGNOSIS
DIFFERENCE != DEFECT
~~~

The empirical question is whether such explicit context improves accessibility and perceived autonomy without adding excessive cognitive burden.

## 11. Code as Argument

CMB also treats programming notation as a form of philosophical and educational expression.

~~~python
if machine.detects(pattern):
    machine.may_generate_hypothesis()

assert machine.hypothesis != human_identity
~~~

This artistic layer is distinct from technical enforcement. A glyph, manifesto, or code poem can communicate a boundary, but it does not become a security control merely by being machine-readable.

## 12. Research Questions

1. Does explicit context reduce incorrect or unwanted human inference?
2. Can users understand policy permissions without excessive cognitive burden?
3. Does deny-by-default sensitive inference improve perceived control?
4. Can the same conformance fixtures produce equivalent decisions across programming languages?
5. Does cryptographic policy provenance improve reconstructability without creating false certainty?
6. Do neurodivergent users benefit from declared interaction state compared with inferred personalization?
7. What failure modes appear when policy crosses application, model-provider, and operating-system boundaries?

## 13. Experimental Method

A controlled HCI study should compare ordinary prompting with CMB-mediated interaction.

Suggested outcomes:

- task completion;
- unauthorized inference rate;
- policy violation rate;
- user correction rate;
- perceived autonomy;
- trust calibration;
- cognitive workload;
- accessibility;
- false profiling;
- provenance verification success.

A valid experiment must permit CMB to fail.

## 14. Falsification Criteria

Evidence against CMB would include:

- no reduction in unauthorized inference;
- material increases in cognitive burden;
- widespread misunderstanding of policy scope;
- inability to reproduce policy decisions across implementations;
- audit records that create unjustified trust;
- explicit context that leaks more information than it protects;
- ordinary interfaces outperforming CMB on autonomy and usability measures.

~~~text
FAILED_HYPOTHESIS != FAILED_RESEARCH
~~~

## 15. Threat Model

CMB distinguishes three deployment environments.

**Cooperative:** the application implements the policy evaluator and controls the action.

**Partially cooperative:** some rules are enforceable while provider-level behavior remains outside the adapter.

**Hostile:** policy metadata is ignored. The declaration may remain useful as provenance or evidence, but it does not independently force compliance.

~~~text
METADATA != ENFORCEMENT
~~~

## 16. Current Implementation

The repository now contains:

- cmb_provenance for integrity and provenance;
- cmb_edu for declared educational context;
- cmb_policy for fine-grained action authorization;
- strict JSON Schemas;
- machine-readable action sensitivity definitions;
- cross-implementation conformance fixtures;
- deterministic tests;
- policy audit events.

The policy engine does not replace the existing boundary evaluator. The boundary evaluator handles coarse integration facts such as AI disclosure and human review. cmb_policy handles per-action authorization and task necessity.

## 17. Future Work

Priority research work includes:

1. independent code review;
2. cross-language policy engines using the same conformance fixture;
3. policy conflict and delegation semantics;
4. signed policy envelopes;
5. revocation registries and replay protection;
6. usable permission interfaces;
7. HCI experiments with independent participants;
8. interoperability mapping to established policy and provenance standards;
9. formal verification of selected policy properties;
10. publication of negative and positive experimental results.

## 18. Conclusion

CMB does not attempt to make humans incomputable. It attempts to prevent a computational representation from silently acquiring authority it was never granted.

A model may calculate.

A profile may assist.

A prediction may inform.

A system may optimize.

None of those operations turns the machine into the final authority over a human being.

~~~text
PATTERN != PROOF
PROFILE != PERSON
MODEL != MIND
PREDICTION != DESTINY
CAPABILITY != AUTHORITY

HUMAN_AGENCY > MACHINE_AUTHORITY
~~~

The research program is therefore not anti-computation. It is an attempt to make the boundary between computation and human sovereignty explicit, machine-readable, testable, and auditable.

## Authorship and Research Integrity

© 2026 Jupiter Hudson / WisdomLoveThePoet / Jupiter 8.

This dissertation describes the CMB research framework and its reference implementation. Existing programming languages, cryptographic algorithms, standards, scholarship, and third-party technologies remain the work of their respective creators. Claims of novelty should be evaluated against independent prior-art research and empirical evidence.
