"""Parser for the experimental CMB-EDU Dual-Brain Stream syntax.

The parser records human-declared interaction context. It does not infer,
diagnose, or persist psychological state.
"""

from __future__ import annotations

import re
from typing import Any


class CMBParseError(ValueError):
    """Raised when a CMB-EDU stream violates the grammar or policy."""


class CMBDualBrainParser:
    FRAMEWORK = "CMB-EDU-v1.0"
    INVARIANTS = {
        "PATTERN_NOT_PROOF": "MACHINE_PATTERN_IS_NOT_HUMAN_TRUTH",
        "PROFILE_NOT_PERSON": "AVATAR_IS_NOT_HEART",
        "PREDICTION_NOT_DESTINY": "MACHINE_GUESSES_I_CHOOSE",
        "ATTENTION_NOT_CONSENT": "LOOKING_IS_NOT_PERMISSION",
        "DIFFERENCE_NOT_DEFECT": "DIFFERENT_IS_NOT_BROKEN",
        "MODEL_NOT_MIND": "MODEL_IS_NOT_MY_MIND",
    }
    DEFAULT_PRIVACY = {
        "persistence": "ephemeral",
        "training_permission": False,
        "profiling_permission": False,
        "secondary_use_permission": False,
        "psychological_inference_permission": False,
    }
    _STREAM = re.compile(
        r"^(?P<lens>[^:]+)::(?P<mode>[A-Z_]+)\s*"
        r"->\s*(?:STATE|DECLARE)\[(?P<states>[^\]]*)\]\s*"
        r"=>\s*(?P<instruction>.+?)\s*"
        r"->\s*(?P<boundary>[A-Z_]+)\s*;\s*$"
    )

    def parse_stream(self, stream_text: str) -> dict[str, Any]:
        if not isinstance(stream_text, str) or not stream_text.strip():
            raise CMBParseError("stream_text must be a non-empty string")
        if len(stream_text) > 4096:
            raise CMBParseError("stream exceeds the 4096-character safety limit")

        match = self._STREAM.fullmatch(stream_text.strip())
        if match is None:
            raise CMBParseError("malformed CMB-EDU stream")

        data = match.groupdict()
        boundary = data["boundary"]
        if boundary not in self.INVARIANTS:
            raise CMBParseError(f"unknown sovereignty boundary: {boundary}")

        states = [state.strip() for state in data["states"].split("||") if state.strip()]
        if not states:
            raise CMBParseError("at least one human-declared context state is required")
        if len(states) > 8:
            raise CMBParseError("no more than 8 declared context states are allowed")

        return {
            "schema": "cmb.edu.v1",
            "meta": {
                "framework": self.FRAMEWORK,
                "human_lens": data["lens"].strip(),
                "cognitive_mode": data["mode"],
            },
            "context": {
                "source": "human_declared",
                "states": states,
                "machine_inferred": False,
                "temporal_scope": "current_interaction",
            },
            "execution": {"raw_instruction": data["instruction"].strip()},
            "sovereignty_gate": {
                "declared_invariant": boundary,
                "enforced_translation": self.INVARIANTS[boundary],
            },
            "privacy": dict(self.DEFAULT_PRIVACY),
        }
