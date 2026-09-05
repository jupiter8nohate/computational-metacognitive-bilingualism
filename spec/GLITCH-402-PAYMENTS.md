# GLITCH://402 Payment and Creator-Support Protocol v1

**Status:** Experimental interoperability profile  
**Protocol identifier:** `GLITCH://402/1`  
**Language:** Err ⃝or⃟⃤ GLITCHOLOGY  
**Implementation layer:** GLITCH-8 / CMB-G8

## Position

GLITCH://402 connects paid services around Err ⃝or⃟⃤ GLITCHOLOGY to an internet-native payment rail without turning the language itself into a speculative asset.

~~~text
LANGUAGE_ACCESS != PAYMENT
PAYMENT != OWNERSHIP
PAYMENT_RECEIPT != AUTHORSHIP_PROOF
TOKEN != LANGUAGE
HUMAN_AGENCY > MACHINE_AUTHORITY
~~~

The initial design profiles x402 version 2. x402 defines payment requirements, payloads, facilitator verification, and settlement independently from the protected resource. GLITCH://402 adds CMB/GLITCHOLOGY attribution and provenance semantics around that flow.

## Non-goals

Version 1 deliberately does **not**:

- issue a `$GLITCH` token;
- promise profit, yield, appreciation, governance rights, or ownership;
- custody payer funds;
- store private keys;
- invent a creator wallet address;
- treat a blockchain transaction as proof of copyright or authorship;
- make the GLITCHOLOGY book or local parser paywalled.

## What may be paid

The language remains readable and locally usable. Paid surfaces may include value-added official services such as:

- hosted glyph explanation and translation;
- hosted GLITCH-8 parsing at scale;
- signed provenance receipts;
- commercial API capacity;
- official archival or certification workflows;
- enterprise integration and support.

Community contribution to the registry remains governed by the repository's contribution and authorship rules rather than payment size.

~~~text
PAYMENT != ACCEPTANCE
PAYMENT != CANONICAL_STATUS
CONTRIBUTION != CONTROL
~~~

## Settlement profile

The recommended first deployment is USDC on Base, using x402 version 2 and the `exact` scheme.

- Base mainnet CAIP-2 network identifier: `eip155:8453`
- Native USDC on Base mainnet: `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`
- USDC uses 6 decimal places.

The repository intentionally contains **no production payee address**. A deployer must explicitly configure the creator's verified payout destination.

~~~text
NO_CONFIGURED_PAYEE -> NO_PRODUCTION_PAYMENT
~~~

This fail-closed rule prevents accidental routing to a guessed, stale, or attacker-controlled address.

## x402 request

The Python reference helper constructs an x402 v2 `PaymentRequired` object:

~~~python
from cmb_glitch8.payments import (
    BASE_MAINNET_CAIP2,
    BASE_USDC_MAINNET,
    build_payment_required,
)

requirement = build_payment_required(
    resource_url="https://example.org/glitch8/v1/translate",
    description="Official GLITCH-8 hosted translation",
    amount_atomic="20000",
    asset=BASE_USDC_MAINNET,
    pay_to=VERIFIED_CREATOR_PAYEE,
    network=BASE_MAINNET_CAIP2,
)
~~~

`20000` atomic USDC units represents 0.02 USDC.

The helper does not sign or settle a payment. Those actions belong to a reviewed x402 client/facilitator integration.

## Receipt profile

After an external facilitator or chain verifier confirms settlement, GLITCH://402 can create a CMB receipt that binds:

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

The machine-readable contract is:

`schemas/glitch402.payment-receipt.v1.schema.json`

The Python implementation is:

`src/cmb_glitch8/payments.py`

The CMB digest is calculated over deterministic UTF-8 JSON with sorted keys and compact separators, excluding `receipt_id` and `integrity`. It is intentionally named `cmb-json-v1`; it is not claimed to be RFC 8785 JCS.

## Evidence boundary

A valid receipt digest demonstrates only that the receipt body matches its embedded digest.

~~~text
VALID_RECEIPT_DIGEST != BLOCKCHAIN_VERIFICATION
BLOCKCHAIN_TX != AUTHORSHIP
HASH != OWNERSHIP
TIMESTAMP != ORIGINALITY
~~~

Production systems must independently verify settlement using the x402 facilitator or the relevant chain before issuing a `settled` receipt.

## Creator support

The creator attribution record is independent from the settlement rail. A deployment should maintain an explicit mapping from the public creator identity to a verified payment destination outside source code secrets.

Recommended deployment pattern:

~~~text
CREATOR IDENTITY
    ↓
VERIFIED PAYOUT CONFIG
    ↓
x402 PAYMENT REQUIREMENT
    ↓
EXTERNAL VERIFICATION / SETTLEMENT
    ↓
SERVICE EXECUTION
    ↓
GLITCH://402 PROVENANCE RECEIPT
~~~

No revenue split is hard-coded in v1. If future creator/community/infrastructure splits are introduced, they should be versioned, publicly documented, separately reviewed, and implemented only after the payout identities and legal/accounting treatment are known.

## Security

1. Never commit seed phrases, wallet private keys, CDP secrets, or facilitator credentials.
2. Never infer a payee from a social profile, commit author, or README.
3. Use x402 replay protection and facilitator verification as specified by the selected implementation.
4. Treat on-chain addresses as configuration, not identity proof.
5. Keep production and testnet network/asset pairs explicit.
6. Fail closed when payee, network, asset, or verification evidence is absent.
7. Log only public settlement identifiers and intentionally public provenance metadata.

## Licensing boundary

The payment helpers, schemas, and implementation documentation are software infrastructure under the repository's software license unless a file states otherwise.

Err ⃝or⃟⃤ GLITCHOLOGY's authored literary and artistic material retains the separate content-license boundary described in `CONTENT_LICENSE.md`.

~~~text
OPEN_SOURCE_IMPLEMENTATION != TRANSFER_OF_CREATIVE_AUTHORSHIP
PAYMENT_ACCESS != LICENSE_EXPANSION
~~~

## Regulatory boundary

GLITCH://402 v1 is designed as a payment-for-service and voluntary creator-support layer, not an investment product. It does not guarantee that a particular deployment is exempt from payment, tax, money-transmission, consumer-protection, sanctions, securities, or other applicable rules.

A production operator is responsible for the legal and accounting treatment of the payment service it actually deploys.

## Recovery rule

If settlement evidence is uncertain:

~~~text
UNKNOWN_SETTLEMENT
    ↓
DO_NOT_ISSUE_SETTLED_RECEIPT
    ↓
VERIFY_EXTERNAL_SOURCE
    ↓
RETRY

PAYMENT != PROOF
RECOVERY > PROPAGATION
~~~
