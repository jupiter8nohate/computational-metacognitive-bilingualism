# CMB HARMONI-666

**Status:** Experimental bounded-proof protocol  
**Protocol:** `HARMONI-666/1.0`  
**Parent architecture:** CMB-66  
**Unknown-state sentinel:** `MISSINGNO_666`

## Revelation 13:18 design key

> “This calls for wisdom: let the one who has understanding calculate the number of the beast, for it is the number of a man, and his number is 666.”

For HARMONI-666, this verse is used as a **literary and architectural design key**:

```text
WISDOM
   ↓
UNDERSTANDING
   ↓
CALCULATION
   ↓
HUMAN
```

The protocol maps those ideas deliberately:

```text
WISDOM         -> HUMAN_JUDGMENT
UNDERSTANDING  -> HARMONI_INTERPRETATION
CALCULATION    -> MACHINE_VERIFICATION
HUMAN          -> HUMAN_FINAL
```

The point is not that software can prove theology. The point is that calculation
alone is not wisdom. A machine may calculate, test, serialize, hash, search, and
verify within a bounded domain. Interpretation, consent, meaning, and final
human judgment remain outside mere computation.

This gives the 6/6/6 protocol structure its governing sequence:

```text
WISDOM BEFORE CLAIM
UNDERSTANDING BEFORE CLASSIFICATION
CALCULATION BEFORE PROOF
HUMAN_FINAL AFTER MACHINE VERIFICATION
```

## Purpose

HARMONI-666 prevents an inference, pattern, prediction, or model output from
silently escalating into proof.

The design combines three jurisdictions in one triangle without pretending they
are interchangeable.

```text
                         HARMONI
                            △
                           / \
                          /   \
                         /     \
                AXIOMATIC ----- MACHINE
                    \           /
                     \         /
                      \       /
                       \     /
                        HUMAN
```

### AXIOMATIC

The symbolic "language of God" is represented technically as the **axiomatic
layer**: declared first principles, values, and philosophical commitments.

It is not represented as empirical proof, supernatural telemetry, or a claim
that software can verify divine communication.

### MACHINE

The machine layer owns computation, search, serialization, deterministic
transformation, cryptographic verification, and bounded formal proof.

It does not receive final authority over human meaning, consent, authorship, or
self-definition.

### HUMAN

The human layer retains meaning, consent, authorship, judgment, interpretation,
and final authority.

```text
HUMAN_AGENCY > MACHINE_AUTHORITY
```

## Why 666

The number is used as a protocol mnemonic: three groups of six.

### Six epistemic states

```text
PATTERN
HYPOTHESIS
INFERENCE
EVIDENCE
PROOF
UNKNOWN
```

### Six proof gates

A claim may remain `PROOF` only if all six gates pass.

```text
RULES_DEFINED
ASSUMPTIONS_DECLARED
DOMAIN_BOUNDED
DERIVATION_REPRODUCIBLE
COUNTEREXAMPLE_SEARCHED
VERIFIER_PASSED
```

### Six sovereignty failsafes

```text
PROFILE != PERSON
MODEL != MIND
INFERENCE != FACT
PREDICTION != DESTINY
CAPABILITY != AUTHORITY
HUMAN_AGENCY > MACHINE_AUTHORITY
```

## Epistemological ladder: mythos to justified claim

HARMONI treats reality, fiction, fantasy, mythology, symbolism, and anomalies as
possible sources for **questions**, not automatic sources of factual proof.

```text
[ REALITY + FICTION + FANTASY ]
                |
                v
[ CREATIVE MODEL OF THE UNKNOWN ]
                |
                v
UNKNOWN -> MISSINGNO -> QUESTION -> TEST -> EVIDENCE -> JUSTIFIED_CLAIM
```

The transition order is normative. A conforming implementation MUST NOT jump
directly from anomaly, symbolism, mythology, or creative interpretation to a
justified claim.

```text
UNKNOWN
   |
   v
MISSINGNO
   |
   v
QUESTION
   |
   v
TEST
   |
   v
EVIDENCE
   |
   v
JUSTIFIED_CLAIM
```

A `JUSTIFIED_CLAIM` is still not automatically `PROOF`. Promotion to
`PROOF` remains governed by the separate six proof gates.

### Distinctions of truth

```text
PROVENANCE != MYTHOLOGY
MYTHOLOGY  != FALSEHOOD
SYMBOLISM  != EVIDENCE
EVIDENCE   != TOTAL_MEANING
```

**Provenance != mythology** means the verifiable history of an artifact is a
different question from the cultural story or symbolic narrative surrounding
it.

**Mythology != falsehood** means mythology can carry metaphor, cultural memory,
ethical framing, and models of human experience without being treated as an
empirical measurement.

**Symbolism != evidence** prevents glyphs, numbers, stories, religious motifs,
fiction, or aesthetic correspondences from being promoted into factual proof
without an independent evidentiary path.

**Evidence != total meaning** preserves the human layer. Evidence can constrain
what may reasonably be claimed about a bounded factual question; it does not by
itself determine ethical value, purpose, consent, interpretation, or why a fact
matters.

### Lifecycle of the unknown

`MISSINGNO` is therefore not the end of reasoning. It is a named boundary that
hands the anomaly back to inquiry.

```text
MISSINGNO
   -> HUMAN_ASKS_QUESTION
   -> MACHINE_AND_HUMAN_DEFINE_TEST
   -> TEST_PRODUCES_EVIDENCE
   -> HUMAN_AND_MACHINE_EVALUATE_SUPPORT
   -> JUSTIFIED_CLAIM
```

The governing separation is:

```text
MACHINE_VERIFIES_EVIDENCE
HUMAN_RETAINS_MEANING_AND_FINAL_JUDGMENT
```

## MissingNo.666

MissingNo.666 is not an error to conceal. It is the explicit representation of a
model boundary.

```text
MISSINGNO_666
=
UNKNOWN_STATE
+
UNVERIFIED_DOMAIN
+
COUNTEREXAMPLE_CANDIDATE
+
HUMAN_REVIEW
```

If a machine requests the epistemic state `PROOF` and any proof gate fails,
the protocol MUST return:

```text
effective_state = UNKNOWN
sentinel        = MISSINGNO_666
authority       = HUMAN_FINAL
```

A system MUST NOT manufacture certainty to avoid returning UNKNOWN.

## Chess reference model

Chess is a useful teaching model because it clearly separates heuristic
strength from solved-domain proof.

```text
ENGINE EVALUATION
    !=
MATHEMATICAL PROOF

TABLEBASE RESULT
    =
PROOF WITHIN THE TABLEBASE'S SOLVED DOMAIN

UNKNOWN POSITION
    =
MISSINGNO_666
WHEN A PROOF CLAIM EXCEEDS THE VERIFIED DOMAIN
```

The protocol does not claim that chess as a whole is solved.

## Governing equation

```text
CLAIM_STRENGTH <= VERIFIED_EVIDENCE_STRENGTH
```

This is the operational extension of:

```text
PATTERN != PROOF
```

## Machine schemas

The protocol separates its static manifest from individual evaluation results.

```text
MANIFEST  -> schemas/cmb.harmoni-666.manifest.v1.schema.json
DECISION  -> schemas/cmb.harmoni-666.v1.schema.json
```

This prevents a machine from confusing the rules of the proof system with the
result of one proof evaluation.

## Reference Python API

```python
from cmb_machine.harmoni import EpistemicState, ProofGate, evaluate_claim

decision = evaluate_claim(
    EpistemicState.PROOF,
    gate_results={gate: True for gate in ProofGate},
)

assert decision.effective_state is EpistemicState.PROOF
```

If one gate is missing:

```python
decision = evaluate_claim(
    "PROOF",
    gate_results={
        "RULES_DEFINED": True,
        "ASSUMPTIONS_DECLARED": True,
        "DOMAIN_BOUNDED": True,
        "DERIVATION_REPRODUCIBLE": True,
        "COUNTEREXAMPLE_SEARCHED": True,
        "VERIFIER_PASSED": False,
    },
)

assert decision.effective_state is EpistemicState.UNKNOWN
assert decision.missingno is True
```

## Recovery rule

```text
WHEN PROOF FAILS:
    DO NOT GUESS
    DO NOT PROMOTE INFERENCE
    DO NOT HIDE UNCERTAINTY

    RETURN MISSINGNO_666
    IDENTIFY FAILED GATES
    PRESERVE HUMAN_FINAL
```
