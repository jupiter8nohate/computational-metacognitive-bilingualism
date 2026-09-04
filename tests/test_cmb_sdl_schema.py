from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from cmb_sdl import compile_text


def test_authority_ir_schema_accepts_reference_compilation() -> None:
    root = Path(__file__).resolve().parents[1]
    schema = json.loads(
        (root / "schemas/cmb.authority-ir.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    source = (root / "examples/cmb_sdl/research.cmb").read_text(
        encoding="utf-8"
    )
    ir = compile_text(source)
    Draft202012Validator(
        schema, format_checker=FormatChecker()
    ).validate(ir)
