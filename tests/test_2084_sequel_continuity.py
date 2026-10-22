"""Publication and fictional chronology guards for DEATH NOTE 2084 sequels."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORIES = {
    6: ROOT / "docs/DEATH_NOTE_2084_LEDGER_OF_INVISIBLE_YEARS.md",
    7: ROOT / "docs/DEATH_NOTE_2084_POST_GROUND_BASELINE.md",
    8: ROOT / "docs/DEATH_NOTE_2084_WITNESS_IN_LIGHTHOUSE.md",
}
REQUIRED_LINKS = (
    "DEATH_NOTE_2084_POST_GROUND_BASELINE.md",
    "DEATH_NOTE_2084_WITNESS_IN_LIGHTHOUSE.md",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_three_sequel_transmissions_exist_and_are_ordered() -> None:
    six, seven, eight = (read(STORIES[i]) for i in (6, 7, 8))
    assert "SIXTH TRANSMISSION" in six
    assert "SEVENTH TRANSMISSION" in seven
    assert "EIGHTH TRANSMISSION" in eight
    for path in REQUIRED_LINKS:
        assert path in read(ROOT / "mkdocs.yml")
        assert path in read(ROOT / "docs/2084/index.md")
        assert path in read(ROOT / "docs/story-universe/index.md")


def test_repair_preserves_time_and_evidence_boundaries() -> None:
    sixth, seventh, eighth = (read(STORIES[i]) for i in (6, 7, 8))
    assert "00:12:11" in sixth
    assert "00:12:11" in seventh
    assert "03:26:11" in seventh
    assert "03:14" in seventh
    assert "not proof" in seventh.lower() or "without independent proof" in seventh.lower()
    assert "FICTION" in seventh.upper()
    assert "FICTION" in eighth.upper()
    assert "EIGHTY-YEAR" in eighth.upper() or "eighty-year" in eighth.lower()


def test_generated_witness_never_grants_nia_consent() -> None:
    seventh, eighth = (read(STORIES[i]) for i in (7, 8))
    assert "Edda Vale" in seventh
    assert "Edda Vale" in eighth
    assert "simulated Edda" in eighth
    assert "HUMAN_AGENCY > MACHINE_AUTHORITY" in eighth
    assert "COPY != CONSENT" in eighth
    assert "Station Seven" in eighth
    assert "never" in eighth.lower()
    assert "WITNESS_BACKTRACE_PROTOCOL.md" in eighth


def test_story_canon_requires_human_reading_paths() -> None:
    continuity = read(ROOT / "docs/story-universe/continuity.md")
    assert "| VI |" in continuity
    assert "| VII |" in continuity
    assert "| VIII |" in continuity
    assert "00:12:11" in continuity
    for index in (7, 8):
        assert STORIES[index].exists()


def test_no_falsely_executable_override_claims() -> None:
    for index in (7, 8):
        chapter = read(STORIES[index])
        assert "AI-assisted" in chapter
        assert "FICTION" in chapter.upper()
        assert "source" in chapter.lower()
        assert "WITNESS_BACKTRACE_PROTOCOL.md" in chapter
