from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from cmb_glitch8.cli import main as glitch8_main
from cmb_glitch8.payments import (
    BASE_MAINNET_CAIP2,
    BASE_USDC_MAINNET,
    GLITCH402_PROTOCOL,
    GLITCH402_DEPLOYMENT_STATUS,
    Glitch402Error,
    build_payment_required,
    create_verified_settlement_receipt,
    validate_receipt_integrity,
)


PAYEE = "0x1111111111111111111111111111111111111111"
PAYER = "0x2222222222222222222222222222222222222222"
TX = "0x" + ("ab" * 32)
ARTIFACT = "cd" * 32


def _receipt() -> dict:
    return create_verified_settlement_receipt(
        operation="glitch.translate",
        resource_uri="https://example.org/glitch8/v1/translate",
        artifact_sha256=ARTIFACT,
        creator_name="Jupiter Hudson / WisdomLoveThePoet / Jupiter 8",
        creator_attribution_uri=(
            "https://github.com/jupiter8nohate/"
            "computational-metacognitive-bilingualism"
        ),
        network=BASE_MAINNET_CAIP2,
        asset=BASE_USDC_MAINNET,
        amount_atomic="20000",
        decimals=6,
        payer=PAYER,
        payee=PAYEE,
        transaction_hash=TX,
        verification_source="facilitator",
        verification_evidence="facilitator:settlement:example-123",
        verified_at="2026-09-05T23:00:00Z",
        provider="test-facilitator",
    )


def test_payment_required_is_x402_v2_and_requires_explicit_payee() -> None:
    value = build_payment_required(
        resource_url="https://example.org/glitch8/v1/translate",
        description="Official GLITCH-8 translation",
        amount_atomic="20000",
        asset=BASE_USDC_MAINNET,
        pay_to=PAYEE,
    )

    assert value["x402Version"] == 2
    assert value["accepts"][0]["network"] == "eip155:8453"
    assert value["accepts"][0]["asset"] == BASE_USDC_MAINNET
    assert value["accepts"][0]["payTo"] == PAYEE
    assert value["extensions"]["glitch402"]["info"]["protocol"] == GLITCH402_PROTOCOL


@pytest.mark.parametrize("amount", ["0", "-1", "1.5", ""])
def test_payment_required_rejects_invalid_atomic_amount(amount: str) -> None:
    with pytest.raises(Glitch402Error):
        build_payment_required(
            resource_url="https://example.org/service",
            description="test",
            amount_atomic=amount,
            asset=BASE_USDC_MAINNET,
            pay_to=PAYEE,
        )


def test_payment_required_rejects_guessed_or_missing_evm_payee() -> None:
    with pytest.raises(Glitch402Error, match="pay_to"):
        build_payment_required(
            resource_url="https://example.org/service",
            description="test",
            amount_atomic="1",
            asset=BASE_USDC_MAINNET,
            pay_to="creator-wallet-goes-here",
        )


def test_receipt_is_deterministic_and_integrity_validates() -> None:
    first = _receipt()
    second = _receipt()

    assert first["receipt_id"] == second["receipt_id"]
    assert first["integrity"]["sha256"] == second["integrity"]["sha256"]
    validate_receipt_integrity(first)


def test_receipt_tampering_is_detected() -> None:
    receipt = _receipt()
    changed = copy.deepcopy(receipt)
    changed["settlement"]["amount_atomic"] = "999999"

    with pytest.raises(Glitch402Error, match="digest mismatch"):
        validate_receipt_integrity(changed)


def test_receipt_matches_json_schema() -> None:
    root = Path(__file__).resolve().parents[1]
    schema = json.loads(
        (root / "schemas" / "glitch402.payment-receipt.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    Draft202012Validator(schema).validate(_receipt())


def test_receipt_contains_no_secret_key_fields() -> None:
    serialized = json.dumps(_receipt()).lower()
    assert "private_key" not in serialized
    assert "seed_phrase" not in serialized
    assert "wallet_secret" not in serialized


def test_cli_renders_payment_requirement(capsys: pytest.CaptureFixture[str]) -> None:
    code = glitch8_main(
        [
            "payment",
            "require",
            "--resource-url",
            "https://example.org/glitch8/v1/translate",
            "--description",
            "Official GLITCH-8 translation",
            "--amount-atomic",
            "20000",
            "--asset",
            BASE_USDC_MAINNET,
            "--pay-to",
            PAYEE,
        ]
    )
    assert code == 0
    value = json.loads(capsys.readouterr().out)
    assert value["x402Version"] == 2
    assert value["accepts"][0]["payTo"] == PAYEE


def test_cli_validates_receipt_file(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    receipt_path = tmp_path / "receipt.json"
    receipt_path.write_text(
        json.dumps(_receipt(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    code = glitch8_main(["payment", "receipt-validate", str(receipt_path)])
    assert code == 0
    assert "VALID GLITCH://402 RECEIPT" in capsys.readouterr().out


def test_payment_required_declares_incubation_status() -> None:
    value = build_payment_required(
        resource_url="https://example.org/glitch8/v1/research",
        description="GLITCH-8 research fixture",
        amount_atomic="1",
        asset=BASE_USDC_MAINNET,
        pay_to=PAYEE,
    )
    info = value["extensions"]["glitch402"]["info"]
    assert GLITCH402_DEPLOYMENT_STATUS == "incubation-no-production-settlement"
    assert info["deployment_status"] == GLITCH402_DEPLOYMENT_STATUS
