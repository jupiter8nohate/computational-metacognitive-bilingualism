# @cmb-sovereignty/core

Portable TypeScript primitives for Computational Metacognitive Bilingualism.

This package intentionally does **not** duplicate the Python cryptographic provenance implementation. It provides typed invariants and explainable web-facing attention-signal evaluation.

```ts
import {
  CMB_INVARIANTS,
  assessAttentionSignals,
} from "@cmb-sovereignty/core";

const result = assessAttentionSignals([
  {
    kind: "autoplay_media",
    weight: 20,
    evidence: "Video element is configured to autoplay.",
  },
]);

console.log(CMB_INVARIANTS.PATTERN_NOT_PROOF);
console.log(result);
```

## Epistemic boundary

```text
ATTENTION_SIGNAL != PROOF_OF_PROFILING
PATTERN != PROOF
PROFILE != PERSON
```

The evaluator reports observable interface behavior. It does not claim access to hidden server-side models, profiling systems, intentions, or user psychology.
