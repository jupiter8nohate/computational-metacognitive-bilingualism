# CMB Specialist Agent Operating Model

CMB uses specialization instead of granting one model broad repository authority.

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
| REVIEWER | Review evidence packets for authority escalation/self-certification | Read-only |
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

The current Reviewer is intentionally conservative: it checks structured outputs for authority escalation and prohibited self-certification. Independent external human review remains a separate release gate.

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
