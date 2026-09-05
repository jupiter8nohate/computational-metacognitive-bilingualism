# GLITCH-8 Living Registry

GLITCH-8 is designed as a registry-driven language.

The canonical source of truth is:

src/cmb_glitch8/glyphs.v1.json

The book and generated glyph reference are human-readable views of that registry.

## Authoring cycle

~~~text
NEW_GLYPH
↓
DEFINE
↓
VALIDATE
↓
REGISTER
↓
VERSION
↓
LOAD
↓
PARSE
↓
GENERATE_REFERENCE
~~~

## Add a glyph

1. Copy the example definition:

~~~text
examples/glitch8/new-glyph.example.json
~~~

2. Edit the glyph, name, category, semantic key, definition, CMB invariant, machine semantics, human semantics, runtime behavior, example, version, and status.

3. Validate the current registry:

~~~bash
glitch8 glyph validate
~~~

4. Add the definition:

~~~bash
glitch8 glyph add examples/glitch8/new-glyph.example.json \
  --reference-output books/GLITCH8_GLYPH_REFERENCE.md
~~~

When a glyph is added successfully, the registry language version receives a patch bump.

## Explain a glyph

~~~bash
glitch8 glyph explain "▂▃▄▅▆▇▉"
~~~

JSON form:

~~~bash
glitch8 glyph explain "▂▃▄▅▆▇▉" --json
~~~

## List glyphs

~~~bash
glitch8 glyph list
glitch8 glyph list --category uncertainty
glitch8 glyph list --status experimental
~~~

## Parse a GLITCH-8 statement

~~~bash
glitch8 statement parse "⁇ [GO] profile_prediction :: UNVERIFIED :: HUMAN_REVIEW"
~~~

Canonical syntax:

~~~text
GLYPH [RUNTIME] CLAIM :: STATE :: AUTHORITY
~~~

Supported runtime tags:

~~~text
[PY] Python
[RS] Rust
[GO] Go
[TS] TypeScript
[PL] Prolog
[HS] Haskell
[CL] Common Lisp
[C]  C
[G8] GLITCH-8 semantic layer
~~~

## Build the generated reference

~~~bash
glitch8 reference build
~~~

or:

~~~bash
python scripts/generate_glitch8_reference.py
~~~

The generated file is:

books/GLITCH8_GLYPH_REFERENCE.md

Do not hand-maintain duplicate canonical definitions in several files.

~~~text
REGISTRY = SOURCE_OF_TRUTH
BOOK = HUMAN_VIEW
PARSER = MACHINE_VIEW
~~~

## Collision rule

Every canonical glyph needs a unique semantic_key.

If a proposed glyph means exactly the same thing as an existing glyph, prefer an alias.

~~~text
NEW_SYMBOL + SAME_MEANING
→ ALIAS

NEW_SYMBOL + DISTINCT_MEANING
→ NEW_GLYPH
~~~

This is intentional.

~~~text
CATEGORY != IDENTITY
PATTERN != PROOF
PROFILE != PERSON
MODEL != MIND
HUMAN_AGENCY > MACHINE_AUTHORITY
~~~

## Status lifecycle

~~~text
experimental
↓
proposed
↓
canonical
↓
deprecated
↓
retired
~~~

A new glyph does not need to become canonical immediately.

## Technical boundary

The registry gives glyphs formal GLITCH-8 semantics and makes them loadable by the reference implementation.

A registry entry does not, by itself, create legal authority, operating-system privileges, cryptographic proof, or enforcement outside software that explicitly implements GLITCH-8.
