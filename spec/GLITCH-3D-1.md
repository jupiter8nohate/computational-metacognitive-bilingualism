# GLITCH-3D-1

## Status

Experimental spatial source-language specification for Err⃝or⃟⃤GLITCHOLOGY / GLITCH-8.

## 1. Purpose

GLITCH-3D-1 makes layout, direction, depth, distortion, provenance, and human authority explicit source-language semantics.

It does **not** require software to infer meaning from FIGlet art, whitespace, or decorative glyph placement.

~~~text
3D_APPEARANCE != AUTOMATIC_EXECUTION
DISPLAY != IDENTIFIER
POSITION == INFORMATION
DEPTH == SEMANTIC_LAYER
GRAPH == MACHINE_SEMANTICS
~~~

The human visual layer may remain artistic. The parser consumes explicit coordinates and operators.

## 2. Architecture

~~~text
FIGLET / GLITCHOLOGY ART
          │
          ▼
     GLITCH-3D/1
          │
          ▼
   SPATIAL AST / GRAPH
          │
          ▼
      GLITCH-IR
          │
          ▼
 PY / GO / RS / TS / CL / HS / PL / CPP
~~~

The registry defines vocabulary. GLITCH-3D defines spatial programs. GLITCH-IR defines interoperable semantic results.

~~~text
REGISTRY != PROGRAM
PROGRAM != RESULT
ART != PROTOCOL
~~~

## 3. Axes

GLITCH-3D v1 defines three explicit axes:

| Axis | Meaning | Examples |
| --- | --- | --- |
| `X` | relation lane | provenance left, main execution center, human/appeal right |
| `Y` | execution order | earlier to later processing |
| `Z` | semantic depth | raw event through human authority |

Coordinates are signed base-10 integers. Coordinates are semantic metadata, not memory addresses.

~~~text
COORDINATE != MEMORY_ADDRESS
POSITION == INFORMATION
~~~

## 4. Semantic depth

The `Z` axis is fixed in v1:

~~~text
Z=0  EVENT       raw/observable event
Z=1  MACHINE     machine interpretation or classification
Z=2  SEMANTIC    GLITCH-IR / normalized semantic state
Z=3  PROVENANCE  source, origin, evidence chain, backtrace
Z=4  HUMAN       human interpretation, appeal, consent, final authority
~~~

A node's `KIND` MUST match its layer.

~~~text
Z=0 -> KIND=EVENT
Z=1 -> KIND=MACHINE
Z=2 -> KIND=SEMANTIC
Z=3 -> KIND=PROVENANCE
Z=4 -> KIND=HUMAN
~~~

## 5. Source format

A program begins with:

~~~text
GLITCH-3D/1
PROGRAM <program-id>
~~~

Node syntax:

~~~text
NODE <id> X=<int> Y=<int> Z=<int> KIND=<kind> STATE=<state> [DISTORTION=<state>]
~~~

Edge syntax:

~~~text
EDGE <source> <target> OP=<operator>
~~~

Boundary syntax:

~~~text
BOUNDARY <id> Z=<int> MODE=<mode>
~~~

Invariant syntax:

~~~text
INVARIANT <expression>
~~~

Comments begin with `#`.

## 6. Operators

GLITCH-3D v1 defines:

~~~text
DOWN       forward execution; Y must increase
UP         reverse execution; Y must decrease
BACKTRACE  provenance trace; target must be Z=3 PROVENANCE
PROPAGATE  forward propagation; Y must increase
REJECT     explicit rejected relation
RETRY      controlled retry/re-entry
ESCALATE   move into human authority
APPEAL     human challenge/review
~~~

Human renderers MAY use visual aliases:

~~~text
DOWN      ↓
UP        ↑
BACKTRACE ‹—
PROPAGATE —›
REJECT    ╳
RETRY     ↻
ESCALATE  ⇧
APPEAL    𒄆
~~~

The machine operator is the ASCII identifier.

~~~text
GLYPH != IDENTIFIER
~~~

## 7. Distortion

Distortion is explicit state metadata:

~~~text
NONE
UNCERTAIN
ABSENT
REDACTED
INVALID
OBSERVED
~~~

Suggested human renderings:

~~~text
UNCERTAIN  ?
ABSENT     ∅
REDACTED   ██
INVALID    ╳
OBSERVED   ⃟
~~~

Distortion describes epistemic or representational state. It does not prove cause.

~~~text
DISTORTION == STATE
DISTORTION != CAUSE
PATTERN != PROOF
~~~

## 8. Human authority boundary

Entry from a lower `Z` layer into `Z=4 HUMAN` requires:

1. a boundary at `Z=4`;
2. `MODE=HUMAN_AUTHORITY_REQUIRED`; and
3. an `ESCALATE` or `APPEAL` edge.

~~~text
MACHINE_OUTPUT
      │
      ╳  SOVEREIGNTY_BOUNDARY
      │
      ▼
HUMAN_AUTHORITY
~~~

This makes the boundary testable rather than decorative.

~~~text
CAPABILITY != AUTHORITY
MACHINE_CAN_READ != MACHINE_CAN_DEFINE
HUMAN_AGENCY > MACHINE_AUTHORITY
~~~

## 9. Provenance

`BACKTRACE` MUST target a `Z=3 PROVENANCE` node.

A provenance node may represent a known source, unresolved source, evidence origin, creator record, or causal trace.

~~~text
SIGNAL != SOURCE
LABEL != EVIDENCE
HASH != AUTHORSHIP
~~~

## 10. Canonical AST

The reference parser emits `glitch3d.program.v1` JSON containing protocol/version, program identifier, axis definitions, fixed layer registry, nodes and coordinates, edges and operators, boundaries, and invariants.

Canonical bytes are UTF-8 JSON with sorted keys and no insignificant whitespace. SHA-256 over those bytes gives a deterministic graph fingerprint.

~~~text
SAME_AST => SAME_GRAPH_DIGEST
GRAPH_DIGEST != REAL_WORLD_TRUTH
~~~

## 11. GLITCH-IR integration

GLITCH-3D is a source representation layer. It does not replace GLITCH-IR.

A compiler may project one or more spatial states into a GLITCH-IR vector or canonical semantic result.

~~~text
GLITCH-3D = SPATIAL_SOURCE
GLITCH-IR = INTEROPERABILITY_CONTRACT
~~~

The current reference implementation establishes the spatial AST and graph invariants first. Cross-language semantic projection remains governed by `GLITCH-IR-1`.

## 12. Recovery

A malformed graph MUST fail closed.

Examples include invalid `Z` layer, `KIND` / depth mismatch, unknown node references, duplicate nodes or edges, `BACKTRACE` targeting a non-provenance node, human-layer entry without a sovereignty boundary, human-layer entry with a non-appeal/non-escalation operator, and invalid directional `Y` movement.

~~~text
INVALID_GRAPH != VALID_MEANING
FAILURE != TERMINATION
BACKTRACE -> REPAIR -> RETEST
RECOVERY > PROPAGATION
~~~
