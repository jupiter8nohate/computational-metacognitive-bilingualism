# CMB-SRP-2: Deterministic Change Detection and Attestation Bridge

## Status

Experimental compatible extension of CMB-SRP-1.

CMB-SRP-2 adds deterministic source-change classification before runtime policy
assessment. It does not claim to infer developer intent, prove a vulnerability,
or replace language-native security analysis.

## 1. Position

SRP-1 answers:

> Given a named operation, what controls are required before execution?

SRP-2 adds the preceding question:

> Which named operations are implicated by the concrete files and syntax that
> changed?

The complete path is:

~~~text
SOURCE CHANGE
    -> DETERMINISTIC DETECTOR
    -> CANDIDATE OPERATION
    -> CMB FRICTION ENGINE
    -> REQUIRED CONTROLS
    -> HUMAN AUTHORIZATION / EVIDENCE
    -> ALLOW OR DENY
~~~

The detector result is deliberately bounded:

~~~text
PATTERN != PROOF
RISK_CLASSIFICATION != INTENT
DETECTION != VULNERABILITY
~~~

## 2. Path-sensitive rules

The canonical `cmb.toml` may define deterministic glob rules that map sensitive
paths to CMB operations.

Examples include:

- deployment and release workflows -> `deploy_production`;
- infrastructure trees -> `deploy_production`;
- IAM, RBAC, and permission trees -> `modify_permissions`;
- authentication trees -> `manage_authentication`.

A path rule is a conservative routing signal. It does not prove the semantic
meaning of the entire file.

## 3. Python AST rules

The reference implementation parses Python with the standard-library `ast`
module and matches configured call names after basic import-alias resolution.

This is materially stronger than raw text or regex matching because comments and
string literals do not trigger call rules.

The implementation currently recognizes configured examples such as:

~~~text
os.chmod(...)
posthog.capture(...)
analytics.track(...)
login_user(...)
~~~

It does not claim complete semantic analysis, data-flow analysis, taint
analysis, or cross-language equivalence.

Unsupported languages still receive path-sensitive analysis.

## 4. Fail-closed parse boundary

For Python files under AST analysis, a syntax error is recorded as a scanner
error. The canonical policy sets:

~~~toml
fail_closed_on_python_parse_error = true
~~~

The CLI therefore returns a non-zero status when analyzed Python cannot be
parsed.

The scanner does not copy source text into the error report.

## 5. Deterministic scan report

The scan report has a canonical SHA-256 digest over:

- active policy digest;
- Git base/head identifiers when available;
- sorted file names;
- sorted findings;
- sorted scanner errors; and
- sorted candidate operations.

No wall-clock timestamp is included in the digest input.

This allows the later human authorization to bind to the exact classification
report:

~~~text
AUTHORIZATION.subject_digest == SCAN_REPORT.report_digest
~~~

A changed report invalidates that binding.

## 6. Automatic gate composition

`cmbc gate-report` feeds every detected operation back into the SRP runtime.

~~~bash
cmbc scan-git \
  --base origin/main \
  --head HEAD \
  --policy cmb.toml \
  --output cmb-scan.json

cmbc gate-report \
  --report cmb-scan.json \
  --policy cmb.toml \
  --project OWNER/REPOSITORY
~~~

Low-friction operations may pass automatically.

High-friction operations fail closed until their required controls are supplied
through the existing SRP authorization and evidence interface.

## 7. CMB-SRP2 attestation predicate v1

`cmbc statement` exports an **unsigned** in-toto Statement v1 whose subject is
the canonical scan report digest.

The statement includes:

- policy digest;
- report digest;
- verification state;
- detected operations;
- criticality summary;
- findings and scanner errors; and
- Git base/head references.

~~~text
UNSIGNED_STATEMENT != ATTESTATION
ATTESTATION != CORRECTNESS
PROVENANCE != TRUTH
~~~

The exported statement is intended as an interoperability bridge for later
signing or attachment to software-supply-chain systems. CMB does not claim that
writing the JSON file creates a Sigstore signature, SLSA provenance, or an
in-toto verification result.

## 8. Current detector limits

The reference detector is intentionally small and inspectable.

It currently does not provide:

- whole-program control-flow analysis;
- taint tracking;
- semantic analysis for Go, Rust, JavaScript, TypeScript, or C/C++;
- proof that a tracking API actually transmitted personal data;
- proof that an authentication call weakened authentication;
- proof that an infrastructure file was deployed.

These are future interoperability points, not facts silently inferred by SRP-2.

## 9. Recovery

Every finding includes a path, rule identifier, detector type, and bounded
evidence label.

Recovery remains inspectable:

~~~text
FINDING
    -> REVIEW RULE
    -> REVIEW SOURCE
    -> CONFIRM / REJECT CLASSIFICATION
    -> SUPPLY REQUIRED CONTROLS
    -> RE-RUN
~~~

CMB-SRP-2 therefore automates routing without converting pattern recognition
into epistemic authority.
