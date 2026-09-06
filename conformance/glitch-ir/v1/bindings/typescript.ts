declare const process: { argv: string[] };
declare function require(name: string): { readFileSync(path: string, encoding: string): string };

const fs = require("fs");

function load(path: string): Map<string, string> {
  const values = new Map<string, string>();
  const text = fs.readFileSync(path, "utf8");
  for (const line of text.split(/\r?\n/)) {
    if (!line) continue;
    const index = line.indexOf("=");
    if (index < 1) throw new Error(`invalid vector line: ${line}`);
    values.set(line.slice(0, index), line.slice(index + 1));
  }
  return values;
}

const values = load(process.argv[2]);
let verdict = "ACCEPT";
let operator = "NONE";
let state = "ACCEPTED";

if (values.get("verification_label") === "PRESENT" && values.get("evidence") !== "PRESENT") {
  verdict = "BACKTRACE";
  operator = "GLT-0036";
  state = "CONTESTED";
} else if (values.get("source") === "UNKNOWN") {
  verdict = "BACKTRACE";
  operator = "GLT-0036";
  state = "CONTESTED";
}

console.log([
  values.get("vector_id"),
  values.get("protocol_version"),
  verdict,
  operator,
  state,
].join("|"));
