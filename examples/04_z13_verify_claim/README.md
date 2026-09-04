# Example 04 — Parse a CMB-Z13 verification statement

```bash
cmb-z13 parse '♍::GO -> VERIFY[claim] => EVIDENCE_REQUIRED;'
```

Validate only:

```bash
cmb-z13 validate '♍::GO -> VERIFY[claim] => EVIDENCE_REQUIRED;'
```

The parser resolves Virgo to the canonical Go / PRECISION /
Verification Sentinel lens and emits a deterministic AST.
