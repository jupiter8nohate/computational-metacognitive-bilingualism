# Release Procedure

Version 1.3.1 uses a tag-triggered GitHub Actions release with keyless Sigstore signatures.

## Preconditions

1. The `main` branch CI matrix passes on Python 3.10, 3.11, 3.12, and 3.13.
2. The canonical-receipt CI job successfully seals and verifies the public CMB artifact set inside a Git worktree.
3. `python -m build` produces one source distribution and one wheel.
4. The tag exactly matches the package version, for example `v1.3.1`.
5. The tag points to the reviewed commit that should appear in the artifact seal receipt.
6. The canonical public CMB artifact set is present and committed:
   - `MANIFESTO.md`
   - `CMB_Polyglot_Firewall_Specification.md`
   - `manifestos/DEMONS_NEED_ATTENTION_DNA.md`
   - `manifestos/DNA_CHICKEN_RUN_MANIFESTO.md`
   - `manifestos/CMB_UNCLASSIFIABLE_INDEX.md`
   - `manifestos/CMB_Z13_MANIFESTO.md`
   - `manifestos/CMB_Z13_LANGUAGE_SPEC.md`
   - `library/cmb-z13.registry.json`
   - `policy/CMB_GLOBAL_ADVOCACY_CHARTER.md`
   - `library/catalog.json`

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
manifestos/DNA_CHICKEN_RUN_MANIFESTO.md
manifestos/CMB_UNCLASSIFIABLE_INDEX.md
manifestos/CMB_Z13_MANIFESTO.md
manifestos/CMB_Z13_LANGUAGE_SPEC.md
library/cmb-z13.registry.json
policy/CMB_GLOBAL_ADVOCACY_CHARTER.md
library/catalog.json
```

Because the receipt uses explicit-file-set coverage, adding a file to the repository does not silently add it to the provenance claim. New canonical artifacts must be deliberately added to `CANONICAL_PUBLIC_ARTIFACTS`, the tests, and this documentation.

The CMB-Z13 manifesto, language specification, and machine registry are treated as one canonical symbolic-language bundle. The Global Advocacy Charter is treated as a canonical public policy proposal. Its inclusion in a cryptographic receipt proves integrity of the covered bytes under the receipt's stated conditions; it does not transform proposed principles into enacted law or independently establish legal rights.

No long-lived signing key is stored in the repository. A signature establishes a verifiable relationship between release bytes and the workflow identity; it does not independently prove creative authorship or legal ownership.

## Verify downloaded release files

Verify `SHA256SUMS`, then verify the Sigstore bundles using Sigstore's documented identity and issuer checks for this repository's release workflow. GitHub attestations can also be checked with `gh attestation verify` against this repository.

Do not publish a public receipt registry until this release process has completed successfully. A later registry should store signed receipts and timestamp evidence, not private drafts, unpublished creative works, or unnecessary personal information.


## Experimental CMB-Z13 release check

The wheel also installs the experimental `cmb-z13` reference CLI. Before tagging:

```bash
cmb-z13 --version
cmb-z13 validate '♍::GO -> VERIFY[claim] => EVIDENCE_REQUIRED;'
```

This confirms packaging and canonical mapping behavior; it does not promote CMB-Z13 to a stable compatibility promise.
