# CMB-CAP example

CMB-CAP credentials contain signatures, timestamps, nonces, and public keys.
This directory intentionally does not commit a private signing key or a
pre-generated credential whose timestamps could become stale.

Generate a local example:

```bash
python -m pip install -e ".[sovereignty]"
cmb-cap keygen --private-key .cmb/demo.key --public-key .cmb/demo.pub
cmb-cap issue-sdl examples/cmb_sdl/research.cmb \
  --private-key .cmb/demo.key \
  --output dist/demo.cmb-cap.json
cmb-cap verify dist/demo.cmb-cap.json --public-key .cmb/demo.pub
```

The embedded public key supports offline signature verification. Pinning the
expected public key adds an external trust decision. Neither mechanism alone
proves legal identity.
