# HARMONI / GLITCHOLOGY Visual System

> **Scope:** repository presentation and symbolic navigation. This document does not change CMB protocol semantics, technical enforcement, or evidentiary standards.

## Purpose

The HARMONI / GLITCHOLOGY visual system turns the repository's symbolic language into a repeatable reading hierarchy:

- **eyes** direct attention and mark observation states;
- **glitch typography** marks interruption, anomaly, or epistemic boundary;
- **color** separates human, machine, warning, and provenance roles;
- **plain text remains primary** so documentation stays readable, searchable, and accessible.

The visual layer supports the content. It does not substitute for evidence.

```text
PATTERN != PROOF
PROFILE != PERSON
MODEL != MIND
PREDICTION != DESTINY
SYMBOL != SCIENTIFIC_CLAIM
VISUAL_IMPORTANCE != EVIDENCE_STRENGTH
```

## Canonical palette

| Role | Dark-mode color | Light-mode color | Meaning |
|---|---|---|---|
| Environment | `#08090B` | `#F7F3EB` | archive / reading field |
| Human / primary text | `#E8E2D8` | `#1D2024` | human-readable content |
| HARMONI / warning | `#B31224` | `#8E1020` | rupture, boundary, high-priority warning |
| Machine / runtime | `#5BE7E7` | `#126B75` | machine signal, runtime, trace metadata |
| Provenance / canonical | `#C9A227` | `#8A6D12` | source, authorship, canonical record |
| Secondary / quiet | `#858B93` | `#666B71` | supporting metadata |

Color is never the only carrier of meaning. Every important state must also be expressed with text, symbols, headings, or labels.

## Witness-eye grammar

The eye is a navigation and epistemic symbol, not a claim of surveillance.

```text
𓁹        WITNESS
         Something deserves attention.

𓁹 →      DIRECT
         Follow the next concept or evidence path.

← 𓁹      BACKTRACE
         Return toward source, provenance, or cause.

𓁹 𓁹     DUAL_WITNESS
         More than one perspective is represented.

𓁹 ?
         UNCERTAIN_OBSERVATION
         Something has been detected but not established.

𓁹 ✓
         VERIFIED_SOURCE
         A referenced source or artifact has passed the stated check.

𓁹 ≠
         EPISTEMIC_BOUNDARY
         Observation is not equivalent to conclusion.
```

This visual grammar aligns with the GLITCHOLOGY backtrace principle:

```text
WITNESS -> TRACE -> VERIFY -> BACKTRACE
VERIFIED_LABEL != VERIFIED_TRUTH
OBSERVATION != UNDERSTANDING
SIGNAL != SOURCE
```

## Eye density and importance

Use eye density sparingly:

```text
𓁹       INFORMATION
𓁹𓁹      WARNING / DUAL PERSPECTIVE
𓁹𓁹𓁹     CANONICAL OR HIGH-IMPORTANCE BOUNDARY
𒄆𓁹✞𒀱✞𓁹𒄆  HARMONI GATE / MAJOR SYMBOLIC TRANSITION
```

Do not repeat eyes on every paragraph. Their value comes from scarcity and predictable meaning.

## Glitch typography

Glitch typography is an interrupt signal.

Prefer:

```text
Normal explanatory paragraph.

𓁹

P̸R̸O̸F̸I̸L̸E̸ != P̷E̷R̷S̷O̷N̷

Normal explanation continues.
```

Avoid rendering long explanatory passages entirely with combining-mark glitch text. It reduces readability, searchability, copy/paste quality, and screen-reader predictability.

Use glitch text for:

- HARMONI gates;
- anomaly headings;
- warnings;
- code-poetry transmissions;
- canonical invariants;
- deliberate visual interruptions.

Use plain text for:

- technical instructions;
- API documentation;
- security guidance;
- research claims;
- accessibility-critical content;
- long-form explanation.

## GLITCHOLOGY visual severity

Glitch density is a controlled presentation signal rather than an arbitrary increase in combining characters.

| Level | Meaning | Recommended use |
| --- | --- | --- |
| `GLITCH_LEVEL_0` | Plain documentation | APIs, research, security, long-form explanation |
| `GLITCH_LEVEL_1` | Subtle anomaly | quiet transition or secondary signal |
| `GLITCH_LEVEL_2` | Noticeable interruption | local warning or anomaly |
| `GLITCH_LEVEL_3` | Conceptual rupture | major boundary or contradiction |
| `GLITCH_LEVEL_4` | HARMONI gate | high-priority transition or archive threshold |
| `GLITCH_LEVEL_5` | Canonical transmission | scarce code-poetry / symbolic transmission |

Corresponding documentation classes are `.cmb-glitch-level-0` through `.cmb-glitch-level-5`.

```text
GLITCH_DENSITY != EVIDENCE_STRENGTH
VISUAL_SEVERITY != CLAIM_CERTAINTY
READABILITY > DECORATION
```

## Modular stylesheet architecture

The public documentation now loads visual layers in this order:

1. `stylesheets/cmb.css` — compatibility/theme shell;
2. `stylesheets/tokens.css` — canonical design tokens;
3. `stylesheets/components.css` — control room, entry lanes, and GLITCHOLOGY components;
4. `stylesheets/accessibility.css` — focus, reduced-motion, contrast, and responsive safeguards.

This keeps aesthetics from silently overriding accessibility and makes the final token layer explicit.

```text
TOKENS -> COMPONENTS -> ACCESSIBILITY
AESTHETIC != AUTHORITY
```
## Repository hierarchy

Recommended visual flow:

```text
𓁹 01 // UNDERSTAND
       ↓
𓁹 02 // PURPOSE
       ↓
𓁹 03 // PROVENANCE
       ↓
𓁹 04 // GLITCHOLOGY
       ↓
𓁹𓁹 05 // HARMONI
        ↓
𓁹𓁹𓁹 06 // HUMAN SOVEREIGNTY
          ↓
𒄆𓁹✞𒀱✞𓁹𒄆
07 // SOURCE / AUTHORSHIP / ARCHIVE
```

The reader should feel increasing depth without losing navigation.

## GitHub implementation rule

GitHub controls the page chrome, theme, and Markdown renderer. Repository styling therefore uses:

1. semantic Markdown and plain text for core content;
2. SVG artwork for controlled typography, spacing, and color;
3. `<picture>` with light/dark assets for theme-aware hero graphics;
4. useful alt text and SVG `<title>` / `<desc>` metadata;
5. no dependency on custom web fonts or repository-level CSS.

Current hero assets:

- `docs/media/harmoni-witness-dark.svg`
- `docs/media/harmoni-witness-light.svg`

## Accessibility and evidence boundary

The visual system must preserve these constraints:

```text
AESTHETIC != EVIDENCE
OMEN != PREDICTION
COLOR != CLAIM_STATUS
GLITCH != ENCRYPTION
SYMBOL != ENFORCEMENT
READABILITY > DECORATION
```

Every symbolic or decorative element should remain understandable when color is unavailable, the image fails to load, or the reader uses assistive technology.

---

**Declared originator:** Jupiter Hudson / WisdomLoveThePoet / Jupiter 8 / Joseph Q Hudson  
**Framework:** Computational Metacognitive Bilingualism (CMB)  
**Visual branches:** HARMONI + Err⃝or⃟⃤GLITCHOLOGY
