(() => {
  "use strict";
  const root = document.getElementById("cmb-observatory");
  if (!root) return;
  const base = new URL("../machine/", window.location.href);
  const el = (id) => document.getElementById(id);
  const node = (tag, value, className = "") => {
    const result = document.createElement(tag);
    result.textContent = String(value ?? "");
    if (className) result.className = className;
    return result;
  };
  const load = async (file) => {
    const response = await fetch(new URL(file, base), { cache: "no-store" });
    if (!response.ok) throw new Error(file + ": HTTP " + response.status);
    return response.json();
  };
  const loadOptional = async (file) => {
    try { return await load(file); } catch (_) { return null; }
  };
  const safeLink = (url, label) => {
    try {
      const parsed = new URL(url);
      if (parsed.protocol !== "https:" && parsed.protocol !== "http:") return null;
      const anchor = node("a", label);
      anchor.href = parsed.href;
      anchor.rel = "noopener noreferrer";
      anchor.target = "_blank";
      return anchor;
    } catch (_) { return null; }
  };
  const state = { watch: null, intelligence: null, assessments: new Map(), dossiers: new Map(), current: [] };
  const addMetric = (name, value) => {
    const box = document.createElement("div");
    box.append(node("strong", value), node("span", name));
    return box;
  };
  const filterValue = (id) => el(id).value;
  const filtered = () => {
    const query = filterValue("watch-search").trim().toLocaleLowerCase();
    const boundary = filterValue("watch-boundary");
    const sector = filterValue("watch-sector");
    const rights = filterValue("watch-rights");
    const priority = filterValue("watch-priority");
    const language = filterValue("watch-language");
    const legal = filterValue("watch-legal");
    return state.watch.articles.filter((item) => {
      const dossier = state.dossiers.get(item.id);
      return (item.title + " " + item.domain).toLocaleLowerCase().includes(query) &&
        (!boundary || item.boundary_ids.includes(boundary)) &&
        (!sector || item.sector_ids.includes(sector)) &&
        (!language || (item.language || "unspecified") === language) &&
        (!rights || (dossier && dossier.rights_lenses.includes(rights))) &&
        (!priority || (dossier && dossier.triage_priority === priority)) &&
        (!legal || (dossier && dossier.legal_watch_candidate));
    });
  };
  const draw = () => {
    state.current = filtered();
    const list = el("watch-results");
    list.replaceChildren();
    for (const item of state.current) {
      const dossier = state.dossiers.get(item.id);
      const card = document.createElement("article");
      card.append(node("h3", item.title),
        node("p", item.domain + " | " + (item.seen_at || "Date unavailable") +
          " | " + item.boundary_ids.join(", ")));
      const link = safeLink(item.url, "Original publisher");
      if (link) card.append(link);
      const assessment = state.assessments.get(item.id);
      const grade = dossier?.traceability_grade || assessment?.traceability_grade || "NOT_ASSESSED";
      card.append(node("small", "Attribution: " + grade +
        ". Independent claim corroboration: NOT CHECKED."));
      if (dossier) {
        card.append(node("p", "Review priority: " +
          dossier.triage_priority.replaceAll("_", " ") +
          " (not a severity score).", "cmb-review-priority"));
        if (dossier.rights_lenses.length) {
          card.append(node("p", "Research lenses: " +
            dossier.rights_lenses.join(", ").replaceAll("_", " ")));
        }
        if (dossier.legal_watch_candidate) {
          card.append(node("p", "Legal process mentioned: primary legal source not checked."));
        }
        if (dossier.triage_reasons.length) {
          card.append(node("small", "Rule triggers: " + dossier.triage_reasons.join(", ")));
        }
        const details = document.createElement("details");
        details.append(node("summary", "Human review questions"));
        const questions = document.createElement("ul");
        for (const question of dossier.review_questions) {
          const li = document.createElement("li");
          li.textContent = question;
          questions.append(li);
        }
        details.append(questions);
        card.append(details);
        const archive = dossier.source_links.find((source) => source.type === "archive_lookup");
        const archiveLink = archive && safeLink(archive.url, "Archive history lookup (capture not guaranteed)");
        if (archiveLink) card.append(archiveLink);
      }
      list.append(card);
    }
    el("watch-count").textContent = state.current.length + " of " +
      state.watch.articles.length + " published links shown. Headline != verified fact.";
  };
  const quoteCsv = (value) => {
    let text = String(value ?? "");
    // Prevent spreadsheet formula execution when users open exported source headlines.
    if (/^[\s]*[=+\-@\t\r]/.test(text)) text = "'" + text;
    return '"' + text.replaceAll('"', '""') + '"';
  };
  const exportCsv = () => {
    if (!state.watch) return;
    const rows = [["Title", "Publisher", "Published/seen", "URL", "Boundaries",
      "Sectors", "Rights lenses", "Review priority", "Legal research candidate",
      "Claim verification", "Source language"]];
    for (const item of state.current) {
      const dossier = state.dossiers.get(item.id);
      rows.push([item.title, item.domain, item.seen_at || "", item.url,
        item.boundary_ids.join(";"), item.sector_ids.join(";"),
        (dossier?.rights_lenses || []).join(";"), dossier?.triage_priority || "UNASSESSED",
        dossier?.legal_watch_candidate ? "YES" : "NO",
        "NOT_INDEPENDENTLY_CHECKED", item.language || "unspecified"]);
    }
    const csv = rows.map((values) => values.map(quoteCsv).join(",")).join("\r\n");
    const url = URL.createObjectURL(new Blob(["\ufeff", csv], { type: "text/csv;charset=utf-8" }));
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "cmb-watch-source-links.csv";
    anchor.click();
    URL.revokeObjectURL(url);
  };
  const drawHistory = (history, intelligence) => {
    const chart = el("watch-history-chart");
    chart.replaceChildren();
    let days;
    if (intelligence?.history) {
      days = intelligence.history.slice(-14).map((day) =>
        [day.day, day.observed_links, day.distinct_links_within_day]);
    } else {
      const count = new Map();
      for (const record of history.entries || []) {
        const day = record.collected_at.slice(0, 10);
        count.set(day, (count.get(day) || 0) + record.article_count);
      }
      days = [...count].slice(-14).map(([date, links]) => [date, links, null]);
    }
    const maximum = Math.max(1, ...days.map((item) => item[1]));
    for (const [day, total, unique] of days) {
      const item = document.createElement("div");
      item.append(node("span", day));
      const bar = document.createElement("div");
      bar.className = "cmb-observatory-bar";
      bar.style.width = Math.round(total / maximum * 100) + "%";
      bar.setAttribute("role", "img");
      bar.setAttribute("aria-label", day + ": " + total + " collected links" +
        (unique == null ? "" : ", " + unique + " distinct URLs within day"));
      item.append(bar, node("span", total));
      chart.append(item);
    }
    el("watch-history-status").textContent = days.length ?
      "Latest " + days.length + " days. Bars count repeated collections, not incidents." :
      "Historical comparison is unavailable until distinct collections are archived.";
  };
  Promise.all([load("global-ai-watch.json"), load("global-ai-watch-health.json"),
    load("global-ai-watch-history.json"), load("global-ai-watch-assessments.json"),
    loadOptional("global-ai-watch-intelligence.json")])
    .then(([watch, health, history, assessments, intelligence]) => {
      if (!Array.isArray(watch.articles)) throw new Error("Invalid Watch articles");
      state.watch = watch;
      state.assessments = new Map((assessments.articles || []).map((a) => [a.article_id, a]));
      const consistent = intelligence &&
        intelligence.schema_version === "cmb.watch-intelligence.v1" &&
        intelligence.snapshot_generated_at === watch.generated_at &&
        intelligence.health_checked_at === health.checked_at &&
        Array.isArray(intelligence.dossiers);
      state.intelligence = consistent ? intelligence : null;
      state.dossiers = new Map((state.intelligence?.dossiers || []).map((a) => [a.article_id, a]));
      el("watch-intelligence-note").textContent = consistent ?
        "Rule-based human-review dossiers available. Review priority is not a risk or fact-check score." :
        "Additional research dossiers unavailable or from a different collection. Showing source records only.";
      const lastMs = Date.parse(health.last_successful_collection);
      const age = Number.isFinite(lastMs) ?
        Math.max(0, Math.floor((Date.now() - lastMs) / 60000)) : Infinity;
      const freshness = age >= 360 ? "STALE" : age > 120 ? "DELAYED" : health.status;
      el("watch-health-summary").replaceChildren(
        addMetric("Collection state", freshness || "UNKNOWN"),
        addMetric("Last successful collection", health.last_successful_collection || "Unknown"),
        addMetric("Minutes since collection", Number.isFinite(age) ? age : "Unknown"),
        addMetric("Publisher domains", health.publisher_domain_count),
        addMetric("Archived collections", history.entries?.length || 0),
        addMetric("Review-first links", state.intelligence?.coverage?.triage_priorities?.REVIEW_FIRST ?? "Not assessed")
      );
      if (freshness !== "CURRENT") {
        root.prepend(node("p", "Freshness warning: " + freshness +
          ". Previous articles must not be treated as new observations.", "cmb-observatory-warning"));
      }
      const sectors = [...new Set(watch.articles.flatMap((a) => a.sector_ids || []))].sort();
      const languages = [...new Set(watch.articles.map((a) => a.language || "unspecified"))].sort();
      for (const sector of sectors) {
        const option = node("option", sector.replaceAll("_", " "));
        option.value = sector;
        el("watch-sector").append(option);
      }
      for (const language of languages) {
        const option = node("option", language);
        option.value = language;
        el("watch-language").append(option);
      }
      for (const id of ["watch-search", "watch-boundary", "watch-sector", "watch-rights",
        "watch-priority", "watch-language", "watch-legal"]) {
        el(id).addEventListener("input", draw);
      }
      el("watch-export").addEventListener("click", exportCsv);
      el("watch-reset").addEventListener("click", () => {
        for (const id of ["watch-search", "watch-boundary", "watch-sector", "watch-rights",
          "watch-priority", "watch-language", "watch-legal"]) el(id).value = "";
        draw();
      });
      draw();
      drawHistory(history, state.intelligence);
      el("watch-loading").remove();
    })
    .catch((error) => {
      el("watch-loading").textContent =
        "The published evidence ledger could not be loaded. Please use the static Global AI Watch page. " +
        error.message;
    });
})();
