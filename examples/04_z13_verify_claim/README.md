# Example 04 ✦ CMB-Z13 verification

```bash
cmb-z13 validate --file examples/04_z13_verify_claim/statement.cmbz13
cmb-z13 parse --file examples/04_z13_verify_claim/statement.cmbz13
cmb-z13 explain --file examples/04_z13_verify_claim/statement.cmbz13
```

Expected semantic core:

```text
Virgo / Go
PRECISION
VERIFY[claim]
=> EVIDENCE_REQUIRED
authority = HUMAN_FINAL
```
