from __future__ import annotations

import hashlib
from datetime import datetime, timezone

import pytest

from cmb_sdl import SDLValidationError, compile_text, validate_authority_ir, validate_delegation
from cmb_sdl.compiler import canonical_json


PARENT = """cmb/1
HUMAN "Jupiter Hudson"
AGENT coordinator
ALLOW web.search
ALLOW document.read
DENY person.profile
SCOPE project cmb
PURPOSE "public research"
EXPIRES 2030-01-01T00:00:00Z
REQUIRE citations
ON uncertainty => ASK_HUMAN
ON scope_violation => HALT
ON expiry => REVOKE
DELEGABLE true
RETURN receipt
"""

CHILD = """cmb/1
HUMAN "Jupiter Hudson"
AGENT worker
ALLOW web.search
DENY person.profile
SCOPE project cmb
PURPOSE "public research"
EXPIRES 2029-01-01T00:00:00Z
REQUIRE citations
REQUIRE provenance
ON uncertainty => ASK_HUMAN
ON scope_violation => HALT
ON expiry => REVOKE
DELEGABLE false
RETURN receipt
"""


def test_compile_is_deterministic() -> None:
    first = compile_text(PARENT)
    second = compile_text(PARENT)
    assert first == second
    assert first["digest"].startswith("sha256:")
    assert first["capabilities"]["allow"] == ["document.read", "web.search"]


def test_conflicting_capability_fails_closed() -> None:
    broken = PARENT.replace("DENY person.profile", "DENY web.search")
    with pytest.raises(SDLValidationError, match="both ALLOW and DENY"):
        compile_text(broken)


def test_unknown_statement_fails_closed() -> None:
    with pytest.raises(SDLValidationError, match="unknown statement"):
        compile_text(PARENT + "\nMAGIC spread.everywhere\n")


def test_delegation_can_only_reduce_authority() -> None:
    validate_delegation(
        compile_text(PARENT),
        compile_text(CHILD),
        now=datetime(2028, 1, 1, tzinfo=timezone.utc),
    )


def test_delegation_cannot_expand_capabilities() -> None:
    child = CHILD.replace("ALLOW web.search", "ALLOW shell.execute")
    with pytest.raises(SDLValidationError, match="absent from parent"):
        validate_delegation(
            compile_text(PARENT),
            compile_text(child),
            now=datetime(2028, 1, 1, tzinfo=timezone.utc),
        )


def test_non_delegable_parent_is_enforced() -> None:
    parent = PARENT.replace("DELEGABLE true", "DELEGABLE false")
    with pytest.raises(SDLValidationError, match="not delegable"):
        validate_delegation(
            compile_text(parent),
            compile_text(CHILD),
            now=datetime(2028, 1, 1, tzinfo=timezone.utc),
        )


def test_authority_ir_digest_detects_tampering() -> None:
    from cmb_sdl import validate_authority_ir

    ir = compile_text(PARENT)
    ir["purpose"] = "different purpose"
    with pytest.raises(SDLValidationError, match="digest mismatch"):
        validate_authority_ir(ir)


def test_delegation_preserves_parent_handlers() -> None:
    child = CHILD.replace("ON uncertainty => ASK_HUMAN\n", "")
    with pytest.raises(SDLValidationError, match="required parent handler"):
        validate_delegation(
            compile_text(PARENT),
            compile_text(child),
            now=datetime(2028, 1, 1, tzinfo=timezone.utc),
        )


def _rehash(ir: dict[str, object]) -> None:
    core = {key: value for key, value in ir.items() if key != "digest"}
    ir["digest"] = "sha256:" + hashlib.sha256(canonical_json(core)).hexdigest()


def test_string_false_cannot_enable_delegation() -> None:
    parent = compile_text(PARENT)
    parent["delegable"] = "false"
    _rehash(parent)

    with pytest.raises(SDLValidationError, match="delegable must be a boolean"):
        validate_delegation(
            parent,
            compile_text(CHILD),
            now=datetime(2028, 1, 1, tzinfo=timezone.utc),
        )


def test_authority_ir_rejects_non_human_issuer_even_with_valid_digest() -> None:
    ir = compile_text(PARENT)
    ir["issuer"]["type"] = "machine"
    _rehash(ir)

    with pytest.raises(SDLValidationError, match="issuer.type must be 'human'"):
        validate_authority_ir(ir)


def test_authority_ir_rejects_unknown_fields_even_with_valid_digest() -> None:
    ir = compile_text(PARENT)
    ir["machine_override"] = True
    _rehash(ir)

    with pytest.raises(SDLValidationError, match="unknown fields"):
        validate_authority_ir(ir)


def test_authority_ir_rejects_mutated_invariant_set() -> None:
    ir = compile_text(PARENT)
    ir["invariants"] = ["CAPABILITY == AUTHORITY"]
    _rehash(ir)

    with pytest.raises(SDLValidationError, match="canonical CMB-SDL-1 set"):
        validate_authority_ir(ir)
