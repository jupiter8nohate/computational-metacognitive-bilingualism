import { chromium } from "playwright";
import { readFileSync, mkdirSync } from "node:fs";
import { resolve } from "node:path";
import assert from "node:assert/strict";

const base = process.env.EVOLUTION_URL ?? "http://127.0.0.1:8000";
const axeSource = readFileSync(resolve("node_modules/axe-core/axe.min.js"), "utf8");
const browser = await chromium.launch({ headless: true });
mkdirSync("artifacts/evolution", { recursive: true });

async function inspect(page, pathname, scope, screenshot) {
  await page.goto(base + pathname, { waitUntil: "networkidle" });
  await page.addScriptTag({ content: axeSource });
  const results = await page.evaluate(async selector => {
    return window.axe.run(selector, { runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"] } });
  }, scope);
  const violations = results.violations.filter(v => ["critical", "serious"].includes(v.impact));
  assert.equal(violations.length, 0, JSON.stringify(violations.map(v => ({ id: v.id, nodes: v.nodes.length }))));
  await page.screenshot({ path: screenshot, fullPage: true });
}

try {
  const desktop = await browser.newPage({ viewport: { width: 1366, height: 850 } });
  await inspect(desktop, "/", "#cmb-evolution-gates", "artifacts/evolution/home-desktop.png");
  assert.equal(await desktop.locator("#cmb-evolution-gates a").count(), 4);
  await inspect(desktop, "/2084/", "#cmb-nine-transmissions", "artifacts/evolution/reader-desktop.png");
  assert.equal(await desktop.locator("#cmb-nine-transmissions input[type=checkbox]").count(), 9);
  await desktop.locator("#cmb-nine-transmissions input[type=checkbox]").first().check();
  await desktop.getByText("1 of 9 transmissions marked read in this open page.").waitFor();

  await desktop.goto(base + "/DEATH_NOTE_2084/", { waitUntil: "networkidle" });
  assert.equal(await desktop.locator(".cmb-chapter-nav").count(), 1);
  assert.equal(await desktop.locator(".cmb-chapter-nav a").count(), 2);

  const mobile = await browser.newPage({ viewport: { width: 375, height: 812 }, isMobile: true });
  await inspect(mobile, "/", "#cmb-evolution-gates", "artifacts/evolution/home-mobile.png");
  await inspect(mobile, "/2084/", "#cmb-nine-transmissions", "artifacts/evolution/reader-mobile.png");
  assert.ok(await mobile.locator(".cmb-reader li").count() === 9);
  console.log("Evolution browser navigation and scoped axe-core smoke checks passed.");
} finally {
  await browser.close();
}
