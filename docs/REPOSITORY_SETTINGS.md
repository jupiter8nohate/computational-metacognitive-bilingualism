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
- connect GitHub to Zenodo and archive a signed release when available.

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

The committed Dependency Review workflow currently degrades cleanly when Dependency Graph is disabled. After enabling the graph, remove `continue-on-error: true` so high-severity dependency changes become a blocking PR check.

## Protect `main`

In **Settings → Branches / Rulesets**, prefer:

- require a pull request before merging;
- require status checks to pass;
- require conversation resolution;
- block force pushes;
- block branch deletion;
- require linear history if it matches the project's squash-merge workflow.

## Release and DOI gate

The repository is prepared for a signed v1.4.0 release, but publishing the GitHub release and enabling Zenodo archival remain account-authorized actions.

```text
COMMITTED_CONFIGURATION != ENABLED_PLATFORM_SETTING
RELEASE_READY != RELEASE_PUBLISHED
DOI_READY != DOI_MINTED
PUBLISHED != INDEXED
```
