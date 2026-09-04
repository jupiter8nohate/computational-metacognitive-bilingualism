"""Flamingoglyph Code (FGC) compiler for CMB-EDU lessons."""

from __future__ import annotations

import re

from .models import ContextEnvelope
from .parser import CMBParseError
from .policy import canonical_boundary, privacy_from_tokens, translate_boundary

_MAX_STREAM_LENGTH = 4096
_MAX_STATES = 8
_TOKEN_SPLIT = re.compile(r"\s*(?:\+|\n)\s*")
_VARIATION_SELECTOR = "\ufe0f"

FGC_LEGEND: dict[str, str] = {
    "🧠": "human_declared_context",
    "❤": "human_declared_feeling",
    "👁": "notice",
    "❓": "question",
    "⚡": "action",
    "🪐": "context_or_mode",
    "🛡": "boundary",
    "🔒": "private",
    "⏳": "ephemeral",
    "🤖": "machine",
    "🧑": "human",
    "✅": "consent_yes",
    "🚫": "deny",
    "🔍": "verify",
    "🎨": "create",
    "🔁": "try_again",
    "💡": "new_idea",
}
_PREFIXES = tuple(sorted(FGC_LEGEND, key=len, reverse=True))


def _payload(token: str, glyph: str) -> str:
    return token[len(glyph) :].strip()


class FGCEmojiParser:
    """Compile simple FGC classroom glyphs into a CMB-EDU envelope."""

    def parse_envelope(self, text: str) -> ContextEnvelope:
        if not isinstance(text, str) or not text.strip():
            raise CMBParseError("FGC learning stream must be a non-empty string")
        if len(text) > _MAX_STREAM_LENGTH:
            raise CMBParseError(
                f"FGC stream exceeds the {_MAX_STREAM_LENGTH}-character safety limit"
            )

        states: list[str] = []
        mode = "LEARNING"
        instruction = "REFLECT"
        boundary = "PROFILE_NOT_PERSON"
        privacy_tokens = [
            "EPHEMERAL",
            "NO_PROFILE",
            "NO_TRAIN",
            "NO_PSYCHOLOGICAL_INFERENCE",
        ]

        normalized_text = text.replace(_VARIATION_SELECTOR, "")
        for raw_token in _TOKEN_SPLIT.split(normalized_text.strip()):
            token = raw_token.strip()
            if not token:
                continue

            glyph = next(
                (prefix for prefix in _PREFIXES if token.startswith(prefix)),
                None,
            )
            if glyph is None:
                raise CMBParseError(f"unknown FGC token: {token!r}")

            value = _payload(token, glyph)
            if glyph in {"🧠", "❤"} and value:
                states.append(value.lower())
            elif glyph == "🪐" and value:
                mode = value.upper().replace(" ", "_")
            elif glyph in {"⚡", "🎨", "❓"} and value:
                instruction = value
            elif glyph == "🛡" and value:
                boundary = value.upper().replace(" ", "_")
            elif glyph == "⏳":
                privacy_tokens.append("EPHEMERAL")
            elif glyph == "🔒":
                privacy_tokens.append("PRIVATE")
            elif glyph == "🚫":
                upper = value.upper()
                if "TRAIN" in upper:
                    privacy_tokens.append("NO_TRAIN")
                elif "PROFILE" in upper:
                    privacy_tokens.append("NO_PROFILE")
                elif "SECONDARY" in upper:
                    privacy_tokens.append("NO_SECONDARY_USE")
                elif "INFER" in upper or "PSYCHOLOG" in upper:
                    privacy_tokens.append("NO_PSYCHOLOGICAL_INFERENCE")

        if not states:
            states.append("unspecified")
        if len(states) > _MAX_STATES:
            raise CMBParseError(
                f"no more than {_MAX_STATES} declared context states are allowed"
            )
        if any(len(state) > 64 for state in states):
            raise CMBParseError("declared context states must be at most 64 characters")

        try:
            canonical = canonical_boundary(boundary)
            privacy = privacy_from_tokens(privacy_tokens)
        except ValueError as exc:
            raise CMBParseError(str(exc)) from exc

        first, _, remainder = instruction.partition(" ")
        operation = first.lower() if first else "reflect"
        subject = remainder.strip() or instruction
        if len(instruction) > 2048 or len(subject) > 2048:
            raise CMBParseError("FGC instruction exceeds the 2048-character limit")

        return ContextEnvelope(
            lens="FGC-KIDS",
            mode=mode[:32],
            states=tuple(states),
            raw_instruction=instruction,
            operation=operation,
            subject=subject,
            boundary=canonical,
            boundary_translation=translate_boundary(canonical),
            privacy=privacy,
        )

    def parse_stream(self, text: str) -> dict[str, object]:
        return self.parse_envelope(text).to_dict()
