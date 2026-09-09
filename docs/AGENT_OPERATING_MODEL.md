# CMB Specialist Agent Operating Model

CMB uses specialization instead of granting one model broad repository authority.

The experimental Chess Strategy Engine adds bounded POSITION, TACTICIAN, STRATEGIST, SECURITY, RECOVERY, RED_TEAM, and REVIEWER search roles before the existing Steward mutation gate. Candidate moves are advisory until they survive deterministic policy and fixed verification. The AUTONOMY_ARBITER then converts the selected move into exactly one bounded verdict: PROPOSE_REPAIR, HUMAN_REVIEW, or PRESERVE_POSITION. See [CMB Chess Strategy Engine](CHESS_STRATEGY_ENGINE.md).

CMB-SRC-1 adds a separate pull-request review council with TACTICIAN, SECURITY_SENTINEL, CORRECTNESS_ENGINE, ARCHITECT, TEST_ADVERSARY, GOVERNANCE_GUARD, SKEPTIC, and ARBITER roles. It can emit advisory review verdicts but cannot merge, approve through the GitHub API, publish releases, or expand its own permissions. See [CMB Stockfish Review Council](STOCKFISH_REVIEW_COUNCIL.md).

~~~text
                    HUMAN
                      ♃
                      │
                 STEWARD GATE
                      │
       ┌──────────────┼──────────────┐
       │              │              │
    OBSERVE          VERIFY         PROPOSE
       │              │              │
       ├─ CANON       ├─ RECOVERY    └─ STEWARD
       ├─ LIBRARIAN   ├─ CONFORMANCE
       ├─ ARCHAEOLOGIST
       ├─ ACCESSIBILITY
       ├─ DISCOVERY
       ├─ SECURITY
       └─ RELEASE
                      │
                   REVIEWER
                      │
                      ▼
                  DRAFT PR
                      │
                      ▼
                    HUMAN
~~~

## Authority model

| Role | Primary task | Autonomous write authority |
| --- | --- | --- |
| RECOVERY | Tests and regression verification | No direct free-form authority |
| GLITCH_IR_CONFORMANCE | Cross-language semantic conformance | No |
| REGISTRY_SYNC | Deterministic generated registry views | Generated views only |
| DOCUMENTATION | Strict public documentation build | No |
| CANON | Detect GLITCH-8 semantic drift | Read-only |
| ACCESSIBILITY | Inspect front-door accessibility safeguards | Read-only |
| RELEASE | Check repository-declared release gates | Read-only |
| LIBRARIAN | Detect broken navigation/catalogue targets | Read-only |
| ARCHAEOLOGIST | Backtrace canonical registry history | Read-only |
| DISCOVERY | Inspect machine-discovery contract | Read-only |
| SECURITY | Inspect repository-side security-control files | Read-only |
| DNIS | Verify Digital Nervous Immune System registry and Digital DNA continuity | Read-only |
| REVIEWER | Review evidence packets for authority escalation/self-certification | Read-only |
| POSITION | Build a hashed repository search state | Read-only |
| TACTICIAN | Propose minimum reversible fixes | Propose-only |
| STRATEGIST | Rank architecture and maintenance moves | Propose-only |
| RED_TEAM | Refute candidate moves before selection | Read-only |
| STEWARD | Propose bounded repairs after concrete failures | Existing-file allowlist; draft PR only |

No specialist can merge, publish a release, change security settings, rotate credentials, rewrite its own authority rules, or certify external review.

## Structured evidence packets

Specialist agents communicate through a deterministic envelope rather than by asking another agent to trust conversational confidence.

~~~json
{
  "agent": "CANON",
  "task": "glitch8_semantic_consistency",
  "observed": {"mirror_matches": true},
  "evidence": ["src/cmb_glitch8/glyphs.v1.json", "library/glitch8.glyphs.v1.json"],
  "confidence": 1.0,
  "recommended_action": "No canon repair required.",
  "authority": "read_only",
  "severity": "info"
}
~~~

The packet is a claim envelope. Evidence still has to support the claim.

~~~text
PACKET != PROOF
CONFIDENCE != AUTHORITY
GENERATED != VERIFIED
~~~

## Builder → deterministic checks → reviewer → human

The repair model is not allowed to certify its own work.

~~~text
CONCRETE FAILURE
      │
      ▼
BOUNDED STEWARD PROPOSAL
      │
      ▼
FIXED VERIFICATION
      │
      ▼
SPECIALIST EVIDENCE
      │
      ▼
REVIEWER AUTHORITY CHECK
      │
      ▼
DRAFT PULL REQUEST
      │
      ▼
HUMAN DECISION
~~~

The current Reviewer is intentionally conservative: it checks structured outputs for authority escalation and prohibited self-certification. The Autonomy Arbiter is a second deterministic control boundary. It cannot create edits; it can only permit the existing bounded Steward repair path, fail closed to human review, or preserve the current position. Independent external human review remains a separate release gate.

## Librarian

The Librarian checks MkDocs navigation targets and reports catalogue drift without rewriting authored meaning.

~~~text
ORGANIZE != REAUTHOR
INDEX != IDENTITY
~~~

## Archaeologist

The Archaeologist uses Git history to backtrace the canonical GLITCH-8 registry. Its scope is repository history only; it does not convert a Git commit into proof of historical priority outside the repository.

~~~text
COMMIT_HISTORY = REPOSITORY_EVIDENCE
REPOSITORY_EVIDENCE != UNIVERSAL_PRIORITY_PROOF
SIGNAL != SOURCE
BACKTRACE ‹—
~~~

## Recovery law

~~~text
AGENT_SPECIALIZATION > AGENT_POWER
SEPARATION_OF_DUTIES > SUPER_AGENT
DETERMINISTIC_CHECK > MODEL_OPINION
EVIDENCE > CONFIDENCE
MACHINE_CAN_PROPOSE != MACHINE_CAN_MERGE
HUMAN_AGENCY > MACHINE_AUTHORITY
~~~

## Digital Nervous Immune System

CMB-DNIS-1 adds a bounded cell-agent routing layer without replacing the existing Steward authority model.

~~~text
RECEPTOR_CELL
      |
      v
DENDRITIC_CELL
      |
      v
POSITION_CELL
      |
      v
CHAPERONE_CELL
      |
      v
T_CELL_POLICY_GATE
   /         \\
  v           v
REFLEX     CORTEX_LIAISON
  |           |
  +-----+-----+
        |
        v
B_CELL_PROVENANCE
        |
        v
MEMORY_CELL
~~~

On a concrete denial, MACROPHAGE_RECOVERY may propose a bounded repair through the existing Steward path. It does not gain merge, release, credential, workflow, or security-policy authority.

Every cell packet carries the same Digital DNA digest:

~~~text
PATTERN != PROOF
PROFILE != PERSON
MODEL != MIND
PREDICTION != DESTINY
CAPABILITY != AUTHORITY
AGENT_CAN_PROPOSE != AGENT_CAN_MERGE
HUMAN_AGENCY > MACHINE_AUTHORITY
~~~

See [CMB Digital Nervous Immune System](DIGITAL_NERVOUS_IMMUNE_SYSTEM.md) and `../agents/immune-cell-registry.json`.

## Stockfish pull-request review council

CMB-SRC-1 reviews changed paths and patches as a bounded repository position. Deterministic checks run first. Optional model-assisted specialists receive bounded, untrusted diff text and cannot convert model output into repository authority.

~~~text
PR_DIFF
  |
  v
DETERMINISTIC_SPECIALISTS
  |
  v
SKEPTIC
  |
  v
COUNCIL_VOTE
  |
  v
ARBITER
  |
  +--> APPROVE
  +--> REQUEST_CHANGES
  +--> HUMAN_REVIEW
~~~

The workflow keeps `contents: read` permission. A HUMAN_REVIEW result is an explicit routing decision, not an automated approval. A REQUEST_CHANGES result may fail the review gate, but only a human or separately authorized repository mechanism can merge.

~~~text
REVIEW != MERGE
MODEL_OPINION != EVIDENCE
SCORE != TRUTH
HUMAN_AGENCY > MACHINE_AUTHORITY
~~~
