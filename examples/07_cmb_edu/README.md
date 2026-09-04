# CMB-EDU: parse a child-readable context stream

This example shows the narrow technical purpose of CMB-EDU: translate a
human-declared learning context into a structured envelope without converting
that declaration into a diagnosis or permanent profile.

## CLI

```bash
cmb-edu validate '♌::CREATIVE -> STATE[confident || overstimulated] => GENERATE("dragon_story") -> PROFILE_NOT_PERSON;'

cmb-edu parse '🪐::LEARN -> DECLARE[curious || focused] => ASK("how_do_loops_work") -> PATTERN_NOT_PROOF;'
```

## Python

```python
from cmb_edu import CMBDualBrainParser

parser = CMBDualBrainParser()
envelope = parser.parse_stream(
    '🪐::LEARN -> DECLARE[curious || focused] '
    '=> ASK("how_do_loops_work") -> PATTERN_NOT_PROOF;'
)

assert envelope["context"]["source"] == "human_declared"
assert envelope["context"]["machine_inferred"] is False
assert envelope["privacy"]["training_permission"] is False
assert envelope["privacy"]["profiling_permission"] is False
```

The privacy fields are protocol declarations. An integrating application still
has to implement actual access control, retention, consent, and enforcement.


## FGC emoji example

The same privacy-first envelope can be built from child-facing Flamingoglyph Code:

```bash
cmb-edu parse-fgc '🧠 CURIOUS + 🪐 LEARNING + ⚡ ASK WHY + 🛡️ NO_PROFILE + ⏳ EPHEMERAL'
```

Python:

```python
from cmb_edu import FGCEmojiParser

payload = FGCEmojiParser().parse_stream(
    "🧠 CURIOUS + 🪐 LEARNING + ⚡ ASK WHY + 🛡️ NO_PROFILE + ⏳ EPHEMERAL"
)
```

Both the text parser and FGC parser emit the `cmb.edu.v1` envelope. The glyph syntax is a teaching surface, not a separate identity classifier.
