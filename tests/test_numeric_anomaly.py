from __future__ import annotations

import pytest

from cmb_agents.numeric_anomaly import (
    analyze,
    benchmark_pair_kind,
    detect_bicipher_lattices,
    detect_cipher_rectangles,
    detect_pair_anomalies,
    vector_for,
)


def _alpha_id(value: int) -> str:
    chars: list[str] = []
    current = value
    while True:
        current, remainder = divmod(current, 26)
        chars.append(chr(ord("A") + remainder))
        if current == 0:
            return "".join(reversed(chars))
        current -= 1


def test_known_social_vectors() -> None:
    assert vector_for("FOLLOWER").to_dict() == {
        "ordinal": 106,
        "reverse": 110,
        "reduction": 43,
    }
    assert vector_for("IDENTITY").to_dict() == {
        "ordinal": 106,
        "reverse": 110,
        "reduction": 43,
    }
    assert vector_for("JUPITER").to_dict() == {
        "ordinal": 99,
        "reverse": 90,
        "reduction": 36,
    }
    assert vector_for("CONSENT").to_dict() == {
        "ordinal": 90,
        "reverse": 99,
        "reduction": 27,
    }


def test_triple_vector_collision() -> None:
    anomalies = detect_pair_anomalies(["FOLLOWER", "IDENTITY"])
    assert len(anomalies) == 1
    assert anomalies[0].kind == "TRIPLE_VECTOR_COLLISION"
    assert anomalies[0].matched_axes == ("ordinal", "reverse", "reduction")
    assert anomalies[0].rarity_status == "UNMEASURED"


def test_reciprocal_social_mirrors() -> None:
    terms = [
        "JUPITER",
        "CONSENT",
        "COMMENT",
        "NETWORK",
        "HUMAN",
        "VIEWS",
        "ERROR",
        "TREND",
        "UNKNOWN",
        "ACCOUNT",
    ]
    reciprocal_pairs = {
        frozenset((item.left, item.right))
        for item in detect_pair_anomalies(terms)
        if item.kind == "RECIPROCAL_MIRROR"
    }
    assert frozenset(("JUPITER", "CONSENT")) in reciprocal_pairs
    assert frozenset(("COMMENT", "NETWORK")) in reciprocal_pairs
    assert frozenset(("HUMAN", "VIEWS")) in reciprocal_pairs
    assert frozenset(("ERROR", "TREND")) in reciprocal_pairs
    assert frozenset(("UNKNOWN", "ACCOUNT")) in reciprocal_pairs


def test_hashtag_backtrace_partial_vector_twin() -> None:
    anomalies = detect_pair_anomalies(["HASHTAG", "BACKTRACE"])
    assert len(anomalies) == 1
    anomaly = anomalies[0]
    assert anomaly.kind == "PARTIAL_VECTOR_TWIN"
    assert anomaly.matched_axes == ("ordinal", "reduction")


def test_governance_cipher_rectangle() -> None:
    rectangles = detect_cipher_rectangles(
        ["PATTERN", "PRIVACY", "CATEGORY", "JUDGMENT"]
    )
    assert len(rectangles) == 1
    rectangle = rectangles[0]
    assert rectangle.ordinal == 94
    assert rectangle.reverse_values == (95, 122)
    assert rectangle.reduction_values == (31, 40)
    assert set(rectangle.terms) == {
        "PATTERN",
        "PRIVACY",
        "CATEGORY",
        "JUDGMENT",
    }
    assert rectangle.rarity_status == "UNMEASURED"


def test_signal_viral_social_lattice() -> None:
    lattices = detect_bicipher_lattices(
        ["SIGNAL", "AUDIENCE", "VIRAL", "REACH"]
    )
    assert len(lattices) == 1
    lattice = lattices[0]
    assert {lattice.first_axis, lattice.second_axis} == {"ordinal", "reduction"}
    assert set(lattice.bridge_terms) == {"SIGNAL", "VIRAL"}
    assert set(lattice.first_terms) | set(lattice.second_terms) == {
        "SIGNAL",
        "AUDIENCE",
        "VIRAL",
        "REACH",
    }


def test_rarity_is_not_claimed_without_large_corpus() -> None:
    benchmark = benchmark_pair_kind(
        ["JUPITER", "CONSENT", "COMMENT", "NETWORK"],
        "RECIPROCAL_MIRROR",
    )
    assert benchmark.corpus_size == 4
    assert benchmark.candidate_pairs == 6
    assert benchmark.observed_pairs == 2
    assert benchmark.rarity_status == "UNMEASURED"
    assert benchmark.observed_frequency == pytest.approx(2 / 6)


def test_large_corpus_reports_measurement_not_universal_rarity() -> None:
    corpus = [f"TERM{_alpha_id(index)}" for index in range(500)]
    benchmark = benchmark_pair_kind(
        corpus,
        "TRIPLE_VECTOR_COLLISION",
        minimum_corpus_size=500,
    )
    assert benchmark.corpus_size == 500
    assert benchmark.rarity_status in {
        "EMPIRICALLY_MEASURED",
        "NOT_OBSERVED_IN_CORPUS",
    }


def test_analyze_keeps_epistemic_boundaries() -> None:
    report = analyze(["FOLLOWER", "IDENTITY", "JUPITER", "CONSENT"])
    assert report["schema_version"] == "cmb.numeric-anomaly.v1"
    assert "PATTERN != PROOF" in report["boundaries"]
    assert "RARITY_CLAIM_REQUIRES_CORPUS" in report["boundaries"]


def test_rejects_terms_without_ascii_letters() -> None:
    with pytest.raises(ValueError):
        vector_for("𓁹🫐⃟")
