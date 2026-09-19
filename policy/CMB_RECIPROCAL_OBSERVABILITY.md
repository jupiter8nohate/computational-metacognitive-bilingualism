# CMB Reciprocal Observability

## Status

Proposed policy layer for the World Retina living-book branch.

## Principle

Traditional surveillance concentrates visibility in the observer. Reciprocal observability requires the observer's purpose, data use, model, inference, retention, and authority to become inspectable and challengeable.

~~~text
SURVEILLANCE:
OBSERVER -> SUBJECT

RECIPROCAL_OBSERVABILITY:
HUMAN <-> SYSTEM <-> INSTITUTION
~~~

## Required properties

A system operating under this proposal SHOULD expose:

1. declared observation purpose;
2. sensor or source provenance;
3. data categories collected;
4. transformation and model-version history;
5. uncertainty and known limitations;
6. retention and deletion rules;
7. secondary-use policy;
8. human appeal or correction route;
9. authorization boundary for consequential action; and
10. an audit trail sufficient to reconstruct material decisions.

## Human-derived signals

Human gaze, retinal imagery, biometric-adjacent measurements, and other person-derived visual signals require a separate trust domain.

~~~text
CONSENT_TO_COLLECT != CONSENT_TO_REPURPOSE
OBSERVATION != IDENTITY
CORRELATION != CHARACTER
PROFILE != PERSON
~~~

## Surveillance classes

### Protective observability

Target: threats to humans and systems.

### Planetary observability

Target: environmental and infrastructure systems.

### Institutional observability

Target: organizations, automated systems, public processes, and consequential models.

### Consensual personal observation

Target: bounded human-provided signals for explicit purposes.

## Invalid shortcut

~~~text
ANOMALY
  -> HOSTILITY
  -> FORCE
~~~

is not a valid CMB reasoning chain.

The bounded chain is:

~~~text
ANOMALY
  -> MULTIPLE_HYPOTHESES
  -> SOURCE_VERIFICATION
  -> COUNTEREVIDENCE
  -> UNCERTAINTY
  -> AUTHORIZED_HUMAN_DECISION
  -> BOUNDED_ACTION
~~~

## Eye and hand separation

~~~text
SENSOR != EFFECTOR
MODEL != AUTHORITY
RECOMMENDATION != AUTHORIZATION
LEARNING_AUTHORITY != ACTION_AUTHORITY
~~~

## Invariants

~~~text
PATTERN != PROOF
PROFILE != PERSON
MODEL != MIND
PREDICTION != DESTINY
OBSERVATION != UNDERSTANDING
MEMORY != TRUTH
CAPABILITY != AUTHORITY
HUMAN_AGENCY > MACHINE_AUTHORITY
~~~
