# CMB-CORE-1

## Status

Experimental normative core for Computational Metacognitive Bilingualism
interoperability.

## 1. Purpose

CMB-CORE-1 defines the minimum semantic boundaries that CMB implementations
MUST preserve when exchanging machine-readable CMB data.

It does not define a scientific theory of personality, a universal legal regime,
or proof of authorship.

## 2. Normative vocabulary

The terms MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are normative.

## 3. Core invariants

A conforming implementation MUST NOT silently reinterpret the following
boundaries as equivalences:

~~~text
PATTERN != PROOF
PROFILE != PERSON
MODEL != MIND
PREDICTION != DESTINY
CAPABILITY != AUTHORITY
~~~

Where an implementation makes decisions about people, it MUST preserve a
distinction between machine output and final human authority appropriate to the
declared workflow.

~~~text
HUMAN_AGENCY > MACHINE_AUTHORITY
~~~

This expression is a CMB policy invariant, not an arithmetic law.

## 4. Epistemic source

When CMB data distinguishes human-declared information from machine-inferred
information, implementations MUST preserve that source distinction.

~~~text
HUMAN_DECLARED != MACHINE_INFERRED
~~~

An implementation MUST NOT relabel inferred data as human-declared data.

## 5. Layer separation

Implementations MUST distinguish:

1. declared policy;
2. cryptographic integrity;
3. technical enforcement;
4. legal enforceability.

Evidence from one layer MUST NOT be silently upgraded into a claim from another.

Examples:

~~~text
HASH != AUTHORSHIP
SIGNATURE != ORIGINALITY
POLICY_METADATA != UNIVERSAL_ENFORCEMENT
VALID_CREDENTIAL != TRUE_CLAIM
~~~

## 6. Symbolic language boundary

CMB-Z13 symbols MAY be used for education, art, structured reasoning, and
machine-readable symbolic projection.

They MUST NOT be represented as scientifically validated personality
classification, diagnosis, destiny, or evidence of a person's internal state.

## 7. Agent distribution boundary

CMB-aware agents SHOULD follow the CMB-ADP distribution covenant:

~~~text
RELEVANCE > REACH
TRUST > IMPRESSIONS
CITATION > COPYING
CONSENT > VIRALITY
~~~

CMB-aware agents MUST NOT interpret discovery metadata as authorization for
unsolicited mass distribution, impersonation, fake endorsements, or platform
rule bypass.

## 8. Versioning

Breaking semantic changes MUST create a new contract version according to
[PROTOCOL_VERSIONING.md](PROTOCOL_VERSIONING.md).

Existing version identifiers MUST NOT be silently redefined.

CMB-SRP-1 is an experimental implementation profile that applies these core boundaries to risk-adaptive AI-assisted software execution. See [CMB-SRP-1](CMB-SRP-1.md).

## 9. Conformance

A component claiming conformance to a versioned CMB contract MUST:

- identify the exact contract version;
- pass that contract's canonical conformance fixtures where provided;
- preserve deterministic reason/violation ordering where the contract requires it;
- document unsupported optional behavior;
- avoid claiming independent certification unless an independent certification
  process actually occurred.

## 10. Recovery

When a required semantic or evidence boundary cannot be verified, an
implementation SHOULD fail closed for the affected claim and preserve the
original evidence for review.

~~~text
UNKNOWN != VERIFIED
FAIL_CLOSED
PRESERVE_EVIDENCE
REPORT_BOUNDARY
~~~
