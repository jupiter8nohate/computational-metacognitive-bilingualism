# CMB Distribution Ecosystem

CMB is a framework with multiple implementation surfaces. Distribution should preserve those boundaries rather than collapsing every idea into one package.

```text
CMB = framework
cmb-provenance = provenance implementation
CMB-Z13 = symbolic computational language
CMB-ADP = agent discovery protocol
CMB-EDU = educational layer
CMB Playground = interaction layer
CMB Cognitive Lens = user-control layer

CMB != ONE_PROGRAM
```

## Distribution sequence

1. Publish the existing Python package to PyPI as `cmb-provenance`.
2. Publish the interoperable TypeScript surface as `@cmb-sovereignty/core`.
3. Ship the CMB Cognitive Lens browser extension.
4. Deploy the static CMB-Z13 Playground.
5. Build creator-media and research material around demonstrable software behavior.
6. Pursue privacy, neurodiversity, digital-humanities, and AI-governance collaborations.

## Accuracy boundary

The browser extension evaluates observable interface signals. It does not claim access to hidden platform models or server-side profiling systems.

```text
ATTENTION_SIGNAL != PROOF_OF_PROFILING
PATTERN != PROOF
PROFILE != PERSON
```

Examples of observable signals include autoplay media, repeated engagement prompts, sticky feed controls, and high-volume scrolling interfaces.

## Privacy defaults

```text
telemetry = OFF
cloud_processing = OFF
personal_profile = NONE
page_analysis = LOCAL
hidden_psychological_inference = DENIED
user_override = ALWAYS
```

## Package boundaries

### Python

`cmb-provenance` remains the canonical provenance, sealing, verification, C2PA-facing, CMB-Z13 CLI, CMB-EDU CLI, and agent-discovery distribution.

### TypeScript

`@cmb-sovereignty/core` exposes portable invariants, typed attention-signal evaluation, and shared machine-readable contracts for web applications and agents. It does not duplicate cryptographic sealing.

### Browser extension

The extension is a local cognitive-literacy tool. It computes explainable attention-signal scores from page behavior and renders the exact observations that produced the score.

### Playground

The playground translates user-entered text into CMB-Z13 Guardian Mode perspectives. It is educational and symbolic. It does not diagnose personality, infer mental state, or claim scientific validity for zodiac mappings.

## Release gates

Before public registry publication:

- all Python tests pass;
- built wheel and sdist install successfully in a clean environment;
- package metadata is correct;
- trusted publishing is configured for PyPI;
- TypeScript package tests and type checks pass;
- extension declares no remote code and no telemetry;
- playground remains static and privacy-preserving;
- release notes distinguish declared policy, cryptographic integrity, technical enforcement, and legal enforceability.

## Adoption loop

```text
GitHub
   ↓
PyPI / npm
   ↓
Browser Extension
   ↓
Interactive Playground
   ↓
Short-form demonstrations
   ↓
Research / policy discussion
   ↓
Developer adoption
   ↺
```

The objective is relevance-first distribution, not forced virality.

```text
RELEVANCE > REACH
TRUST > IMPRESSIONS
CITATION > COPYING
CONSENT > VIRALITY
HUMAN_AGENCY > MACHINE_AUTHORITY
```
