# CMB-CAP-1: Capability Authorization Passport

## Status

Experimental cryptographically signed portability layer for CMB-SDL authority.

CMB-CAP-1 turns a valid `cmb.authority-ir.v1` document into a self-contained,
Ed25519-signed credential that another process can verify offline.

```text
CMB-SDL
  -> Authority IR
  -> CMB-CAP
  -> VERIFY
  -> ALLOW / DENY / ESCALATE
```

CMB-CAP does not replace operating-system permissions, OAuth, MCP authorization,
A2A authentication, legal authority, identity proofing, or consent law.

## 1. Core invariants

```text
CAPABILITY != AUTHORITY
SIGNATURE != IDENTITY
CREDENTIAL != CONSENT
DECLARED_POLICY != ENFORCEMENT
DELEGATED_AUTHORITY <= RECEIVED_AUTHORITY
HUMAN_AGENCY > MACHINE_AUTHORITY
```

A valid signature proves possession of the private key corresponding to the
credential's embedded public key. It does not independently prove the civil,
legal, organizational, or personal identity of the key holder.

Deployments that need trusted issuer identity MUST pin or resolve the expected
public-key fingerprint through a separate trust mechanism.

## 2. Credential contents

A CMB-CAP credential contains:

- protocol and schema identifiers;
- a deterministic credential URN;
- the declared human issuer;
- the agent subject;
- the complete CMB Authority IR;
- issuance and expiry timestamps;
- a random nonce;
- an optional parent credential digest;
- MCP, A2A, and W3C VC interoperability metadata; and
- an Ed25519 signature with the corresponding public key.

The public key is embedded so a credential can be cryptographically checked
offline. This provides portability, not identity proofing.

## 3. Signing

The reference implementation signs canonical JSON using Ed25519.

```text
SIGNED_BYTES = canonical_json(credential_without_proof_signature)
```

The proof contains:

```json
{
  "type": "CMBEd25519SignatureV1",
  "created": "2026-09-04T19:30:00Z",
  "verification_method": "cmb:key:sha256:<public-key-fingerprint>",
  "public_key_b64": "<base64 raw Ed25519 public key>",
  "signature": "<base64 Ed25519 signature>"
}
```

The proof type is CMB-specific. It MUST NOT be represented as a W3C Data
Integrity proof unless an implementation actually implements and passes the
applicable W3C cryptosuite requirements.

## 4. Verification

A conforming reference verifier checks:

1. CMB-CAP schema and protocol identifiers;
2. embedded Authority IR integrity;
3. issuer and subject consistency with the Authority IR;
4. expiry consistency;
5. issuance and expiry time boundaries;
6. embedded public-key fingerprint;
7. optional externally pinned key fingerprint;
8. Ed25519 signature validity; and
9. parent lineage and monotonic delegation when a parent is declared.

Failure is explicit.

```text
CAP_EXPIRED
CAP_SIGNATURE_INVALID
CAP_EXPECTED_KEY_MISMATCH
CAP_PARENT_REQUIRED
CAP_PARENT_DIGEST_MISMATCH
CAP_DELEGATION_SIGNER_MISMATCH
CAP_DELEGATION_INVALID
```

## 5. Delegation

A child credential may bind to a parent credential digest.

The child Authority IR MUST pass CMB-SDL's monotonic delegation rules.

```text
child.allow      subset_of parent.allow
parent.deny      subset_of child.deny
child.scope      subset_of parent.scope
child.expires_at <= parent.expires_at
child.purpose    == parent.purpose
parent.evidence  subset_of child.evidence
```

The root human issuer MUST remain the same in v1.

Because CMB-SDL-1 does not yet carry an independently delegated child signing
key, a v1 child credential MUST also be signed by the same verified Ed25519 root
key as its parent. Merely copying the parent's issuer label or digest is not
sufficient cryptographic delegation.

~~~text
SAME_ISSUER_LABEL != SAME_SIGNING_AUTHORITY
PARENT_DIGEST != CHILD_KEY_AUTHORIZATION
~~~

A future version may allow a parent to explicitly bind a child key fingerprint
inside signed authority. Until that exists, signer continuity is the fail-closed
v1 rule.

CMB-CAP-1 does not yet define autonomous agent key delegation or a complete
multi-hop trust-chain format. Multi-hop verification should be performed from
root to leaf by supplying and checking each parent credential.

## 6. CLI

Install the sovereignty cryptography extra:

```bash
python -m pip install -e ".[sovereignty]"
```

Create a local Ed25519 keypair:

```bash
cmb-cap keygen \
  --private-key .cmb/cap.key \
  --public-key .cmb/cap.pub
```

Issue directly from CMB-SDL:

```bash
cmb-cap issue-sdl examples/cmb_sdl/research.cmb \
  --private-key .cmb/cap.key \
  --output dist/research.cmb-cap.json
```

Verify and pin the expected public key:

```bash
cmb-cap verify dist/research.cmb-cap.json \
  --public-key .cmb/cap.pub
```

Issue a child credential:

```bash
cmb-cap issue-ir child.authority.json \
  --parent parent.cmb-cap.json \
  --private-key .cmb/cap.key \
  --output child.cmb-cap.json
```

## 7. MCP interoperability

CMB-CAP uses the experimental identifier:

```text
io.cmb.capability/v1
```

The reference MCP adapter can verify a supplied credential and return bounded
verification results. Private signing keys are deliberately not accepted by MCP
tools.

```text
PRIVATE_KEY -> LOCAL_SIGNER
PUBLIC_CREDENTIAL -> AGENT_TRANSPORT
```

MCP transport support does not make CMB-CAP part of the official MCP
specification.

## 8. A2A interoperability

CMB-CAP defines an experimental A2A extension URI:

```text
https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/extensions/cmb-cap/v1
```

An A2A AgentExtension declaration may advertise that URI with
`required=false` and params identifying `CMB-CAP-1` and the credential schema.

CMB-CAP is not an official A2A extension and the repository does not claim A2A
conformance merely because it publishes this extension declaration.

## 9. W3C Verifiable Credentials bridge

W3C Verifiable Credentials Data Model 2.0 is a W3C Recommendation. The W3C
credential family also defines Data Integrity and EdDSA cryptosuites.

The reference implementation exports a **VC 2.0-shaped projection** for
interchange experiments. The `cmb-cap export-vc` CLI first verifies the CMB-CAP
credential (and any required parent/key pin supplied by the caller) and refuses
projection when verification fails. The lower-level projection helper remains a
data transformation primitive, so direct library callers are responsible for
verifying before projection. The projection intentionally omits a W3C Data
Integrity proof and marks itself:

```text
VC_2_0_projection_only_not_W3C_Data_Integrity_proof
```

Therefore:

```text
CMB_CAP_SIGNATURE != W3C_DATA_INTEGRITY_CONFORMANCE
VC_SHAPE != VERIFIED_CREDENTIAL_CONFORMANCE
```

A future CMB-CAP profile may implement an exact W3C Data Integrity or JOSE/COSE
binding with dedicated conformance tests.

## 10. Recovery

CMB-CAP fails closed on malformed authority, invalid signatures, expired
credentials, mismatched pinned keys, and invalid delegation.

```text
UNKNOWN_CREDENTIAL != PERMISSION
FAILED_SIGNATURE != RETRY_AS_TRUST
MISSING_PARENT != IGNORE_LINEAGE
EXPIRED_AUTHORITY != CONTINUE
```
