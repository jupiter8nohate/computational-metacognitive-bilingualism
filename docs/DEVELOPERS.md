# For developers

## Stable engineering

Install from a checkout:

```bash
python -m pip install .
cmb-provenance --version
cmb-provenance selftest
```

The stable engineering focus is `cmb_provenance`: explicit artifact sealing, verification, tamper-evident evidence references, and C2PA-facing interoperability.

## CMB boundary policy engine

The repository now includes a framework-agnostic reference evaluator for explicit application policy facts:

```python
from cmb_provenance import BoundaryContext, require_boundary

decision = require_boundary(
    BoundaryContext(
        event_id="decision-42",
        consequential_decision=True,
        ai_involved=True,
        ai_disclosed=True,
        human_review_available=True,
        consent_required=True,
        consent_present=True,
    )
)

assert decision.allowed
assert decision.authority == "HUMAN_FINAL"
```

A rejected boundary raises `BoundaryRejectedError` with a structured decision payload.

The engine enforces declared conditions only. It does not inspect prose and infer identity, intent, diagnosis, mental state, or morality.

Cross-language implementations can use [`cmb.boundary-event.v1.schema.json`](https://github.com/jupiter8nohate/computational-metacognitive-bilingualism/blob/main/schemas/cmb.boundary-event.v1.schema.json) as the shared event contract.

The first framework example is [FastAPI boundary guard](https://github.com/jupiter8nohate/computational-metacognitive-bilingualism/blob/main/examples/06_fastapi_boundary/README.md).

The repository also contains conformance-tested reference adapters for:

- [TypeScript + Express](https://github.com/jupiter8nohate/computational-metacognitive-bilingualism/tree/main/adapters/typescript-express)
- [Rust + Actix Web](https://github.com/jupiter8nohate/computational-metacognitive-bilingualism/tree/main/adapters/rust-actix)
- [Go + standard library](https://github.com/jupiter8nohate/computational-metacognitive-bilingualism/tree/main/adapters/go)

All four language implementations run [the same boundary-v1 cases](https://github.com/jupiter8nohate/computational-metacognitive-bilingualism/blob/main/conformance/boundary.v1.cases.json). A policy implementation that cannot pass those cases is not v1-conformant.

## Optional MCP agent adapter

The deterministic CMB-ADP-1 service can be exposed through the official MCP
Python SDK without duplicating recommendation logic:

~~~bash
python -m pip install -e ".[mcp]"
cmb-mcp
~~~

See [MCP integration](MCP_INTEGRATION.md). The adapter is an interoperability
surface, not independent certification or permission for unsolicited agent
distribution.

## Experimental CMB-Z13 reference parser

The CMB-Z13 parser is an **experimental reference implementation**, not a personality engine and not a scientific astrology system.

```bash
cmb-z13 validate '♍::GO -> VERIFY[claim] => EVIDENCE_REQUIRED;'
cmb-z13 parse '♏::PROLOG -> INFER[pattern] => HYPOTHESIS;'
cmb-z13 explain '⛎::LISP -> INSPECT[rule] => META(rule);'
```

The parser validates the fixed zodiac/code/operator mapping and emits a deterministic AST under schema `cmb.z13.ast.v1`.

```text
ZODIAC_SYMBOL != PERSON
CODE != IDENTITY
GUARDIAN_MODE != PERSONALITY
```

## Interactive front door

The [Interactive CMB Playground](PLAYGROUND.md) demonstrates local SHA-256 hashing, machine-readable artifact declarations, CMB-Z13 symbolic projections, and the same explicit boundary rules in a zero-dependency browser page.

It is a symbolic reasoning tool, not a 13-language source-code transpiler.

## C2PA

CMB can create a C2PA SDK manifest definition, then uses external C2PA tooling for actual signing and asset binding. See [C2PA interoperability](C2PA_INTEROPERABILITY.md).

## Security

Read [Threat model](THREAT_MODEL.md) before relying on provenance output in a security-sensitive workflow.

## Build and verify the public site

From a repository checkout:

```bash
python -m pip install -e ".[docs]"
python scripts/build_docs.py
python scripts/build_docs.py --check-only
```

The same build command runs in documentation CI and GitHub Pages deployment.
It stages the documented public assets, checks rendered HTML links and images,
requires a real homepage heading, verifies discovery URLs and LLM-map links,
and checks the generated machine bundle's SHA-256 digests. Raw HTML links need
this additional check because MkDocs does not rewrite or validate them.

The output is the ignored `site/` directory. Recovery preserves the previous
local build until the replacement passes validation. The builder refuses to
overwrite unrelated files.

Generated CMB-66 manifests declare `path_base: "manifest_directory"`. Resolve
each artifact's `path` beside `manifest.json`, so bundles can move between a
local checkout and a public server without exposing local filesystem paths.
Clients that previously resolved these paths from their working directory
should use the manifest's parent directory instead.

## Examples

https://github.com/jupiter8nohate/computational-metacognitive-bilingualism/tree/main/examples
