# Example 01 — Seal one file

```bash
printf 'human-authored example\n' > example.txt
cmb-provenance seal example.txt --output example.cmb-receipt.json
```

The receipt covers exactly `example.txt`. It supports byte-integrity and
provenance evidence; it does not automatically prove legal authorship.
