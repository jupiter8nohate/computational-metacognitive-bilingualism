# Living Book and Versioned Autobiography Protocol

**Applies to:** CMB, Err ⃝or⃟⃤ GLITCHOLOGY, autobiographical/canonical writing, and related public archival material.

## Purpose

Git is used here not only as source control but as a transparent record of how an authored body of work changes over time.

The repository may contain living books, language specifications, manifestos, autobiographical material, research notes, and executable reference implementations. Their histories should remain inspectable without pretending that every revision represents a new person or that every contributor owns the narrative.

```text
VERSION_HISTORY != COMPLETE_IDENTITY
CORRECTION != OWNERSHIP
CONTRIBUTION != AUTHORSHIP_OF_THE_WHOLE
```

## Semantic versioning for authored works

Use semantic-versioning language as an editorial convention:

### MAJOR

Use for a foundational structural change, such as:

- a new language architecture;
- a major redefinition of canonical scope;
- a major book restructuring;
- a backwards-incompatible registry/schema change.

### MINOR

Use for additive evolution, such as:

- a new chapter;
- a new glyph family;
- a new philosophical concept;
- a new documented historical period;
- a backwards-compatible feature.

### PATCH

Use for corrective maintenance, such as:

- typos;
- broken links;
- citation corrections;
- formatting repairs;
- non-semantic metadata fixes.

```text
PAST_VERSION != PRESENT_SELF
CHANGE != AUTOMATIC_CONTRADICTION
HISTORY_REMAINS_INSPECTABLE
```

## Pull requests

Pull requests may propose:

- factual corrections;
- citations;
- technical fixes;
- accessibility improvements;
- registry additions;
- documentation improvements; and
- clearly marked interpretive suggestions.

The creator retains final authority over autobiographical voice, intended meaning, and canonical acceptance.

```text
PUBLIC_CAN = {
  SUGGEST,
  CITE,
  QUESTION,
  CORRECT_VERIFIABLE_FACT
}

AUTHOR_RETAINS = {
  VOICE,
  MEANING,
  SELF_DEFINITION,
  CANONICAL_ACCEPTANCE
}
```

## Issues as interactive footnotes

Issues may function as public annotations for:

- factual correction requests;
- source requests;
- questions about chapters;
- glyph proposals;
- requests for clarification;
- research challenges; and
- contradictions requiring review.

An issue is not itself canonical text.

```text
ISSUE != CANON
PR != ACCEPTANCE
MERGE = REPOSITORY_DECISION
```

## Evidence discipline

Autobiographical and historical corrections should distinguish:

- creator declaration;
- primary source;
- independent source;
- inference;
- allegation;
- interpretation; and
- unknown.

```text
MEMORY != TRUTH
PATTERN != PROOF
CLAIM_STRENGTH <= EVIDENCE_STRENGTH
```

## Recovery

Git history should make editorial recovery straightforward:

```text
BAD_CHANGE
  -> IDENTIFY
  -> REVERT_OR_PATCH
  -> DOCUMENT
  -> VERIFY
  -> CONTINUE
```

Do not rewrite published history merely to make the record look cleaner. Correct it transparently.

## Relationship to the public profile

A GitHub profile README can act as the front door, while this repository remains the deeper archive.

Recommended hierarchy:

```text
PROFILE README
  -> CMB
  -> Err ⃝or⃟⃤ GLITCHOLOGY
  -> LIVING BOOKS
  -> GLYPH REGISTRY
  -> CREATIVE COGNITIVE SIGNATURE
  -> PROVENANCE
  -> RELEASE HISTORY
```

Git tracks the history.

Humans determine the meaning.
