# CMB-SRP-1: Sovereignty Runtime Protocol

## Status

Experimental executable protocol for risk-adaptive human authority in AI-assisted
software development.

CMB-SRP-1 is not a replacement for a language compiler, formal verification
system, software supply-chain standard, or applicable law. It is an enforcement
layer that can run before or alongside those systems.

## 1. Core invariant

Verification depth MAY change with operational risk. The definition of evidence
MUST NOT.

~~~text
PATTERN != PROOF
PROFILE != PERSON
MODEL != MIND
PREDICTION != DESTINY
CAPABILITY != AUTHORITY
HUMAN_AGENCY > MACHINE_AUTHORITY
~~~

Low friction therefore means fewer required controls for reversible, low-stakes
work. It does not mean that a statistical pattern becomes proof.

## 2. Risk-adaptive friction

Every named operation has a criticality value from 0.0 through 1.0.

~~~text
effective_friction = max(default_friction, operation.criticality)
~~~

When effective friction is below the configured high-friction threshold, the
runtime MAY permit reversible work without a cryptographic human authorization.

At or above the high-friction threshold, implementations MUST require:

1. scoped human authorization; and
2. evidence that isolated verification occurred.

At or above the critical threshold, implementations MUST additionally require
two-party review evidence.

Operation-specific controls MAY add stricter requirements such as explicit
consent or reproducible-build evidence.

Unknown operations MUST fail closed.

## 3. Scoped human authorization

A CMB authorization is a signed capability, not a universal approval.

The signed payload binds authorization to:

- one operation;
- one project;
- the exact CMB policy digest;
- the exact subject digest;
- the declared human authorizer;
- required controls;
- an issuance time;
- an expiration time; and
- a unique nonce.

~~~text
HUMAN_SIGNATURE != BLANKET_PERMISSION
AUTHORIZATION_SCOPE != FOREVER
~~~

The reference implementation uses Ed25519.

A signature proves that the holder of the corresponding private key signed the
canonical payload. It does not by itself prove identity, correctness, legal
authority, originality, or informed consent.

## 4. Verification state machine

CMB-SRP-1 defines the following ordered states:

~~~text
GENERATED
  -> FIX_PROPOSED
  -> FIX_COMMITTED
  -> FIX_TESTED
  -> FIX_REVIEWED
  -> FIX_ATTESTED
  -> FIX_VERIFIED
  -> FIX_RELEASED
~~~

A conforming implementation MUST NOT silently jump across evidence-bearing
states.

~~~text
FIX_COMMITTED != FIX_TESTED
FIX_TESTED != FIX_REVIEWED
FIX_REVIEWED != FIX_ATTESTED
FIX_ATTESTED != FIX_CORRECT
FIX_VERIFIED != PERFECT
~~~

The state machine records what evidence-bearing process has occurred. It does
not prove that released software is bug-free.

## 5. Policy file

The canonical repository policy lives in `cmb.toml`.

Required principle values deliberately fail closed if altered:

~~~text
pattern_is_proof = false
profile_is_person = false
model_is_mind = false
prediction_is_destiny = false
human_agency_over_machine_authority = true
~~~

## 6. Reference CLI

~~~bash
cmbc validate --policy cmb.toml
cmbc selftest --policy cmb.toml
cmbc assess creative --policy cmb.toml
~~~

Create a local Ed25519 authorization keypair:

~~~bash
cmbc keygen \
  --private-key .cmb/human.key \
  --public-key .cmb/human.pub
~~~

Create a one-hour authorization bound to an exact artifact digest:

~~~bash
cmbc authorize deploy_production \
  --policy cmb.toml \
  --project OWNER/REPOSITORY \
  --subject-digest sha256:<64-hex-digest> \
  --authorized-by human-reviewer \
  --private-key .cmb/human.key \
  --output .cmb/deploy.authorization.json
~~~

Execution still requires the non-signature controls demanded by the policy:

~~~bash
cmbc assess deploy_production \
  --policy cmb.toml \
  --project OWNER/REPOSITORY \
  --subject-digest sha256:<64-hex-digest> \
  --authorization .cmb/deploy.authorization.json \
  --public-key .cmb/human.pub \
  --evidence isolated_verification=sha256:<receipt> \
  --evidence reproducible_build=sha256:<attestation> \
  --evidence two_party_review=sha256:<review>
~~~

## 7. CI/CD role

The GitHub Actions reference gate validates the runtime policy, runs deterministic
self-tests, and proves that a production deployment fails closed when scoped
authorization is absent.

Repository branch rules or deployment environments can make that status check a
required condition for merge or release.

Future CMB-SRP revisions may add path-sensitive change classification, in-toto
links, SLSA provenance inputs, and Sigstore-backed authorization identities.

## 8. Layer separation

CMB-SRP-1 preserves the CMB-CORE-1 distinction between:

1. declared policy;
2. cryptographic integrity;
3. technical enforcement; and
4. legal enforceability.

~~~text
SIGNED_AUTHORIZATION != CORRECT_CODE
SIGNED_AUTHORIZATION != LEGAL_PERMISSION
PROVENANCE != TRUTH
RISK_SCORE != PROOF
~~~

## 9. Recovery

Failures must identify the missing boundary rather than silently substituting
machine confidence for evidence.

Examples:

~~~text
AUTHORIZATION_REQUIRED
AUTH_EXPIRED
AUTH_POLICY_DIGEST_MISMATCH
EVIDENCE_REQUIRED:isolated_verification
UNKNOWN_OPERATION_FAIL_CLOSED
~~~

This is the executable form of the CMB principle that machine capability does not
create machine authority.
