# CMB protocol versioning

## Goal

Version identifiers are semantic contracts, not decoration.

~~~text
SAME_VERSION -> SAME_REQUIRED_MEANING
NEW_REQUIRED_MEANING -> NEW_VERSION
~~~

## Compatibility classes

### Patch

A patch MAY:

- correct documentation without changing required behavior;
- add tests for behavior already required;
- improve diagnostics while preserving stable machine-readable codes;
- harden implementations without changing accepted semantic inputs.

A patch MUST NOT change required outcomes for an existing valid fixture.

### Minor

A minor version MAY add optional, backwards-compatible fields or capabilities.

Older implementations MUST be able to ignore those additions when the
underlying format explicitly permits extensibility.

A minor version MUST NOT silently make an optional field required.

### Major / contract generation

A new major or contract generation is REQUIRED when a change:

- changes the meaning of an existing field;
- changes deterministic decision order;
- changes stable rejection codes;
- changes an invariant's normative interpretation;
- makes previously valid data invalid without an explicit migration contract;
- makes previously rejected behavior conformant.

## Schema identifiers

Published schema/version identifiers MUST be immutable in meaning.

For example:

~~~text
cmb.boundary-event.v1
cmb.policy-envelope.v1
cmb.agent-registry.v1
~~~

A corrected replacement with different semantics MUST receive a new identifier.

## Cross-language rule

Reference implementations in different languages MUST consume the same
language-neutral fixtures where practical.

~~~text
SAME_INPUT
  -> SAME_CONTRACT_VERSION
  -> SAME_REQUIRED_DECISION
  -> SAME_STABLE_CODES
~~~

Language-specific error text MAY differ unless explicitly made normative.

## Experimental protocols

Experimental status permits evolution. It does not permit silent reinterpretation.

When an experimental contract changes incompatibly:

1. publish a new version;
2. preserve old fixtures;
3. document migration;
4. update reference implementations;
5. keep old historical artifacts interpretable.

## External standards

When CMB integrates with an external standard, CMB MUST state the exact tested
standard or SDK generation when material.

~~~text
INTEGRATION != CONFORMANCE
SDK_USAGE != CERTIFICATION
~~~
