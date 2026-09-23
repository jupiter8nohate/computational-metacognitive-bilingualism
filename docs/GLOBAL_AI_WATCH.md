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
| Bounded refresh | Scheduled metadata scan; static outbound links only | <code>FRESH != VERIFIED</code> |
| Story grouping | Deterministic headline-similarity clusters | <code>HEADLINE_SIMILARITY != FACT_CORROBORATION</code> |
| Publication budget | At most a small, diverse set of links per build | <code>MORE_DATA != MORE_TRUTH</code> |
| CMB mapping | Explicit keyword rules map stories to PREDICT / GENERATE / ACT | <code>CMB_TAG != SOURCE_ENDORSEMENT</code> |
| Machine access | Public JSON snapshot and JSON Schema | <code>STRUCTURED != PROVEN</code> |
| Source preservation | Original publisher URL is always retained | <code>SUMMARY != SOURCE</code> |

## Current link ledger

The deployment scans a bounded GDELT metadata sample, applies CMB classification and deduplication in memory, then publishes only a small set of outbound links. The browser does not fetch GDELT directly and the repository does not store article bodies, excerpts, images, or mirrored copies.

<!-- CMB_GLOBAL_AI_WATCH_GENERATED_START -->

<div id="cmb-watch-status" class="cmb-watch-status">CURATED TEST LEDGER // 10 verified outbound links // no article bodies stored</div>

<ul class="cmb-news-links">
<li><a href="https://keyt.com/politics/cnn-us-politics/2026/09/18/exclusive-us-military-had-close-call-after-using-ai-for-false-intelligence-report-sources-say/" rel="noopener noreferrer">Exclusive: US military had close call after using AI for false intelligence report, sources say</a> <small>CNN via KEYT News Channel 3-12 · 2026-09-18 · PREDICT + ACT</small></li>
<li><a href="https://www.reuters.com/legal/litigation/banks-warn-ai-shopping-bots-raise-scam-fraud-data-privacy-risks-2026-09-22/" rel="noopener noreferrer">Banks warn AI shopping bots raise scam, fraud and data-privacy risks</a> <small>Reuters · 2026-09-22 · ACT</small></li>
<li><a href="https://apnews.com/article/089e75b95bc935af092da7b79d92706d" rel="noopener noreferrer">OpenAI flags concerning new AI behavior and vows to track it more closely</a> <small>Associated Press · 2026-09-17 · ACT + GENERATE</small></li>
<li><a href="https://www.reuters.com/legal/litigation/ex-google-safety-chief-warns-ai-could-harm-children-more-than-social-media-did-2026-09-22/" rel="noopener noreferrer">Ex-Google safety chief warns AI could harm children more than social media did</a> <small>Reuters · 2026-09-22 · GENERATE</small></li>
<li><a href="https://www.interpol.int/en/News-and-Events/News/2026/INTERPOL-report-finds-AI-linked-to-more-than-half-of-cybercrime-in-Africa" rel="noopener noreferrer">INTERPOL report finds AI linked to more than half of cybercrime in Africa</a> <small>INTERPOL · 2026-08-03 · GENERATE + ACT</small></li>
<li><a href="https://www.abc.net.au/news/2026-09-09/foreign-ai-network-deepfaking-australian-politicians/107129044" rel="noopener noreferrer">Foreign 'AI slopaganda' network targets Australian politicians with deepfakes</a> <small>ABC News Australia · 2026-09-09 · GENERATE</small></li>
<li><a href="https://www.reuters.com/legal/government/us-judiciary-developing-new-guidance-courts-use-ai-2026-09-17/" rel="noopener noreferrer">US judiciary developing new guidance on courts' use of AI</a> <small>Reuters · 2026-09-17 · GENERATE + ACT</small></li>
<li><a href="https://www.reuters.com/business/media-telecom/smart-glasses-ai-pins-privacy-fears-challenge-techs-next-big-bet-2026-09-22/" rel="noopener noreferrer">From smart glasses to AI pins, privacy fears challenge tech's next big bet</a> <small>Reuters · 2026-09-22 · PREDICT</small></li>
<li><a href="https://www.reuters.com/legal/litigation/chinas-huawei-forecasts-billions-agents-will-dominate-ai-traffic-by-2035-2026-09-16/" rel="noopener noreferrer">China's Huawei forecasts billions of agents will dominate AI traffic by 2035</a> <small>Reuters · 2026-09-16 · ACT</small></li>
<li><a href="https://www.interpol.int/en/News-and-Events/News/2026/Counter-terrorism-operation-leverages-artificial-intelligence-to-identify-126-terrorism-suspects" rel="noopener noreferrer">Counter-terrorism operation leverages artificial intelligence to identify 126 terrorism suspects</a> <small>INTERPOL · 2026-09-18 · PREDICT + ACT</small></li>
</ul>

<p class="cmb-watch-method-note"><strong>Seed rule:</strong> these ten links exercise distinct CMB boundaries. Scheduled refreshes may rotate the public ledger, but the publication budget remains ten links.</p>

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

The canonical GitHub Pages deployment scans a bounded metadata sample during documentation deployment and on an hourly schedule. GitHub Actions scheduling is best-effort, so the interval is not a real-time guarantee. Only the selected outbound links are published; the larger analysis sample is discarded after the build.

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
