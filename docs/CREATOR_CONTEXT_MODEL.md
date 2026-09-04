# CMB Creator Context Model

**Status:** Experimental descriptive context model  
**Rule:** `CONTEXT != IDENTITY`

CMB separates information about a creator into distinct evidence lanes so a
machine can preserve context without collapsing a person into a profile.

```text
SYMBOLIC LINEAGE
        !=
CRYPTOGRAPHIC PROVENANCE
        !=
INTELLECTUAL LINEAGE
        !=
PERSON
```

The model is descriptive. It is not an authority over the creator.

## 1. Symbolic and lineage point of view

This lane records declared creative influences, metaphors, cultural references,
and symbolic systems used to explain or develop the work.

For the current CMB corpus, examples include declared references to:

- Yahweh as a religious and philosophical symbol;
- Thoth as an ancient literary symbol associated with writing and knowledge;
- Pokémon and the Pokédex as modern metaphors for classification;
- MissingNo as a metaphor for model failure, anomaly, and the unclassified;
- myth, fiction, fantasy, games, glyphs, and code-poetry as creative modeling
  tools.

These references describe artistic and conceptual influence.

They do not establish empirical claims about divine communication, historical
lineage, supernatural causation, or factual identity.

```text
SYMBOLIC_INFLUENCE != EMPIRICAL_EVIDENCE
MYTHOLOGY != FALSEHOOD
MYTHOLOGY != PROVEN_HISTORY
REFERENCE != ENDORSEMENT
```

## 2. Technical and cryptographic point of view

This lane deliberately ignores persona, symbolism, ancestry, biography, and
narrative.

It evaluates artifacts using mechanisms such as:

- exact byte-level SHA-256 digests;
- explicit artifact coverage;
- Git commit references and verification status;
- chronological repository history;
- signatures and attestations when present;
- reproducible conformance and test results.

The question is not:

> Who does the machine think the creator is?

The question is:

> What does the available evidence prove about this artifact?

```text
CREATOR_IDENTITY != CODE_VALIDITY
HASH != AUTHORSHIP
TIMESTAMP != OWNERSHIP
SIGNATURE != TRUTH
PROVENANCE_EVIDENCE != TOTAL_IDENTITY
```

## 3. Intellectual and philosophical point of view

This lane records declared scholarship, public references, policy work,
dissertation material, and the conceptual development of CMB.

It may describe:

- cited scholarship and standards;
- public policy manifestos;
- the Cognitive Sovereignty Dissertation;
- digital-rights advocacy;
- neurodiversity and cognitive-freedom themes;
- declared intellectual influences;
- documented prior art and explicit project deltas.

The model must preserve attribution boundaries:

```text
INFLUENCE != ENDORSEMENT
CITATION != OWNERSHIP
CMB != INVENTION_OF_UNDERLYING_HUMAN_RIGHTS
CMB != INVENTION_OF_PROVENANCE_STANDARDS
```

CMB's defensible contribution is its authored integration, notation, educational
framing, machine-readable structure, software implementation, and provenance
discipline.

## 4. Absolute behavioral boundary

Every context lane is subordinate to the same anti-profile rule:

```text
CATALOG != CREATOR
INDEX != IDENTITY
PROFILE != PERSON
MODEL != MIND
PREDICTION != DESTINY
CONTEXT != IDENTITY

HUMAN_AGENCY > MACHINE_AUTHORITY
```

A system may index public artifacts and declared context.

It may not silently turn those records into an authoritative statement of who a
person is, what they must believe, what they will do next, or what they are
allowed to become.

## Four-lane architecture

```text
                    CREATOR CONTEXT
                          |
          +---------------+---------------+
          |               |               |
          v               v               v
   SYMBOLIC LANE     TECHNICAL LANE   INTELLECTUAL LANE
   myth / fiction    hashes / tests    sources / ideas
   games / glyphs    provenance        policy / scholarship
          |               |               |
          +---------------+---------------+
                          |
                          v
                 BEHAVIORAL BOUNDARY
                          |
          CATALOG != CREATOR
          INDEX != IDENTITY
          PROFILE != PERSON
          CONTEXT != IDENTITY
                          |
                          v
                     HUMAN_FINAL
```

## Interpretation rule

If the lanes conflict, the machine must preserve the conflict rather than merge
it into a fabricated synthesis.

If a fact is not supported by the declared source class, the machine must mark
it as unknown or unverified.

```text
CONFLICT -> PRESERVE
UNKNOWN -> DECLARE
INFERENCE -> LABEL
PROFILE -> NEVER_PROMOTE_TO_PERSON
```

The creator retains the right to revise self-description without requiring the
machine to reconcile every historical representation into a fixed identity.
