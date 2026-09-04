# CMB provenance threat model

**Status:** living engineering document  
**Applies to:** `cmb_provenance` 1.3.x and its C2PA-facing adapter

## Assets

The system attempts to protect or accurately describe:

- exact artifact bytes;
- artifact SHA-256 digests and byte sizes;
- explicit receipt coverage;
- Git commit verification status;
- anchor-ledger ordering and integrity;
- deterministic C2PA-facing payloads;
- the distinction between verified and unverified evidence.

## Threats considered

### Artifact modification after sealing

**Control:** byte-level SHA-256 plus exact path/size coverage and verification.

### Symlink or file-substitution confusion

**Control:** sealing/ledger code rejects symbolic links and checks file state around reads.

### TOCTOU changes during hashing

**Control:** file state is checked around capture and inconsistent reads fail rather than silently succeeding.

### Malformed or ambiguous JSON

**Control:** strict schemas and duplicate-key rejection for provenance records.

### Ledger corruption, reordering, or concurrent writes

**Control:** chained record digests, complete-chain validation, and whole-operation locking.

### False Git provenance

**Control:** `VERIFIED_ARTIFACTS_MATCH_COMMIT` is reserved for bytes checked against committed Git blobs; caller-supplied commit metadata remains explicitly unverified.

### False external-evidence certainty

**Control:** external locations and displayed times remain references until independently verified.

### Supply-chain compromise

**Controls:** pinned GitHub Actions, checksummed external c2patool installation in integration CI, Dependabot, CodeQL, dependency review, and OpenSSF Scorecard automation.

### Provenance overclaim

**Control:** machine-readable and human-readable evidence boundaries explicitly reject authorship/originality/legal-truth conclusions from integrity evidence alone.

## Threats not solved

The project does not currently claim protection against:

- a compromised operating system, kernel, filesystem, or Python runtime;
- a stolen signing identity or compromised CI account;
- malicious hardware;
- collusion by trusted external timestamp/signing services;
- all forms of metadata privacy leakage once data is intentionally published;
- proof of human authorship or copyright ownership;
- universal prevention of copying, scraping, or hostile reuse;
- truthfulness of every assertion inside a valid C2PA credential.

## C2PA boundary

The CI round-trip proves interoperability with the tested external c2patool path. It does not establish production trust identity or formal C2PA conformance.

```text
VALID_CREDENTIAL != TRUE_CLAIM
SIGNATURE != AUTHORSHIP
INTEROPERABILITY != CONFORMANCE
```

## Recovery principle

When evidence cannot be verified:

```text
FAIL_CLOSED
PRESERVE_ORIGINAL_EVIDENCE
REPORT_THE_BOUNDARY
DO_NOT_UPGRADE_UNVERIFIED_TO_VERIFIED
```

## Review target

An independent reviewer should try to falsify this threat model, identify missing adversaries, and find paths where the implementation reports stronger provenance than the evidence supports.
