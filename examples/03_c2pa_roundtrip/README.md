# Example 03 — C2PA round trip

The repository's CI performs this test flow:

```text
CMB receipt
  -> deterministic CMB payload
  -> C2PA manifest definition
  -> external c2patool signs/binds a test PNG
  -> generic c2patool reads the asset
  -> CI verifies the exact CMB payload survived
```

Relevant files:

- `.github/workflows/c2pa-integration.yml`
- `scripts/make_c2pa_test_png.py`
- `scripts/verify_c2pa_roundtrip.py`
- `docs/C2PA_INTEROPERABILITY.md`

This is interoperability evidence, not formal C2PA conformance.
