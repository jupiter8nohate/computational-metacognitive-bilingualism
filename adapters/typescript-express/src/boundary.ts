export const BOUNDARY_SCHEMA_VERSION = "cmb.boundary-event.v1" as const;
export const BOUNDARY_AUTHORITY = "HUMAN_FINAL" as const;

export const BOUNDARY_CODES = [
  "AI_DISCLOSURE_REQUIRED",
  "HUMAN_REVIEW_REQUIRED",
  "PROFILE_IS_NOT_PERSON",
  "PREDICTION_IS_NOT_DESTINY",
  "CONSENT_REQUIRED",
] as const;

export type BoundaryCode = (typeof BOUNDARY_CODES)[number];

export interface BoundaryEvent {
  readonly schema_version: typeof BOUNDARY_SCHEMA_VERSION;
  readonly event_id: string | null;
  readonly consequential_decision: boolean;
  readonly ai_involved: boolean;
  readonly ai_disclosed: boolean;
  readonly human_review_available: boolean;
  readonly profile_treated_as_person: boolean;
  readonly prediction_treated_as_destiny: boolean;
  readonly consent_required: boolean;
  readonly consent_present: boolean;
}

export interface BoundaryViolation {
  readonly code: BoundaryCode;
  readonly invariant: string;
  readonly message: string;
}

export interface BoundaryDecision {
  readonly allowed: boolean;
  readonly authority: typeof BOUNDARY_AUTHORITY;
  readonly violations: readonly BoundaryViolation[];
}

const EVENT_KEYS = [
  "schema_version",
  "event_id",
  "consequential_decision",
  "ai_involved",
  "ai_disclosed",
  "human_review_available",
  "profile_treated_as_person",
  "prediction_treated_as_destiny",
  "consent_required",
  "consent_present",
] as const;

const BOOLEAN_KEYS = [
  "consequential_decision",
  "ai_involved",
  "ai_disclosed",
  "human_review_available",
  "profile_treated_as_person",
  "prediction_treated_as_destiny",
  "consent_required",
  "consent_present",
] as const;

type EventKey = (typeof EVENT_KEYS)[number];
type EventRecord = Record<string, unknown> & Record<EventKey, unknown>;

function assertRecord(value: unknown): asserts value is Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new TypeError("boundary event must be a JSON object");
  }
}

function assertExactKeys(value: Record<string, unknown>): asserts value is EventRecord {
  const expected = new Set<string>(EVENT_KEYS);
  const actual = Object.keys(value);

  for (const key of actual) {
    if (!expected.has(key)) {
      throw new TypeError(`unknown boundary event field: ${key}`);
    }
  }

  for (const key of EVENT_KEYS) {
    if (!(key in value)) {
      throw new TypeError(`missing boundary event field: ${key}`);
    }
  }
}

export function parseBoundaryEvent(value: unknown): BoundaryEvent {
  assertRecord(value);
  assertExactKeys(value);

  if (value.schema_version !== BOUNDARY_SCHEMA_VERSION) {
    throw new TypeError(`schema_version must equal ${BOUNDARY_SCHEMA_VERSION}`);
  }

  const eventId = value.event_id;
  if (eventId !== null) {
    if (typeof eventId !== "string") {
      throw new TypeError("event_id must be a string or null");
    }
    if (eventId.trim().length === 0) {
      throw new TypeError("event_id must be non-empty when supplied");
    }
  }

  for (const key of BOOLEAN_KEYS) {
    if (typeof value[key] !== "boolean") {
      throw new TypeError(`${key} must be boolean`);
    }
  }

  return {
    schema_version: BOUNDARY_SCHEMA_VERSION,
    event_id: eventId,
    consequential_decision: value.consequential_decision as boolean,
    ai_involved: value.ai_involved as boolean,
    ai_disclosed: value.ai_disclosed as boolean,
    human_review_available: value.human_review_available as boolean,
    profile_treated_as_person: value.profile_treated_as_person as boolean,
    prediction_treated_as_destiny: value.prediction_treated_as_destiny as boolean,
    consent_required: value.consent_required as boolean,
    consent_present: value.consent_present as boolean,
  };
}

export function evaluateBoundary(value: unknown): BoundaryDecision {
  const event = parseBoundaryEvent(value);
  const violations: BoundaryViolation[] = [];

  if (event.ai_involved && !event.ai_disclosed) {
    violations.push({
      code: "AI_DISCLOSURE_REQUIRED",
      invariant: "CAPABILITY != AUTHORITY",
      message:
        "AI involvement must be disclosed when this boundary policy requires transparency.",
    });
  }

  if (event.consequential_decision && !event.human_review_available) {
    violations.push({
      code: "HUMAN_REVIEW_REQUIRED",
      invariant: "HUMAN_AGENCY > MACHINE_AUTHORITY",
      message:
        "Consequential automated decisions require an available human review path.",
    });
  }

  if (event.profile_treated_as_person) {
    violations.push({
      code: "PROFILE_IS_NOT_PERSON",
      invariant: "PROFILE != PERSON",
      message:
        "A profile may inform a workflow but must not be treated as the person itself.",
    });
  }

  if (event.prediction_treated_as_destiny) {
    violations.push({
      code: "PREDICTION_IS_NOT_DESTINY",
      invariant: "PREDICTION != DESTINY",
      message:
        "A prediction must not be treated as an inevitable human outcome.",
    });
  }

  if (event.consent_required && !event.consent_present) {
    violations.push({
      code: "CONSENT_REQUIRED",
      invariant: "ATTENTION != CONSENT",
      message: "The declared operation requires consent before it may proceed.",
    });
  }

  return Object.freeze({
    allowed: violations.length === 0,
    authority: BOUNDARY_AUTHORITY,
    violations: Object.freeze(violations.map((item) => Object.freeze(item))),
  });
}

export class BoundaryRejectedError extends Error {
  public readonly decision: BoundaryDecision;

  public constructor(decision: BoundaryDecision) {
    super(
      `CMB boundary rejected event: ${decision.violations
        .map((item) => item.code)
        .join(", ")}`,
    );
    this.name = "BoundaryRejectedError";
    this.decision = decision;
  }
}

export function requireBoundary(value: unknown): BoundaryDecision {
  const decision = evaluateBoundary(value);
  if (!decision.allowed) {
    throw new BoundaryRejectedError(decision);
  }
  return decision;
}
