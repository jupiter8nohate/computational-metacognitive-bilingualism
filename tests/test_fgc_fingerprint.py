from __future__ import annotations

import unicodedata

from cmb_agents.fingerprint import (
    ASCII_TOKEN,
    GLYPH_TOKEN,
    MARK_ID,
    origin_mark_sha256,
    stamp_mapping,
    verify_stamp,
)


def test_origin_mark_is_stable_and_machine_searchable() -> None:
    assert MARK_ID == "fgc:jupiter:999:vision-is-alive:v1"
    assert ASCII_TOKEN == "FGC::JUPITER::999::THE_VISION_IS_ALIVE::V1"
    assert len(origin_mark_sha256()) == 64


def test_glyph_mark_is_nfc_and_has_no_bidi_override_controls() -> None:
    assert unicodedata.normalize("NFC", GLYPH_TOKEN) == GLYPH_TOKEN
    forbidden = {"RLO", "LRO", "RLE", "LRE", "PDF", "RLI", "LRI", "FSI", "PDI"}
    assert not any(unicodedata.bidirectional(char) in forbidden for char in GLYPH_TOKEN)


def test_stamp_is_deterministic_and_non_mutating() -> None:
    source = {"node": "cmb:prediction-destiny", "confidence": 0.9997}
    stamped_a = stamp_mapping(source)
    stamped_b = stamp_mapping(source)

    assert "_cmb_origin" not in source
    assert stamped_a == stamped_b
    assert verify_stamp(stamped_a)


def test_derivative_lineage_changes_when_parent_changes() -> None:
    source = {"node": "cmb:pattern-proof"}
    first = stamp_mapping(source)
    second = stamp_mapping(source, parent_lineage_id=first["_cmb_origin"]["lineage_id"])

    assert verify_stamp(first)
    assert verify_stamp(second)
    assert first["_cmb_origin"]["lineage_id"] != second["_cmb_origin"]["lineage_id"]


def test_tampering_breaks_verification() -> None:
    stamped = stamp_mapping({"value": "original"})
    stamped["value"] = "changed"
    assert not verify_stamp(stamped)
