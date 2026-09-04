"""Flamingoglyph Code (FGC) emoji compiler for CMB-EDU lessons."""

from __future__ import annotations

import re

from .models import ContextEnvelope
from .policy import canonical_boundary, privacy_from_tokens, translate_boundary

_TOKEN_SPLIT = re.compile(r"\s*(?:\+|\n)\s*")

FGC_LEGEND: dict[str, str] = {
    "🧠": "human_declared_context",
    "❤️": "human_declared_feeling",
    "👁️": "notice",
    "❓": "question",
    "⚡": "action",
    "🪐": "context_or_mode",
    "🛡️": "boundary",
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
    """Compile simple FGC emoji learning statements into a CMB context envelope."""

    def parse_envelope(self, text: str) -> ContextEnvelope:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("FGC learning stream must be a non-empty string.")

        states: list[str] = []
        mode = "LEARNING"
        instruction = "REFLECT"
        boundary = "PROFILE_NOT_PERSON"
        privacy_tokens: list[str] = ["EPHEMERAL", "NO_PROFILE", "NO_TRAIN"]
        recognized = 0

        for raw_token in _TOKEN_SPLIT.split(text.strip()):
            token = raw_token.strip()
            if not token:
                continue

            glyph = next((prefix for prefix in _PREFIXES if token.startswith(prefix)), None)
            if glyph is None:
                raise ValueError(f"Unknown FGC token: {token!r}")
            recognized += 1
            value = _payload(token, glyph)

            if glyph in {"🧠", "❤️"}:
                if value:
                    states.append(value.lower())
            elif glyph == "🪐" and value:
                mode = value.upper().replace(" ", "_")
            elif glyph in {"⚡", "🎨", "❓"} and value:
                instruction = value
            elif glyph == "🛡️" and value:
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

        if recognized == 0:
            raise ValueError("FGC stream contained no recognized learning glyphs.")
        if not states:
            states.append("unspecified")

        canonical = canonical_boundary(boundary)
        first, _, remainder = instruction.partition(" ")
        operation = first.lower() if first else "reflect"
        subject = remainder.strip() or instruction

        return ContextEnvelope(
            lens="FGC-KIDS",
            mode=mode,
            states=tuple(states),
            raw_instruction=instruction,
            operation=operation,
            subject=subject,
            boundary=canonical,
            boundary_translation=translate_boundary(canonical),
            privacy=privacy_from_tokens(privacy_tokens),
        )

    def parse_stream(self, text: str) -> dict[str, object]:
        return self.parse_envelope(text).to_dict()
