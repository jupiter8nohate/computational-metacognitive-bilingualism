# CMB // Global AI Intelligence Dashboard

A metadata-only research interface for tracking AI reporting, attribution, possible
civil-rights implications, human-machine authority boundaries, and review questions.

**Boundary:** This is not a live incident feed, independent fact check, automated
legal analysis, harm score, or system for profiling people. All headlines are
attributed leads that require source review. Labels refer to **human review
priority**, not severity. Reported source country is not incident location.

<div class="cmb-observatory" id="cmb-observatory" aria-live="off">
  <p id="watch-loading" role="status">Loading the latest published research ledger...</p>
  <div id="watch-health-summary" class="cmb-observatory-metrics" aria-label="Collection health"></div>
  <p id="watch-intelligence-note" role="status"></p>
  <div class="cmb-observatory-filters" role="group" aria-label="Research filters">
    <label>Search headlines or publishers
      <input id="watch-search" type="search" placeholder="accessibility, privacy, courts" autocomplete="off">
    </label>
    <label>CMB boundary
      <select id="watch-boundary"><option value="">All boundaries</option><option value="PREDICT">Predict</option><option value="GENERATE">Generate</option><option value="ACT">Act</option></select>
    </label>
    <label>Sector <select id="watch-sector"><option value="">All sectors</option></select></label>
    <label>Human-rights research lens
      <select id="watch-rights">
        <option value="">All rights lenses</option>
        <option value="accessibility_disability">Accessibility / disability</option>
        <option value="privacy_consent">Privacy / consent</option>
        <option value="equal_treatment">Equal treatment</option>
        <option value="due_process">Due process</option>
        <option value="children_safety">Children / safety</option>
      </select>
    </label>
    <label>Review queue
      <select id="watch-priority"><option value="">All links</option><option value="REVIEW_FIRST">Review first</option><option value="ROUTINE_REVIEW">Routine review</option></select>
    </label>
    <label>Reported source language
      <select id="watch-language"><option value="">All languages</option></select>
    </label>
    <label>Legal research
      <select id="watch-legal"><option value="">All links</option><option value="yes">Potential legal relevance</option></select>
    </label>
  </div>
  <div class="cmb-observatory-actions">
    <button id="watch-export" type="button">Export filtered CSV</button>
    <button id="watch-reset" type="button">Reset filters</button>
  </div>
  <p id="watch-count" role="status" aria-live="polite"></p>
  <div id="watch-results" class="cmb-observatory-results"></div>
  <h2>Collection history and source diversity</h2>
  <p>Counts represent **collected publisher links**, not verified incidents,
  independent sources, or global prevalence. A link may reappear across hours.</p>
  <div id="watch-history-chart" class="cmb-observatory-chart" aria-label="Recent collection history"></div>
  <p id="watch-history-status" role="status"></p>
</div>

**Trust rule:** Publisher URLs establish attribution only, and source-domain checks
do not establish truth. The triage model never assigns a credibility score to a
person or publisher, and does not automatically verify claims or legal violations.

[Source snapshot](https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/machine/global-ai-watch.json) |
[Review dossiers](https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/machine/global-ai-watch-intelligence.json) |
[JSON Schema](https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/schemas/cmb.watch-intelligence.v1.schema.json) |
[Collection health](https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/machine/global-ai-watch-health.json) |
[Public history](https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/machine/global-ai-watch-history.json) |
[Source assessments](https://jupiter8nohate.github.io/computational-metacognitive-bilingualism/machine/global-ai-watch-assessments.json)

