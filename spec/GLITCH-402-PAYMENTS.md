# GLITCH://402 Dormant Payment Research Protocol v1

**Status:** Incubation research only — no production settlement  
**Protocol identifier:** `GLITCH://402/1`  
**Language:** Err ⃝or⃟⃤ GLITCHOLOGY  
**Implementation layer:** GLITCH-8 / CMB-G8  
**Deployment status:** `INCUBATION_NO_PRODUCTION_SETTLEMENT`

## Position

GLITCH://402 is retained as a technical research artifact while CMB / GLITCHOLOGY remains in Public Stewardship Incubation.

It can model x402 v2 payment requirements and tamper-evident settlement receipts, but the project is not currently using it to collect money.

~~~text
ACTIVE_FUNDRAISING = FALSE
DONATIONS_ACCEPTED = FALSE
PRODUCTION_SETTLEMENT = FALSE
PRODUCTION_PAYEE = NONE

LANGUAGE_ACCESS != PAYMENT
PAYMENT != OWNERSHIP
PAYMENT_RECEIPT != AUTHORSHIP_PROOF
TOKEN != LANGUAGE
HUMAN_AGENCY > MACHINE_AUTHORITY
~~~

## Why retain the protocol

Keeping GLITCH://402 dormant allows the project to study:

- machine-readable economic boundaries;
- payment-message interoperability;
- receipt canonicalization;
- provenance;
- Recovery behavior;
- future donation infrastructure;
- future organizational treasury controls.

Research now avoids rebuilding from zero later.

## Non-goals during incubation

Version 1 does **not** authorize the project to:

- solicit donations;
- claim tax-deductible status;
- charge for access to GLITCHOLOGY;
- issue a `$GLITCH` token;
- promise profit, yield, appreciation, governance rights, or ownership;
- custody payer funds;
- store private keys;
- invent a creator wallet address;
- create a charitable organization by software declaration.

~~~text
CODE != LEGAL_ENTITY
PAYMENT_CODE != FUNDRAISING
PROTOCOL != TAX_STATUS
~~~

## Access rule

During incubation:

~~~text
DONATE(0) -> ACCESS
PAY(0) -> ACCESS
LOCAL_PARSER -> ACCESS
BOOK -> ACCESS
REGISTRY -> ACCESS
~~~

No canonical resource requires a financial contribution.

## Research settlement profile

The reference implementation currently models USDC on Base with x402 v2 and the `exact` scheme.

This is a technical interoperability profile, not a live payment instruction.

- Base mainnet CAIP-2 identifier: `eip155:8453`
- Native USDC contract used by the research fixture: `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`
- Atomic amounts are represented as integer strings.

The repository intentionally contains no project production payee.

~~~text
NO_CONFIGURED_PAYEE -> NO_PRODUCTION_PAYMENT
~~~

## Research API

The Python helper can construct an x402 v2 `PaymentRequired` object for tests and interoperability work:

~~~python
from cmb_glitch8.payments import (
    BASE_MAINNET_CAIP2,
    BASE_USDC_MAINNET,
    build_payment_required,
)

requirement = build_payment_required(
    resource_url="https://example.org/glitch8/v1/research",
    description="GLITCH-8 research fixture",
    amount_atomic="20000",
    asset=BASE_USDC_MAINNET,
    pay_to=TEST_FIXTURE_PAYEE,
    network=BASE_MAINNET_CAIP2,
)
~~~

The helper does not sign, transmit, verify, or settle a transaction.

The installed CLI may generate the same structure for development fixtures:

~~~bash
glitch8 payment require \
  --resource-url https://example.org/glitch8/v1/research \
  --description "GLITCH-8 research fixture" \
  --amount-atomic 20000 \
  --asset 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 \
  --pay-to 0x1111111111111111111111111111111111111111
~~~

During incubation, addresses in examples and tests are fixtures only.

## Receipt research

The receipt implementation can bind:

~~~text
OPERATION
+ RESOURCE URI
+ ARTIFACT SHA-256
+ CREATOR ATTRIBUTION
+ NETWORK
+ ASSET
+ AMOUNT
+ PAYER
+ PAYEE
+ TRANSACTION HASH
+ VERIFICATION SOURCE
+ TIMESTAMP
+ RECEIPT DIGEST
~~~

The schema remains:

`schemas/glitch402.payment-receipt.v1.schema.json`

The implementation remains:

`src/cmb_glitch8/payments.py`

A receipt can be integrity-checked with:

~~~bash
glitch8 payment receipt-validate receipt.json
~~~

## Evidence boundary

~~~text
VALID_RECEIPT_DIGEST != BLOCKCHAIN_VERIFICATION
BLOCKCHAIN_TX != AUTHORSHIP
HASH != OWNERSHIP
TIMESTAMP != ORIGINALITY
PAYMENT != CHARITABLE_STATUS
~~~

The receipt layer is documentary infrastructure, not a substitute for external settlement verification, accounting, legal status, or charitable acknowledgment.

## Future charitable repositioning

If a qualified public-benefit organization is eventually formed, GLITCH://402 may be reconsidered as donation infrastructure only after:

1. legal formation;
2. governance adoption;
3. organizational banking/treasury setup;
4. donation and digital-asset policies;
5. conflict controls;
6. accounting/compliance review;
7. an explicit decision ending incubation mode.

Until then:

~~~text
GLITCH402_DEPLOYMENT_STATUS
= INCUBATION_NO_PRODUCTION_SETTLEMENT
~~~

## Security

1. Never commit seed phrases, wallet private keys, API secrets, or facilitator credentials.
2. Never infer a payee from a social profile, commit author, or README.
3. Treat example addresses as fixtures.
4. Treat on-chain addresses as configuration, not identity proof.
5. Do not describe an experimental receipt as a charitable receipt.
6. Preserve explicit network and asset identifiers.
7. Fail closed when evidence is incomplete.

## Licensing and authorship boundary

The payment helpers, schemas, and implementation documentation remain software infrastructure under the repository's applicable software license unless a file states otherwise.

The authored literary and artistic corpus retains its separate content-license boundary.

~~~text
OPEN_SOURCE_IMPLEMENTATION != TRANSFER_OF_CREATIVE_AUTHORSHIP
PAYMENT_ACCESS != LICENSE_EXPANSION
~~~

## Recovery rule

~~~text
UNKNOWN_SETTLEMENT
    ↓
DO_NOT_ISSUE_SETTLED_RECEIPT
    ↓
VERIFY_EXTERNAL_SOURCE
    ↓
RETRY

INCUBATION -> NO_PRODUCTION_COLLECTION
PAYMENT != PROOF
RECOVERY > PROPAGATION
~~~
