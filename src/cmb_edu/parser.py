"""Parser for the experimental CMB-EDU Dual-Brain Stream syntax.

The parser records human-declared interaction context. It does not infer,
diagnose, or persist psychological state.
"""

from __future__ import annotations

import re
from typing import Any

from .models import ContextEnvelope, PrivacyPolicy
from .policy import (
    INVARIANT_TRANSLATIONS,
    canonical_boundary,
    privacy_from_tokens,
    translate_boundary,
)


class CMBParseError(ValueError):
    """Raised when a CMB-EDU stream violates the grammar or policy."""


_MAX_STREAM_LENGTH = 4096
_MAX_STATES = 8

_LEGACY_STREAM = re.compile(
    r"^(?P<lens>[^:]+)::(?P<mode>[A-Za-z_]+)\s*"
    r"->\s*(?:STATE|DECLARE)\[(?P<states>[^\]]*)\]\s*"
    r"=>\s*(?P<instruction>.+?)\s*"
    r"->\s*(?P<boundary>[A-Za-z_]+)"
    r"(?:\s*->\s*PRIVACY\[(?P<privacy>[^\]]*)\])?\s*;\s*$"
)

_EXPLICIT_STREAM = re.compile(
    r"^(?P<lens>[^:]+)::(?P<mode>[A-Za-z_]+)\s*"
    r"->\s*DECLARE\[(?P<states>[^\]]*)\]\s*"
    r"->\s*ASK\[(?P<instruction>[^\]]+)\]\s*"
    r"->\s*BOUNDARY\[(?P<boundary>[A-Za-z_]+)\]"
    r"(?:\s*->\s*PRIVACY\[(?P<privacy>[^\]]*)\])?\s*;\s*$"
)

_CALL = re.compile(
    r"^(?P<operation>[A-Za-z_][A-Za-z0-9_]*)\((?P<argument>.*)\)$"
)


def _split_double_pipe(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split("||") if item.strip()]


def _decode_instruction(raw: str, *, explicit: bool) -> tuple[str, str]:
    instruction = raw.strip()
    if explicit:
        return "ask", instruction.strip('"'')

    call = _CALL.fullmatch(instruction)
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
        match = _EXPLICIT_STREAM.fullmatch(stream)
        explicit = match is not None
        if match is None:
            match = _LEGACY_STREAM.fullmatch(stream)
        if match is None:
            raise CMBParseError("malformed CMB-EDU stream")

        data = match.groupdict()
        lens = data["lens"].strip()
        mode = data["mode"].strip().upper()
        states = tuple(_split_double_pipe(data.get("states")))
        raw_instruction = data["instruction"].strip()

        if len(lens) > 32:
            raise CMBParseError("human lens must be at most 32 characters")
        if len(mode) > 32:
            raise CMBParseError("cognitive mode must be at most 32 characters")
        if not states:
            raise CMBParseError(
                "at least one human-declared context state is required"
            )
        if len(states) > _MAX_STATES:
            raise CMBParseError(
                f"no more than {_MAX_STATES} declared context states are allowed"
            )
        if any(len(state) > 64 for state in states):
            raise CMBParseError("declared context states must be at most 64 characters")
        if len(raw_instruction) > 2048:
            raise CMBParseError("instruction exceeds the 2048-character limit")

        try:
            boundary = canonical_boundary(data["boundary"])
        except ValueError as exc:
            raise CMBParseError(
                f"unknown sovereignty boundary: {data['boundary']}"
            ) from exc

        try:
            privacy = privacy_from_tokens(
                _split_double_pipe(data.get("privacy"))
            )
        except ValueError as exc:
            raise CMBParseError(str(exc)) from exc

        operation, subject = _decode_instruction(
            raw_instruction,
            explicit=explicit,
        )

        return ContextEnvelope(
            lens=lens,
            mode=mode,
            states=states,
            raw_instruction=raw_instruction,
            operation=operation,
            subject=subject,
            boundary=boundary,
            boundary_translation=translate_boundary(boundary),
            privacy=privacy,
        )

    def parse_stream(self, stream_text: str) -> dict[str, Any]:
        return self.parse_envelope(stream_text).to_dict()
