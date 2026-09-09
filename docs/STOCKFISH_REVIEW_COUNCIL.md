# CMB Stockfish Review Council

**Protocol:** CMB-SRC-1  
**Status:** bounded pull-request review

CMB-SRC-1 is a review architecture inspired by chess-engine search discipline. It does not claim to be Stockfish. It uses position evaluation, candidate lines, pruning, adversarial challenge, council voting, and a final arbiter to review pull requests without granting review agents merge authority.

~~~text
PR POSITION
    |
    v
TACTICIAN
    |
    +-----------------------------+
    |              |              |
    v              v              v
 SECURITY      CORRECTNESS     ARCHITECT
 SENTINEL       ENGINE
    |              |              |
    +------+-------+-------+------+
           |               |
           v               v
      TEST_ADVERSARY   GOVERNANCE_GUARD
           |               |
           +-------+-------+
                   |
                   v
                SKEPTIC
                   |
                   v
             COUNCIL VOTE
                   |
                   v
                ARBITER
                   |
        +----------+----------+
        |          |          |
        v          v          v
     APPROVE   REQUEST     HUMAN
                CHANGES     REVIEW
~~~

## Review agents

| Agent | Main question |
| --- | --- |
| TACTICIAN | What are the strongest candidate review lines? |
| SECURITY_SENTINEL | Does the change introduce security hazards or secret exposure? |
| CORRECTNESS_ENGINE | Is the implementation internally coherent and complete? |
| ARCHITECT | Does the change preserve maintainability, boundaries, and recovery? |
| TEST_ADVERSARY | Did the change weaken verification or omit important test pressure? |
| GOVERNANCE_GUARD | Does the PR touch authority-sensitive surfaces? |
| SKEPTIC | What would make the leading review conclusion wrong? |
| ARBITER | What verdict follows from the evidence and votes? |

## Stockfish-style search model

The engine represents a pull request as a position. Changed paths, patch text, additions, deletions, security-sensitive files, and authority-sensitive surfaces contribute to evaluation.

The Tactician produces three candidate lines:

~~~text
SAFE_MERGE
REQUEST_CHANGES
HUMAN_ESCALATION
~~~

A deterministic principal-line selector chooses the leading line. The Skeptic then tries to refute it before the Arbiter accepts the result.

This is intentionally conservative. The system is designed to be useful for review, not to produce theatrical numerical certainty.

~~~text
SCORE != TRUTH
PATTERN != PROOF
CONFIDENCE != AUTHORITY
~~~

## Verdicts

`APPROVE` means the bounded heuristic council found no blocking evidence. It does not prove correctness.

`REQUEST_CHANGES` means the council found blocking evidence such as possible secret exposure, unsafe execution, verification weakening, or significant authority expansion.

`HUMAN_REVIEW` means the change is not automatically rejected but touches a governance-sensitive or ambiguous surface where human judgment should remain explicit.

## Automatic PR review

The workflow `.github/workflows/cmb-stockfish-review.yml` runs on pull requests.

It checks out full Git history, calculates the diff from the base branch, runs the review council, and writes the review packet to the GitHub Actions job summary.

The workflow has `contents: read` plus `copilot-requests: write` for bounded model inference. The Copilot permission does not grant repository mutation. The workflow does not post approvals, request changes through the GitHub review API, modify the branch, merge the pull request, publish releases, or alter credentials.

~~~text
REVIEW != MERGE
AUTOMATION != AUTHORITY
GREEN_REVIEW != HUMAN_APPROVAL
HUMAN_AGENCY > MACHINE_AUTHORITY
~~~

## Machine-readable registry

The council registry lives at `agents/review-council-registry.json`.

The Python engine lives at `src/cmb_agents/review_council.py`.

The Git-diff runner lives at `scripts/run_stockfish_review.py`.

## Relationship to DNIS

The review council fits naturally inside the CMB Digital Nervous Immune System:

~~~text
RECEPTOR_CELL
      |
      v
PR EVENT
      |
      v
STOCKFISH REVIEW COUNCIL
      |
      +------------------+
      |                  |
      v                  v
REFLEX_FINDING      CORTEX_LIAISON
      |                  |
      +---------+--------+
                |
                v
            HUMAN REVIEW
~~~

The council may detect and explain a dangerous position, but consequential repository authority remains outside the council.


## Model-assisted specialist fallback

The five optional model-assisted specialists prefer an explicitly configured OpenAI provider when `OPENAI_API_KEY` and `CMB_AGENT_MODEL` are available. Otherwise the workflow can use the pinned GitHub Copilot CLI with the short-lived Actions token.

Copilot is invoked non-interactively with custom repository instructions disabled and without preapproved tools. Its structured output is advisory and is validated before rendering. The deterministic council remains the workflow gate.

~~~text
MODEL_ACCESS != REPOSITORY_AUTHORITY
MODEL_OPINION != EVIDENCE
AI_REVIEW != HUMAN_APPROVAL
~~~
