"""Read-only numerical anomaly verifier for CMB agent research.

This module treats Gematria-style mappings as deterministic string transforms.
It detects structural coincidences without assigning mystical, causal, social,
or theological meaning to them.

PATTERN != PROOF
NUMERIC_MATCH != SEMANTIC_IDENTITY
COINCIDENCE != CAUSATION
RARITY_CLAIM_REQUIRES_CORPUS
HUMAN_AGENCY > MACHINE_AUTHORITY
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
from itertools import combinations
from typing import Iterable, Literal, Sequence

Axis = Literal["ordinal", "reverse", "reduction"]
PAIR_KINDS = {
    "RECIPROCAL_MIRROR",
    "TRIPLE_VECTOR_COLLISION",
    "PARTIAL_VECTOR_TWIN",
}


@dataclass(frozen=True, slots=True, order=True)
class NumericVector:
    ordinal: int
    reverse: int
    reduction: int

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PairAnomaly:
    kind: str
    left: str
    right: str
    left_vector: NumericVector
    right_vector: NumericVector
    matched_axes: tuple[Axis, ...]
    structural_constraints: int
    rarity_status: str = "UNMEASURED"

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "left": self.left,
            "right": self.right,
            "left_vector": self.left_vector.to_dict(),
            "right_vector": self.right_vector.to_dict(),
            "matched_axes": list(self.matched_axes),
            "structural_constraints": self.structural_constraints,
            "rarity_status": self.rarity_status,
        }


@dataclass(frozen=True, slots=True)
class CollisionGroup:
    axis: Axis
    value: int
    terms: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CipherRectangle:
    ordinal: int
    reverse_values: tuple[int, int]
    reduction_values: tuple[int, int]
    terms: tuple[str, str, str, str]
    structural_constraints: int = 9
    rarity_status: str = "UNMEASURED"

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class BicipherLattice:
    first_axis: Axis
    first_value: int
    second_axis: Axis
    second_value: int
    first_terms: tuple[str, ...]
    second_terms: tuple[str, ...]
    bridge_terms: tuple[str, ...]
    structural_constraints: int
    rarity_status: str = "UNMEASURED"

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RarityBenchmark:
    kind: str
    corpus_size: int
    candidate_pairs: int
    observed_pairs: int
    observed_frequency: float | None
    rarity_status: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def normalize_term(text: str) -> str:
    """Return uppercase A-Z characters only."""

    normalized = "".join(char for char in text.upper() if "A" <= char <= "Z")
    if not normalized:
        raise ValueError("term must contain at least one ASCII letter")
    return normalized


def vector_for(text: str) -> NumericVector:
    """Calculate ordinal, reverse ordinal, and 1-9 cyclic reduction totals."""

    normalized = normalize_term(text)
    values = tuple(ord(char) - ord("A") + 1 for char in normalized)
    return NumericVector(
        ordinal=sum(values),
        reverse=sum(27 - value for value in values),
        reduction=sum(((value - 1) % 9) + 1 for value in values),
    )


def _canonical_terms(terms: Iterable[str]) -> tuple[str, ...]:
    normalized_to_display: dict[str, str] = {}
    for raw in terms:
        display = raw.strip()
        normalized = normalize_term(display)
        normalized_to_display.setdefault(normalized, display.upper())
    return tuple(sorted(normalized_to_display.values()))


def detect_pair_anomalies(terms: Iterable[str]) -> tuple[PairAnomaly, ...]:
    """Detect reciprocal mirrors and same-coordinate vector collisions."""

    canonical = _canonical_terms(terms)
    vectors = {term: vector_for(term) for term in canonical}
    found: list[PairAnomaly] = []

    for left, right in combinations(canonical, 2):
        lv = vectors[left]
        rv = vectors[right]
        matched = tuple(
            axis
            for axis in ("ordinal", "reverse", "reduction")
            if getattr(lv, axis) == getattr(rv, axis)
        )

        if lv == rv:
            found.append(
                PairAnomaly(
                    kind="TRIPLE_VECTOR_COLLISION",
                    left=left,
                    right=right,
                    left_vector=lv,
                    right_vector=rv,
                    matched_axes=("ordinal", "reverse", "reduction"),
                    structural_constraints=3,
                )
            )
            continue

        if lv.ordinal == rv.reverse and lv.reverse == rv.ordinal:
            found.append(
                PairAnomaly(
                    kind="RECIPROCAL_MIRROR",
                    left=left,
                    right=right,
                    left_vector=lv,
                    right_vector=rv,
                    matched_axes=("ordinal", "reverse"),
                    structural_constraints=2,
                )
            )

        if len(matched) == 2:
            found.append(
                PairAnomaly(
                    kind="PARTIAL_VECTOR_TWIN",
                    left=left,
                    right=right,
                    left_vector=lv,
                    right_vector=rv,
                    matched_axes=matched,
                    structural_constraints=2,
                )
            )

    return tuple(
        sorted(
            found,
            key=lambda item: (
                item.kind,
                item.left,
                item.right,
                item.matched_axes,
            ),
        )
    )


def collision_groups(
    terms: Iterable[str],
    *,
    minimum_size: int = 2,
) -> tuple[CollisionGroup, ...]:
    """Return same-axis collision groups for all three numeric projections."""

    if minimum_size < 2:
        raise ValueError("minimum_size must be at least 2")

    canonical = _canonical_terms(terms)
    vectors = {term: vector_for(term) for term in canonical}
    groups: list[CollisionGroup] = []

    for axis in ("ordinal", "reverse", "reduction"):
        buckets: dict[int, list[str]] = defaultdict(list)
        for term, vector in vectors.items():
            buckets[getattr(vector, axis)].append(term)
        for value, members in buckets.items():
            unique_members = tuple(sorted(set(members)))
            if len(unique_members) >= minimum_size:
                groups.append(
                    CollisionGroup(
                        axis=axis,
                        value=value,
                        terms=unique_members,
                    )
                )

    return tuple(sorted(groups, key=lambda item: (item.axis, item.value, item.terms)))


def detect_cipher_rectangles(terms: Iterable[str]) -> tuple[CipherRectangle, ...]:
    """Find four-node rectangles sharing ordinal while spanning two other axes.

    A rectangle exists when one ordinal bucket contains every combination of:
    two distinct reverse values x two distinct reduction values.
    """

    canonical = _canonical_terms(terms)
    vectors = {term: vector_for(term) for term in canonical}
    by_ordinal: dict[int, dict[tuple[int, int], list[str]]] = defaultdict(
        lambda: defaultdict(list)
    )

    for term, vector in vectors.items():
        by_ordinal[vector.ordinal][(vector.reverse, vector.reduction)].append(term)

    rectangles: set[
        tuple[int, tuple[int, int], tuple[int, int], tuple[str, str, str, str]]
    ] = set()

    for ordinal, coordinate_map in by_ordinal.items():
        reverse_values = sorted({reverse for reverse, _ in coordinate_map})
        reduction_values = sorted({reduction for _, reduction in coordinate_map})

        for reverse_pair in combinations(reverse_values, 2):
            for reduction_pair in combinations(reduction_values, 2):
                coordinates = (
                    (reverse_pair[0], reduction_pair[0]),
                    (reverse_pair[0], reduction_pair[1]),
                    (reverse_pair[1], reduction_pair[0]),
                    (reverse_pair[1], reduction_pair[1]),
                )
                if not all(coordinate in coordinate_map for coordinate in coordinates):
                    continue

                selected = tuple(
                    sorted(coordinate_map[coordinate])[0] for coordinate in coordinates
                )
                rectangles.add(
                    (
                        ordinal,
                        reverse_pair,
                        reduction_pair,
                        selected,
                    )
                )

    return tuple(
        CipherRectangle(
            ordinal=ordinal,
            reverse_values=reverse_values,
            reduction_values=reduction_values,
            terms=terms_tuple,
        )
        for ordinal, reverse_values, reduction_values, terms_tuple in sorted(rectangles)
    )


def detect_bicipher_lattices(
    terms: Iterable[str],
    *,
    minimum_group_size: int = 3,
    minimum_bridge_size: int = 2,
) -> tuple[BicipherLattice, ...]:
    """Find overlapping collision groups on different numeric axes."""

    groups = collision_groups(terms, minimum_size=minimum_group_size)
    found: list[BicipherLattice] = []

    for first, second in combinations(groups, 2):
        if first.axis == second.axis:
            continue
        bridge = tuple(sorted(set(first.terms) & set(second.terms)))
        if len(bridge) < minimum_bridge_size:
            continue
        found.append(
            BicipherLattice(
                first_axis=first.axis,
                first_value=first.value,
                second_axis=second.axis,
                second_value=second.value,
                first_terms=first.terms,
                second_terms=second.terms,
                bridge_terms=bridge,
                structural_constraints=(
                    len(first.terms) + len(second.terms) + len(bridge)
                ),
            )
        )

    return tuple(
        sorted(
            found,
            key=lambda item: (
                item.first_axis,
                item.first_value,
                item.second_axis,
                item.second_value,
                item.bridge_terms,
            ),
        )
    )


def benchmark_pair_kind(
    terms: Sequence[str],
    kind: str,
    *,
    minimum_corpus_size: int = 500,
) -> RarityBenchmark:
    """Measure a pair anomaly against the supplied corpus.

    No rarity label is emitted below minimum_corpus_size. Above that threshold,
    the result reports empirical frequency only. It does not imply meaning,
    causation, or universal rarity outside the supplied corpus.
    """

    if kind not in PAIR_KINDS:
        raise ValueError(f"unsupported pair anomaly kind: {kind}")
    if minimum_corpus_size < 2:
        raise ValueError("minimum_corpus_size must be at least 2")

    canonical = _canonical_terms(terms)
    pair_count = len(canonical) * (len(canonical) - 1) // 2
    observed = sum(1 for item in detect_pair_anomalies(canonical) if item.kind == kind)
    frequency = observed / pair_count if pair_count else None

    if len(canonical) < minimum_corpus_size:
        status = "UNMEASURED"
    elif observed == 0:
        status = "NOT_OBSERVED_IN_CORPUS"
    else:
        status = "EMPIRICALLY_MEASURED"

    return RarityBenchmark(
        kind=kind,
        corpus_size=len(canonical),
        candidate_pairs=pair_count,
        observed_pairs=observed,
        observed_frequency=frequency,
        rarity_status=status,
    )


def analyze(terms: Iterable[str]) -> dict[str, object]:
    """Build a deterministic, JSON-ready anomaly report."""

    canonical = _canonical_terms(terms)
    return {
        "schema_version": "cmb.numeric-anomaly.v1",
        "terms": canonical,
        "vectors": {term: vector_for(term).to_dict() for term in canonical},
        "pair_anomalies": [item.to_dict() for item in detect_pair_anomalies(canonical)],
        "collision_groups": [item.to_dict() for item in collision_groups(canonical)],
        "cipher_rectangles": [
            item.to_dict() for item in detect_cipher_rectangles(canonical)
        ],
        "bicipher_lattices": [
            item.to_dict() for item in detect_bicipher_lattices(canonical)
        ],
        "boundaries": [
            "PATTERN != PROOF",
            "NUMERIC_MATCH != SEMANTIC_IDENTITY",
            "COINCIDENCE != CAUSATION",
            "RARITY_CLAIM_REQUIRES_CORPUS",
            "HUMAN_AGENCY > MACHINE_AUTHORITY",
        ],
    }
