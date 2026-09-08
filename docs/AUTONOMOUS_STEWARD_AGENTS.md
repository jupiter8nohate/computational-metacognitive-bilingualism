# CMB Autonomous Steward Agents

## Purpose

The CMB Steward Agents are a bounded maintenance system for work that can continue while the maintainer is away.

They are intentionally separated from the CMB Agent Discovery Protocol. Discovery agents explain, cite, and expose CMB. Steward agents inspect and maintain the repository.

~~~text
DISCOVERY_AGENT != MAINTENANCE_AGENT
MACHINE_CAN_PROPOSE != MACHINE_CAN_MERGE
CAPABILITY != AUTHORITY
HUMAN_AGENCY > MACHINE_AUTHORITY
~~~

## Agent roles

The scheduled steward now separates deterministic maintenance from read-only specialist review:

1. **RECOVERY** — runs the repository test suite, checks patch integrity, and verifies repairs.
2. **GLITCH_IR_CONFORMANCE** — runs the GLT-8101 eight-language semantic conformance harness.
3. **REGISTRY_SYNC** — regenerates the GLITCH-8 human reference and public machine-readable registry mirror.
4. **DOCUMENTATION** — performs a strict public documentation build and verifies public discovery assets.
5. **CANON** — checks GLITCH-8 source/mirror/reference semantic consistency.
6. **ACCESSIBILITY** — checks primary entry surfaces for alt-text and CSS accessibility safeguards.
7. **RELEASE** — checks repository-declared v1.5 release boundaries without self-certifying external gates.
8. **LIBRARIAN** — checks documentation navigation targets and catalogue integrity.
9. **ARCHAEOLOGIST** — backtraces the canonical registry through repository Git history.
10. **DISCOVERY** — validates the machine-discovery contract.
11. **SECURITY** — verifies repository-side security-control files are present.
12. **REVIEWER** — rejects evidence packets that escalate authority or self-certify external gates.
13. **POSITION** - builds a hashed repository position from the exact commit, deterministic audit state, evidence packets, and latest changed paths.
14. **TACTICIAN** - searches for the smallest immediate repair to a concrete failure.
15. **STRATEGIST** - evaluates architecture and maintenance consequences without bypassing stabilization scope.
16. **RED_TEAM** - attempts to refute candidate moves before deterministic selection.
17. **STEWARD** — when deterministic checks fail and an AI model is configured, asks the model for a bounded structured repair plan.

The chess roles are proposal and review roles. They do not receive direct repository mutation authority. The Strategy Engine feeds an advisory principal variation into the existing bounded Steward repair path.

The specialist roles are read-only. They communicate through structured evidence packets. See [CMB Specialist Agent Operating Model](AGENT_OPERATING_MODEL.md) and [CMB Chess Strategy Engine](CHESS_STRATEGY_ENGINE.md).

## Schedule

The workflow is `.github/workflows/cmb-steward-agents.yml`.

It runs once per day at `08:17 UTC` and may also be launched manually with `workflow_dispatch`.

The schedule is maintenance cadence, not a guarantee that a code change will be created every day.

## AI activation

Deterministic audits work without an AI provider.

AI-assisted repair requires two repository settings:

- GitHub Actions secret: `OPENAI_API_KEY`
- GitHub Actions repository variable: `CMB_AGENT_MODEL`

The implementation uses the OpenAI Responses API and requests a strict JSON-schema repair response. The repository does not store the API key.

If either setting is absent, the Steward role reports that AI repair was skipped. It does not invent a configured model or silently fall back to another provider.

## Mutation policy

The AI repair path may modify only existing files supplied to it as repair context.

Permitted areas include `src/cmb_glitch8/`, `src/cmb_agents/`, `src/cmb_machine/`, `docs/`, `books/`, `examples/`, and `README.md`.

Protected areas include `.github/`, `tests/`, `scripts/`, `schemas/`, `machine/`, `agents/`, `policy/`, `receipts/`, `SECURITY.md`, `LICENSE`, `NOTICE`, `pyproject.toml`, `cmb.toml`, and `src/cmb_agents/steward.py`.

The model therefore cannot rewrite its own authority boundary, weaken tests, alter workflows, replace schemas, modify security policy, or change machine authority records through the autonomous repair path.

Generated GLITCH-8 public views are separately allowed because they are rebuilt deterministically from the canonical registry.

## Repair protocol

~~~text
DETERMINISTIC AUDIT
        │
        ├── all checks pass ──────────────► NO AI REPAIR
        │
        └── concrete failure
                 │
                 ▼
           BOUNDED CONTEXT
                 │
                 ▼
          STRUCTURED AI PLAN
                 │
                 ▼
           PATH VALIDATION
                 │
                 ▼
             APPLY EDIT
                 │
                 ▼
          FIXED VERIFICATION
                 │
                 ├── FAIL ──► STOP
                 │
                 └── PASS
                       │
                       ▼
                 DRAFT PULL REQUEST
                       │
                       ▼
                   HUMAN REVIEW
~~~

The model does not receive a general shell. It cannot return commands for the workflow to execute. The runner executes only fixed commands defined in trusted source.

## Pull-request authority

If verified allowlisted changes exist, the workflow may create a branch named `cmb-agent/steward-<github-run-id>` and open a **draft pull request**.

The steward does not merge the PR. If another Steward PR is already open, the workflow does not create a duplicate.

~~~text
AI_CHANGE != ACCEPTED_CHANGE
TEST_PASS != HUMAN_APPROVAL
PR != MERGE
~~~

## Local commands

~~~bash
cmb-steward audit --report /tmp/cmb-steward-audit.json
cmb-steward repair --report /tmp/cmb-steward-audit.json
cmb-steward verify
cmb-steward validate-diff
~~~

For local AI repair, set `OPENAI_API_KEY` and `CMB_AGENT_MODEL` in the environment. Do not commit API keys.

## Structured specialist evidence

Every specialist emits a packet with `agent`, `task`, `observed`, `evidence`, `confidence`, `recommended_action`, `authority`, and `severity`. The Reviewer inspects those packets before they are treated as Steward evidence.

The latest repository-side audit is also rendered as [CMB System Status](generated/CMB_SYSTEM_STATUS.md) and `generated/cmb-system-status.json`. These files do not claim to verify GitHub platform settings, an external reviewer, or a DOI.

```text
PACKET != PROOF
CONFIDENCE != AUTHORITY
SELF_REVIEW != INDEPENDENT_REVIEW
```

## Practical work it can perform

The current system can detect regressions while the maintainer is offline; detect GLT-8101 semantic drift across eight language engines; repair generated GLITCH-8 references and public registry mirrors; detect broken documentation builds; use a configured model to propose minimal repairs to concrete failures; reject edits outside the allowed scope; rerun deterministic verification; and open a reviewable draft PR when a repair survives verification.

It is deliberately **not** configured to autonomously merge, release, modify security rules, rotate credentials, alter legal material, or expand its own permissions.

## Recovery law

~~~text
OBSERVE
  ↓
VERIFY
  ↓
PROPOSE
  ↓
CONSTRAIN
  ↓
TEST
  ↓
PR
  ↓
HUMAN

AUTONOMY != UNBOUNDED_AUTHORITY
RECOVERY > SILENT_FAILURE
~~~
