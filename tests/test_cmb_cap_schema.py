from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from cmb_cap import issue_from_sdl
from cmb_policy.authorization import generate_ed25519_keypair


def test_cmb_cap_schema_accepts_reference_credential() -> None:
    root = Path(__file__).resolve().parents[1]
    schema = json.loads(
        (root / "schemas/cmb.capability-credential.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    source = (root / "examples/cmb_sdl/research.cmb").read_text(encoding="utf-8")
    private_key, _ = generate_ed25519_keypair()
    credential = issue_from_sdl(
        source,
        private_key_b64=private_key,
        now=datetime(2028, 1, 1, tzinfo=timezone.utc),
        nonce="0123456789abcdef0123456789abcdef",
    )

    Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    ).validate(credential)
