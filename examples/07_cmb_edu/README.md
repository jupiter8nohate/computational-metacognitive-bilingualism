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
