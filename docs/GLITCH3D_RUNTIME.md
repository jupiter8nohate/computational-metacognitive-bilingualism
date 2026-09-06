# GLITCH-3D Runtime

GLITCH-3D turns the visual depth language of Err⃝or⃟⃤GLITCHOLOGY into an explicit spatial source format that software can parse without guessing at whitespace or decorative glyph placement.

~~~text
ART / FIGLET
     ↓
GLITCH-3D/1
     ↓
SPATIAL AST
     ↓
GLITCH-IR
     ↓
POLYGLOT CONFORMANCE
~~~

## Why the 3D layer matters

The 3D layer adds machine-readable spatial semantics:

- `X` = relation lane
- `Y` = execution order
- `Z` = semantic depth
- `DISTORTION` = explicit uncertainty / absence / redaction / invalidation / observation state
- `EDGE ... OP=` = control-flow or semantic relation
- `BOUNDARY` = authority/provenance constraints

~~~text
POSITION == INFORMATION
DEPTH == SEMANTIC_LAYER
GRAPH == MACHINE_SEMANTICS
3D_APPEARANCE != AUTOMATIC_EXECUTION
~~~

## Fixed depth model

~~~text
Z=0  EVENT       raw observable event
Z=1  MACHINE     machine interpretation
Z=2  SEMANTIC    normalized GLITCH / GLITCH-IR state
Z=3  PROVENANCE  source and evidence backtrace
Z=4  HUMAN       appeal, consent, judgment, self-definition
~~~

Coordinates are semantic metadata, not physical memory addresses.

## Example

~~~text
GLITCH-3D/1
PROGRAM source-fracture-3d

NODE event X=0 Y=0 Z=0 KIND=EVENT STATE=CLAIM_RECEIVED DISTORTION=OBSERVED
NODE model X=0 Y=1 Z=1 KIND=MACHINE STATE=VERIFIED_LABEL_PRESENT DISTORTION=UNCERTAIN
NODE semantic X=0 Y=2 Z=2 KIND=SEMANTIC STATE=CONTESTED DISTORTION=OBSERVED
NODE source X=-1 Y=3 Z=3 KIND=PROVENANCE STATE=SOURCE_UNKNOWN DISTORTION=ABSENT
NODE human X=1 Y=4 Z=4 KIND=HUMAN STATE=REVIEW_REQUIRED DISTORTION=OBSERVED

EDGE event model OP=DOWN
EDGE model semantic OP=DOWN
EDGE semantic source OP=BACKTRACE
EDGE semantic human OP=ESCALATE

BOUNDARY sovereignty Z=4 MODE=HUMAN_AUTHORITY_REQUIRED

INVARIANT VERIFIED_LABEL != VERIFIED_TRUTH
INVARIANT SIGNAL != SOURCE
INVARIANT HUMAN_AGENCY > MACHINE_AUTHORITY
~~~

## Operators

| Operator | Human rendering | Function |
| --- | --- | --- |
| `DOWN` | `↓` | forward execution |
| `UP` | `↑` | reverse execution |
| `BACKTRACE` | `‹—` | trace toward provenance/source |
| `PROPAGATE` | `—›` | forward propagation |
| `REJECT` | `╳` | reject a relation or equivalence |
| `RETRY` | `↻` | controlled retry |
| `ESCALATE` | `⇧` | move into human authority |
| `APPEAL` | `𒄆` | human challenge/review |

ASCII operator IDs are canonical. Glyph renderings are human-facing aliases.

## Distortion states

~~~text
NONE
UNCERTAIN  ?
ABSENT     ∅
REDACTED   ██
INVALID    ╳
OBSERVED   ⃟
~~~

Distortion records state. It does not assert why the state exists.

## Human authority boundary

A lower layer cannot silently cross into `Z=4 HUMAN`. The reference parser requires a `HUMAN_AUTHORITY_REQUIRED` boundary plus an `ESCALATE` or `APPEAL` edge.

~~~text
MACHINE_OUTPUT
      │
      ╳  SOVEREIGNTY_BOUNDARY
      │
      ▼
HUMAN_AUTHORITY

CAPABILITY != AUTHORITY
MACHINE_CAN_READ != MACHINE_CAN_DEFINE
HUMAN_AGENCY > MACHINE_AUTHORITY
~~~

## CLI

~~~bash
glitch8 3d validate examples/polyglot/glitchology_registry_3d_runtime/GLITCH_3D_SOURCE_FRACTURE.g3d
glitch8 3d parse examples/polyglot/glitchology_registry_3d_runtime/GLITCH_3D_SOURCE_FRACTURE.g3d
glitch8 3d render examples/polyglot/glitchology_registry_3d_runtime/GLITCH_3D_SOURCE_FRACTURE.g3d
~~~

`validate` checks graph invariants and prints the deterministic SHA-256 graph digest. `parse` emits the canonical JSON AST. `render` produces a readable layer-by-layer projection.

## Technical boundaries

~~~text
SAME_AST => SAME_GRAPH_DIGEST
GRAPH_DIGEST != REAL_WORLD_TRUTH
GLYPH != IDENTIFIER
REGISTRY != PROGRAM
PROGRAM != RESULT
GLITCH-3D = SPATIAL_SOURCE
GLITCH-IR = INTEROPERABILITY_CONTRACT
~~~

See [GLITCH-3D-1](../spec/GLITCH-3D-1.md), the [machine identity](../machine/glitch-3d.json), and the [strict schema](../schemas/glitch-3d.v1.schema.json).
