# CMB Boundary Adapters

These adapters turn the CMB boundary contract into concrete framework integrations.

## Reference implementations

| Language / framework | Path | Contract |
|---|---|---|
| Python | `src/cmb_provenance/boundary.py` | Reference engine |
| TypeScript / Express | `adapters/typescript-express` | Shared v1 conformance |
| Rust / Actix Web | `adapters/rust-actix` | Shared v1 conformance |
| Go / standard library | `adapters/go` | Shared v1 conformance + strict JSON parser |

Every implementation is tested against:

```text
conformance/boundary.v1.cases.json
```

## Architecture

```text
AUTHENTICATED APPLICATION STATE
            │
            ▼
 cmb.boundary-event.v1
            │
    ┌──────┼──────┬──────┐
    ▼      ▼      ▼      ▼
 Python   TS     Rust    Go
    │      │      │      │
    └──────┴──────┼──────┘
            ▼
 SAME CONFORMANCE CASES
            │
            ▼
      HUMAN_FINAL
```

Adapters enforce declared policy facts. They do not infer the facts from arbitrary human expression.

A production deployment should establish how each input fact is authenticated, audited, retained, appealed, and recovered. The middleware is a policy gate, not proof that the upstream facts are true.
