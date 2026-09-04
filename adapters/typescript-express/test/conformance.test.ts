import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import test from "node:test";

import { evaluateBoundary, parseBoundaryEvent } from "../src/boundary.js";

interface ExpectedViolation {
  readonly code: string;
  readonly invariant: string;
}

interface ExpectedDecision {
  readonly allowed: boolean;
  readonly authority: string;
  readonly violations: readonly ExpectedViolation[];
}

interface FixtureCase {
  readonly id: string;
  readonly event: unknown;
  readonly expected: ExpectedDecision;
}

interface Fixture {
  readonly schema_version: string;
  readonly cases: readonly FixtureCase[];
}

const fixturePath = resolve(
  process.cwd(),
  "../../conformance/boundary.v1.cases.json",
);
const fixture = JSON.parse(readFileSync(fixturePath, "utf8")) as Fixture;

function normalizeDecision(value: unknown): ExpectedDecision {
  const decision = evaluateBoundary(value);
  return {
    allowed: decision.allowed,
    authority: decision.authority,
    violations: decision.violations.map(({ code, invariant }) => ({
      code,
      invariant,
    })),
  };
}

test("fixture version is stable", () => {
  assert.equal(fixture.schema_version, "cmb.boundary-conformance.v1");
});

for (const fixtureCase of fixture.cases) {
  test(`conformance: ${fixtureCase.id}`, () => {
    assert.deepEqual(normalizeDecision(fixtureCase.event), fixtureCase.expected);
  });
}

test("parser rejects unknown fields", () => {
  const baseline = fixture.cases[0];
  assert.ok(baseline);

  assert.throws(
    () =>
      parseBoundaryEvent({
        ...(baseline.event as Record<string, unknown>),
        machine_authority: true,
      }),
    /unknown boundary event field/,
  );
});

test("parser rejects non-boolean policy facts", () => {
  const baseline = fixture.cases[0];
  assert.ok(baseline);

  assert.throws(
    () =>
      parseBoundaryEvent({
        ...(baseline.event as Record<string, unknown>),
        ai_involved: 1,
      }),
    /ai_involved must be boolean/,
  );
});
