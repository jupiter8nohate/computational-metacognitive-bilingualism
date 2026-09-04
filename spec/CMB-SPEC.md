# CMB Policy Specification v1.0

## Status

Experimental normative specification for the cmb_policy reference implementation.

## 1. Purpose

CMB Policy v1 defines deterministic authorization semantics for machine actions performed within a declared human task.

The policy layer is distinct from provenance, legal enforceability, and platform-wide guarantees.

~~~text
DECLARATION != ENFORCEMENT
PROVENANCE != TRUTH
CAPABILITY != AUTHORITY
~~~

## 2. Normative Vocabulary

The terms MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY describe conformance expectations.

## 3. Policy Envelope

A valid policy envelope MUST conform to:

- schemas/cmb.policy-envelope.v1.schema.json

Required fields:

- schema;
- policy_id;
- version;
- scope;
- task_actions;
- allow;
- deny;
- revoked.

The default application scope SHOULD be THIS_REQUEST.

## 4. Action Registry

Implementations MUST assign supported actions the same sensitivity semantics as:

- spec/cmb.actions.v1.json

Sensitivity levels are:

- L0 ordinary transformation;
- L1 contextual interpretation;
- L2 personal inference;
- L3 sensitive inference;
- L4 persistent profiling;
- L5 high-stakes decision.

L2 through L5 MUST require explicit permission.

## 5. Evaluation Order

A conforming evaluator MUST process an action in this order:

1. If the policy is revoked, DENY with policy_revoked.
2. If the action is explicitly denied, DENY with explicit_prohibition.
3. If the action is unknown, DENY with unknown_action.
4. If the action is outside task_actions, DENY with not_task_necessary.
5. If the action is L2-L5 and lacks explicit allow, DENY with explicit_permission_required.
6. If the action is explicitly allowed, ALLOW with explicit_permission.
7. Otherwise, for a known L0-L1 task action, ALLOW with task_necessary.

Order is normative because it determines the stable reason code.

## 6. Conflict Rule

DENY MUST dominate ALLOW when the same action appears in both sets.

## 7. Task Containment

An explicit permission MUST NOT enlarge the declared task.

~~~text
ALLOW[CREATE_PROFILE] + TASK[SUMMARIZE]
-> CREATE_PROFILE DENIED
~~~

## 8. Unknown Actions

Unknown actions MUST fail closed.

A new operation MUST be registered before it can be authorized by a conforming implementation.

## 9. Revocation

A revoked policy MUST deny all evaluated actions.

Historical permission MUST NOT be interpreted as future authorization.

## 10. Audit Events

Implementations MAY emit an audit event conforming to:

- schemas/cmb.policy-audit.v1.schema.json

An audit event represents the policy evaluator's decision. It MUST NOT be described as proof that an external provider or hostile system complied.

## 11. Conformance

Implementations MUST pass the canonical fixture:

- conformance/cmb-policy-v1.json

See [CONFORMANCE.md](CONFORMANCE.md).

## 12. Reference API

~~~python
from cmb_policy import PolicyEnvelope, evaluate_action

policy = PolicyEnvelope.from_dict({
    "policy_id": "example-1",
    "task_actions": ["SUMMARIZE"],
    "allow": [],
    "deny": ["CREATE_PROFILE"],
})

decision = evaluate_action("SUMMARIZE", policy)
assert decision.allowed
~~~

Sensitive operation example:

~~~python
policy = PolicyEnvelope.from_dict({
    "policy_id": "example-2",
    "task_actions": ["INFER_DIAGNOSIS"],
    "allow": [],
    "deny": [],
})

decision = evaluate_action("INFER_DIAGNOSIS", policy)
assert not decision.allowed
assert decision.reason.value == "explicit_permission_required"
~~~

## 13. Security Boundary

The reference engine can enforce policy only when it controls the execution point.

A platform that ignores the evaluator is outside the technical enforcement boundary.

~~~text
METADATA != FIREWALL
POLICY_FILE != UNIVERSAL_CONTROL
~~~

## 14. Core Principle

~~~text
PATTERN != PROOF
PROFILE != PERSON
MODEL != MIND
PREDICTION != DESTINY
CAPABILITY != AUTHORITY

HUMAN_AGENCY > MACHINE_AUTHORITY
~~~
