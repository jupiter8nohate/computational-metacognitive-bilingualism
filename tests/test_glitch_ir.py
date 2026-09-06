from __future__ import annotations

import hashlib
import json
import unicodedata
from pathlib import Path

from jsonschema import Draft202012Validator


def _normalize(value: object) -> object:
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    if isinstance(value, dict):
        return {key: _normalize(value[key]) for key in sorted(value)}
    return value


def _canonical_bytes(value: object) -> bytes:
    normalized = _normalize(value)
    return json.dumps(
        normalized,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def test_glt_8101_vector_matches_schema_and_is_deterministic() -> None:
    root = Path(__file__).resolve().parents[1]
    schema = json.loads(
        (root / "schemas" / "glitch-ir.v1.schema.json").read_text(encoding="utf-8")
    )
    vector = json.loads(
        (
            root
            / "conformance"
            / "glitch-ir"
            / "v1"
            / "canonical-synchrony.json"
        ).read_text(encoding="utf-8")
    )
    expected = vector["expected"]

    Draft202012Validator(schema).validate(expected)

    first = _canonical_bytes(expected)
    second = _canonical_bytes(json.loads(first.decode("utf-8")))
    assert first == second
    assert hashlib.sha256(first).hexdigest() == hashlib.sha256(second).hexdigest()


def test_glt_8101_preserves_epistemic_boundaries() -> None:
    root = Path(__file__).resolve().parents[1]
    vector = json.loads(
        (
            root
            / "conformance"
            / "glitch-ir"
            / "v1"
            / "canonical-synchrony.json"
        ).read_text(encoding="utf-8")
    )
    expected = vector["expected"]

    assert expected["protocol"] == "GLT-8101"
    assert expected["operator"] == "GLT-0036"
    assert expected["state"] == "BACKTRACE"
    assert expected["verdict"] == "CONTESTED"
    assert expected["source"] == "SOURCE_UNKNOWN"
    assert expected["human_review"] is True
    assert "DIGEST_MATCH != TRUTH" in vector["invariants"]
