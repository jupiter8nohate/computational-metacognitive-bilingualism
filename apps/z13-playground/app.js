const MODES = [
  { symbol: "♑", sign: "Capricorn", language: "C", role: "Foundation", op: "BOUNDARY" },
  { symbol: "♒", sign: "Aquarius", language: "Rust", role: "Future Architect", op: "OWNERSHIP" },
  { symbol: "♓", sign: "Pisces", language: "Haskell", role: "Meaning", op: "MEANING" },
  { symbol: "♈", sign: "Aries", language: "C++", role: "Action", op: "ACT" },
  { symbol: "♉", sign: "Taurus", language: "Java", role: "Stability", op: "PRESERVE" },
  { symbol: "♊", sign: "Gemini", language: "TypeScript", role: "Bilingual Interface", op: "TRANSLATE" },
  { symbol: "♋", sign: "Cancer", language: "Python", role: "Context", op: "DECLARE_CONTEXT" },
  { symbol: "♌", sign: "Leo", language: "Swift", role: "Authorship", op: "AUTHOR" },
  { symbol: "♍", sign: "Virgo", language: "Go", role: "Verification", op: "VERIFY" },
  { symbol: "♎", sign: "Libra", language: "Kotlin", role: "Balance", op: "REVIEW" },
  { symbol: "♏", sign: "Scorpio", language: "Prolog", role: "Inference", op: "HYPOTHESIZE" },
  { symbol: "⛎", sign: "Ophiuchus", language: "Common Lisp", role: "Metacognition", op: "INSPECT_RULE" },
  { symbol: "♐", sign: "Sagittarius", language: "Julia", role: "Exploration", op: "EXPLORE" },
];

const input = document.querySelector("#input");
const output = document.querySelector("#output");
const translateButton = document.querySelector("#translate");
const clearButton = document.querySelector("#clear");
const viewButtons = [...document.querySelectorAll(".view")];

let activeView = "human";
let currentText = input.value.trim();

function summarize(text) {
  const compact = text.replace(/\s+/g, " ").trim();
  return compact.length > 92 ? `${compact.slice(0, 89)}...` : compact;
}

function humanText(mode, text) {
  const prompt = summarize(text);
  const messages = {
    BOUNDARY: `Define what the system may observe without letting observation become authority.\nINPUT: "${prompt}"`,
    OWNERSHIP: `Ask who owns the data, decision, and override path. Human agency remains explicit.\nINPUT: "${prompt}"`,
    MEANING: `Separate computation from lived meaning. A model output is not the person's inner experience.\nINPUT: "${prompt}"`,
    ACT: `Convert the claim into an action that can be reviewed, reversed, and stopped by a human.\nINPUT: "${prompt}"`,
    PRESERVE: `Protect stable rights while systems change. Difference is not a defect to normalize away.\nINPUT: "${prompt}"`,
    TRANSLATE: `Translate machine prediction into plain language without presenting inference as identity.\nINPUT: "${prompt}"`,
    DECLARE_CONTEXT: `Prefer context the human explicitly provides over hidden psychological inference.\nINPUT: "${prompt}"`,
    AUTHOR: `Keep authorship and self-definition with the human. The system may assist, not overwrite.\nINPUT: "${prompt}"`,
    VERIFY: `Require evidence before elevating a pattern into a factual claim.\nINPUT: "${prompt}"`,
    REVIEW: `Balance machine assistance with appeal, explanation, and meaningful human review.\nINPUT: "${prompt}"`,
    HYPOTHESIZE: `Treat inference as a hypothesis that can be wrong. Preserve competing explanations.\nINPUT: "${prompt}"`,
    INSPECT_RULE: `Inspect the rule making the judgment. Ask what assumption, metric, or optimization objective produced it.\nINPUT: "${prompt}"`,
    EXPLORE: `Search alternative interpretations and consequences before fixing one prediction as destiny.\nINPUT: "${prompt}"`,
  };
  return messages[mode.op];
}

function machineText(mode, text) {
  return [
    `${mode.symbol}::${mode.language.toUpperCase().replace(/\s+/g, "_")}`,
    `OP=${mode.op}`,
    `INPUT=${JSON.stringify(summarize(text))}`,
    "ASSERT PATTERN != PROOF",
    "ASSERT PROFILE != PERSON",
    "ASSERT HUMAN_AGENCY > MACHINE_AUTHORITY",
  ].join("\n");
}

function flamingoglyphText(mode, text) {
  return [
    `${mode.symbol} ⚯ 𓁻 ♃ // ${mode.role.toUpperCase()}`,
    `[${mode.op}] → ${summarize(text)}`,
    "⃤ PATTERN ≠ PROOF",
    "𓅓 MODEL ≠ MIND",
    "🪐 HUMAN_AGENCY > MACHINE_AUTHORITY",
  ].join("\n");
}

function card(mode, text) {
  const article = document.createElement("article");
  article.className = "card";

  const symbol = document.createElement("div");
  symbol.className = "symbol";
  symbol.textContent = mode.symbol;

  const title = document.createElement("h3");
  title.textContent = `${mode.sign} // ${mode.role}`;

  const language = document.createElement("div");
  language.className = "language";
  language.textContent = mode.language;

  const body = document.createElement("pre");
  body.textContent =
    activeView === "machine"
      ? machineText(mode, text)
      : activeView === "flamingoglyph"
        ? flamingoglyphText(mode, text)
        : humanText(mode, text);

  article.append(symbol, title, language, body);
  return article;
}

function render() {
  output.replaceChildren();

  if (!currentText) {
    const empty = document.createElement("article");
    empty.className = "card";
    empty.textContent = "Enter text to begin.";
    output.append(empty);
    return;
  }

  for (const mode of MODES) {
    output.append(card(mode, currentText));
  }
}

translateButton.addEventListener("click", () => {
  currentText = input.value.trim();
  render();
});

clearButton.addEventListener("click", () => {
  input.value = "";
  currentText = "";
  render();
  input.focus();
});

for (const button of viewButtons) {
  button.addEventListener("click", () => {
    activeView = button.dataset.view;
    for (const candidate of viewButtons) {
      candidate.classList.toggle("active", candidate === button);
    }
    render();
  });
}

render();
