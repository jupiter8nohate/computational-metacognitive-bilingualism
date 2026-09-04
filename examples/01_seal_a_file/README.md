# Example 01 ✦ seal one file

From the repository root:

```bash
cmb-provenance seal \
  examples/01_seal_a_file/artifact.txt \
  --output /tmp/example.cmb-receipt.json
```

The receipt covers exactly that file. It does not silently cover the rest of the repository.
