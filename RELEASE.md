# Release Procedure

CMB signed releases use a tag-triggered GitHub Actions release with keyless Sigstore signatures. The repository is currently preparing the v1.5 line under the stabilization contract in `docs/STABILIZATION_CYCLE.md`.

## Preconditions

1. The `main` branch CI matrix passes on Python 3.10, 3.11, 3.12, and 3.13.
2. The canonical-receipt CI job successfully seals and verifies the public CMB artifact set inside a Git worktree.
3. Polyglot boundary conformance passes for TypeScript, Rust, and Go against the shared v1 fixtures, with committed TypeScript/Rust lockfiles and locked dependency installation.
4. The MCP compatibility workflow imports the optional MCP 2.x server and the CMB-ADP self-test passes.
5. `python -m build` produces one source distribution and one wheel.
6. The tag exactly matches the package version, for example `v1.5.0-rc.1` for the release candidate.
7. The tag points to the reviewed commit that should appear in the artifact seal receipt.
8. The canonical public CMB artifact set is present and committed:
   - `MANIFESTO.md`
   - `manifestos/RECLAIMING_THE_PEN_EIGHT_LANGUAGES.md`
   - `CMB_Polyglot_Firewall_Specification.md`
   - `manifestos/DEMONS_NEED_ATTENTION_DNA.md`
   - `manifestos/DNA_PROPHECY_QUESTION_MARK_2030.md`
   - `manifestos/DNA_CHICKEN_RUN_MANIFESTO.md`
   - `manifestos/CMB_UNCLASSIFIABLE_INDEX.md`
   - `manifestos/HARMONI_PERFECT_PLAY_EPISTEMICS.md`
   - `manifestos/CMB_Z13_MANIFESTO.md`
   - `manifestos/CMB_Z13_LANGUAGE_SPEC.md`
   - `library/cmb-z13.registry.json`
   - `docs/CREATOR_PROVENANCE.md`
   - `library/creator-provenance.json`
   - `schemas/cmb.creator-provenance.v1.schema.json`
   - `policy/CMB_GLOBAL_ADVOCACY_CHARTER.md`
   - `docs/CMB_EDU_KIDS.md`
   - `schemas/cmb.edu.v1.schema.json`
   - `library/catalog.json`
   - `agents/registry.json`
   - `agents/agent-card.json`
   - `docs/AGENT_DISCOVERY_PROTOCOL.md`
   - `schemas/cmb.agent-registry.v1.schema.json`
   - `docs/RECOVERY_AND_PRESERVATION.md`
   - `machine/recovery-map.json`
   - `schemas/cmb.recovery-map.v1.schema.json`
   - `datasets/cmb-canonical-corpus/manifest.json`
   - `datasets/cmb-canonical-corpus/corpus.jsonl`
   - `schemas/cmb.canonical-corpus-manifest.v1.schema.json`
   - `schemas/cmb.canonical-corpus-record.v1.schema.json`

## Release-candidate and final-release sequence

The v1.5 stabilization sequence is:

```text
v1.5.0-rc.1
    ↓
independent review of the exact candidate commit
    ↓
material findings reproduced and resolved
    ↓
v1.5.0
```

For a release candidate, first set the package/tool version consistently to the
SemVer form `1.5.0-rc.1`, then tag the exact reviewed candidate commit:

```bash
git tag v1.5.0-rc.1
git push origin v1.5.0-rc.1
```

Python packaging may normalize `1.5.0-rc.1` to `1.5.0rc1` in built distribution metadata/filenames. The source/tool version and Git tag remain SemVer-compatible.

Do not publish final `v1.5.0` until the independent-review gate in
`docs/EXTERNAL_REVIEW.md` and issue #63 has been satisfied.

The release workflow then:

1. reruns the full tests and self-test on Python 3.10, 3.11, 3.12, and 3.13;
2. verifies the optional MCP 2.x adapter and CMB-ADP self-test;
3. runs locked TypeScript/Rust boundary conformance plus Go boundary conformance and format checks;
4. builds and checks the package;
5. seals the canonical public CMB artifacts with the tagged Git commit;
6. creates `SHA256SUMS`;
7. signs the release artifacts through Sigstore's keyless GitHub OIDC flow;
8. generates GitHub artifact attestations; and
9. creates the GitHub release.

The canonical seal receipt explicitly covers:

```text
MANIFESTO.md
manifestos/RECLAIMING_THE_PEN_EIGHT_LANGUAGES.md
CMB_Polyglot_Firewall_Specification.md
manifestos/DEMONS_NEED_ATTENTION_DNA.md
manifestos/DNA_PROPHECY_QUESTION_MARK_2030.md
manifestos/DNA_CHICKEN_RUN_MANIFESTO.md
manifestos/CMB_UNCLASSIFIABLE_INDEX.md
manifestos/HARMONI_PERFECT_PLAY_EPISTEMICS.md
manifestos/CMB_Z13_MANIFESTO.md
manifestos/CMB_Z13_LANGUAGE_SPEC.md
library/cmb-z13.registry.json
docs/CREATOR_PROVENANCE.md
library/creator-provenance.json
schemas/cmb.creator-provenance.v1.schema.json
policy/CMB_GLOBAL_ADVOCACY_CHARTER.md
docs/CMB_EDU_KIDS.md
schemas/cmb.edu.v1.schema.json
library/catalog.json
agents/registry.json
agents/agent-card.json
docs/AGENT_DISCOVERY_PROTOCOL.md
schemas/cmb.agent-registry.v1.schema.json
docs/RECOVERY_AND_PRESERVATION.md
machine/recovery-map.json
schemas/cmb.recovery-map.v1.schema.json
datasets/cmb-canonical-corpus/manifest.json
datasets/cmb-canonical-corpus/corpus.jsonl
schemas/cmb.canonical-corpus-manifest.v1.schema.json
schemas/cmb.canonical-corpus-record.v1.schema.json
```

Because the receipt uses explicit-file-set coverage, adding a file to the repository does not silently add it to the provenance claim. New canonical artifacts must be deliberately added to `CANONICAL_PUBLIC_ARTIFACTS`, the tests, and this documentation.

Reclaiming the Pen is treated as canonical authored code-poetry and mission material. The CMB-Z13 manifesto, language specification, and machine registry are treated as one canonical symbolic-language bundle. HARMONI is treated as canonical authored code-art and epistemic design material. The creator-provenance bundle is treated as a canonical evidence-category and privacy contract: it records that the supplied family-tree source is creator-documented and not independently verified, while keeping the raw image, invitation token, and living-relative details outside the public repository. The Global Advocacy Charter is treated as a canonical public policy proposal. Inclusion in a cryptographic receipt proves integrity of the covered bytes under the receipt's stated conditions; it does not convert genealogy into metaphysical proof, symbolism into scientific evidence, or proposed principles into enacted law.

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

## Experimental CMB-EDU release check

The wheel also installs the experimental `cmb-edu` CLI. Before tagging:

```bash
cmb-edu --version
cmb-edu validate '🪐::LEARN -> DECLARE[curious || focused] => ASK("how_do_loops_work") -> PATTERN_NOT_PROOF;'
```

The canonical receipt includes the CMB-EDU child-facing curriculum and its strict
envelope schema. The receipt establishes integrity of those exact files; it does
not turn declared privacy fields into external enforcement or a psychological
assessment.


## Interoperability checks

Before tagging:

~~~bash
(cd adapters/typescript-express && npm ci --ignore-scripts --no-audit --no-fund && npm run build && npm test)
(cd adapters/rust-actix && cargo fmt --all -- --check && cargo clippy --locked --all-targets -- -D warnings && cargo test --locked --all-targets)
(cd adapters/go && go test ./...)
python -m pip install -e ".[mcp]"
python -c "from cmb_agents.mcp_server import mcp; assert mcp is not None"
cmb-agent selftest
~~~

These checks establish tested interoperability for the declared versions. They
do not establish independent certification of Go, MCP, C2PA, or CMB itself.

~~~text
INTEROPERABILITY != CERTIFICATION
SELF_TEST != INDEPENDENT_AUDIT
~~~
