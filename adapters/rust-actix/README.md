# CMB Boundary Adapter - Rust + Actix Web

This crate implements the same `cmb.boundary-event.v1` policy semantics as the Python reference engine and the TypeScript adapter.

## Test

```bash
cargo test
```

The test suite compiles the shared repository fixture directly into the test binary:

```text
../../conformance/boundary.v1.cases.json
```

## Run

```bash
cargo run
```

POST a complete boundary event to:

```text
http://127.0.0.1:8000/cmb/boundary/v1
```

Responses:

- `200` - boundary allowed;
- `422` - valid event rejected by CMB policy;
- `400` - supported JSON shape but invalid semantic fields;
- malformed JSON or unknown fields are rejected by Actix/Serde before the handler.

## Design boundary

The Rust types use `deny_unknown_fields` so v1 cannot silently accept policy fields the implementation does not understand.

The adapter does not infer facts about a person. Production services must derive policy facts from authenticated, auditable application state.

Before publishing this crate independently, commit and review a generated `Cargo.lock` for deployment reproducibility.
