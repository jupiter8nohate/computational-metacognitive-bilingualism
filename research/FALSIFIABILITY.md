# CMB falsifiability and evidence matrix

CMB contains software, policy proposals, educational claims, philosophical
positions, and authored art. They do not all use the same evidence standard.

This document defines what would be required to test important empirical claims
instead of treating repository existence as proof.

## Claim class 1: software correctness

Example claim:

> The boundary adapters implement the same v1 semantic decisions.

Evidence required:

- shared language-neutral fixtures;
- deterministic cross-language test results;
- invalid-input testing;
- regression tests for stable reason-code ordering.

Potential falsification:

- one implementation returns a different required decision or stable code for
  the same canonical fixture.

## Claim class 2: provenance correctness

Example claim:

> A CMB receipt detects modification of a covered artifact under the documented
> threat model.

Evidence required:

- exact-byte hashing tests;
- corrupted-artifact tests;
- receipt/schema validation;
- race/concurrency tests;
- independent review of overclaim paths.

Potential falsification:

- covered bytes can change while verification still reports a valid match under
  conditions the threat model claims to handle.

## Claim class 3: educational effectiveness

Example claim:

> CMB notation improves understanding of distinctions such as prediction versus
> destiny or profile versus person.

Repository existence does not prove this.

Evidence required:

- defined target population;
- pre/post comprehension measure;
- comparison condition;
- documented intervention;
- effect size and uncertainty;
- replication or independent evaluation where possible.

Potential falsification:

- no practically meaningful improvement compared with the control condition.

## Claim class 4: accessibility / neurodiversity benefit

Example claim:

> CMB's multimodal notation is more accessible for some neurodivergent learners.

This is a testable hypothesis, not a universal fact.

Evidence required:

- participatory study design;
- accessibility metrics selected with affected users;
- subgroup reporting that avoids treating neurodivergent people as homogeneous;
- qualitative and quantitative feedback;
- explicit failure/negative-result reporting.

Potential falsification:

- target users find the notation no more usable, less usable, or materially more
  confusing than comparison formats.

## Claim class 5: policy usefulness

Example claim:

> CMB's machine-readable human-agency declarations help teams implement clearer
> consent or review boundaries.

Evidence required:

- real integration case studies;
- measurable policy/compliance outcomes;
- error and appeal analysis;
- comparison with existing governance controls.

Potential falsification:

- the declarations do not change operational behavior, cannot be integrated
  reliably, or produce worse outcomes than simpler existing controls.

## Claim class 6: historical novelty

Example claim:

> A CMB technique is historically first or uniquely novel.

Evidence required:

- systematic prior-art search;
- dated primary sources;
- clear definition of the claimed innovation;
- independent scholarly review.

Potential falsification:

- earlier substantially equivalent work is identified.

## Evidence hierarchy

~~~text
AUTHORED_ASSERTION
    < SELF_TEST
    < REPRODUCIBLE_EXTERNAL_TEST
    < INDEPENDENT REVIEW
    < MULTI-SITE / REPLICATED EVIDENCE
~~~

The hierarchy is contextual rather than absolute, but claim strength MUST NOT
exceed evidence strength.

## Governing rule

~~~text
PATTERN != PROOF
SELF_TEST != INDEPENDENT_AUDIT
REPOSITORY != EMPIRICAL_VALIDATION
CONFIDENCE != EVIDENCE
~~~
