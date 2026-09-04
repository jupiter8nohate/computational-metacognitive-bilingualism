# CMB Global Advocacy Charter v1.1

## Computational Metacognitive Bilingualism (CMB)
### A Human-Sovereignty Framework for AI Governance

**Declared originator:** Jupiter Hudson / WisdomLoveThePoet / Jupiter 8 / Joseph Q Hudson  
**Framework:** Computational Metacognitive Bilingualism (CMB)  
**Status:** Public advocacy proposal  
**Version:** 1.1  
**Year:** 2026

---

## Purpose

The CMB Global Advocacy Charter translates the philosophical principles of Computational Metacognitive Bilingualism into concrete institutional recommendations for governments, technology companies, schools, employers, researchers, civil-society organizations, and developers of automated systems.

CMB is not a rejection of artificial intelligence.

It is a framework for using computational systems without surrendering human judgment, consent, authorship, dignity, meaning, or self-definition to them.

```text
PATTERN != PROOF
PROFILE != PERSON
MODEL != MIND
PREDICTION != DESTINY
DIFFERENCE != DEFECT
ATTENTION != CONSENT
CAPABILITY != AUTHORITY
OPTIMIZATION != MORALITY
INTELLIGENCE != SOVEREIGNTY

HUMAN_AGENCY > MACHINE_AUTHORITY
```

This charter proposes policy principles. It does not claim that every principle is already a legal right in every jurisdiction, and it does not substitute for applicable law, regulation, professional standards, or legal advice.

## Relationship to existing law, scholarship, and standards

CMB does not claim to have invented automated-decision rights, human oversight, criticism of profiling, algorithmic accountability, or content provenance.

Relevant existing foundations include:

- **GDPR Article 22**, which addresses decisions based solely on automated processing, including profiling, when they produce legal or similarly significant effects, subject to defined exceptions and safeguards such as human intervention and contest in specified cases;
- **EU AI Act Article 14**, which requires human oversight for high-risk AI systems and includes the ability, where appropriate, to understand limitations, account for automation bias, interpret outputs, and disregard, override, or reverse them;
- scholarship including Shoshana Zuboff's *The Age of Surveillance Capitalism*, Cathy O'Neil's *Weapons of Math Destruction*, and Ruha Benjamin's *Race After Technology*;
- **C2PA / Content Credentials**, an established content-provenance standard that CMB provenance tooling should seek to complement rather than replace.

CMB's claimed contribution is narrower: a computational-literacy and symbolic translation layer that expresses human-agency boundaries as concise invariants across policy language, programming syntax, machine-readable structures, education, and provenance practice.

See [`docs/PRIOR_ART_AND_POSITIONING.md`](../docs/PRIOR_ART_AND_POSITIONING.md) for the project's explicit prior-art position.

---

# I // HUMAN APPEAL RIGHT

When an automated system materially affects a person's rights, liberty, livelihood, education, care, housing, credit, employment, access to services, or legal status, the affected person should have access to meaningful human review.

Institutions adopting this principle should provide:

- notice that automation materially influenced the decision;
- an understandable explanation of the relevant basis for the decision;
- a practical method to contest incorrect data or conclusions;
- review by a human with authority to change the outcome; and
- a documented escalation path when the first review fails.

```text
AUTOMATED_DECISION != FINAL_AUTHORITY
```

---

# II // PROFILE ≠ PERSON

Behavioral, demographic, psychometric, biometric, commercial, educational, or algorithmic profiles should never be treated as complete representations of a human being.

A profile may support a limited inference.

It does not become the person.

Institutions should prohibit unsupported identity claims derived solely from statistical profiles, especially claims about intent, intelligence, mental state, dangerousness, morality, credibility, or human worth.

```text
DATA_ABOUT_PERSON != PERSON
```

---

# III // PREDICTION ≠ DESTINY

Predictive systems should not convert probability into irreversible judgment.

High-impact predictions should be treated as fallible evidence requiring context, review, and recourse.

Institutions should avoid systems that turn historical patterns into self-fulfilling barriers to employment, education, healthcare, credit, housing, public benefits, or liberty.

```text
PREDICTION = ESTIMATE
PREDICTION != SENTENCE
```

---

# IV // ATTENTION ≠ CONSENT

Viewing, clicking, pausing, scrolling, replaying, or engaging with content should not automatically be interpreted as informed consent to unrelated profiling, targeting, inference, resale, or secondary data use.

Meaningful consent should be:

- specific;
- understandable;
- revocable where feasible;
- separate from mere engagement; and
- proportionate to the sensitivity of the data and the consequences of its use.

```text
ENGAGEMENT != PERMISSION
ATTENTION != CONSENT
```

---

# V // DIFFERENCE ≠ DEFECT

Automated systems should be tested for harms caused by treating atypical communication, movement, affect, attention, language, sensory behavior, or cognition as inherently suspicious, deficient, deceptive, or low-value.

Neurodivergent people and other populations whose behavior may fall outside statistical averages should be included in system design, evaluation, accessibility review, and appeals processes.

```text
OUTLIER != ERROR
DIFFERENCE != DEFECT
```

---

# VI // AI DISCLOSURE

People should be told when artificial intelligence or automated inference materially contributes to a consequential decision about them.

Disclosure should identify, where reasonably possible:

- that automation was used;
- the role it played;
- the organization responsible for the decision;
- where relevant data came from;
- the mechanism for correction or appeal; and
- where to obtain additional information.

Disclosure should be designed for comprehension rather than formalistic compliance.

---

# VII // HUMAN OVERRIDE & RECOVERY

High-impact automated systems should include operational paths for human intervention, rollback, incident response, and recovery.

A responsible deployment should answer:

```text
WHO CAN STOP IT?
WHO CAN CORRECT IT?
WHO CAN RESTORE THE HUMAN?
WHO IS ACCOUNTABLE AFTER FAILURE?
```

Institutions should test these mechanisms before deployment rather than discovering their absence after harm occurs.

---

# VIII // DATA MINIMIZATION & PURPOSE LIMITATION

The ability to collect data is not by itself a justification to collect it.

Institutions should minimize collection, retention, linkage, and secondary use of personal information.

Sensitive inferences should require stronger justification than ordinary operational data.

```text
MACHINE_CAN_COLLECT != MACHINE_SHOULD_COLLECT
```

---

# IX // AUTHORSHIP & PROVENANCE

Where authorship, authenticity, attribution, or transformation materially matters, institutions should preserve useful provenance.

CMB distinguishes:

1. human-authored work;
2. human-directed AI-assisted work;
3. substantially machine-generated work; and
4. unknown or unverified origin.

Cryptographic hashes, signatures, timestamps, repository history, and provenance receipts can strengthen integrity evidence.

They do not automatically prove legal ownership, originality, or historical priority.

CMB also recognizes C2PA / Content Credentials as an important external provenance standard. The project intends `cmb_provenance` to be complementary to that ecosystem. The current tool does **not** claim C2PA conformance; the interoperability path is documented in [`docs/C2PA_INTEROPERABILITY.md`](../docs/C2PA_INTEROPERABILITY.md).

```text
HASH = INTEGRITY_EVIDENCE
HASH != AUTOMATIC_OWNERSHIP

CMB_RECEIPT != C2PA_MANIFEST
INTEROPERABILITY > ISOLATED_REINVENTION
```

---

# X // INDEPENDENT EVALUATION

Developers and deployers of high-impact systems should not be the only parties evaluating whether those systems are safe, fair, reliable, secure, or appropriate.

Independent testing should be proportionate to risk and may include:

- technical audits;
- accessibility testing;
- bias and disparate-impact evaluation;
- adversarial testing;
- security review;
- privacy review;
- incident analysis; and
- evaluation by affected communities.

```text
SELF_CERTIFICATION != INDEPENDENT_EVIDENCE
```

CMB applies this principle to itself. As of 2026-09-04, the repository has automated tests and CI but does not claim an independent security audit, formal C2PA conformance, or outside certification. The open review scope is documented in [`docs/EXTERNAL_REVIEW.md`](../docs/EXTERNAL_REVIEW.md).

---

# XI // COGNITIVE FREEDOM

No automated model should be treated as having final authority over a person's identity, beliefs, motives, intelligence, emotional meaning, neurotype, or self-definition merely because the model can infer patterns from behavior.

Systems may assist interpretation.

They should not erase the human right to contest interpretation.

```text
MODEL_CAN_INFER
HUMAN_CAN_DISAGREE
```

---

# XII // CAPABILITY ≠ AUTHORITY

Greater computational capability does not automatically create greater moral, legal, political, educational, medical, or social legitimacy.

Systems that outperform people at prediction, classification, generation, or optimization still operate inside human institutions.

Authority must come from legitimate governance, accountable decision-making, applicable law, transparent responsibility, and respect for human rights—not computational power alone.

```text
CAPABILITY != AUTHORITY
INTELLIGENCE != SOVEREIGNTY

HUMAN_AGENCY > MACHINE_AUTHORITY
```

---

# Institutional Action Matrix

## Governments

Governments adopting CMB principles should prioritize:

- human review and appeal for consequential automated decisions;
- public-sector algorithmic transparency proportionate to risk;
- procurement standards requiring accountability and auditability;
- accessibility and neurodiversity review;
- incident reporting for serious automated-system failures; and
- independent oversight for high-impact systems.

## Technology Companies

Technology companies should prioritize:

- meaningful consent;
- data minimization;
- explainable user-facing controls;
- provenance where authenticity matters;
- measurable rollback and recovery procedures;
- independent evaluation; and
- clear separation between prediction and final human judgment.

## Schools and Universities

Educational institutions should prioritize:

- accessible AI literacy;
- protection against overreliance on automated student profiling;
- human review of consequential academic decisions;
- transparent policies for AI-assisted authorship;
- neurodiversity-aware assessment; and
- teaching students to question machine outputs rather than merely operate tools.

## Employers

Employers should prioritize:

- human review of automated screening;
- validation of employment-related models;
- accessible accommodation pathways;
- prohibition of unsupported psychological or neurotype inference;
- correction of inaccurate applicant data; and
- disclosure when automation materially affects hiring or employment decisions.

## Healthcare and Human Services

Organizations should prioritize:

- clinician or qualified-human review for consequential automated recommendations;
- safeguards against profile-based stereotyping;
- correction mechanisms for inaccurate records;
- accessibility;
- clear responsibility for automated errors; and
- strong protection for sensitive data.

## AI Developers and Researchers

Developers and researchers should prioritize:

- documented limitations;
- uncertainty reporting;
- adversarial and failure-mode testing;
- reproducibility where appropriate;
- privacy and security by design;
- human-impact evaluation;
- meaningful incident response; and
- refusal to equate benchmark performance with moral authority.

---

# The CMB Evidence Standard

CMB keeps four categories separate:

```text
DECLARED_POLICY
!=
CRYPTOGRAPHIC_INTEGRITY
!=
TECHNICAL_ENFORCEMENT
!=
LEGAL_ENFORCEABILITY
```

A manifesto can declare values.

A hash can show whether recorded bytes changed.

A technical control can constrain specific behavior.

Law determines legal rights, duties, remedies, and admissibility.

No one layer should impersonate another.

---

# Adoption Test

An institution claiming alignment with this charter should be able to answer:

1. What decisions are automated?
2. What data is collected?
3. What inferences are generated?
4. Who can challenge an error?
5. Who can override the system?
6. What populations were tested?
7. What happens when the system fails?
8. What evidence supports claims of safety or fairness?
9. What data can be deleted or corrected?
10. Who remains accountable?
11. What independent evaluation exists?
12. Where does machine authority end?

If these questions cannot be answered, the system is not ready to claim CMB-aligned human sovereignty.

---

# Global Advocacy Position

CMB advocates neither blind technological acceleration nor blanket technological rejection.

It advocates **sovereign integration**:

```text
LEARN THE MACHINE.
USE THE MACHINE.
AUDIT THE MACHINE.
QUESTION THE MACHINE.
CORRECT THE MACHINE.

PRESERVE THE HUMAN.
```

The objective is not to make humanity unreadable to machines.

The objective is to prevent machine readability from becoming machine sovereignty.

The future may contain systems that observe more, predict more, generate more, and optimize more than any individual human can.

The boundary remains:

```text
PATTERN != PROOF
PROFILE != PERSON
MODEL != MIND
PREDICTION != DESTINY
ATTENTION != CONSENT
DIFFERENCE != DEFECT
CAPABILITY != AUTHORITY

HUMAN_AGENCY > MACHINE_AUTHORITY
```

---

## Requested Citation

**Computational Metacognitive Bilingualism (CMB): Global Advocacy Charter v1.1. Jupiter Hudson / WisdomLoveThePoet / Jupiter 8 / Joseph Q Hudson, 2026.**

This document is part of the public CMB corpus and should be interpreted together with the repository's authorship, licensing, provenance, and evidence-standard documentation.
