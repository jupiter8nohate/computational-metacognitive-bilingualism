# Chapter 31: Formal Semantics of Computational Metacognitive Bilingualism

## 31.1 Purpose

This chapter translates the CMB principle:

~~~text
HUMAN_AGENCY > MACHINE_AUTHORITY
~~~

into a machine-testable authorization model.

The objective is not to encode the entire human mind. The objective is to represent the limits of machine authority for a declared task.

~~~text
REPRESENTATION != HUMAN
~~~

## 31.2 Formal Interaction Model

A CMB interaction is represented by:

~~~text
C = (H, T, P, D, I, E, A)
~~~

where:

- H = human-declared context;
- T = task actions;
- P = explicit permissions;
- D = explicit denials;
- I = epistemic invariants;
- E = execution environment;
- A = audit record.

A requested action must be necessary to the task and must survive policy evaluation.

## 31.3 Authority Ordering

For the reference policy layer:

~~~text
SYSTEM SAFETY / APPLICABLE EXTERNAL CONSTRAINTS
                    >
EXPLICIT HUMAN PROHIBITION
                    >
EXPLICIT HUMAN PERMISSION
                    >
DECLARED TASK NECESSITY
                    >
DEFAULT MINIMIZATION
                    >
OPTIMIZATION
~~~

The policy engine itself does not interpret law. This ordering states that machine optimization does not override a policy prohibition.

~~~text
OPTIMIZATION != MORALITY
CAPABILITY != AUTHORITY
~~~

## 31.4 Scope

The policy envelope supports:

~~~text
THIS_REQUEST
THIS_SESSION
THIS_ARTIFACT
THIS_PROJECT
UNTIL_REVOKED
~~~

The default is THIS_REQUEST.

A past context does not automatically propagate into a later interaction.

~~~text
PAST_STATE != PRESENT_IDENTITY
~~~

## 31.5 Revocation

A revoked policy denies all actions evaluated under that policy.

~~~text
Consent(t) != Consent(t+1)
~~~

Historical audit records may show that permission previously existed. They do not create future authorization.

## 31.6 Deny Dominance

If an action appears in both allow and deny sets, deny wins.

~~~text
D intersect P -> D
~~~

This removes ambiguity from conflict resolution.

## 31.7 Task Containment

Explicit permission cannot silently enlarge the task.

If CREATE_PROFILE is allowed but the declared task contains only SUMMARIZE, CREATE_PROFILE remains denied.

~~~text
PERMISSION != TASK_NECESSITY
~~~

This implements a form of computational data minimization.

## 31.8 Sensitivity Levels

The canonical registry defines:

~~~text
L0 ORDINARY_TRANSFORMATION
L1 CONTEXTUAL_INTERPRETATION
L2 PERSONAL_INFERENCE
L3 SENSITIVE_INFERENCE
L4 PERSISTENT_PROFILING
L5 HIGH_STAKES_DECISION
~~~

Actions at L2 or above require explicit permission.

The current machine-readable registry is:

- spec/cmb.actions.v1.json

## 31.9 Deterministic Evaluation Function

For action R and policy C:

~~~text
if policy.revoked:
    DENY(policy_revoked)

if R in deny:
    DENY(explicit_prohibition)

if R not in action_registry:
    DENY(unknown_action)

if R not in task_actions:
    DENY(not_task_necessary)

if sensitivity(R) >= L2 and R not in allow:
    DENY(explicit_permission_required)

if R in allow:
    ALLOW(explicit_permission)

ALLOW(task_necessary)
~~~

The order is part of the semantics.

## 31.10 Fail-Closed Unknown Actions

Unknown operations are denied because an implementation cannot safely assign an unknown action a sensitivity level.

~~~text
UNKNOWN -> DENY
~~~

A new action must enter the registry before a conforming implementation can authorize it.

## 31.11 Ordinary Task Actions

Ordinary transformations and contextual artifact analysis may proceed when they are explicitly part of the declared task and are not denied.

Examples include:

- SUMMARIZE
- TRANSLATE
- FORMAT
- COMPARE
- EXTRACT_ARGUMENT

This avoids requiring ceremonial permission for every ordinary operation while still enforcing task containment.

## 31.12 Sensitive Human Inference

Examples include:

- INFER_PERSONALITY
- INFER_COGNITIVE_CAPABILITY
- INFER_DIAGNOSIS
- INFER_EMOTIONAL_VULNERABILITY
- CREATE_PROFILE
- LINK_BEHAVIOR_ACROSS_CONTEXTS

These operations require explicit permission in addition to task necessity.

A request to analyze text is not equivalent to permission to infer a person.

## 31.13 Audit Semantics

Each evaluated action can produce a structured audit event containing:

- request ID;
- action;
- ALLOW or DENY;
- reason code;
- policy ID;
- policy version;
- scope;
- UTC timestamp.

An audit event records what the policy evaluator decided.

It does not prove that every surrounding component complied.

~~~text
AUDIT_RECORD != UNIVERSAL_EXECUTION_PROOF
~~~

## 31.14 Policy Schema

The normative machine-readable contract is:

- schemas/cmb.policy-envelope.v1.schema.json

The schema is strict and rejects undeclared properties.

This is intentional. A field such as shadow_profile cannot be silently inserted into a valid policy envelope without failing schema validation.

## 31.15 Audit Schema

Audit records use:

- schemas/cmb.policy-audit.v1.schema.json

The schema fixes decision and reason vocabularies so downstream implementations can compare outcomes deterministically.

## 31.16 Conformance Fixtures

The canonical cross-language fixture is:

- conformance/cmb-policy-v1.json

It tests at least:

1. ordinary task authorization;
2. deny dominance;
3. explicit permission for sensitive inference;
4. sensitive action authorization;
5. task containment;
6. fail-closed unknown actions;
7. revocation.

A future Go, Rust, TypeScript, Java, or other implementation is conformant only if the same fixture produces the same decision and reason codes.

## 31.17 Provenance Separation

The policy layer is deliberately separate from provenance.

~~~text
POLICY      = what is authorized
ENFORCEMENT = what the runtime blocks or permits
PROVENANCE  = evidence about recorded artifacts and history
LAW         = jurisdiction-dependent rights and obligations
~~~

Therefore:

~~~text
POLICY != PROVENANCE
PROVENANCE != TRUTH
SIGNATURE != PERSONHOOD
HASH != AUTHORSHIP
~~~

## 31.18 Relationship to Existing CMB Boundary Evaluation

The existing cmb_provenance.boundary module evaluates coarse facts such as:

- AI disclosure;
- human review availability;
- profile/person confusion;
- prediction/destiny confusion;
- required consent.

The cmb_policy package adds a different layer: authorization of specific machine actions.

The two layers are complementary.

## 31.19 Conformance Properties

A conforming implementation MUST:

- evaluate in the canonical order;
- make explicit denial dominant;
- fail closed for unknown actions;
- deny actions outside the declared task;
- require explicit permission for L2-L5 actions;
- preserve policy scope;
- honor revocation;
- emit stable reason codes;
- distinguish declaration from enforcement.

A conforming implementation MUST NOT claim:

- metadata forces hostile systems to comply;
- hashes prove biological authorship;
- signatures prove truth;
- a machine profile is the person;
- a prediction is an inevitable human outcome.

## 31.20 Core Safety Properties

### Denial Safety

~~~text
action in D -> Execute(action) = false
~~~

for an execution environment controlled by the policy gate.

### Task Containment

~~~text
action not in T -> Authorized(action) = false
~~~

### Sensitive Permission

~~~text
Sensitivity(action) >= L2
and action not in P
-> Authorized(action) = false
~~~

### Revocation

~~~text
revoked(policy) -> Authorized(any action) = false
~~~

### Profile Non-Identity

~~~text
Profile(H) != H
~~~

This final property is normative rather than a Python type-system property. The software can prevent specific profile operations; it cannot mathematically encode the totality of a person.

## 31.21 Falsifiability

The formal model should be reconsidered if experiments show that:

- users consistently misunderstand task and permission boundaries;
- policy setup creates disproportionate cognitive load;
- implementations cannot reproduce fixture outcomes;
- task containment materially harms legitimate functionality;
- sensitive authorization fails to reduce unwanted inference;
- audit records cause users to overestimate actual enforcement.

## 31.22 Canonical Equation

The reference architecture can be summarized as:

~~~text
CMB = Declaration
    + Task Necessity
    + Policy
    + Provenance
    + Enforcement
    + Auditability
~~~

subject to:

~~~text
REPRESENTATION != PERSON
HUMAN_AGENCY > MACHINE_AUTHORITY
~~~

This equation describes a research architecture, not a claim of total control over external platforms.

## 31.23 Closing

The machine may calculate.

The policy engine decides whether a controlled execution point is authorized to perform a declared action.

The human retains the ability to define the task, prohibit operations, revoke policy, correct representations, and contest machine-generated claims.

~~~text
PATTERN != PROOF
PROFILE != PERSON
MODEL != MIND
PREDICTION != DESTINY

DECLARED_POLICY != TECHNICAL_ENFORCEMENT
PROVENANCE != TRUTH
CAPABILITY != AUTHORITY

HUMAN_AGENCY > MACHINE_AUTHORITY
~~~
