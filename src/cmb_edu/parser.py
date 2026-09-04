"""Parser for the experimental CMB-EDU Dual-Brain Stream syntax.

The parser records human-declared interaction context. It does not infer,
diagnose, or persist psychological state.
"""

from __future__ import annotations

import re

from .errors import CMBParseError
from .models import ContextEnvelope, PrivacyPolicy
from .policy import (
    INVARIANT_TRANSLATIONS,
    canonical_boundary,
    privacy_from_tokens,
    translate_boundary,
)

_MAX_STREAM_LENGTH = 4096
_MAX_STATES = 8

_LEGACY_PATTERN = re.compile(
    r"^(?P<lens>.+?)::(?P<mode>[A-Za-z_]+)\s*"
    r"->\s*(?:STATE|DECLARE)\[(?P<states>[^\]]*)\]\s*"
    r"=>\s*(?P<instruction>.+?)\s*"
    r"->\s*(?P<boundary>[A-Za-z_]+)"
    r"(?:\s*->\s*PRIVACY\[(?P<privacy>[^\]]*)\])?\s*;$"
)

_MODERN_PATTERN = re.compile(
    r"^(?P<lens>.+?)::(?P<mode>[A-Za-z_]+)\s*"
    r"->\s*DECLARE\[(?P<states>[^\]]*)\]\s*"
    r"->\s*ASK\[(?P<instruction>[^\]]+)\]\s*"
    r"->\s*BOUNDARY\[(?P<boundary>[A-Za-z_]+)\]"
    r"(?:\s*->\s*PRIVACY\[(?P<privacy>[^\]]*)\])?\s*;$"
)

_CALL_PATTERN = re.compile(
    r"^(?P<operation>[A-Za-z_][A-Za-z0-9_]*)\((?P<argument>.*)\)$"
)


def _split_double_pipe(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split("||") if item.strip()]


def _decode_instruction(raw: str, *, modern: bool) -> tuple[str, str]:
    instruction = raw.strip()
    if modern:
        return "ask", instruction.strip('"'')

    call = _CALL_PATTERN.fullmatch(instruction)
    if call is None:
        first, _, remainder = instruction.partition(" ")
        return first.lower(), remainder.strip() or instruction

    operation = call.group("operation").lower()
    argument = call.group("argument").strip()
    if (
        len(argument) >= 2
        and argument[0] == argument[-1]
        and argument[0] in {"'", '"'}
    ):
        argument = argument[1:-1]
    return operation, argument


class CMBDualBrainParser:
    """Parse CMB educational streams into privacy-first structured envelopes."""

    FRAMEWORK = "CMB-EDU-v1.0"
    INVARIANTS = dict(INVARIANT_TRANSLATIONS)
    DEFAULT_PRIVACY = PrivacyPolicy().to_dict()

    def parse_envelope(self, stream_text: str) -> ContextEnvelope:
        if not isinstance(stream_text, str) or not stream_text.strip():
            raise CMBParseError("stream_text must be a non-empty string")
        if len(stream_text) > _MAX_STREAM_LENGTH:
            raise CMBParseError(
                f"stream exceeds the {_MAX_STREAM_LENGTH}-character safety limit"
            )

        stream = stream_text.strip()
        match = _MODERN_PATTERN.fullmatch(stream)
        modern = match is not None
        if match is None:
            match = _LEGACY_PATTERN.fullmatch(stream)
        if match is None:
            raise CMBParseError(
                "malformed CMB-EDU stream; use DECLARE/ASK/BOUNDARY syntax "
                "or the compatible STATE => instruction form"
            )

        data = match.groupdict()
        states = tuple(_split_double_pipe(data.get("states")))
        if not states:
            raise CMBParseError(
                "at least one human-declared context state is required"
            )
        if len(states) > _MAX_STATES:
            raise CMBParseError(
                f"no more than {_MAX_STATES} declared context states are allowed"
            )

        try:
            boundary = canonical_boundary(data["boundary"])
            privacy = privacy_from_tokens(_split_double_pipe(data.get("privacy")))
        except ValueError as exc:
            raise CMBParseError(str(exc)) from exc

        operation, subject = _decode_instruction(
            data["instruction"],
            modern=modern,
        )

        return ContextEnvelope(
            lens=data["lens"].strip(),
            mode=data["mode"].strip().upper(),
            states=states,
            raw_instruction=data["instruction"].strip(),
            operation=operation,
            subject=subject,
            boundary=boundary,
            boundary_translation=translate_boundary(boundary),
            privacy=privacy,
        )

    def parse_stream(self, stream_text: str) -> dict[str, object]:
        """Return the public JSON-serializable CMB-EDU v1 payload."""

        return self.parse_envelope(stream_text).to_dict()
