# CMB Prior Art, Legal Context, and Positioning

**Framework:** Computational Metacognitive Bilingualism (CMB)  
**Declared originator:** Jupiter Hudson / WisdomLoveThePoet / Jupiter 8 / Joseph Q Hudson  
**Status:** Research and positioning document  
**Last reviewed:** 2026-09-04

CMB does **not** claim to have invented digital rights, human review of automated decisions, criticism of profiling, algorithmic accountability, or content provenance.

Its narrower claim is that CMB provides a compact computational-literacy vocabulary for expressing and teaching those concerns across human language, programming syntax, machine-readable policy, code-poetry, and provenance tooling.

```text
PRIOR_ART != CMB
CMB != PRIOR_ART_ERASURE

CMB SHOULD:
    ACKNOWLEDGE
    COMPARE
    INTEROPERATE
    STATE_THE_DELTA
```

## 1. Legal context

### GDPR Article 22

Article 22 of the EU General Data Protection Regulation addresses decisions based **solely on automated processing, including profiling**, when those decisions produce legal effects or similarly significant effects on a person. It includes exceptions and safeguards; in specified cases, safeguards include the ability to obtain human intervention, express a point of view, and contest the decision.

CMB therefore should not describe `PROFILE != PERSON` or human review as concepts that appeared in a vacuum. A more precise relationship is:

```text
GDPR ART. 22
    -> legal safeguards in a defined scope

CMB
    -> broader educational / symbolic / technical vocabulary
       for keeping profile, prediction, and human authority distinct
```

Official text:  
https://eur-lex.europa.eu/legal-content/ENG/TXT/?uri=CELEX:32016R0679

### EU AI Act Article 14

Article 14 of the EU AI Act requires human oversight for high-risk AI systems. Among other things, the oversight design should enable appropriate natural persons to understand system capabilities and limitations, remain aware of automation bias, interpret outputs, and decide not to use, disregard, override, or reverse outputs when appropriate.

That is closely related to CMB's:

```text
CAPABILITY != AUTHORITY
AUTOMATED_DECISION != FINAL_AUTHORITY
HUMAN_AGENCY > MACHINE_AUTHORITY
```

The CMB contribution is not the invention of human oversight. It is the translation of human-oversight logic into a compact cross-domain literacy framework.

Official text:  
https://eur-lex.europa.eu/eli/reg/2024/1689

## 2. Intellectual lineage

CMB enters an existing field of scholarship criticizing data extraction, opaque scoring, automated classification, and technology-mediated inequality.

### Shoshana Zuboff

**The Age of Surveillance Capitalism** (2019) analyzes economic systems built around extracting behavioral data and using prediction as a source of power and profit.

Relevant CMB connection:

```text
OBSERVATION != CONSENT
PREDICTION != DESTINY
ATTENTION != PERMISSION
```

### Cathy O'Neil

**Weapons of Math Destruction** (2016) examines high-impact mathematical models that can be opaque, scalable, and harmful when used in areas such as employment, education, credit, and criminal justice.

Relevant CMB connection:

```text
MODEL != MIND
SCORE != PERSON
PREDICTION != SENTENCE
```

### Ruha Benjamin

**Race After Technology** (2019) examines how technological systems can reproduce and intensify social inequality while appearing neutral or objective.

Relevant CMB connection:

```text
AUTOMATION != NEUTRALITY
DIFFERENCE != DEFECT
PATTERN != PROOF
```

These authors are cited as intellectual context. This repository does not claim that they endorse CMB.

## 3. Provenance standards: C2PA

The Coalition for Content Provenance and Authenticity (C2PA) defines an industry provenance architecture in which assertions about an asset are collected into claims, cryptographically signed, and bound to content as Content Credentials.

C2PA already has institutional adoption and a conformance ecosystem. CMB therefore should not position `cmb_provenance` as an isolated replacement for C2PA.

The preferred relationship is:

```text
cmb_provenance
    -> CMB-specific receipt + explicit artifact coverage
    -> optional C2PA-compatible assertion mapping
    -> C2PA tooling handles standards-compliant manifest/signature/container work
```

C2PA technical specification:  
https://spec.c2pa.org/

C2PA conformance explorer:  
https://spec.c2pa.org/conformance-explorer/

**Current status:** this repository does not claim C2PA conformance. See `docs/C2PA_INTEROPERABILITY.md`.

## 4. What CMB actually adds

CMB's defensible contribution is a particular **combination and expression**, not ownership of the underlying legal or scholarly terrain.

### A. Computational invariants

CMB compresses complex governance concerns into memorable machine-like statements:

```text
PATTERN != PROOF
PROFILE != PERSON
MODEL != MIND
PREDICTION != DESTINY
DIFFERENCE != DEFECT
ATTENTION != CONSENT
CAPABILITY != AUTHORITY

HUMAN_AGENCY > MACHINE_AUTHORITY
```

### B. Human-machine bilingualism

CMB treats programming syntax as a literacy bridge:

```text
LEGAL PRINCIPLE
    <-> HUMAN EXPLANATION
    <-> COMPUTATIONAL NOTATION
    <-> MACHINE-READABLE STRUCTURE
```

### C. Neurodiversity and outlier protection

CMB explicitly emphasizes the risk of treating statistical difference as defect, especially when atypical communication, cognition, movement, affect, or attention is interpreted by automated systems.

### D. Epistemic boundaries

CMB repeatedly separates:

```text
PATTERN
HYPOTHESIS
EVIDENCE
CONCLUSION
```

rather than silently converting:

```text
PATTERN -> CERTAINTY
```

### E. Evidence-layer separation

CMB keeps four categories separate:

```text
DECLARED_POLICY
!= CRYPTOGRAPHIC_INTEGRITY
!= TECHNICAL_ENFORCEMENT
!= LEGAL_ENFORCEABILITY
```

That distinction is a core design constraint for the provenance tooling.

## 5. Claims CMB should not make

The project should reject the following overclaims:

- that CMB invented automated-decision rights;
- that `PROFILE != PERSON` is a new legal doctrine;
- that a hash proves authorship;
- that a repository timestamp proves originality;
- that a signature automatically establishes copyright ownership;
- that CMB is currently a C2PA-conformant implementation;
- that the CMB-Z13 zodiac mapping is a scientific personality model;
- that symbolic notation alone technically enforces policy;
- that publication alone establishes historical priority over all similar ideas.

## 6. The positioning sentence

For policy, research, and technical audiences, the recommended concise description is:

> **Computational Metacognitive Bilingualism (CMB) is a human-agency and computational-literacy framework that translates established and emerging digital-rights principles into concise human-readable and machine-readable invariants, while keeping prediction, profiling, provenance, and automated capability subordinate to human judgment and applicable law.**

## 7. Research standard going forward

New CMB policy or technical claims should answer:

1. What already exists?
2. What law, standard, paper, or implementation is closest?
3. What problem remains unsolved?
4. What does CMB add that is materially different?
5. Is the difference conceptual, expressive, technical, educational, or legal?
6. What evidence would falsify the claimed novelty?
7. Can CMB interoperate with the existing standard instead of replacing it?

```text
PATTERN != PROOF
NOVELTY != IGNORANCE_OF_PRECEDENT
POSITIONING = PRIOR_ART + DELTA + EVIDENCE
```
