# Go CMB Boundary Adapter

This directory is the Go reference implementation of the versioned
`cmb.boundary-event.v1` contract.

## Design

The adapter deliberately uses only the Go standard library.

It provides:

- strict JSON transport parsing;
- rejection of unknown fields;
- rejection of duplicate top-level keys;
- rejection of trailing JSON values;
- schema-version validation;
- deterministic violation ordering;
- the same `HUMAN_FINAL` authority result as the Python, TypeScript, and Rust implementations;
- shared conformance testing against `../../conformance/boundary.v1.cases.json`.

## Run

~~~bash
cd adapters/go
go test ./...
~~~

## Example

~~~go
event := cmbboundary.BoundaryEvent{
    SchemaVersion:         cmbboundary.SchemaVersion,
    AIInvolved:            true,
    AIDisclosed:           true,
    ConsequentialDecision: true,
    HumanReviewAvailable:  true,
}

decision, err := cmbboundary.RequireBoundary(event)
if err != nil {
    return err
}
if !decision.Allowed {
    panic("unreachable")
}
~~~

## Boundary

The Go adapter evaluates explicit application state.

It does not infer identity, diagnosis, mental state, intent, personality, or moral
status from human language.

~~~text
EXPLICIT_FACT != BEHAVIORAL_INFERENCE
PROFILE != PERSON
PREDICTION != DESTINY
HUMAN_AGENCY > MACHINE_AUTHORITY
~~~
