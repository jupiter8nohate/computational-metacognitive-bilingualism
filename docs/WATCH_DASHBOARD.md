# CMB // Global AI Intelligence Dashboard

This public research dashboard reads the **latest deployed JSON snapshot**, its
evidence checklist, collection-health report, and the append-only public history.
It is not a real-time stream or an independent verification service.

<div class="cmb-observatory" id="cmb-observatory" aria-live="polite">
  <p id="watch-loading">Loading the latest published evidence ledger...</p>
  <div id="watch-health-summary" class="cmb-observatory-metrics"></div>
  <div class="cmb-observatory-filters">
    <label>Search titles <input id="watch-search" type="search" placeholder="privacy, robots, surveillance" autocomplete="off"></label>
    <label>CMB boundary
      <select id="watch-boundary"><option value="">All boundaries</option><option value="PREDICT">Predict</option><option value="GENERATE">Generate</option><option value="ACT">Act</option></select>
    </label>
    <label>Sector <select id="watch-sector"><option value="">All sectors</option></select></label>
  </div>
  <p id="watch-count" role="status"></p>
  <div id="watch-results" class="cmb-observatory-results"></div>
  <h2>Collection history</h2>
  <p>Bars count *collected publisher links*, not independently confirmed events.</p>
  <div id="watch-history-chart" class="cmb-observatory-chart"></div>
  <p id="watch-history-status"></p>
</div>

**Evidence rule:** A publisher link verifies where a claim was reported, not
whether the claim is true. Source-country information is not assumed from a
publisher's headquarters, and sources do not endorse CMB by appearing here.

[Machine health](../machine/global-ai-watch-health.json) |
[Public history](../machine/global-ai-watch-history.json) |
[Source assessments](../machine/global-ai-watch-assessments.json) |
[D.N.A. Living Codex](../DNA_LIVING_CODEX/)
