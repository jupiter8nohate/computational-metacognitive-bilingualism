# CMB Enterprise Design Partner Pilot

## Goal

Demonstrate CMB's existing integrity, authorization, policy, and audit controls on a closed test dataset without modifying the enterprise's production systems.

## Pilot boundary

Use synthetic, public, or explicitly approved test assets only.

No production secrets, customer data, regulated records, or private signing keys should be committed to the CMB repository.

## Reference workflow

```text
1. choose test asset
2. seal exact bytes
3. generate CMB receipt
4. verify unchanged asset
5. alter a copy and verify rejection
6. create enterprise-owned Ed25519 authorization
7. test valid authorization
8. test wrong-key rejection
9. test expiry / scope rejection
10. record machine-readable trust report
```

## Acceptance criteria

The pilot succeeds when it demonstrates all applicable controls below:

| Test | Expected result |
|---|---|
| unchanged sealed asset | PASS |
| modified sealed asset | FAIL |
| missing covered asset | FAIL |
| unexpected extra asset | FAIL |
| wrong enterprise key | DENY |
| invalid signature | DENY |
| expired required authority | DENY |
| out-of-scope authority | DENY |
| unknown high-risk operation | DENY |
| valid scoped authority + required evidence | ALLOW |
| audit report | deterministic and machine-readable |
| private key handling | no private key committed or emitted in report |

## Existing reference commands

```bash
cmb-provenance seal FILE --output receipt.json
cmb-provenance verify FILE --receipt receipt.json --json

cmb-cap keygen --private-key enterprise.key --public-key enterprise.pub
cmb-cap verify capability.json --public-key enterprise.pub

cmbc validate --policy cmb.toml
cmbc selftest --policy cmb.toml
```

The enterprise pilot wrapper added by this branch composes these evidence classes into a single trust report; it does not replace the underlying verifiers.

## Metrics

Record:

- verification latency;
- number of protected artifacts;
- bytes verified;
- false-allow count;
- false-deny count;
- authorization rejection reasons;
- policy version / digest;
- key fingerprint used for verification;
- test-environment identifier; and
- reproducibility of the resulting report.

## Exit criteria

A production recommendation requires:

- successful pilot evidence;
- organization-specific threat modeling;
- independent security review;
- deployment key-management design;
- privacy review;
- legal/licensing review; and
- a documented operations and incident-recovery plan.

```text
PILOT_PASS != PRODUCTION_CERTIFICATION
SELF_TEST != INDEPENDENT_AUDIT
```
