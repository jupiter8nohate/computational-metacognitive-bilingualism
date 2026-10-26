"""Check the Quiet Weapons research companion's evidence boundaries and discovery."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SLUG = "DEATH_NOTE_2084_QUIET_WEAPONS_EVIDENCE_MIRROR"
PAGE = ROOT / "docs" / f"{SLUG}.md"
STORY = ROOT / "docs/DEATH_NOTE_2084_QUIET_WEAPONS_TEN_FALSE_DIAGNOSES.md"
TERMS = (
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


def test_ten_terms_are_literary_and_appropriately_bounded() -> None:
    content = read(PAGE)
    for term in TERMS:
        assert term in content
        assert term.replace("™", "®") not in content
    for index in range(1, 11):
        assert f"| **QW-{index:02}** |" in content
        assert f"## QW-{index:02} //" in content
    assert "fictional, creator-designated literary terms" in content
    assert "DISTRESS != DIAGNOSIS" in content
    assert "ASSOCIATION != CAUSATION" in content
    assert "PATTERN != PROOF" in content
    assert "HUMAN_AGENCY > MACHINE_AUTHORITY" in content
    assert "AI-assisted" in content


def test_dangerous_medical_and_causal_overclaims_are_explicitly_rejected() -> None:
    content = read(PAGE)
    for warning in (
        "SCROLLING IS NOT CATATONIA",
        "Dopamine depletion causing catatonia",
        "not a universal explanation",
        "not evidence",
        "it is inaccurate to assert",
        "not that a chatbot is physically present",
        "identical neurochemistry",
        "cannot establish which factor caused another",
        "timely medical evaluation",
    ):
        assert warning.lower() in content.lower()


def test_source_register_uses_real_https_references() -> None:
    content = read(PAGE)
    links = re.findall(r"\]\((https://[^)\s]+)\)", content)
    hosts = {urlsplit(link).hostname for link in links}
    assert len(links) >= 14
    assert {
        "pubmed.ncbi.nlm.nih.gov",
        "pmc.ncbi.nlm.nih.gov",
        "www.nature.com",
        "doi.org",
        "my.clevelandclinic.org",
        "arxiv.org",
    } <= hosts
    assert "preprint" in content.lower()
    assert "Cross-sectional" in content


def test_companion_crosslinks_navigation_and_site_bundle() -> None:
    assert f"{SLUG}.md" in read(ROOT / "mkdocs.yml")
    assert f'"{SLUG}/index.html"' in read(ROOT / "scripts/build_docs.py")
    for name in (
        "docs/DEATH_NOTE_2084_QUIET_WEAPONS_TEN_FALSE_DIAGNOSES.md",
        "docs/2084/index.md",
        "docs/story-universe/index.md",
        "docs/ARCHIVE_READING_MAP.md",
    ):
        assert f"{SLUG}.md" in read(ROOT / name)
    assert "QUIET WEAPONS" in read(STORY)
