# Example 02 — Verify one receipt

After running Example 01:

```bash
cmb-provenance verify example.txt \
  --receipt example.cmb-receipt.json
```

Changing the file's bytes should cause verification to fail.
