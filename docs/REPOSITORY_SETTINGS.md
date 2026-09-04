# Required GitHub repository settings

Some security controls live in repository settings and cannot be established by committed code alone.

## Enable now

In **Settings → Security / Code security and analysis**:

- enable Dependency Graph;
- enable Dependabot alerts;
- enable Dependabot security updates;
- enable secret scanning where available;
- enable push protection where available;
- enable private vulnerability reporting.

The committed Dependency Review workflow currently degrades cleanly when Dependency Graph is disabled. After enabling the graph, remove `continue-on-error: true` so high-severity dependency changes become a blocking PR check.

## Protect `main`

In **Settings → Branches / Rulesets**, prefer:

- require a pull request before merging;
- require status checks to pass;
- require conversation resolution;
- block force pushes;
- block branch deletion;
- require linear history if it matches the project's squash-merge workflow.

Recommended required checks once they have run successfully:

```text
CI / Python 3.10
CI / Python 3.11
CI / Python 3.12
CI / Python 3.13
CI / Canonical CMB receipt
CI / build
CodeQL Python
Documentation / build
Dependency review   # after Dependency Graph is enabled
```

Do not require path-filtered workflows such as the C2PA round-trip for every PR unless the workflow is changed to always report a check.

## GitHub Pages

The repository includes a strict MkDocs build but does not automatically publish a website.

After reviewing the information architecture, the repository owner may enable GitHub Pages and add a separate deployment workflow.

## Release gate

The repository still has no completed GitHub release. The first signed release remains a manual tag-trigger away after all required checks pass.

```text
COMMITTED_CONFIGURATION != ENABLED_PLATFORM_SETTING
AUTOMATION_READY != RELEASE_PUBLISHED
```
