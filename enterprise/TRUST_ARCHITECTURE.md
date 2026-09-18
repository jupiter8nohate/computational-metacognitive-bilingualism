# CMB Enterprise Trust Architecture

## Core design rule

CMB must not make the creator's personal signing key the operational root of an enterprise deployment.

Instead, CMB separates **canonical provenance** from **enterprise authority**.

```text
CREATOR / PROJECT PROVENANCE
          |
          | authenticates canonical project history and releases
          v
     CMB RELEASE
          |
          +-----------------------------+
          |                             |
          v                             v
ENTERPRISE A TRUST DOMAIN        ENTERPRISE B TRUST DOMAIN
          |                             |
  enterprise-owned keys           enterprise-owned keys
          |                             |
  policy + IAM + gateway          policy + IAM + gateway
```

## Root A — canonical provenance

Purpose:

- identify canonical CMB releases;
- preserve release chronology and artifact integrity;
- carry repository provenance evidence;
- support Sigstore / GitHub attestation verification;
- preserve creator attribution and documented project lineage.

This root is **not** an enterprise administrator credential.

```text
CREATOR_PROVENANCE_ROOT != PRODUCTION_ADMIN
RELEASE_SIGNATURE != REMOTE_CONTROL
```

## Root B — enterprise operational authority

Purpose:

- authorize enterprise-specific actions;
- bind decisions to organization-controlled keys;
- support rotation, expiry, revocation, and scoped delegation;
- integrate with IAM, KMS/HSM, CI/CD, policy engines, and audit systems.

The enterprise owns and protects these keys.

CMB-CAP and CMB-SRP provide experimental reference mechanisms for signed authority and fail-closed policy gates. Production deployments should anchor issuer identity through organization-approved trust infrastructure rather than treating an embedded key as self-authenticating identity.

## Trust decision

A production gateway should evaluate independent evidence classes rather than collapsing them into one boolean.

```text
artifact_integrity
release_provenance
enterprise_authority
policy_evaluation
deployment_identity
audit_evidence
        |
        v
ALLOW | DENY | HUMAN_REVIEW
```

Each status must remain inspectable.

## Failure rules

- Modified artifact: **DENY**
- Invalid or expired required enterprise authority: **DENY**
- Unknown required operation: **DENY**
- Missing required evidence: **DENY**
- Unresolved identity or policy ambiguity where policy permits escalation: **HUMAN_REVIEW**
- Valid integrity + valid scoped authority + satisfied policy: **ALLOW**

## Recovery

Key compromise must not destroy the historical record.

Recommended production controls:

1. offline recovery keys or organization KMS/HSM procedures;
2. documented key rotation;
3. short-lived operational authorization;
4. independent audit logs;
5. multiple maintainers for protocol governance;
6. reproducible release verification where feasible; and
7. explicit separation of project provenance keys from enterprise deployment keys.

```text
ONE_KEY != WHOLE_SYSTEM
RECOVERY > SINGLE_POINT_OF_FAILURE
```
