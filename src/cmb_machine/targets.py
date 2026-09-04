"""Deterministic CMB-66 machine target renderers.

Every renderer receives a mapping that has already been stamped with the
canonical FGC origin mark. Text targets also repeat the stable ASCII token in a
parse-safe header. Binary targets carry the same token as encoded data.
"""

from __future__ import annotations

import base64
import json
import math
import struct
from collections.abc import Mapping
from typing import Any, Callable

from cmb_agents.fingerprint import ASCII_TOKEN, MARK_ID, canonical_json_bytes

Renderer = Callable[[Mapping[str, Any]], bytes]


def _json(stamped: Mapping[str, Any]) -> bytes:
    return canonical_json_bytes(stamped) + b"\n"


def _jsonld(stamped: Mapping[str, Any]) -> bytes:
    payload = dict(stamped)
    payload["@context"] = {
        "cmb": "https://github.com/jupiter8nohate/computational-metacognitive-bilingualism#",
        "schema_version": "cmb:schemaVersion",
        "protocol": "cmb:protocol",
        "_cmb_origin": "cmb:origin",
    }
    payload["@id"] = f"urn:cmb:artifact:{stamped['_cmb_origin']['lineage_id']}"
    payload["@type"] = "cmb:MachineSemanticArtifact"
    return canonical_json_bytes(payload) + b"\n"


def _escape_turtle(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
    )


def _turtle(stamped: Mapping[str, Any]) -> bytes:
    origin = stamped["_cmb_origin"]
    ir_b64 = base64.b64encode(canonical_json_bytes(stamped)).decode("ascii")
    lines = [
        "@prefix cmb: <https://github.com/jupiter8nohate/computational-metacognitive-bilingualism#> .",
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",
        "",
        "<urn:cmb:machine-artifact>",
        '  a cmb:MachineSemanticArtifact ;',
        f'  cmb:markId "{_escape_turtle(str(origin["mark_id"]))}" ;',
        f'  cmb:asciiToken "{_escape_turtle(str(origin["canonical_ascii_token"]))}" ;',
        f'  cmb:originDigest "{_escape_turtle(str(origin["origin_mark_sha256"]))}" ;',
        f'  cmb:contentDigest "{_escape_turtle(str(origin["content_sha256"]))}" ;',
        f'  cmb:lineageId "{_escape_turtle(str(origin["lineage_id"]))}" ;',
        f'  cmb:canonicalJsonBase64 "{ir_b64}" .',
        "",
    ]
    return "\n".join(lines).encode("utf-8")


def _prolog_quote(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "''")


def _prolog(stamped: Mapping[str, Any]) -> bytes:
    origin = stamped["_cmb_origin"]
    ir_b64 = base64.b64encode(canonical_json_bytes(stamped)).decode("ascii")
    facts = [
        f"% CMB-66 ORIGIN {ASCII_TOKEN}",
        f"cmb_origin_mark('{_prolog_quote(str(origin['mark_id']))}').",
        f"cmb_ascii_token('{_prolog_quote(str(origin['canonical_ascii_token']))}').",
        f"cmb_origin_sha256('{_prolog_quote(str(origin['origin_mark_sha256']))}').",
        f"cmb_content_sha256('{_prolog_quote(str(origin['content_sha256']))}').",
        f"cmb_lineage_id('{_prolog_quote(str(origin['lineage_id']))}').",
        f"cmb_canonical_json_base64('{ir_b64}').",
    ]
    for invariant in stamped.get("invariants", []):
        if isinstance(invariant, Mapping):
            facts.append(
                "cmb_invariant("
                + ",".join(
                    f"'{_prolog_quote(str(invariant.get(key, '')))}'"
                    for key in ("id", "lhs", "operator", "rhs")
                )
                + ")."
            )
    return ("\n".join(facts) + "\n").encode("utf-8")


def _rego(stamped: Mapping[str, Any]) -> bytes:
    origin = stamped["_cmb_origin"]
    body_json = json.dumps(stamped, ensure_ascii=False, sort_keys=True, indent=2)
    text = f"""# CMB-66 ORIGIN {ASCII_TOKEN}
package cmb.generated

fgc_origin := {{
  "mark_id": {json.dumps(origin["mark_id"], ensure_ascii=False)},
  "ascii_token": {json.dumps(origin["canonical_ascii_token"], ensure_ascii=False)},
  "origin_mark_sha256": {json.dumps(origin["origin_mark_sha256"], ensure_ascii=False)},
  "content_sha256": {json.dumps(origin["content_sha256"], ensure_ascii=False)},
  "lineage_id": {json.dumps(origin["lineage_id"], ensure_ascii=False)}
}}

cmb_ir := {body_json}

default allow := false

allow if {{
  input.human_authorized == true
}}

deny contains "CMB:INFERENCE_NOT_AUTHORITY" if {{
  input.epistemic_status == "INFERENCE"
  input.automated_execution == true
  input.human_authorized != true
}}
"""
    return text.encode("utf-8")


def _smt_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '""')


def _smtlib(stamped: Mapping[str, Any]) -> bytes:
    origin = stamped["_cmb_origin"]
    payload_b64 = base64.b64encode(canonical_json_bytes(stamped)).decode("ascii")
    text = f"""; CMB-66 ORIGIN {ASCII_TOKEN}
(set-logic ALL)
(declare-const cmb_fgc_mark_id String)
(declare-const cmb_ascii_token String)
(declare-const cmb_origin_mark_sha256 String)
(declare-const cmb_content_sha256 String)
(declare-const cmb_lineage_id String)
(declare-const cmb_canonical_json_base64 String)
(declare-const cmb_human_agency_over_machine_authority Bool)

(assert (= cmb_fgc_mark_id "{_smt_string(str(origin["mark_id"]))}"))
(assert (= cmb_ascii_token "{_smt_string(str(origin["canonical_ascii_token"]))}"))
(assert (= cmb_origin_mark_sha256 "{_smt_string(str(origin["origin_mark_sha256"]))}"))
(assert (= cmb_content_sha256 "{_smt_string(str(origin["content_sha256"]))}"))
(assert (= cmb_lineage_id "{_smt_string(str(origin["lineage_id"]))}"))
(assert (= cmb_canonical_json_base64 "{payload_b64}"))
(assert cmb_human_agency_over_machine_authority)
(check-sat)
"""
    return text.encode("utf-8")


def _digital_asset_metadata(stamped: Mapping[str, Any]) -> bytes:
    origin = stamped["_cmb_origin"]
    payload = {
        "name": "CMB Machine Semantic Artifact",
        "description": "CMB-66 machine-native semantic artifact",
        "attributes": [
            {"trait_type": "CMB Protocol", "value": str(stamped.get("protocol", "CMB-66"))},
            {"trait_type": "FGC Mark", "value": str(origin["mark_id"])},
            {"trait_type": "Lineage", "value": str(origin["lineage_id"])},
        ],
        "properties": {
            "cmb": stamped,
            "fgc_ascii_token": origin["canonical_ascii_token"],
            "origin_mark_sha256": origin["origin_mark_sha256"],
            "content_sha256": origin["content_sha256"],
        },
    }
    return canonical_json_bytes(payload) + b"\n"


def _cbor_uint(major: int, value: int) -> bytes:
    if value < 0:
        raise ValueError("CBOR unsigned value cannot be negative")
    prefix = major << 5
    if value < 24:
        return bytes([prefix | value])
    if value <= 0xFF:
        return bytes([prefix | 24, value])
    if value <= 0xFFFF:
        return bytes([prefix | 25]) + struct.pack(">H", value)
    if value <= 0xFFFFFFFF:
        return bytes([prefix | 26]) + struct.pack(">I", value)
    return bytes([prefix | 27]) + struct.pack(">Q", value)


def _cbor_encode(value: Any) -> bytes:
    if value is None:
        return b"\xf6"
    if value is False:
        return b"\xf4"
    if value is True:
        return b"\xf5"
    if isinstance(value, int):
        if value >= 0:
            return _cbor_uint(0, value)
        return _cbor_uint(1, -1 - value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("CMB canonical CBOR rejects non-finite floats")
        return b"\xfb" + struct.pack(">d", value)
    if isinstance(value, bytes):
        return _cbor_uint(2, len(value)) + value
    if isinstance(value, str):
        encoded = value.encode("utf-8")
        return _cbor_uint(3, len(encoded)) + encoded
    if isinstance(value, (list, tuple)):
        encoded_items = [_cbor_encode(item) for item in value]
        return _cbor_uint(4, len(encoded_items)) + b"".join(encoded_items)
    if isinstance(value, Mapping):
        encoded_pairs = []
        for key, item in value.items():
            encoded_key = _cbor_encode(str(key))
            encoded_pairs.append((encoded_key, _cbor_encode(item)))
        encoded_pairs.sort(key=lambda pair: (len(pair[0]), pair[0]))
        return _cbor_uint(5, len(encoded_pairs)) + b"".join(
            key + item for key, item in encoded_pairs
        )
    raise TypeError(f"Unsupported CBOR type: {type(value).__name__}")


def _cbor(stamped: Mapping[str, Any]) -> bytes:
    return _cbor_encode(stamped)


def _varint(value: int) -> bytes:
    out = bytearray()
    while True:
        current = value & 0x7F
        value >>= 7
        if value:
            out.append(current | 0x80)
        else:
            out.append(current)
            return bytes(out)


def _protobuf_string(field_number: int, value: str) -> bytes:
    encoded = value.encode("utf-8")
    tag = (field_number << 3) | 2
    return _varint(tag) + _varint(len(encoded)) + encoded


def _protobuf(stamped: Mapping[str, Any]) -> bytes:
    origin = stamped["_cmb_origin"]
    canonical = canonical_json_bytes(stamped).decode("utf-8")
    fields = (
        (1, canonical),
        (2, str(origin["mark_id"])),
        (3, str(origin["canonical_ascii_token"])),
        (4, str(origin["origin_mark_sha256"])),
        (5, str(origin["content_sha256"])),
        (6, str(origin["lineage_id"])),
    )
    return b"".join(_protobuf_string(number, value) for number, value in fields)


RENDERERS: dict[str, tuple[str, str, Renderer]] = {
    "json": (".json", "application/json", _json),
    "jsonld": (".jsonld", "application/ld+json", _jsonld),
    "turtle": (".ttl", "text/turtle", _turtle),
    "prolog": (".pl", "text/x-prolog", _prolog),
    "rego": (".rego", "text/plain", _rego),
    "smtlib": (".smt2", "text/plain", _smtlib),
    "cbor": (".cbor", "application/cbor", _cbor),
    "protobuf": (".pb", "application/x-protobuf", _protobuf),
    "digital_asset_metadata": (".asset.json", "application/json", _digital_asset_metadata),
}


def target_metadata() -> dict[str, dict[str, str]]:
    return {
        name: {"extension": extension, "media_type": media_type}
        for name, (extension, media_type, _) in sorted(RENDERERS.items())
    }


def renderer_for(target: str) -> tuple[str, str, Renderer]:
    try:
        return RENDERERS[target]
    except KeyError as exc:
        known = ", ".join(sorted(RENDERERS))
        raise ValueError(f"Unsupported CMB-66 target {target!r}. Expected one of: {known}") from exc
