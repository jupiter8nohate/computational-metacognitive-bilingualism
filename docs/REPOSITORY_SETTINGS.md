# Required GitHub repository settings

Some controls live in GitHub or external service settings and cannot be established by committed code alone.

## GitHub Pages

GitHub Pages is deployed automatically from `.github/workflows/pages.yml`.

Canonical public site:

https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/

The deployment publishes documentation plus machine-facing discovery assets, schemas, specifications, agent metadata, `llms.txt`, the knowledge graph, and the discovery manifest.

## Search and AI discovery settings

Repository code now supplies the crawlable site, sitemap, robots file, canonical concept pages, JSON-LD, FAQ, retrieval glossary, agent card, knowledge graph, and machine discovery manifest.

Account-level actions still required:

- verify the Pages URL-prefix property in Google Search Console;
- submit `https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/sitemap.xml`;
- inspect/request indexing for the homepage and highest-value concept URLs;
- verify the site in Bing Webmaster Tools and submit the same sitemap;
- configure repository Topics;
- upload the repository social-preview image;
- connect GitHub to Zenodo and archive the chosen signed release (v1.4.1 is already published) when DOI archival is desired.

See [Search and AI Discovery Operations](SEARCH_DISCOVERY.md).

## Recommended GitHub Topics

```text
artificial-intelligence
ai-ethics
digital-rights
human-agency
metacognition
cognitive-sovereignty
provenance
content-authenticity
c2pa
cryptography
neurodiversity
computational-literacy
ai-agents
mcp
python
rust
golang
digital-identity
ai-safety
human-computer-interaction
```

## Security controls

In **Settings → Security / Code security and analysis**:

- enable Dependency Graph;
- enable Dependabot alerts;
- enable Dependabot security updates;
- enable secret scanning where available;
- enable push protection where available;
- enable private vulnerability reporting.

The Dependency Review workflow uses GitHub Dependency Review when the Dependency Graph is available. Its fallback runs strict Python and lockfile vulnerability scans. The active ruleset requires the `dependency-review` check.

## Protect `main`

GitHub reported `main` protected by the active [Protect main ruleset](https://github.com/jupiter8nohate/computational-metacognitive-bilingualism/rules/22362595) on November 5, 2026. The ruleset requires pull requests, squash merges, linear history, resolved review threads, and up-to-date passing checks. It blocks force pushes and deletion.

The required checks are Python 3.10 through 3.13, Canonical CMB receipt, CMB SRP-2, CodeQL Python, and dependency review. The ruleset requires zero approving reviews. The separate independent-review gate for the final v1.5 release is tracked in [issue #63](https://github.com/jupiter8nohate/computational-metacognitive-bilingualism/issues/63).

## Release and DOI gate

Signed releases are operational; v1.4.1 is published with release artifacts, checksums, a CMB source receipt, and Sigstore bundles. Zenodo archival and DOI minting remain external account-authorized actions.

```text
COMMITTED_CONFIGURATION != ENABLED_PLATFORM_SETTING
PUBLISHED_RELEASE != CURRENT_MAIN
SIGNED_RELEASE_PUBLISHED != DOI_MINTED
PUBLISHED != INDEXED
```
