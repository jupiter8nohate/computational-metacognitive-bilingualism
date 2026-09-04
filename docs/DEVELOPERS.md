# For developers

## Stable engineering

Install from a checkout:

```bash
python -m pip install .
cmb-provenance --version
cmb-provenance selftest
```

The stable engineering focus is `cmb_provenance`: explicit artifact sealing, verification, tamper-evident evidence references, and C2PA-facing interoperability.

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

## C2PA

CMB can create a C2PA SDK manifest definition, then uses external C2PA tooling for actual signing and asset binding. See [C2PA interoperability](C2PA_INTEROPERABILITY.md).

## Security

Read [Threat model](THREAT_MODEL.md) before relying on provenance output in a security-sensitive workflow.

## Examples

https://github.com/jupiter8nohate/computational-metacognitive-bilingualism/tree/main/examples
