"""Publication and clinical-boundary guards for the fictional Quiet Weapons dossier."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUG = "DEATH_NOTE_2084_QUIET_WEAPONS_TEN_FALSE_DIAGNOSES"
PAGE = ROOT / "docs" / f"{SLUG}.md"
MARKS = (
    "Algophrenia™",
    "Synchroschizia™",
    "Mirror-Echo Paranoia™",
    "Feed-Induced Katatonia™",
    "Dataphrenic Dissociation™",
    "Chronosynaptic Phantasmia™",
    "Cyber-Somatic Infestation Delusion™",
    "Echo-Chamber Monomania™",
    "Phantom-Presence Neuroschism™",
    "Glitch-Identity Dysmorphia™",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_all_ten_coined_terms_present_and_marked_as_literary() -> None:
    text = read(PAGE)
    for mark in MARKS:
        assert mark in text
    assert "QW-01" in text and "QW-10" in text
    assert "not recognized psychiatric diagnoses" in text
    assert "FICTIONAL MISCLASSIFICATION" in text
    assert "not a numbered tenth transmission" in text.lower()
    assert "No ® is claimed" in text
    for mark in MARKS:
        assert mark.replace("™", "®") not in text


def test_emergency_boundaries_and_source_requirements() -> None:
    text = read(PAGE)
    assert "prompt medical attention" in text
    assert "Real catatonia/unresponsiveness" in text
    assert "no evidence that the street had become a rendering" in text.lower()
    assert "National Institute of Mental Health" in text
    assert "World Health Organization" in text
    assert "uspto.gov" in text
    assert "AI-assisted development" in text
    assert "HUMAN_AGENCY > MACHINE_AUTHORITY" in text


def test_page_is_discoverable_and_required_by_build() -> None:
    navigation = read(ROOT / "mkdocs.yml")
    site_build = read(ROOT / "scripts/build_docs.py")
    assert f"{SLUG}.md" in navigation
    assert f'"{SLUG}/index.html"' in site_build
    assert "stylesheets/quiet-weapons.css" in navigation
    assert '"stylesheets/quiet-weapons.css"' in site_build
    for path in (
        "docs/2084/index.md",
        "docs/story-universe/index.md",
        "docs/ARCHIVE_READING_MAP.md",
        "docs/DNA_BIBLE_TRADEMARK.md",
    ):
        assert SLUG in read(ROOT / path)
    assert (ROOT / "docs/stylesheets/quiet-weapons.css").exists()


def test_trademark_claim_does_not_imply_registration_or_clinical_authority() -> None:
    trademark = read(ROOT / "docs/DNA_BIBLE_TRADEMARK.md")
    for mark in MARKS:
        assert mark in trademark
    assert "not validated conditions" in trademark
    assert "not been represented here as filed or registered marks" in trademark
