# CMB normative specifications

This directory separates **normative protocol behavior** from manifestos,
research hypotheses, educational material, and implementation details.

## Specifications

| Document | Status | Scope |
|---|---|---|
| [CMB-CORE-1](CMB-CORE-1.md) | Experimental normative core | layer separation, authority boundaries, conformance vocabulary |
| [CMB Policy Specification v1](CMB-SPEC.md) | Experimental normative specification | deterministic policy authorization |
| [Protocol versioning](PROTOCOL_VERSIONING.md) | Normative process | compatibility and breaking-change rules |
| [Action registry](cmb.actions.v1.json) | Versioned registry | policy action sensitivity |

## Rule

~~~text
MANIFESTO != SPECIFICATION
SPECIFICATION != IMPLEMENTATION
IMPLEMENTATION != CONFORMANCE
CONFORMANCE != CERTIFICATION
~~~

A specification states required behavior. A reference implementation is evidence
that the behavior can be implemented. Conformance requires passing the declared
tests for the relevant version. Certification or endorsement requires an
independent process that this repository must not invent for itself.

## CMB-SDL-1

[CMB-SDL-1](CMB-SDL-1.md) defines the experimental deterministic human-to-agent authority language and compiles to `cmb.authority-ir.v1`. Its central delegation invariant is `DELEGATED_AUTHORITY <= RECEIVED_AUTHORITY`.

## CMB-CAP-1

[CMB-CAP-1](CMB-CAP-1.md) defines the experimental Ed25519-signed portability layer for CMB-SDL authority. It preserves the distinction between cryptographic signature verification, trusted issuer identity, declared authority, technical enforcement, and legal permission.
