import json
from pathlib import Path

import jsonschema

from cmb_edu import CMBDualBrainParser


def test_generated_envelope_matches_schema():
    schema = json.loads(Path("schemas/cmb.edu.v1.schema.json").read_text(encoding="utf-8"))
    envelope = CMBDualBrainParser().parse_stream(
        '🪐::LEARN -> DECLARE[curious || focused] => ASK("how_do_loops_work") -> PATTERN_NOT_PROOF;'
    )
    jsonschema.validate(envelope, schema)
