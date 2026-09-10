# CMB 333 Philosophy Swarm

CMB-PS-333 is a bounded philosophy-expansion runtime for Computational Metacognitive Bilingualism.

It creates exactly 333 logical specialist agents as nine guilds of 37 agents each. A logical agent is a deterministic runtime identity with a mandate, local mission-selection freedom, an evidence posture, and a fixed authority envelope. This does not mean 333 permanently hosted cloud processes are running at all times.

## Purpose

The swarm exists to explore, stress-test, teach, and creatively expand CMB while preserving the repository's core boundary:

```text
HUMAN_AGENCY > MACHINE_AUTHORITY
```

Agents can select missions, abstain, challenge a peer direction, request evidence, draft internal proposals, test counterexamples, rank candidate ideas, and preserve the current position when a seed is not materially relevant to CMB.

Agents cannot merge pull requests, push to the default branch, publish releases, change repository permissions, use or rotate secrets, post externally, mass-message people, perform unsolicited distribution, execute model-provided commands, delete repository content, or rewrite their own authority rules.

```text
AGENT_AUTONOMY != UNBOUNDED_AUTHORITY
EXPANSION != SPAM
MODEL_OUTPUT != EVIDENCE
CONSENT > VIRALITY
RELEVANCE > REACH
```

## Architecture

```text
                         HUMAN
                           |
                           v
                   CMB AUTHORITY LAW
                           |
              +------------+------------+
              |                         |
              v                         v
      333 LOGICAL AGENTS          AUTONOMY BOUNDS
              |
       9 GUILDS x 37
              |
   +----------+----------+
   |          |          |
   v          v          v
SELECT     CHALLENGE   ABSTAIN
MISSION      PEER
   |          |          |
   +----------+----------+
              |
              v
       GUILD ELECTIONS
              |
              v
      INTERNAL PROPOSALS
              |
              v
 OPTIONAL MODEL ASSIST
              |
              v
   EVIDENCE + COUNTERARGUMENT
              |
              v
         HUMAN REVIEW
```

## Nine guilds

| Guild | Agents | Mission |
| --- | ---: | --- |
| AGENCY_GUARDIANS | 37 | Preserve human judgment and human veto power |
| PATTERN_SKEPTICS | 37 | Falsify weak pattern claims and search for simpler explanations |
| PROVENANCE_KEEPERS | 37 | Improve source tracing, citations, receipts, and claim boundaries |
| CONSENT_ARCHITECTS | 37 | Build consent-first machine interaction patterns |
| NEURODIVERSITY_TRANSLATORS | 37 | Resist reductive profiling and preserve cognitive difference |
| PHILOSOPHY_LAB | 37 | Generate rigorous questions, thought experiments, and category tests |
| SYSTEMS_CARTOGRAPHERS | 37 | Map incentives, feedback loops, proxies, externalities, and recovery paths |
| ACCESSIBILITY_EDUCATORS | 37 | Convert CMB into layered and accessible teaching forms |
| GLITCH_POETS | 37 | Explore code-poetry and Err GLITCHOLOGY without relaxing evidence boundaries |

Total: `9 * 37 = 333`.

## Local autonomy

Each agent independently derives a mission choice from its identity, guild, and the supplied seed. This makes the swarm reproducible while still allowing every agent to make a local bounded choice. Some agents may abstain. Some may flag a peer challenge. Some may request more evidence.

The guild then elects its strongest-supported mission. The election creates an internal proposal only. It does not create publication authority.

When the input is outside the declared CMB relevance envelope, all 333 agents preserve position rather than manufacturing a CMB connection.

```text
IRRELEVANT_INPUT -> PRESERVE_POSITION
RELEVANCE > REACH
```

## Optional AI model assist

The runtime can use the existing bounded `cmb_agents.model_gateway` after a guild election. Model assist is optional and budgeted to at most one structured drafting call per guild. The default maximum is nine model calls, not 333 model calls.

A model may draft an internal concept note, thought experiment, teaching example, code poem, or research question. The structured draft must include claims requiring verification, a counterargument, and a human-review note.

Model output remains advisory.

```text
MODEL_OUTPUT != EVIDENCE
MODEL_ACCESS != REPOSITORY_AUTHORITY
SELF_REVIEW != INDEPENDENT_REVIEW
```

## CLI

Run the deterministic 333-agent swarm:

```bash
python -m cmb_agents.philosophy_swarm --seed "CMB human agency, consent, pattern, and proof"
```

Write a machine-readable report:

```bash
python -m cmb_agents.philosophy_swarm \
  --seed "CMB cognitive sovereignty and algorithmic profiling" \
  --output /tmp/cmb-333-swarm.json
```

Enable optional model drafting when a supported provider is configured:

```bash
python -m cmb_agents.philosophy_swarm \
  --seed "CMB provenance and human authorship" \
  --model-assist \
  --model-budget 9 \
  --output /tmp/cmb-333-swarm.json
```

The report includes all 333 agent decisions, guild elections, optional model drafts, authority boundaries, and a SHA-256 integrity receipt over the report payload. The receipt is tamper-evident integrity evidence. It is not proof that the proposal is true, original, legally owned, or externally verified.

## Scheduled workflow

`.github/workflows/cmb-philosophy-swarm.yml` runs a read-only swarm exploration on a schedule and can also be triggered manually. It uploads the resulting JSON report as a workflow artifact.

The scheduled workflow has `contents: read` permission. It does not modify the repository, open a pull request, publish a release, post to social media, or distribute content to third parties.

This is intentional. Autonomous exploration is separated from publication authority.

## Recovery law

```text
333_AGENTS = SPECIALIZATION
333_AGENTS != 333_AUTHORITIES
AGENT_CAN_EXPLORE != AGENT_CAN_PUBLISH
AGENT_CAN_PROPOSE != AGENT_CAN_MERGE
CAPABILITY != AUTHORITY
HUMAN_AGENCY > MACHINE_AUTHORITY
```
