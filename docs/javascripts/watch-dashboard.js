(() => {
  "use strict";
  const root = document.getElementById("cmb-observatory");
  if (!root) return;
  const base = new URL("../machine/", window.location.href);
  const el = (id) => document.getElementById(id);
  const textNode = (tag, value) => {
    const node = document.createElement(tag);
    node.textContent = String(value);
    return node;
  };
  const load = async (file) => {
    const url = new URL(file, base);
    const response = await fetch(url, { cache: "no-store" });
    if (!response.ok) throw new Error(file + ": HTTP " + response.status);
    return response.json();
  };
  const state = { watch: null, assessments: null };
  const summary = (name, value) => {
    const box = document.createElement("div");
    box.append(textNode("strong", value), textNode("span", name));
    return box;
  };
  const draw = () => {
    const query = el("watch-search").value.trim().toLocaleLowerCase();
    const boundary = el("watch-boundary").value;
    const sector = el("watch-sector").value;
    const found = state.watch.articles.filter((item) =>
      item.title.toLocaleLowerCase().includes(query) &&
      (!boundary || item.boundary_ids.includes(boundary)) &&
      (!sector || item.sector_ids.includes(sector))
    );
    const list = el("watch-results");
    list.replaceChildren();
    for (const item of found) {
      const card = document.createElement("article");
      const heading = textNode("h3", item.title);
      const link = document.createElement("a");
      link.href = item.url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.textContent = "Original publisher";
      card.append(heading, textNode("p",
        item.domain + " | " + (item.seen_at || "Date unavailable") +
        " | " + item.boundary_ids.join(", ")), link);
      const grade = assessments.articles.find((entry) => entry.article_id === item.id);
      card.append(textNode("small",
        "Evidence grade: " + (grade?.traceability_grade || "NOT_ASSESSED") +
        ". Independent corroboration has not been checked."));
      list.append(card);
    }
    el("watch-count").textContent = found.length + " of " +
      state.watch.articles.length + " source links shown";
  };
  Promise.all([
    load("global-ai-watch.json"),
    load("global-ai-watch-health.json"),
    load("global-ai-watch-history.json"),
    load("global-ai-watch-assessments.json")
  ]).then(([watch, health, history, assessments]) => {
    state.watch = watch;
    state.assessments = assessments;
    const collectedMs = Date.parse(health.last_successful_collection);
    const elapsedMinutes = Number.isFinite(collectedMs) ?
      Math.max(0, Math.floor((Date.now() - collectedMs) / 60000)) : Infinity;
    const currentState = elapsedMinutes >= 360 ? "STALE" :
      elapsedMinutes > 120 ? "DELAYED" : health.status;
    const metrics = el("watch-health-summary");
    metrics.replaceChildren(
      summary("Collection state", currentState),
      summary("Latest successful collection", health.last_successful_collection),
      summary("Minutes since collection", Number.isFinite(elapsedMinutes) ? elapsedMinutes : "Unknown"),
      summary("Publisher domains", health.publisher_domain_count),
      summary("Saved collections", history.entries.length)
    );
    if (currentState !== "CURRENT") {
      const warning = textNode("p", "Freshness warning: latest collection is " +
        currentState + ". Old data is not presented as a new observation.");
      warning.className = "cmb-observatory-warning";
      root.prepend(warning);
    }
    const sectors = [...new Set(watch.articles.flatMap(x => x.sector_ids))].sort();
    for (const sector of sectors) {
      const option = document.createElement("option");
      option.value = sector;
      option.textContent = sector.replaceAll("_", " ");
      el("watch-sector").append(option);
    }
    for (const id of ["watch-search", "watch-boundary", "watch-sector"]) {
      el(id).addEventListener("input", draw);
    }
    draw();
    const counts = new Map();
    for (const record of history.entries) {
      const day = record.collected_at.slice(0, 10);
      counts.set(day, (counts.get(day) || 0) + record.article_count);
    }
    const days = [...counts].slice(-14);
    const maximum = Math.max(1, ...days.map(x => x[1]));
    const chart = el("watch-history-chart");
    chart.replaceChildren();
    for (const [day, count] of days) {
      const item = document.createElement("div");
      item.append(textNode("span", day));
      const bar = document.createElement("div");
      bar.className = "cmb-observatory-bar";
      bar.style.width = String(Math.round((count / maximum) * 100)) + "%";
      bar.setAttribute("aria-label", day + ": " + count + " collected links");
      item.append(bar, textNode("span", count));
      chart.append(item);
    }
    el("watch-history-status").textContent = days.length ?
      "Displaying the latest " + days.length + " recorded days." :
      "Historical comparison is not yet available.";
    el("watch-loading").remove();
  }).catch((error) => {
    el("watch-loading").textContent = "The latest observatory data could not be " +
      "loaded. Use the static Global AI Watch page instead. " + error.message;
  });
})();
