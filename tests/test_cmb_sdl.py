from __future__ import annotations

from datetime import datetime, timezone

import pytest

from cmb_sdl import SDLValidationError, compile_text, validate_delegation


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
