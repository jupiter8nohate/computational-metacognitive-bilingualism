# Registry Publishing

The repository contains release workflows for PyPI and npm, but registry-side trusted-publisher configuration must exist before either workflow can publish.

## PyPI

Target project:

```text
cmb-provenance
```

Recommended authentication: PyPI Trusted Publishing with GitHub Actions OIDC.

Configure the PyPI publisher for:

```text
owner: jupiter8nohate
repository: computational-metacognitive-bilingualism
workflow: publish-pypi.yml
environment: pypi
```

Then run **Publish cmb-provenance to PyPI** from GitHub Actions.

The workflow builds the wheel and source distribution, installs the wheel, runs the CLI self-test, passes the build artifacts to a separate publishing job, and publishes through PyPI OIDC.

## npm

Target package:

```text
@cmb-sovereignty/core
```

The npm organization or scope must exist and permit publication by the project owner before the first publish.

Configure an npm Trusted Publisher for:

```text
GitHub owner: jupiter8nohate
repository: computational-metacognitive-bilingualism
workflow: publish-npm.yml
environment: npm
```

Then run **Publish CMB TypeScript core to npm** from GitHub Actions.

The workflow uses a GitHub-hosted runner, Node 24, OIDC, type checking, a production build, and a dry-run package inspection before publication.

## Security boundary

Registry publication proves where a package was built and published when provenance/trusted-publishing features are active. It does not independently prove authorship, originality, legal ownership, or the correctness of every claim inside the package.

```text
PACKAGE_PROVENANCE != AUTHORSHIP_PROOF
SIGNATURE != ORIGINALITY
REGISTRY != LEGAL_JUDGMENT
```
