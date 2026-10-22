/* D.N.A. Bible Codex. No third-party scripts, cookies, network analytics, or persistent choices. */
(() => {
  "use strict";
  const root = document.getElementById("dna-codex");
  if (!root) return;

  const gateScenarios = Object.freeze({
    L: ["LEDGER", "The Ministry has recorded your curiosity as a lifetime obligation.", "A record can be challenged. Demand its source and a correction process."],
    U: ["UNIVERSAL", "One identity token now opens every essential service, and follows you into every room.", "Convenience should not require unlimited cross-service identification."],
    C: ["COMPLIANCE", "A reading tool requires agreement to unrelated behavioral monitoring.", "The useful service and the unnecessary profiling can be separated."],
    I: ["INFERENCE", "A predicted attitude is presented as your declared belief.", "An inference is not testimony from the person being classified."],
    F: ["FORECASTING", "A future possibility is treated as an already completed act.", "Risk estimates require context, uncertainty, and contestable decisions."],
    E: ["EXTRACTION", "A free lesson asks for permanent attention data as its hidden tuition.", "The real cost must be disclosed and a less-invasive option considered."],
    R: ["RANKING", "A civic score outranks your own explanation of a disputed event.", "An automated score cannot substitute for accountable human review."]
  });

  const setPressed = (buttons, selected) => {
    buttons.forEach(button => {
      const isSelected = button === selected;
      button.setAttribute("aria-pressed", String(isSelected));
    });
  };

  const modeButtons = Array.from(root.querySelectorAll("[data-dna-mode]"));
  const witness = root.querySelector("[data-dna-witness]");
  const selectMode = mode => {
    const selected = modeButtons.find(button => button.dataset.dnaMode === mode);
    if (!selected || !witness) return;
    setPressed(modeButtons, selected);
    witness.hidden = mode !== "witness";
  };
  modeButtons.forEach(button => button.addEventListener("click", () => selectMode(button.dataset.dnaMode)));
  selectMode("story");

  const title = root.querySelector("#dna-gate-title");
  const question = root.querySelector("#dna-gate-question");
  const outcome = root.querySelector("#dna-gate-outcome");
  const gateButtons = Array.from(root.querySelectorAll("[data-dna-gate]"));
  let currentGate = null;
  for (const button of gateButtons) {
    button.addEventListener("click", () => {
      const letter = button.dataset.dnaGate;
      const scenario = gateScenarios[letter];
      if (!scenario) return;
      currentGate = letter;
      setPressed(gateButtons, button);
      title.textContent = "GATE " + letter + " // " + scenario[0];
      question.textContent = scenario[1];
      outcome.textContent = "Choose a fictional response. Nothing is saved or transmitted.";
    });
  }
  for (const button of root.querySelectorAll("[data-dna-decision]")) {
    button.addEventListener("click", () => {
      if (!currentGate) {
        outcome.textContent = "Select a gate before choosing a response.";
        return;
      }
      const scenario = gateScenarios[currentGate];
      const decision = button.dataset.dnaDecision;
      if (decision === "accept") outcome.textContent = "FICTION: The Ministry opens the door but extends its authority. This choice is not a real consent transaction.";
      if (decision === "contest") outcome.textContent = "FICTION: Your objection is registered. " + scenario[2];
      if (decision === "human") outcome.textContent = "FICTION: The review desk must identify a responsible person. " + scenario[2];
    });
  }

  const isInternalRoute = route => typeof route === "string" &&
    /^(?:[a-zA-Z0-9_-]+\/)*[a-zA-Z0-9_.-]+\/?$/.test(route) &&
    !route.split("/").includes("..") && !route.split("/").includes(".");
  const linkToRoute = route => new URL("../" + route, window.location.href).href;
  const makeText = (tag, content, className) => {
    const el = document.createElement(tag);
    el.textContent = content;
    if (className) el.className = className;
    return el;
  };
  const makeLink = (label, href) => {
    const anchor = makeText("a", label);
    anchor.href = href;
    if (/^https:\/\//i.test(href)) {
      anchor.rel = "noopener noreferrer";
    }
    return anchor;
  };
  const fetchJson = async attribute => {
    const path = root.dataset[attribute];
    if (!path) throw new Error("Missing data path");
    const response = await fetch(new URL(path, window.location.href), {credentials:"omit", cache:"no-cache"});
    if (!response.ok) throw new Error("Publication data unavailable");
    return response.json();
  };

  const library = root.querySelector("#dna-library");
  const filterButtons = Array.from(root.querySelectorAll("[data-dna-filter]"));
  let entries = null;
  const renderEntries = filter => {
    if (!library || !Array.isArray(entries)) return;
    const visible = entries.filter(entry => filter === "all" ||
      (filter === "companion" ? entry.kind !== "transmission" : entry.kind === "transmission"));
    const list = document.createElement("ol");
    list.className = "dna-library-list";
    for (const entry of visible) {
      if (!isInternalRoute(entry.route)) continue;
      const li = document.createElement("li");
      li.appendChild(makeLink(entry.title, linkToRoute(entry.route)));
      li.appendChild(makeText("span", entry.kind.replaceAll("_", " ").toUpperCase(), "dna-type"));
      li.appendChild(makeText("p", entry.premise));
      list.appendChild(li);
    }
    library.replaceChildren(list);
  };
  filterButtons.forEach(button => {
    button.addEventListener("click", () => {
      if (!entries) return;
      setPressed(filterButtons, button);
      renderEntries(button.dataset.dnaFilter);
    });
  });

  const atlas = root.querySelector("#dna-atlas");
  const allowedRelations = new Set(["literary_analogy","shared_fictional_universe","documented_context_only","ethical_framework"]);
  const renderAtlas = graph => {
    if (!atlas || graph.schema_version !== "cmb.dna-evidence-graph.v1" ||
        !Array.isArray(graph.nodes) || !Array.isArray(graph.edges)) return;
    const index = new Map(graph.nodes.filter(n => n.id && n.label).map(n => [n.id, n]));
    const heading = makeText("p", graph.disclaimer || "A relationship is not proof.");
    const list = document.createElement("ul");
    list.className = "dna-atlas-list";
    for (const edge of graph.edges) {
      if (!allowedRelations.has(edge.relation) || !index.has(edge.from) || !index.has(edge.to)) continue;
      const left = index.get(edge.from);
      const right = index.get(edge.to);
      const li = document.createElement("li");
      for (const [n, label] of [[left, "Source"],[right, "Connection"]]) {
        const line = document.createElement("div");
        line.appendChild(makeText("span", label + ": ", "dna-type"));
        if (n.url && (/^https:\/\//.test(n.url) || isInternalRoute(n.url))) {
          line.appendChild(makeLink(n.label, /^https:\/\//.test(n.url) ? n.url : linkToRoute(n.url)));
        } else {
          line.appendChild(makeText("span", n.label));
        }
        li.appendChild(line);
      }
      li.appendChild(makeText("small", edge.relation.replaceAll("_", " ")));
      list.appendChild(li);
    }
    if (list.children.length) atlas.replaceChildren(heading, list);
  };

  Promise.allSettled([fetchJson("manifest"),fetchJson("evidence")]).then(([canonResult, evidenceResult]) => {
    if (canonResult.status === "fulfilled" &&
        canonResult.value.schema_version === "cmb.dna-canon.v1" &&
        Array.isArray(canonResult.value.entries)) {
      entries = canonResult.value.entries;
      renderEntries("all");
    }
    if (evidenceResult.status === "fulfilled") renderAtlas(evidenceResult.value);
  });
})();
