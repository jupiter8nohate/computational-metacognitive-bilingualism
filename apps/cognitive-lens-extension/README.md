# CMB Cognitive Lens

A minimal Manifest V3 browser extension that evaluates **observable** attention-capture interface signals on the active page.

It does not claim to detect hidden profiling, infer a person's mental state, or inspect server-side recommendation models.

```text
ATTENTION_SIGNAL != PROOF_OF_PROFILING
PATTERN != PROOF
PROFILE != PERSON
```

## Privacy architecture

- no telemetry;
- no network requests;
- no persistent host permissions;
- no background monitoring;
- inspection runs only after the user clicks the extension;
- analysis executes locally in the active tab;
- results are not stored.

## Local installation

Chrome / Chromium:

1. Open `chrome://extensions`.
2. Enable Developer mode.
3. Choose **Load unpacked**.
4. Select this directory.
5. Open a normal webpage and click **CMB Cognitive Lens**.

Firefox support can be added after validating the WebExtension API differences and packaging requirements.

## Signal model

The prototype currently checks:

- autoplay media;
- repeated engagement-oriented controls;
- notification-prompt language;
- unusually tall feed-like pages;
- fixed or sticky interactive controls.

The score is an explainable heuristic for interface attention pressure, not proof of intent or profiling.
