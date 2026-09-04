"""CMB-EDU sovereignty and privacy policy helpers."""

from __future__ import annotations

from .models import PrivacyPolicy

INVARIANT_TRANSLATIONS: dict[str, str] = {
    "PATTERN_NOT_PROOF": "MACHINE_PATTERN_IS_NOT_HUMAN_TRUTH",
    "PROFILE_NOT_PERSON": "AVATAR_IS_NOT_HEART",
    "PREDICTION_NOT_DESTINY": "MACHINE_GUESSES_I_CHOOSE",
    "ATTENTION_NOT_CONSENT": "LOOKING_IS_NOT_PERMISSION",
    "DIFFERENCE_NOT_DEFECT": "DIFFERENT_IS_NOT_BROKEN",
    "MODEL_NOT_MIND": "MODEL_IS_NOT_MY_MIND",
    "CAPABILITY_NOT_AUTHORITY": "CAN_DO_IS_NOT_MAY_DECIDE",
}

FGC_BOUNDARY_ALIASES: dict[str, str] = {
    "NO_PROFILE": "PROFILE_NOT_PERSON",
    "MACHINE_GUESS": "PREDICTION_NOT_DESTINY",
    "DIFFERENT_NOT_BROKEN": "DIFFERENCE_NOT_DEFECT",
    "HUMAN_DECIDES": "CAPABILITY_NOT_AUTHORITY",
}


def canonical_boundary(boundary: str) -> str:
    normalized = boundary.strip().upper()
    normalized = FGC_BOUNDARY_ALIASES.get(normalized, normalized)
    if normalized not in INVARIANT_TRANSLATIONS:
        raise ValueError(f"unknown sovereignty boundary: {boundary}")
    return normalized


def translate_boundary(boundary: str) -> str:
    return INVARIANT_TRANSLATIONS[canonical_boundary(boundary)]


def privacy_from_tokens(tokens: list[str] | tuple[str, ...] | None) -> PrivacyPolicy:
    """Parse restrictive privacy declarations.

    v1 intentionally supports deny-style declarations only. No token can
    silently enable profiling, training reuse, or psychological inference.
    """

    if not tokens:
        return PrivacyPolicy()

    allowed = {
        "EPHEMERAL",
        "NO_PERSIST",
        "NO_PROFILE",
        "NO_TRAIN",
        "NO_SECONDARY_USE",
        "NO_PSYCHOLOGICAL_INFERENCE",
        "PRIVATE",
    }
    normalized = {token.strip().upper() for token in tokens if token.strip()}
    unknown = normalized - allowed
    if unknown:
        raise ValueError(
            "unknown CMB-EDU privacy token(s): " + ", ".join(sorted(unknown))
        )
    return PrivacyPolicy()
