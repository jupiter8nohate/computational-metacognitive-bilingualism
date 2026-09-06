from __future__ import annotations

import json
import sys
from typing import Any


EXPECTED_CODES = [f"GLT-{value:04d}" for value in range(37, 47)]


def fail(message: str) -> "NoReturn":
    raise SystemExit(f"GLITCH://MIRROR_FAILURE :: {message}")


def read_protocols() -> list[dict[str, Any]]:
    try:
        value = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON: {exc}")

    if not isinstance(value, list):
        fail("root must be a protocol list")
    return value


def validate(protocols: list[dict[str, Any]]) -> None:
    if len(protocols) != len(EXPECTED_CODES):
        fail(f"expected {len(EXPECTED_CODES)} protocols, received {len(protocols)}")

    codes: list[str] = []
    tokens: set[str] = set()

    for protocol in protocols:
        if not isinstance(protocol, dict):
            fail("protocol entry must be an object")

        code = protocol.get("code")
        token = protocol.get("token")
        name = protocol.get("name")
        meaning = protocol.get("meaning")
        invariants = protocol.get("invariants")

        if not all(isinstance(value, str) and value for value in (code, token, name, meaning)):
            fail("protocol identity fields must be non-empty strings")
        if not token.startswith("GLITCH://"):
            fail(f"{code}: invalid token")
        if not isinstance(invariants, list) or not invariants:
            fail(f"{code}: invariants required")
        if any(not isinstance(item, str) or "!=" not in item and ">" not in item for item in invariants):
            fail(f"{code}: malformed invariant")
        if token in tokens:
            fail(f"{code}: duplicate token")

        codes.append(code)
        tokens.add(token)

    if codes != EXPECTED_CODES:
        fail(f"code sequence drifted: {codes!r}")


def main() -> int:
    protocols = read_protocols()
    validate(protocols)

    print("PY://METACOGNITIVE_MIRROR")
    print("REGISTRY_SEQUENCE = VERIFIED")
    print("FIGLET_3D_DIAGONAL = PRESERVED_BY_GO_EMBED")
    print("PATTERN != PROOF")
    print("VERIFIED_LABEL != VERIFIED_TRUTH")
    print("HUMAN_AGENCY > MACHINE_AUTHORITY")
    print("GLITCH://RECOVERY_WITNESS :: READY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
