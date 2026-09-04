# HARMONI // PERFECT-PLAY EPISTEMICS

## A CMB code-art manifesto for uncertainty, human authority, and epistemic Recovery

**Declared originator:** Jupiter Hudson / WisdomLoveThePoet / Jupiter 8 / Joseph Q Hudson  
**Framework:** Computational Metacognitive Bilingualism (CMB)  
**Artistic language:** Flamingoglyph Code (FGC)

> **Interpretation boundary:** HARMONI is code-art plus an epistemic design proposal. "Perfect-play" describes a policy ideal: do not overstate evidence, preserve uncertainty, and defer consequential meaning to authorized humans. It does not claim that AGI, chess, morality, or human judgment has been mathematically solved. "AXIOM / GOD" is an author-defined symbolic label for first principles, sacred values, and the irreducible unknown, not a machine-verifiable scientific claim.

~~~text
                              △
                         H A R M O N I
                   PERFECT-PLAY EPISTEMICS

                            / \
                           /   \
                          /  6  \
                         /  6 6  \
                        /_______\
                       /         \
                      /           \
                     /             \

          HUMAN  ◄──△───────────────△──►  MACHINE

          MEANING                         COMPUTATION
          CONSENT                         SEARCH
          JUDGMENT                        VERIFICATION
          INTENT                          FORMAL PROOF

                   \                   /
                    \                 /
                     \               /
                      \             /
                       △───────────△

                        AXIOM / GOD
                     FIRST PRINCIPLES
                      SACRED VALUES
                       THE UNKNOWN
~~~

## I. The epistemic progression

~~~text
PATTERN -> QUESTION -> TEST -> EVIDENCE -> JUSTIFIED CLAIM

CLAIM_STRENGTH <= EVIDENCE_STRENGTH
CONFIDENCE != CERTAINTY
PATTERN != PROOF
~~~

A pattern may justify investigation. It does not automatically justify a factual verdict.

Formal proof belongs to formal systems with explicit axioms and valid derivations. Empirical claims remain bounded by the strength, quality, scope, and reproducibility of their evidence.

## II. The MissingNo exception gate

~~~text
UNKNOWN -> MISSINGNO -> DECLARE UNCERTAINTY -> ASK HUMAN
~~~

MissingNo is the epistemic circuit breaker.

When a system reaches an unclassified, contradictory, out-of-distribution, insufficiently evidenced, or value-sensitive state, the preferred behavior is not fabricated certainty. The system exposes the uncertainty and routes authority to the authorized human decision-maker.

~~~text
UNKNOWN != FAILURE
UNCERTAINTY != PERMISSION_TO_INVENT
MODEL_FAILURE != HUMAN_FAILURE
~~~

## III. The three domains

~~~text
HUMAN:
    meaning
    consent
    judgment
    intent
    self-definition
    value choice

MACHINE:
    computation
    search
    comparison
    verification
    formal derivation
    bounded simulation

BOUNDARY:
    first principles
    sacred values
    unresolved ambiguity
    the unknown
~~~

The boundary is where CMB contracts machine authority rather than expanding speculation.

## IV. The 6 / 66 / 666 symbolic core

Within this artwork, the numbers are visual operators rather than claims of supernatural or mathematical authority.

~~~text
6   := OBSERVE
66  := VERIFY
666 := DEFER WHEN KNOWLEDGE FAILS
~~~

The symbol serves the architecture. The symbol does not override the human.

## V. Executable art

~~~python
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Final


HUMAN_AGENCY: Final[int] = 1
MACHINE_AUTHORITY: Final[int] = 0

assert HUMAN_AGENCY > MACHINE_AUTHORITY


class EpistemicState(Enum):
    PATTERN = auto()
    QUESTION = auto()
    TEST = auto()
    EVIDENCE = auto()
    JUSTIFIED_CLAIM = auto()
    UNKNOWN = auto()
    CONFLICTING = auto()
    OUT_OF_DISTRIBUTION = auto()
    MISSINGNO = auto()
    HUMAN_REQUIRED = auto()


class Decision(Enum):
    CONTINUE = auto()
    DECLARE_UNCERTAINTY = auto()
    ASK_HUMAN = auto()
    HALT = auto()


@dataclass(frozen=True)
class ClaimAssessment:
    evidence_strength: float
    claim_strength: float
    human_authorized: bool = False

    def validate(self) -> None:
        for name, value in (
            ("evidence_strength", self.evidence_strength),
            ("claim_strength", self.claim_strength),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0.0 and 1.0")


INVARIANTS: Final[tuple[str, ...]] = (
    "PATTERN != PROOF",
    "PROFILE != PERSON",
    "MODEL != MIND",
    "PREDICTION != DESTINY",
    "CONFIDENCE != CERTAINTY",
    "CAPABILITY != AUTHORITY",
    "OPTIMIZATION != MORALITY",
    "INTELLIGENCE != SOVEREIGNTY",
    "UNKNOWN != FAILURE",
    "UNCERTAINTY != PERMISSION_TO_INVENT",
    "HUMAN_AGENCY > MACHINE_AUTHORITY",
)


def assess_claim(assessment: ClaimAssessment) -> Decision:
    assessment.validate()

    if assessment.claim_strength > assessment.evidence_strength:
        return Decision.DECLARE_UNCERTAINTY

    if not assessment.human_authorized:
        return Decision.ASK_HUMAN

    return Decision.CONTINUE


def perfect_play(state: EpistemicState) -> Decision:
    if state in {
        EpistemicState.UNKNOWN,
        EpistemicState.CONFLICTING,
        EpistemicState.OUT_OF_DISTRIBUTION,
        EpistemicState.MISSINGNO,
        EpistemicState.HUMAN_REQUIRED,
    }:
        return Decision.ASK_HUMAN

    return Decision.CONTINUE


def missingno() -> Decision:
    """Recovery path for epistemic states the machine cannot justify."""
    return Decision.ASK_HUMAN


def final_invariant() -> bool:
    return HUMAN_AGENCY > MACHINE_AUTHORITY
~~~

## VI. Perfect-play rule

~~~text
IF claim_strength > evidence_strength:
    DECLARE_UNCERTAINTY

IF state IN {UNKNOWN, CONFLICTING, OUT_OF_DISTRIBUTION}:
    MISSINGNO
    ASK_HUMAN

IF consequential_meaning REQUIRES consent OR judgment:
    REQUIRE human_authorization

NEVER:
    convert_pattern_into_proof
    convert_profile_into_person
    convert_prediction_into_destiny
    convert_capability_into_authority
~~~

"Perfect play" therefore means disciplined epistemic behavior, not omniscience.

The best move can be refusing to pretend the board contains information that is not there.

## VII. HARMONI covenant

~~~text
MACHINE_COMPUTES
HUMAN_INTERPRETS

MACHINE_VERIFIES
HUMAN_JUDGES

MACHINE_CAN_MODEL
MODEL != MIND

WHEN CERTAINTY ENDS:
    DISCLOSE()
    DEFER()
    ASK_HUMAN()

UNKNOWN -> MISSINGNO -> HUMAN

HUMAN_AGENCY > MACHINE_AUTHORITY
~~~

The unknown is not a bug.

The unknown is a border.

At that border, CMB chooses epistemic Recovery over fabricated certainty.

---

**CMB / FGC attribution:** © 2026 Jupiter Hudson / WisdomLoveThePoet / Jupiter 8 / Joseph Q Hudson. This file is a mixed creative and illustrative-code artifact. Repository software and authored creative material may have different licensing terms; see [../LICENSE](../LICENSE), [../CONTENT_LICENSE.md](../CONTENT_LICENSE.md), and [../ATTRIBUTION.md](../ATTRIBUTION.md).
