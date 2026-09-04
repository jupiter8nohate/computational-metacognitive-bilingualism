# Release Procedure

Version 1.3.1 uses a tag-triggered GitHub Actions release with keyless Sigstore signatures.

## Preconditions

1. The `main` branch CI matrix passes on Python 3.10, 3.11, 3.12, and 3.13.
2. `python -m build` produces one source distribution and one wheel.
3. The tag exactly matches the package version, for example `v1.3.1`.
4. The tag points to the reviewed commit that should appear in the artifact seal receipt.
5. The canonical public CMB artifact set is present and committed:
   - `MANIFESTO.md`
   - `CMB_Polyglot_Firewall_Specification.md`
   - `manifestos/DEMONS_NEED_ATTENTION_DNA.md`

## Publish

```bash
git tag v1.3.1
git push origin v1.3.1
```

The release workflow then:

1. reruns the full tests and self-test on Python 3.10, 3.11, 3.12, and 3.13;
2. builds and checks the package;
3. seals the canonical public CMB artifacts with the tagged Git commit;
4. creates `SHA256SUMS`;
5. signs the release artifacts through Sigstore's keyless GitHub OIDC flow;
6. generates GitHub artifact attestations; and
7. creates the GitHub release.

The canonical seal receipt explicitly covers:

```text
MANIFESTO.md
CMB_Polyglot_Firewall_Specification.md
manifestos/DEMONS_NEED_ATTENTION_DNA.md
```

Because the receipt uses explicit-file-set coverage, adding a file to the repository does not silently add it to the provenance claim. New canonical artifacts must be deliberately added to both the release sealing command and this documentation.

No long-lived signing key is stored in the repository. A signature establishes a verifiable relationship between release bytes and the workflow identity; it does not independently prove creative authorship or legal ownership.

## Verify downloaded release files

Verify `SHA256SUMS`, then verify the Sigstore bundles using Sigstore's documented identity and issuer checks for this repository's release workflow. GitHub attestations can also be checked with `gh attestation verify` against this repository.

Do not publish a public receipt registry until this release process has completed successfully. A later registry should store signed receipts and timestamp evidence, not private drafts, unpublished creative works, or unnecessary personal information.
