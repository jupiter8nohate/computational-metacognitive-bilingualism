from __future__ import annotations

from datetime import datetime, timezone

import pytest

from cmb_cap import (
    CapabilityError,
    a2a_extension_declaration,
    credential_digest,
    issue_from_sdl,
    public_key_fingerprint,
    verify_capability,
    vc_projection,
)
from cmb_policy.authorization import generate_ed25519_keypair


NOW = datetime(2028, 1, 1, tzinfo=timezone.utc)

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


def test_issue_and_verify_with_embedded_and_pinned_key() -> None:
    private_key, public_key = generate_ed25519_keypair()
    credential = issue_from_sdl(
        PARENT,
        private_key_b64=private_key,
        now=NOW,
        nonce="0123456789abcdef0123456789abcdef",
    )

    ok, failures = verify_capability(
        credential,
        now=NOW,
        expected_key_fingerprint=public_key_fingerprint(public_key),
    )

    assert ok is True
    assert failures == ()
    assert credential["credential_id"].startswith("urn:cmb:cap:")
    assert credential["proof"]["type"] == "CMBEd25519SignatureV1"


def test_authority_tampering_fails_closed() -> None:
    private_key, _ = generate_ed25519_keypair()
    credential = issue_from_sdl(PARENT, private_key_b64=private_key, now=NOW)
    credential["authority"]["purpose"] = "different purpose"

    ok, failures = verify_capability(credential, now=NOW)

    assert ok is False
    assert "CAP_AUTHORITY_INVALID" in failures


def test_wrong_pinned_key_is_rejected() -> None:
    private_key, _ = generate_ed25519_keypair()
    _, unrelated_public = generate_ed25519_keypair()
    credential = issue_from_sdl(PARENT, private_key_b64=private_key, now=NOW)

    ok, failures = verify_capability(
        credential,
        now=NOW,
        expected_key_fingerprint=public_key_fingerprint(unrelated_public),
    )

    assert ok is False
    assert "CAP_EXPECTED_KEY_MISMATCH" in failures


def test_expired_credential_is_rejected() -> None:
    private_key, _ = generate_ed25519_keypair()
    credential = issue_from_sdl(PARENT, private_key_b64=private_key, now=NOW)

    ok, failures = verify_capability(
        credential,
        now=datetime(2031, 1, 1, tzinfo=timezone.utc),
    )

    assert ok is False
    assert "CAP_EXPIRED" in failures


def test_child_credential_requires_and_validates_parent() -> None:
    private_key, _ = generate_ed25519_keypair()
    parent = issue_from_sdl(PARENT, private_key_b64=private_key, now=NOW)
    child = issue_from_sdl(
        CHILD,
        private_key_b64=private_key,
        now=NOW,
        parent_credential=parent,
    )

    ok, failures = verify_capability(child, now=NOW)
    assert ok is False
    assert failures == ("CAP_PARENT_REQUIRED",)

    ok, failures = verify_capability(
        child,
        now=NOW,
        parent_credential=parent,
    )
    assert ok is True
    assert failures == ()


def test_child_cannot_expand_parent_capabilities() -> None:
    private_key, _ = generate_ed25519_keypair()
    parent = issue_from_sdl(PARENT, private_key_b64=private_key, now=NOW)
    expanded = CHILD.replace("ALLOW web.search", "ALLOW shell.execute")

    with pytest.raises(CapabilityError, match="absent from parent"):
        issue_from_sdl(
            expanded,
            private_key_b64=private_key,
            now=NOW,
            parent_credential=parent,
        )


def test_parent_digest_substitution_is_rejected() -> None:
    private_key, _ = generate_ed25519_keypair()
    parent = issue_from_sdl(
        PARENT,
        private_key_b64=private_key,
        now=NOW,
        nonce="aaaaaaaaaaaaaaaa",
    )
    alternate_parent = issue_from_sdl(
        PARENT,
        private_key_b64=private_key,
        now=NOW,
        nonce="bbbbbbbbbbbbbbbb",
    )
    child = issue_from_sdl(
        CHILD,
        private_key_b64=private_key,
        now=NOW,
        parent_credential=parent,
    )

    assert credential_digest(parent) != credential_digest(alternate_parent)
    ok, failures = verify_capability(
        child,
        now=NOW,
        parent_credential=alternate_parent,
    )
    assert ok is False
    assert "CAP_PARENT_DIGEST_MISMATCH" in failures


def test_vc_projection_does_not_claim_data_integrity_conformance() -> None:
    private_key, _ = generate_ed25519_keypair()
    credential = issue_from_sdl(PARENT, private_key_b64=private_key, now=NOW)
    projection = vc_projection(credential)

    assert "https://www.w3.org/ns/credentials/v2" in projection["@context"]
    assert projection["cmb:standardsStatus"] == (
        "VC_2_0_projection_only_not_W3C_Data_Integrity_proof"
    )
    assert "proof" not in projection


def test_a2a_extension_is_explicitly_optional() -> None:
    extension = a2a_extension_declaration()
    assert extension["required"] is False
    assert extension["params"]["protocol"] == "CMB-CAP-1"


def test_credential_id_tampering_is_rejected() -> None:
    private_key, _ = generate_ed25519_keypair()
    credential = issue_from_sdl(PARENT, private_key_b64=private_key, now=NOW)
    credential["credential_id"] = "urn:cmb:cap:" + ("0" * 64)

    ok, failures = verify_capability(credential, now=NOW)

    assert ok is False
    assert "CAP_CREDENTIAL_ID_MISMATCH" in failures


def test_v1_refuses_unverified_multi_hop_delegation() -> None:
    private_key, _ = generate_ed25519_keypair()
    parent = issue_from_sdl(PARENT, private_key_b64=private_key, now=NOW)
    child_source = CHILD.replace("DELEGABLE false", "DELEGABLE true")
    child = issue_from_sdl(
        child_source,
        private_key_b64=private_key,
        now=NOW,
        parent_credential=parent,
    )

    with pytest.raises(CapabilityError, match="one delegated hop"):
        issue_from_sdl(
            CHILD.replace("AGENT worker", "AGENT leaf"),
            private_key_b64=private_key,
            now=NOW,
            parent_credential=child,
        )


def test_delegated_credential_cannot_switch_signing_keys() -> None:
    parent_private, _ = generate_ed25519_keypair()
    attacker_private, _ = generate_ed25519_keypair()
    parent = issue_from_sdl(
        PARENT,
        private_key_b64=parent_private,
        now=NOW,
    )

    with pytest.raises(CapabilityError, match="same verified root key"):
        issue_from_sdl(
            CHILD,
            private_key_b64=attacker_private,
            now=NOW,
            parent_credential=parent,
        )
