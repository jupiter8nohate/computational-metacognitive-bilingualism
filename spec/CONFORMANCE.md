# CMB Policy v1 Conformance

## Canonical Fixture

The machine-readable fixture is:

- conformance/cmb-policy-v1.json

Every language implementation claiming CMB Policy v1 conformance MUST produce the expected decision and reason for every case.

## Required Cases

| Case | Expected result |
|---|---|
| ordinary_task_is_allowed | ALLOW / task_necessary |
| deny_dominates_allow | DENY / explicit_prohibition |
| sensitive_requires_explicit_permission | DENY / explicit_permission_required |
| sensitive_explicit_permission | ALLOW / explicit_permission |
| permission_does_not_expand_task | DENY / not_task_necessary |
| unknown_fails_closed | DENY / unknown_action |
| revocation_denies_execution | DENY / policy_revoked |

## Drift Protection

The Python tests also compare the executable action registry against:

- spec/cmb.actions.v1.json

A registry change therefore requires an intentional update to both executable semantics and the machine-readable contract.

## Required Semantic Order

Conformance is not only about ALLOW or DENY. The reason code is part of the contract.

For example, a revoked policy containing an explicit denial returns policy_revoked because revocation is evaluated first.

## Adding an Action

A new action requires:

1. a canonical uppercase action name;
2. a sensitivity level;
3. a description;
4. an explicit-permission rule derived from sensitivity;
5. an updated machine-readable registry;
6. tests;
7. conformance cases when the new behavior adds a semantic branch.

## Cross-Language Goal

Future Go, Rust, TypeScript, and other reference adapters SHOULD consume the same conformance fixture.

Equivalent input should produce equivalent policy decisions regardless of implementation language.

~~~text
SAME POLICY + SAME ACTION -> SAME DECISION + SAME REASON
~~~

## Non-Claim

Conformance proves agreement with the CMB Policy v1 semantics. It does not prove legal compliance, moral correctness, provider-wide enforcement, or universal AI alignment.
