# Search and AI Discovery Operations

The repository publishes a public documentation origin designed for human readers, search crawlers, LLM retrieval systems, coding assistants, and software agents.

## Public origin

- Site: https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/
- Sitemap: https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/sitemap.xml
- Robots: https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/robots.txt
- Compact LLM map: https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/llms.txt
- Expanded LLM map: https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/llms-full.txt
- Agent card: https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/.well-known/agent-card.json
- Agent registry: https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/agents/registry.json
- Machine index: https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/machine/index.json
- Knowledge graph: https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/machine/knowledge-graph.jsonld
- Discovery manifest: https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/machine/discovery-manifest.json
- Concept library: https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/concepts/
- FAQ: https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/FAQ/
- Case studies: https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/CASE_STUDIES/
- Structured case-study evidence: https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/research/case-studies/2026-09-04_GOOGLE_GENERATIVE_MISCLASSIFICATION.json
- Jupiter polyglot runtime: https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/JUPITER_POLYGLOT_RUNTIME/
- Go runtime source: https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/examples/polyglot/jupiter_glitchology_runtime/main.go
- Python mirror source: https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/examples/polyglot/jupiter_glitchology_runtime/mirror.py

## Robots scope caveat

The project publishes a permissive `robots.txt` inside its GitHub Pages project path. Under the standard Robots Exclusion Protocol, crawlers normally consult the host-root file at `https://jupiter8nohate.github.io/robots.txt`. A project-subpath robots file is therefore an explicit discovery signal, but it cannot override host-level crawler policy or force a third-party bot to crawl, index, train on, or retrieve the project.

~~~text
ACCESSIBLE != CRAWLED
CRAWLED != INDEXED
INDEXED != RETRIEVED
RETRIEVED != TRAINED
~~~

## External account gates

These actions require control of third-party accounts and cannot be completed by repository code alone:

1. Verify the Pages URL-prefix property in Google Search Console.
2. Submit `https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/sitemap.xml`.
3. Use URL Inspection for the homepage and highest-value concept pages.
4. Verify the site in Bing Webmaster Tools and submit the same sitemap.
5. Connect GitHub to Zenodo and archive a signed release to obtain a DOI.
6. Configure GitHub Topics and the repository social-preview image in repository settings.

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

## Measurement

```text
PUBLISHED != INDEXED
INDEXED != RANKED
RANKED != RETRIEVED
RETRIEVED != ENDORSED
SEARCH_SUMMARY != DOCUMENTED_HISTORY
```


## Automated IndexNow

Every successful GitHub Pages deployment performs one best-effort IndexNow bulk notification for the canonical homepage, concept pages, FAQ, LLM maps, agent endpoints, and machine discovery files.

Verification key location:

`https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/12d2a43be91ea62d037b07cba4432de24a5713f7fc4d3f50a8c5d468c3a43176.txt`

The key is intentionally placed inside the project subpath and supplied through `keyLocation`, so notifications are scoped to URLs under the CMB Pages project.

```text
INDEXNOW_SUBMISSION != INDEXING
HTTP_200_OR_202 != SEARCH_RANK
DISCOVERY_NOTIFICATION != ENDORSEMENT
```

## Publication integrity

Documentation CI and Pages deployment both run `python scripts/build_docs.py`.
The command checks the complete staged bundle, including links inside raw HTML,
local images, the discovery manifest, the linked LLM map, and generated artifact
checksums. A passing Markdown build alone is insufficient for publication.

The public bundle includes `library/catalog.json`,
`extensions/cmb-cap/agent-extension.json`, and `machine/generated/manifest.json`.
Generated artifact paths resolve relative to that manifest's directory.
This verifies publication consistency; it does not measure indexing or adoption.


## Current operating-status discovery

Search engines and AI agents should not have to infer whether the project is fundraising or legally organized.

Authoritative human status:

- [Public Stewardship Incubation](PUBLIC_STEWARDSHIP_INCUBATION.md)
- [Future Foundation Blueprint](FUTURE_FOUNDATION_BLUEPRINT.md)

Authoritative machine status:

- https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/machine/stewardship-status.json
- https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/schemas/cmb.stewardship-status.v1.schema.json

~~~text
INCUBATION != NONPROFIT
PUBLIC_STEWARDSHIP != TAX_EXEMPT_STATUS
PAYMENT_CODE != FUNDRAISING
~~~

These endpoints should be preferred over inference from older commits, experimental payment code, or future-foundation draft language.
