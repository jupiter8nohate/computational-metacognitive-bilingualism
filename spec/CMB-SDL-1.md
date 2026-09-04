# CMB-SDL-1: Sovereign Delegation Language

## Status

Experimental, deterministic human-to-agent authority language for CMB.

CMB-SDL-1 is intentionally small. It does not replace OAuth, MCP, A2A,
Verifiable Credentials, operating-system permissions, or applicable law.
It compiles human-readable authority declarations into a canonical CMB
Authority IR that other runtimes can validate or transport.

## 1. Core boundary

```text
CAPABILITY != AUTHORITY
PURPOSE != PERMISSION
DELEGATED_AUTHORITY <= RECEIVED_AUTHORITY
HUMAN_AGENCY > MACHINE_AUTHORITY
```

An agent may possess a technical capability without possessing CMB authority
to use that capability for a particular purpose, scope, or period.

## 2. Version 1 syntax

A document begins with `cmb/1`. Blank lines and lines beginning with `#` are
ignored.

```text
cmb/1

HUMAN "Jupiter Hudson"
AGENT research_bot

ALLOW web.search
ALLOW document.read
DENY person.profile

SCOPE project "cmb"
PURPOSE "public research"
EXPIRES 2030-01-01T00:00:00Z

REQUIRE citations
REQUIRE provenance

ON uncertainty => ASK_HUMAN
ON scope_violation => HALT
ON expiry => REVOKE

DELEGABLE false
RETURN receipt
```

### Required singleton statements

- `HUMAN <id>`
- `AGENT <id>`
- `PURPOSE <text>`
- `EXPIRES <RFC3339/ISO-8601 timestamp with timezone>`

At least one `ALLOW` and one `SCOPE` are required.

### Repeatable statements

- `ALLOW <capability>`
- `DENY <capability>`
- `SCOPE <kind> <value>`
- `REQUIRE <evidence>`

### Event handlers

Version 1 recognizes:

- `uncertainty`
- `scope_violation`
- `expiry`

Valid handler actions are `ASK_HUMAN`, `HALT`, and `REVOKE`.

Unknown statements, unknown events, conflicting capabilities, malformed
timestamps, and missing required declarations fail closed.

## 3. Authority IR

`cmb-sdl compile` emits `cmb.authority-ir.v1`.

The output is deterministic for semantically identical v1 input because
capabilities, scopes, evidence requirements, and handlers are normalized and
sorted before hashing.

The IR includes a SHA-256 digest over the canonical JSON representation of the
authority core. That digest is an integrity identifier, not a signature and not
proof of identity or legal authority.

## 4. Delegation monotonicity

A child authority is valid only when it is no broader than the parent:

```text
child.allow      subset_of parent.allow
parent.deny      subset_of child.deny
child.scope      subset_of parent.scope
child.expires_at <= parent.expires_at
child.purpose    == parent.purpose
parent.evidence  subset_of child.evidence
```

The parent must explicitly set `DELEGABLE true`.

Parent-required event handlers and receipt requirements must survive delegation.
The reference checker also rejects expired parent and child authority.

Version 1 intentionally uses exact scope membership rather than attempting to
infer semantic containment between arbitrary scope strings.

## 5. CLI

```bash
cmb-sdl compile examples/cmb_sdl/research.cmb \
  --output dist/research.authority.json

cmb-sdl check-delegation \
  parent.authority.json \
  child.authority.json
```

Success returns exit code 0. Parse, validation, or delegation failures return
exit code 2 with a bounded `CMB_SDL_ERROR` message.

## 6. MCP bridge

The optional CMB MCP server exposes `cmb_compile_authority`, which accepts a
CMB-SDL source string and returns the same deterministic Authority IR.

MCP transports the request. CMB-SDL defines the additional authority semantics.

## 7. Layer separation

```text
CMB-SDL != OPERATING_SYSTEM_SANDBOX
CMB-SDL != IDENTITY_PROOF
CMB-SDL != LEGAL_PERMISSION
DIGEST != SIGNATURE
DECLARED_POLICY != ENFORCEMENT
```

A consuming runtime must enforce the resulting authority boundary for CMB-SDL
to have technical effect.

## 8. Recovery

The parser and delegation checker fail closed. A runtime must not silently
reinterpret an unknown statement as permission.

```text
UNKNOWN_STATEMENT => REJECT
UNKNOWN_EVENT => REJECT
ALLOW_AND_DENY_SAME_CAPABILITY => REJECT
DELEGATION_EXPANDS_AUTHORITY => REJECT
EXPIRED_AUTHORITY => REJECT
```
