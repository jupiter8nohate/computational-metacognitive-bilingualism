# CMB Epistemic Radar

<div class="cmb-radar-hero">
<div class="cmb-kicker">CMB://EPISTEMIC_RADAR // PATTERN + DISCREPANCY + TECHNOLOGY + HUMAN JUDGMENT</div>

**CMB Epistemic Radar** is an experimental public AI-news observatory that uses current reporting as a teaching surface.

It does not decide what is true for the reader. It discovers signals, compares related coverage, marks possible discrepancies, identifies concentrated technology vocabulary, and explains which CMB human-authority boundary deserves examination.
</div>

~~~text
                    PUBLIC NEWS
                        |
                        v
                  +-------------+
                  |   SENSOR    |
                  +-------------+
                        |
          +-------------+-------------+
          v             v             v
      PATTERN       DISCREPANCY     EMERGENCE
          |             |             |
          v             v             v
     CMB BOUNDARY   HUMAN REVIEW   NEW TECH TERMS
          \             |             /
           \            |            /
            +-----------+-----------+
                        |
                        v
                  +-------------+
                  |   TEACHER   |
                  +-------------+
                        |
                        v
             EVIDENCE -> VERIFY
               -> JUDGE -> CONSENT
                    -> ACT
~~~

## The design rule

~~~text
MACHINE_CAN:
    discover
    group
    compare
    flag
    count
    explain

MACHINE_CANNOT_CLAIM:
    final_truth
    human_intent
    guilt
    identity
    certainty
    authority

PATTERN != PROOF
DISCREPANCY_FLAG != CONTRADICTION_PROOF
EMERGING_TERM != NEW_TECHNOLOGY_PROOF
HUMAN_AGENCY > MACHINE_AUTHORITY
~~~

## Current radar

The radar is regenerated from public GDELT news metadata during the GitHub Pages build. Its 24-hour sample is compared with a broader seven-day sample. Those samples are finite and should not be treated as exhaustive measurements of the world.

<!-- CMB_EPISTEMIC_RADAR_GENERATED_START -->

<div class="cmb-radar-status">SEED STATE // awaiting first radar build</div>

<div class="cmb-watch-metrics">
<div><strong>0</strong><span>current stories</span></div>
<div><strong>0</strong><span>story clusters</span></div>
<div><strong>0</strong><span>discrepancy flags</span></div>
<div><strong>0</strong><span>technology signals</span></div>
</div>

<div class="cmb-radar-grid">
<div class="cmb-watch-empty">The deployed radar will populate this surface from current public news metadata.</div>
</div>

<!-- CMB_EPISTEMIC_RADAR_GENERATED_END -->

## What "learning" means here

The radar does **not** silently retrain a black-box model.

Each build creates a new temporary baseline from a broader recent news sample, then compares today's sample against it. That allows the structure to notice changes while keeping the method inspectable.

~~~text
RECENT_SAMPLE
    |
    +--> repeated vocabulary
    +--> technology mentions
    +--> source clusters
    +--> CMB boundary frequency
    |
    v
CURRENT_SAMPLE
    |
    +--> concentration change
    +--> new vocabulary candidates
    +--> cross-source language differences
    +--> high-consequence context
    |
    v
HUMAN REVIEW
~~~

This is **adaptive comparison**, not autonomous truth-learning.

## Four engines

### 1. SENSOR // What is being reported?

The sensor uses the public GDELT DOC API to discover recent stories and retains direct publisher links.

It stores metadata, not copied article bodies.

### 2. PATTERN // Which CMB boundary appears?

Every headline can map to one or more explicit categories:

~~~text
PREDICT
    PATTERN != PROOF
    PROFILE != PERSON
    PREDICTION != DESTINY

GENERATE
    MODEL != MIND
    SIMULATION != SOURCE
    GENERATED != VERIFIED

ACT
    RECOMMENDATION != AUTHORIZATION
    CAPABILITY != AUTHORITY
    HUMAN_AGENCY > MACHINE_AUTHORITY
~~~

The rule vocabulary is public in the machine-readable configuration.

### 3. DISCREPANCY // Where should a human compare sources?

Within a headline-similarity cluster, the radar can flag language differences such as:

~~~text
APPROVED <-> BLOCKED
LAUNCHED <-> DELAYED
SAFE <-> DANGEROUS
ACCURATE <-> FAULTY
INCREASED <-> DECREASED
~~~

It can also flag different numbers appearing in related coverage.

These are **review prompts**, not declarations that one publisher is wrong.

### 4. TEACHER // What should a person ask next?

Instead of producing a verdict, the radar generates questions.

~~~text
PREDICT:
"What evidence produced this prediction or classification?"

GENERATE:
"Can this generated claim, image, voice, or text be traced to an authentic source?"

ACT:
"Who authorized the action, and can a human stop or reverse it?"
~~~

That turns daily news into computational literacy.

## Emerging technology detector

The radar watches defined technology families including:

- AI agents and agentic systems
- reasoning models
- multimodal systems
- world models
- embodied AI and humanoid robotics
- synthetic media and voice cloning
- AI-enabled cyber operations
- AI chips and compute infrastructure
- AI for science and medicine
- Model Context Protocol
- agent-to-agent interoperability
- biological and organoid computing

It also extracts **emerging vocabulary candidates** when terms are unusually concentrated in the current sample compared with the broader sample.

A candidate term is not automatically labeled a new technology.

~~~text
TERM_SPIKE -> INVESTIGATE
TERM_SPIKE != INVENTION
TERM_SPIKE != IMPORTANCE
TERM_SPIKE != TRUTH
~~~

## Discrepancy protocol

The radar separates several concepts that ordinary feeds often collapse:

~~~text
DIFFERENT_HEADLINES != CONTRADICTION
MULTIPLE_SOURCES != INDEPENDENT_SOURCES
REPEATED_CLAIM != VERIFIED_CLAIM
NEWER_REPORT != AUTOMATICALLY_MORE_ACCURATE
ARCHIVED_PAGE != TRUE_PAGE
~~~

For consequential stories, the reader should still examine original reporting, primary documents, dates, corrections, and independent confirmation.

## Machine-readable surfaces

- [Radar snapshot](https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/machine/cmb-epistemic-radar.json)
- [Radar rules](https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/machine/cmb-epistemic-radar-config.json)
- [Radar schema](https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/schemas/cmb.epistemic-radar.v1.schema.json)
- [Underlying Global AI Watch](GLOBAL_AI_WATCH.md)
- [Global AI Watch machine snapshot](https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/machine/global-ai-watch.json)

## Epistemic architecture

CMB Epistemic Radar is deliberately different from a recommendation engine.

~~~text
OBSERVE
  |
  v
STRUCTURE
  |
  v
COMPARE
  |
  v
FLAG UNCERTAINTY
  |
  v
SHOW SOURCES
  |
  v
TEACH VERIFICATION
  |
  v
RETURN AUTHORITY TO HUMAN
~~~

The success condition is not:

~~~text
USER_BELIEVES_RADAR
~~~

It is:

~~~text
USER_CAN_EXAMINE_EVIDENCE
USER_CAN_RECOGNIZE_MACHINE_BOUNDARIES
USER_CAN_CHALLENGE_THE_RADAR
USER_RETAINS_JUDGMENT
~~~

## Status boundary

This is an experimental research and education surface inside the CMB documentation system. It is not an intelligence service, fact-checking authority, threat detector, or substitute for professional domain expertise.

~~~text
RADAR_FLAG != FACT_CHECK
RADAR_FLAG != THREAT_ASSESSMENT
RADAR_FLAG != HUMAN_VERDICT
CMB_INTERPRETATION != SOURCE_ENDORSEMENT
~~~
