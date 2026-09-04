"""Line-oriented parser for CMB Sovereign Delegation Language v1."""

from __future__ import annotations

import shlex

from .model import AuthorityDocument, SDLValidationError, ScopeBinding

PROTOCOL_HEADER = "cmb/1"
KNOWN_EVENTS = frozenset({"uncertainty", "scope_violation", "expiry"})
KNOWN_HANDLER_ACTIONS = frozenset({"ASK_HUMAN", "HALT", "REVOKE"})
BOOLEAN_LITERALS = {"true": True, "false": False}


def _tokens(line: str, line_number: int) -> list[str]:
    try:
        return shlex.split(line, comments=False, posix=True)
    except ValueError as exc:
        raise SDLValidationError(f"Line {line_number}: {exc}") from exc


def parse(text: str) -> AuthorityDocument:
    raw_lines = list(enumerate(text.splitlines(), start=1))
    meaningful = [
        (number, line.strip())
        for number, line in raw_lines
        if line.strip() and not line.lstrip().startswith("#")
    ]

    if not meaningful or meaningful[0][1].lower() != PROTOCOL_HEADER:
        raise SDLValidationError("CMB-SDL document must begin with 'cmb/1'.")

    human = ""
    agent = ""
    purpose = ""
    expires_at = ""
    allow: set[str] = set()
    deny: set[str] = set()
    scopes: set[ScopeBinding] = set()
    required: set[str] = set()
    handlers: dict[str, str] = {}
    return_receipt = True
    delegable = False
    seen_singletons: set[str] = set()

    for line_number, line in meaningful[1:]:
        if line.upper().startswith("ON ") and "=>" in line:
            left, right = (part.strip() for part in line.split("=>", 1))
            left_tokens = _tokens(left, line_number)
            right_tokens = _tokens(right, line_number)
            if len(left_tokens) != 2 or left_tokens[0].upper() != "ON" or len(right_tokens) != 1:
                raise SDLValidationError(f"Line {line_number}: malformed ON handler.")
            event = left_tokens[1].lower()
            action = right_tokens[0].upper()
            if event not in KNOWN_EVENTS:
                raise SDLValidationError(f"Line {line_number}: unknown event {event!r}.")
            if action not in KNOWN_HANDLER_ACTIONS:
                raise SDLValidationError(
                    f"Line {line_number}: unknown handler action {action!r}."
                )
            if event in handlers:
                raise SDLValidationError(
                    f"Line {line_number}: duplicate handler for {event!r}."
                )
            handlers[event] = action
            continue

        tokens = _tokens(line, line_number)
        if not tokens:
            continue
        keyword = tokens[0].upper()

        def singleton(name: str) -> None:
            if name in seen_singletons:
                raise SDLValidationError(f"Line {line_number}: duplicate {name}.")
            seen_singletons.add(name)

        if keyword in {"HUMAN", "AGENT", "PURPOSE", "EXPIRES"}:
            if len(tokens) != 2:
                raise SDLValidationError(
                    f"Line {line_number}: {keyword} requires exactly one value."
                )
            singleton(keyword)
            value = tokens[1]
            if keyword == "HUMAN":
                human = value
            elif keyword == "AGENT":
                agent = value
            elif keyword == "PURPOSE":
                purpose = value
            else:
                expires_at = value
        elif keyword in {"ALLOW", "DENY", "REQUIRE"}:
            if len(tokens) != 2:
                raise SDLValidationError(
                    f"Line {line_number}: {keyword} requires exactly one token."
                )
            value = tokens[1]
            if keyword == "ALLOW":
                allow.add(value)
            elif keyword == "DENY":
                deny.add(value)
            else:
                required.add(value)
        elif keyword == "SCOPE":
            if len(tokens) != 3:
                raise SDLValidationError(
                    f"Line {line_number}: SCOPE requires kind and value."
                )
            scopes.add(ScopeBinding(tokens[1], tokens[2]))
        elif keyword == "RETURN":
            if len(tokens) != 2 or tokens[1].lower() != "receipt":
                raise SDLValidationError(
                    f"Line {line_number}: only 'RETURN receipt' is valid in v1."
                )
            singleton("RETURN")
            return_receipt = True
        elif keyword == "DELEGABLE":
            if len(tokens) != 2 or tokens[1].lower() not in BOOLEAN_LITERALS:
                raise SDLValidationError(
                    f"Line {line_number}: DELEGABLE must be true or false."
                )
            singleton("DELEGABLE")
            delegable = BOOLEAN_LITERALS[tokens[1].lower()]
        else:
            raise SDLValidationError(
                f"Line {line_number}: unknown statement {keyword!r}."
            )

    missing = [
        name
        for name, value in (
            ("HUMAN", human),
            ("AGENT", agent),
            ("PURPOSE", purpose),
            ("EXPIRES", expires_at),
        )
        if not value
    ]
    if missing:
        raise SDLValidationError(
            f"Missing required statements: {', '.join(missing)}."
        )

    return AuthorityDocument(
        human=human,
        agent=agent,
        allow=tuple(sorted(allow)),
        deny=tuple(sorted(deny)),
        scopes=tuple(sorted(scopes)),
        purpose=purpose,
        expires_at=expires_at,
        required_evidence=tuple(sorted(required)),
        event_handlers=tuple(sorted(handlers.items())),
        return_receipt=return_receipt,
        delegable=delegable,
    )
