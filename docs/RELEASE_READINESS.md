# v1.3.1 Release Readiness

The repository contains the signed-release workflow, checksum generation,
canonical artifact sealing, Sigstore signing, and GitHub artifact attestations.

The remaining publication gate is a maintainer tag push after the final reviewed
release commit is selected.

## Before tagging

```bash
git checkout main
git pull --ff-only origin main
pytest
cmb-provenance selftest
```

Confirm GitHub Actions on the selected commit are green, including CI and the
C2PA round trip. Review CodeQL, dependency-review, and Scorecard output where
applicable.

## Publish

```bash
git tag v1.3.1 FINAL_REVIEWED_COMMIT_SHA
git push origin v1.3.1
```

The tag-triggered workflow must then run the Python 3.10–3.13 gate, verify the
package version, build distributions, seal the canonical artifact set, create
`SHA256SUMS`, sign with Sigstore, create GitHub attestations, and publish the
GitHub Release.

Do not describe the release as published until that workflow succeeds and the
release artifacts are visible.
