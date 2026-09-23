# CMB Global AI Watch

<div class="cmb-watch-hero">
<div class="cmb-kicker">CMB://GLOBAL_AI_WATCH // OPEN NEWS EVIDENCE LEDGER</div>

CMB Global AI Watch is an experimental public-interest monitoring surface that discovers current reporting about consequential AI systems and maps each headline to the CMB authority boundary.

It is **not** a replacement for GDELT, Dataminr, Meltwater, Nexis, the Internet Archive, or professional journalism. It combines open discovery, transparent rule-based classification, direct source links, archive lookup, and machine-readable output so CMB claims can be tested against current events instead of remaining purely theoretical.
</div>

~~~text
                   AI MODEL
                     |
        +------------+------------+
        v            v            v
     PREDICT       GENERATE      ACT
        |            |            |
        v            v            v
 INTELLIGENCE     DEEPFAKES     AGENTS
 CYBER TARGETS    FAKE VOICES   TRANSACTIONS
 PROFILES         FAKE IMAGES    CYBER ACTIONS
        |            |            |
        +------------+------------+
                     v
                HUMAN SYSTEMS
                     |
                     v
          +--------------------+
          | AUTHORITY BOUNDARY |
          +--------------------+
                     |
                CMB LIVES HERE
                     |
                     v
       EVIDENCE -> VERIFY -> JUDGE
              -> CONSENT -> ACT
~~~

## What this page does

| Capability | CMB implementation | Boundary |
| --- | --- | --- |
| Global discovery | GDELT DOC 2.0 article metadata | <code>DISCOVERY != CONFIRMATION</code> |
| Rapid refresh | Browser live query plus scheduled Pages refresh | <code>FRESH != VERIFIED</code> |
| Story grouping | Deterministic headline-similarity clusters | <code>HEADLINE_SIMILARITY != FACT_CORROBORATION</code> |
| Monitoring filters | Boundary, sector, keyword, source, and country filters | <code>FILTER != FINDING</code> |
| Archive lookup | Direct Wayback Machine history link for every source URL | <code>ARCHIVED != TRUE</code> |
| CMB mapping | Explicit keyword rules map stories to PREDICT / GENERATE / ACT | <code>CMB_TAG != SOURCE_ENDORSEMENT</code> |
| Machine access | Public JSON snapshot and JSON Schema | <code>STRUCTURED != PROVEN</code> |
| Source preservation | Original publisher URL is always retained | <code>SUMMARY != SOURCE</code> |

## Live evidence surface

The static cards below are generated during deployment. When JavaScript is available, the browser also attempts a newer GDELT query and replaces the cards with the latest classified results. The browser cache is intentionally short.

<!-- CMB_GLOBAL_AI_WATCH_GENERATED_START -->

<div id="cmb-watch-status" class="cmb-watch-status">SEED SNAPSHOT // waiting for first GDELT refresh</div>

<div class="cmb-watch-metrics">
<div><strong>0</strong><span>classified stories</span></div>
<div><strong>0</strong><span>source domains</span></div>
<div><strong>0</strong><span>source countries</span></div>
<div><strong>0</strong><span>headline clusters</span></div>
</div>

<div class="cmb-watch-controls">
<label>Search <input id="cmb-watch-search" type="search" placeholder="keyword, outlet, country"></label>
<label>Boundary
<select id="cmb-watch-boundary">
<option value="">All</option>
<option value="PREDICT">Predict</option>
<option value="GENERATE">Generate</option>
<option value="ACT">Act</option>
</select>
</label>
<label>Sector
<select id="cmb-watch-sector">
<option value="">All</option>
<option value="military_security">Military / Security</option>
<option value="elections_information">Elections / Information</option>
<option value="cybercrime">Cybercrime</option>
<option value="finance">Finance</option>
<option value="justice_policing">Justice / Policing</option>
<option value="children_wellbeing">Children / Wellbeing</option>
<option value="workplace_civil_rights">Workplace / Civil Rights</option>
<option value="privacy_surveillance">Privacy / Surveillance</option>
<option value="healthcare">Healthcare</option>
<option value="general">General</option>
</select>
</label>
<button id="cmb-watch-refresh" type="button">Refresh from GDELT</button>
</div>

<div id="cmb-news-grid" class="cmb-news-grid">
<div class="cmb-watch-empty">The deployment collector or browser live query will populate current stories from GDELT.</div>
</div>

<!-- CMB_GLOBAL_AI_WATCH_GENERATED_END -->

## CMB interpretation layer

The monitor does not ask whether a story is "good for CMB." It asks which human-machine boundary the reported system touches.

~~~text
PREDICT:
PATTERN != PROOF
PROFILE != PERSON
PREDICTION != DESTINY

GENERATE:
MODEL != MIND
SIMULATION != SOURCE
GENERATED != VERIFIED

ACT:
RECOMMENDATION != AUTHORIZATION
CAPABILITY != AUTHORITY
HUMAN_AGENCY > MACHINE_AUTHORITY
~~~

A story can map to more than one boundary. For example, an AI intelligence system can **predict**, a generative system can produce the report, and an agent or institution can **act** on it. The highest-risk architecture is therefore often a chain rather than a single model.

~~~text
MACHINE_OUTPUT
    |
    v
INSTITUTIONAL_DOCUMENT
    |
    v
HUMAN TRUST
    |
    v
AUTHORIZATION
    |
    v
REAL-WORLD CONSEQUENCE
~~~

## Source and evidence rules

1. **GDELT is the discovery layer.** The collector uses the public GDELT DOC 2.0 API and keeps the publisher URL returned by GDELT.
2. **Publishers remain the evidence layer.** Readers should open the original story before relying on any factual claim.
3. **Wayback is an archival lookup layer.** Each result includes a history link. The CMB site does not claim that an archive capture exists merely because the history link is present.
4. **No article bodies are copied.** The watch stores headline and source metadata, not republished journalism.
5. **CMB classification is local interpretation.** A CMB label does not mean the publisher, GDELT, or Internet Archive endorses CMB.
6. **Clusters are not corroboration.** Similar headlines can derive from the same wire story, press release, or copied report.

~~~text
NEWS_REPORT != VERIFIED_FACT
MULTIPLE_HEADLINES != INDEPENDENT_CONFIRMATION
CMB_INTERPRETATION != SOURCE_CLAIM
PATTERN != PROOF
~~~

## Public machine endpoints

- [Current machine-readable snapshot](https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/machine/global-ai-watch.json)
- [Watch configuration and deterministic classification rules](https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/machine/global-ai-watch-config.json)
- [JSON Schema](https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/schemas/cmb.global-ai-watch.v1.schema.json)

## External systems and integration boundary

**Actually integrated:** [GDELT Project](https://www.gdeltproject.org/) for open global news discovery.

**Linked for verification:** [Internet Archive Wayback Machine](https://web.archive.org/) for per-URL archive-history lookup.

**Functional reference points, not integrated data sources:** [Dataminr for News](https://www.dataminr.com/products/dataminr-for-news/), [Meltwater Media Monitoring](https://www.meltwater.com/en/products/media-monitoring), and Nexis Newsdesk. Their licensed feeds, proprietary ranking systems, private APIs, and commercial datasets are not copied or represented as part of CMB.

The open-source objective is narrower:

~~~text
DISCOVER
    -> STRUCTURE
    -> TRACE_SOURCE
    -> CLASSIFY_BOUNDARY
    -> CLUSTER
    -> VERIFY
    -> HUMAN_JUDGMENT
~~~

## Refresh model

The canonical GitHub Pages deployment attempts a fresh GDELT snapshot on every documentation deployment and on a scheduled cadence. GitHub Actions scheduling is best-effort, so the target interval is not a real-time guarantee. In the browser, a user can request a fresh GDELT view without waiting for the next deployment.

The underlying GDELT datasets update on their own cadence. CMB Global AI Watch does not control GDELT availability, indexing coverage, source selection, translation, or upstream corrections.

~~~text
UPDATE_INTERVAL != EVENT_TIME
GDELT_COVERAGE != ALL_NEWS
MISSING_RESULT != MISSING_EVENT
FRESHNESS != ACCURACY
~~~

## Stabilization boundary

This is an **experimental research/documentation surface**, not a new authority-bearing CMB core subsystem. It does not alter provenance cryptography, capability credentials, policy enforcement, or the frozen v1.5 release-candidate semantics.

Its function is evidentiary:

~~~text
CURRENT_EVENT
    -> SOURCE
    -> MACHINE-READABLE RECORD
    -> CMB BOUNDARY
    -> HUMAN VERIFICATION
~~~
