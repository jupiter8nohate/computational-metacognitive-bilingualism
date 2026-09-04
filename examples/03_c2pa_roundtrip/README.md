# Example 03 — C2PA interoperability

The repository's `.github/workflows/c2pa-integration.yml` performs the real integration test.

It:

1. installs a pinned, checksummed c2patool;
2. generates deterministic test media;
3. builds a CMB C2PA manifest definition;
4. lets c2patool sign and bind the manifest;
5. reads the signed asset with generic c2patool;
6. verifies the exact CMB payload survived.

Local manifest-definition example:

```bash
cmb-provenance build-c2pa-manifest \
  --receipt tests/fixtures/c2pa_receipt.json \
  --assertion-label com.yourdomain.cmb_provenance \
  --output /tmp/cmb-c2pa-manifest.json
```

A production assertion label must use a domain namespace actually controlled by the asserting entity.
