(() => {
  "use strict";

  const SITE_ROOT = "/computational-metacognitive-bilingualism/";
  const CONFIG_URL = SITE_ROOT + "machine/global-ai-watch-config.json";

  const safeHttpUrl = (value) => {
    try {
      const url = new URL(value, window.location.href);
      if (url.protocol !== "http:" && url.protocol !== "https:") return null;
      return url;
    } catch {
      return null;
    }
  };

  const matchesAny = (text, terms) => {
    const lower = text.toLocaleLowerCase();
    return terms.some((term) => lower.includes(String(term).toLocaleLowerCase()));
  };

  const classify = (title, config) => {
    const boundaryIds = [];
    const invariants = [];
    const sectorIds = [];

    for (const boundary of config.boundaries || []) {
      if (!matchesAny(title, boundary.terms || [])) continue;
      boundaryIds.push(boundary.id);
      for (const invariant of boundary.invariants || []) {
        if (!invariants.includes(invariant)) invariants.push(invariant);
      }
    }

    for (const sector of config.sectors || []) {
      if (matchesAny(title, sector.terms || [])) sectorIds.push(sector.id);
    }

    if (sectorIds.length === 0) sectorIds.push("general");
    return { boundaryIds, sectorIds, invariants };
  };

  const makeLink = (label, href) => {
    const url = safeHttpUrl(href);
    if (!url) return null;
    const anchor = document.createElement("a");
    anchor.textContent = label;
    anchor.href = url.href;
    anchor.rel = "noopener noreferrer";
    return anchor;
  };

  const renderLiveArticle = (raw, config) => {
    const title = String(raw.title || "").trim();
    const url = safeHttpUrl(String(raw.url || ""));
    if (!title || !url) return null;

    const classification = classify(title, config);
    if (classification.boundaryIds.length === 0) return null;

    const article = document.createElement("article");
    article.className = "cmb-news-card";
    article.dataset.boundaries = classification.boundaryIds.join(" ");
    article.dataset.sectors = classification.sectorIds.join(" ");
    article.dataset.country = String(raw.sourcecountry || "Unknown");
    article.dataset.domain = String(raw.domain || url.hostname);

    const signal = document.createElement("div");
    signal.className = "cmb-news-card__signal";
    signal.textContent = classification.boundaryIds.join(" + ");
    article.append(signal);

    const heading = document.createElement("h3");
    heading.textContent = title;
    article.append(heading);

    const meta = document.createElement("div");
    meta.className = "cmb-news-card__meta";
    meta.textContent = [
      raw.domain || url.hostname,
      raw.sourcecountry || "Unknown country",
      raw.language || "Unknown language",
      raw.seendate || "Time unavailable",
    ].join(" · ");
    article.append(meta);

    const invariant = document.createElement("div");
    invariant.className = "cmb-news-card__invariant";
    invariant.textContent = classification.invariants.join(" | ");
    article.append(invariant);

    const actions = document.createElement("div");
    actions.className = "cmb-news-card__actions";
    const original = makeLink("Open original source", url.href);
    const archive = makeLink(
      "Wayback history",
      "https://web.archive.org/web/*/" + url.href
    );
    if (original) actions.append(original);
    if (archive) actions.append(archive);
    article.append(actions);

    return article;
  };

  const jsonp = (url, timeoutMs = 15000) =>
    new Promise((resolve, reject) => {
      const callbackName =
        "__cmbGdeltCallback_" + Date.now() + "_" + Math.random().toString(16).slice(2);
      const script = document.createElement("script");
      let timer = null;

      const cleanup = () => {
        if (timer !== null) window.clearTimeout(timer);
        delete window[callbackName];
        script.remove();
      };

      window[callbackName] = (payload) => {
        cleanup();
        resolve(payload);
      };

      script.onerror = () => {
        cleanup();
        reject(new Error("GDELT JSONP request failed"));
      };

      const target = new URL(url);
      target.searchParams.set("format", "jsonp");
      target.searchParams.set("callback", callbackName);
      script.src = target.href;
      document.head.append(script);

      timer = window.setTimeout(() => {
        cleanup();
        reject(new Error("GDELT JSONP request timed out"));
      }, timeoutMs);
    });

  const buildGdeltUrl = (config) => {
    const target = new URL(config.source.endpoint);
    target.searchParams.set("query", config.query);
    target.searchParams.set("mode", "artlist");
    target.searchParams.set("maxrecords", String(config.max_records || 100));
    target.searchParams.set("timespan", config.timespan || "24h");
    target.searchParams.set("sort", "datedesc");
    return target.href;
  };

  const applyFilters = () => {
    const grid = document.getElementById("cmb-news-grid");
    if (!grid) return;

    const query = (document.getElementById("cmb-watch-search")?.value || "")
      .trim()
      .toLocaleLowerCase();
    const boundary = document.getElementById("cmb-watch-boundary")?.value || "";
    const sector = document.getElementById("cmb-watch-sector")?.value || "";

    for (const card of grid.querySelectorAll(".cmb-news-card")) {
      const haystack = card.textContent.toLocaleLowerCase();
      const boundaryMatch =
        !boundary || (card.dataset.boundaries || "").split(" ").includes(boundary);
      const sectorMatch =
        !sector || (card.dataset.sectors || "").split(" ").includes(sector);
      const queryMatch = !query || haystack.includes(query);
      card.hidden = !(boundaryMatch && sectorMatch && queryMatch);
    }
  };

  const loadConfig = async () => {
    const response = await fetch(CONFIG_URL, {
      cache: "no-store",
      credentials: "same-origin",
    });
    if (!response.ok) throw new Error("Could not load Global AI Watch config");
    return response.json();
  };

  const refreshLive = async () => {
    const grid = document.getElementById("cmb-news-grid");
    const status = document.getElementById("cmb-watch-status");
    if (!grid || !status) return;

    status.textContent = "LIVE REFRESH // querying GDELT";
    const config = await loadConfig();
    const payload = await jsonp(buildGdeltUrl(config));
    const articles = Array.isArray(payload?.articles) ? payload.articles : [];

    const fragment = document.createDocumentFragment();
    let rendered = 0;
    const seen = new Set();

    for (const raw of articles) {
      const source = safeHttpUrl(String(raw.url || ""));
      if (!source || seen.has(source.href)) continue;
      const card = renderLiveArticle(raw, config);
      if (!card) continue;
      seen.add(source.href);
      fragment.append(card);
      rendered += 1;
    }

    grid.replaceChildren(
      fragment.childNodes.length
        ? fragment
        : Object.assign(document.createElement("div"), {
            className: "cmb-watch-empty",
            textContent: "No classified live stories were returned by this sample.",
          })
    );

    status.textContent =
      "LIVE SAMPLE // " +
      new Date().toISOString().replace("T", " ").replace(/\.\d{3}Z$/, " UTC") +
      " // " +
      rendered +
      " classified stories";
    applyFilters();
  };

  document.addEventListener("DOMContentLoaded", () => {
    for (const id of ["cmb-watch-search", "cmb-watch-boundary", "cmb-watch-sector"]) {
      document.getElementById(id)?.addEventListener("input", applyFilters);
      document.getElementById(id)?.addEventListener("change", applyFilters);
    }

    document.getElementById("cmb-watch-refresh")?.addEventListener("click", () => {
      refreshLive().catch((error) => {
        const status = document.getElementById("cmb-watch-status");
        if (status) {
          status.textContent =
            "LIVE REFRESH FAILED // static snapshot preserved // " + error.message;
        }
      });
    });
  });
})();

