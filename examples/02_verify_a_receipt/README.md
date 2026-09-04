# Example 02 ✦ verify a receipt

First create the receipt from Example 01:

```bash
cmb-provenance seal \
  examples/01_seal_a_file/artifact.txt \
  --output /tmp/example.cmb-receipt.json
```

Then verify the same explicit file set:

```bash
cmb-provenance verify \
  examples/01_seal_a_file/artifact.txt \
  --receipt /tmp/example.cmb-receipt.json
```

Modify the artifact and verification should fail.

```text
INTEGRITY_FAILURE != AUTHORSHIP_JUDGMENT
```
