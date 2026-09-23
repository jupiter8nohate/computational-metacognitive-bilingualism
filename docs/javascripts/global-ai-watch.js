(() => {
  "use strict";

  const grid = document.getElementById("cmb-news-grid");
  if (!grid) {
    return;
  }

  const status = document.getElementById("cmb-watch-status");
  const searchInput = document.getElementById("cmb-watch-search");
  const boundarySelect = document.getElementById("cmb-watch-boundary");
  const sectorSelect = document.getElementById("cmb-watch-sector");
  const refreshButton = document.getElementById("cmb-watch-refresh");
  const cacheKey = "cmb-global-ai-watch-v1";
  const stopwords = new Set([
    "about", "after", "against", "artificial", "before", "being", "could",
    "from", "have", "into", "machine", "more", "news", "over", "said",
    "says", "that", "their", "this", "through", "using", "with", "would"
  ]);

  let currentCards = [];

  function safeUrl(raw) {
    try {
      const parsed = new URL(raw);
      if (parsed.protocol !== "http:" && parsed.protocol !== "https:") {
        return null;
      }
      return parsed.href;
    } catch (_error) {
      return null;
    }
  }

  function textMatches(title, terms) {
    const lower = title.toLocaleLowerCase();
    return terms.some((term) => lower.includes(String(term).toLocaleLowerCase()));
  }

  function classify(title, config) {
    const boundaries = [];
    const sectors = [];
    const invariants = [];

    for (const boundary of config.boundaries || []) {
      if (textMatches(title, boundary.terms || [])) {
        boundaries.push(boundary.id);
        for (const invariant of boundary.invariants || []) {
          if (!invariants.includes(invariant)) {
            invariants.push(invariant);
          }
        }
      }
    }

    for (const sector of config.sectors || []) {
      if (textMatches(title, sector.terms || [])) {
        sectors.push(sector.id);
      }
    }

    if (sectors.length === 0) {
      sectors.push("general");
    }

    return { boundaries, sectors, invariants };
  }

  function titleTokens(title) {
    const matches = title.toLocaleLowerCase().match(/[a-z0-9]+/g) || [];
    return new Set(matches.filter((token) => token.length > 2 && !stopwords.has(token)));
  }

  function jaccard(left, right) {
    if (left.size === 0 || right.size === 0) {
      return 0;
    }
    let intersection = 0;
    for (const token of left) {
      if (right.has(token)) {
        intersection += 1;
      }
    }
    const union = new Set([...left, ...right]).size;
    return intersection / union;
  }

  function clusterArticles(articles) {
    const clusters = [];

    for (const article of articles) {
      const tokens = titleTokens(article.title);
      let best = null;
      let bestScore = 0;

      for (const cluster of clusters) {
        const score = jaccard(tokens, cluster.anchorTokens);
        if (score > bestScore) {
          best = cluster;
          bestScore = score;
        }
      }

      if (best && bestScore >= 0.55) {
        best.articles.push(article);
        article.clusterId = best.id;
      } else {
        const cluster = {
          id: "cluster-" + String(clusters.length + 1).padStart(3, "0"),
          anchorTokens: tokens,
          articles: [article]
        };
        clusters.push(cluster);
        article.clusterId = cluster.id;
      }
    }

    for (const cluster of clusters) {
      const sourceCount = new Set(cluster.articles.map((item) => item.domain)).size;
      for (const article of cluster.articles) {
        article.clusterSourceCount = Math.max(1, sourceCount);
      }
    }

    return clusters.length;
  }

  function normalizeArticles(payload, config) {
    const rawArticles = Array.isArray(payload.articles) ? payload.articles : [];
    const seen = new Set();
    const output = [];

    for (const raw of rawArticles) {
      if (!raw || typeof raw !== "object") {
        continue;
      }
      const title = String(raw.title || "").trim();
      const url = safeUrl(String(raw.url || "").trim());
      if (!title || !url) {
        continue;
      }

      const dedupeUrl = new URL(url);
      for (const key of [...dedupeUrl.searchParams.keys()]) {
        const lower = key.toLocaleLowerCase();
        if (lower.startsWith("utm_") || ["fbclid", "gclid", "mc_cid", "mc_eid", "ref", "ref_src"].includes(lower)) {
          dedupeUrl.searchParams.delete(key);
        }
      }
      dedupeUrl.hash = "";
      const dedupeKey = dedupeUrl.href;
      if (seen.has(dedupeKey)) {
        continue;
      }

      const classification = classify(title, config);
      if (classification.boundaries.length === 0) {
        continue;
      }

      seen.add(dedupeKey);
      output.push({
        title,
        url,
        domain: String(raw.domain || new URL(url).hostname),
        seenDate: String(raw.seendate || ""),
        language: raw.language ? String(raw.language) : "Unknown",
        sourceCountry: raw.sourcecountry ? String(raw.sourcecountry) : "Unknown",
        boundaries: classification.boundaries,
        sectors: classification.sectors,
        invariants: classification.invariants,
        clusterId: "",
        clusterSourceCount: 1
      });
    }

    output.sort((a, b) => b.seenDate.localeCompare(a.seenDate));
    const clusterCount = clusterArticles(output);
    return { articles: output, clusterCount };
  }

  function gdeltUrl(config) {
    const target = new URL(config.source.endpoint);
    target.searchParams.set("query", config.query);
    target.searchParams.set("mode", "artlist");
    target.searchParams.set("format", "json");
    target.searchParams.set("maxrecords", String(config.max_records || 100));
    target.searchParams.set("timespan", config.timespan || "24h");
    target.searchParams.set("sort", "datedesc");
    return target.href;
  }

  function labelMap(config, key) {
    const result = new Map();
    for (const item of config[key] || []) {
      result.set(item.id, item.label);
    }
    if (key === "sectors") {
      result.set("general", "General");
    }
    return result;
  }

  function createLink(label, href) {
    const link = document.createElement("a");
    link.textContent = label;
    link.href = href;
    link.rel = "noopener noreferrer";
    return link;
  }

  function createCard(article, config) {
    const boundaryLabels = labelMap(config, "boundaries");
    const sectorLabels = labelMap(config, "sectors");

    const card = document.createElement("article");
    card.className = "cmb-news-card";
    card.dataset.boundaries = article.boundaries.join(" ");
    card.dataset.sectors = article.sectors.join(" ");
    card.dataset.country = article.sourceCountry;
    card.dataset.domain = article.domain;

    const signal = document.createElement("div");
    signal.className = "cmb-news-card__signal";
    signal.textContent =
      article.boundaries.map((item) => boundaryLabels.get(item) || item).join(" + ") +
      " // " +
      article.sectors.map((item) => sectorLabels.get(item) || item).join(" + ");

    const heading = document.createElement("h3");
    heading.textContent = article.title;

    const meta = document.createElement("div");
    meta.className = "cmb-news-card__meta";
    meta.textContent = [
      article.domain,
      article.sourceCountry,
      article.language,
      article.seenDate || "time unavailable"
    ].join(" · ");

    const invariant = document.createElement("div");
    invariant.className = "cmb-news-card__invariant";
    invariant.textContent = article.invariants.join(" | ");

    const cluster = document.createElement("div");
    cluster.className = "cmb-news-card__cluster";
    cluster.textContent =
      article.clusterSourceCount > 1
        ? "Headline-similarity cluster: " + article.clusterSourceCount + " source domains"
        : "Headline-similarity cluster: single source domain";

    const actions = document.createElement("div");
    actions.className = "cmb-news-card__actions";
    actions.appendChild(createLink("Open original source", article.url));
    actions.appendChild(
      createLink(
        "Wayback history",
        String(config.source.archive_history_base || "https://web.archive.org/web/*/") + article.url
      )
    );

    card.append(signal, heading, meta, invariant, cluster, actions);
    return card;
  }

  function updateMetrics(articles, clusterCount) {
    const metricNodes = document.querySelectorAll(".cmb-watch-metrics > div strong");
    if (metricNodes.length < 4) {
      return;
    }
    metricNodes[0].textContent = String(articles.length);
    metricNodes[1].textContent = String(new Set(articles.map((item) => item.domain)).size);
    metricNodes[2].textContent = String(
      new Set(articles.map((item) => item.sourceCountry).filter((item) => item && item !== "Unknown")).size
    );
    metricNodes[3].textContent = String(clusterCount);
  }

  function applyFilters() {
    const query = String(searchInput?.value || "").trim().toLocaleLowerCase();
    const boundary = String(boundarySelect?.value || "");
    const sector = String(sectorSelect?.value || "");

    for (const card of currentCards) {
      const haystack = [
        card.textContent || "",
        card.dataset.country || "",
        card.dataset.domain || ""
      ].join(" ").toLocaleLowerCase();
      const boundaryMatch = !boundary || (card.dataset.boundaries || "").split(" ").includes(boundary);
      const sectorMatch = !sector || (card.dataset.sectors || "").split(" ").includes(sector);
      const queryMatch = !query || haystack.includes(query);
      card.hidden = !(boundaryMatch && sectorMatch && queryMatch);
    }
  }

  function render(articles, clusterCount, config, sourceLabel) {
    grid.replaceChildren();
    currentCards = articles.map((article) => createCard(article, config));
    for (const card of currentCards) {
      grid.appendChild(card);
    }
    if (currentCards.length === 0) {
      const empty = document.createElement("div");
      empty.className = "cmb-watch-empty";
      empty.textContent = "No current GDELT results matched the configured CMB boundary rules.";
      grid.appendChild(empty);
    }
    updateMetrics(articles, clusterCount);
    if (status) {
      status.textContent = sourceLabel + " // " + articles.length + " classified stories";
    }
    applyFilters();
  }

  function readCache(config) {
    try {
      const raw = localStorage.getItem(cacheKey);
      if (!raw) {
        return null;
      }
      const cached = JSON.parse(raw);
      const ageMs = Date.now() - Number(cached.savedAt || 0);
      const ttlMs = Number(config.browser_cache_minutes || 10) * 60 * 1000;
      if (!Number.isFinite(ageMs) || ageMs < 0 || ageMs > ttlMs) {
        return null;
      }
      return cached.payload;
    } catch (_error) {
      return null;
    }
  }

  function writeCache(payload) {
    try {
      localStorage.setItem(cacheKey, JSON.stringify({ savedAt: Date.now(), payload }));
    } catch (_error) {
      // Storage can be disabled. Live rendering does not depend on it.
    }
  }

  async function loadConfig() {
    const configUrl = new URL("../machine/global-ai-watch-config.json", window.location.href);
    const response = await fetch(configUrl.href, { cache: "no-store" });
    if (!response.ok) {
      throw new Error("Config HTTP " + response.status);
    }
    return response.json();
  }

  async function refresh(forceNetwork) {
    if (refreshButton) {
      refreshButton.disabled = true;
    }
    if (status) {
      status.textContent = "GDELT REFRESH // querying public news metadata";
    }

    try {
      const config = await loadConfig();
      let payload = forceNetwork ? null : readCache(config);

      if (!payload) {
        const controller = new AbortController();
        const timeout = window.setTimeout(() => controller.abort(), 15000);
        try {
          const response = await fetch(gdeltUrl(config), {
            cache: "no-store",
            signal: controller.signal
          });
          if (!response.ok) {
            throw new Error("GDELT HTTP " + response.status);
          }
          payload = await response.json();
          writeCache(payload);
        } finally {
          window.clearTimeout(timeout);
        }
      }

      const normalized = normalizeArticles(payload, config);
      render(
        normalized.articles,
        normalized.clusterCount,
        config,
        forceNetwork ? "LIVE GDELT" : "LIVE GDELT / CACHE"
      );
    } catch (error) {
      if (status) {
        status.textContent =
          "STATIC SNAPSHOT // live GDELT refresh unavailable // " +
          (error instanceof Error ? error.message : "unknown error");
      }
      currentCards = [...grid.querySelectorAll(".cmb-news-card")];
      applyFilters();
    } finally {
      if (refreshButton) {
        refreshButton.disabled = false;
      }
    }
  }

  searchInput?.addEventListener("input", applyFilters);
  boundarySelect?.addEventListener("change", applyFilters);
  sectorSelect?.addEventListener("change", applyFilters);
  refreshButton?.addEventListener("click", () => refresh(true));

  refresh(false);
})();
