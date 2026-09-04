"""Parser for CMB-EDU Dual-Brain educational syntax."""

from __future__ import annotations

import re

from .models import ContextEnvelope
from .policy import canonical_boundary, privacy_from_tokens, translate_boundary

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
        return "ask", instruction.strip('"\'')

    call = _CALL_PATTERN.fullmatch(instruction)
    if not call:
        first, _, remainder = instruction.partition(" ")
        return first.lower(), remainder.strip() or instruction

    operation = call.group("operation").lower()
    argument = call.group("argument").strip()
    if len(argument) >= 2 and argument[0] == argument[-1] and argument[0] in {"'", '"'}:
        argument = argument[1:-1]
    return operation, argument


class CMBDualBrainParser:
    """Parse CMB educational streams into privacy-first structured envelopes."""

    def parse_envelope(self, stream_text: str) -> ContextEnvelope:
        if not isinstance(stream_text, str) or not stream_text.strip():
            raise ValueError("CMB Education Stream must be a non-empty string.")

        stream = stream_text.strip()
        match = _MODERN_PATTERN.fullmatch(stream)
        modern = match is not None
        if match is None:
            match = _LEGACY_PATTERN.fullmatch(stream)
        if match is None:
            raise ValueError(
                "Malformed CMB Education Stream. Use DECLARE/ASK/BOUNDARY syntax "
                "or the compatible STATE => instruction form."
            )

        data = match.groupdict()
        states = tuple(_split_double_pipe(data.get("states")))
        if not states:
            raise ValueError("At least one human-declared state/context token is required.")

        boundary = canonical_boundary(data["boundary"])
        privacy = privacy_from_tokens(_split_double_pipe(data.get("privacy")))
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
        """Compatibility API returning a JSON-serializable dictionary."""

        return self.parse_envelope(stream_text).to_dict()
