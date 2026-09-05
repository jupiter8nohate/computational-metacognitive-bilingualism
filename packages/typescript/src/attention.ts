export type AttentionSignalKind =
  | "autoplay_media"
  | "engagement_prompt"
  | "infinite_feed"
  | "sticky_engagement_control"
  | "notification_pressure";

export interface AttentionSignal {
  readonly kind: AttentionSignalKind;
  readonly weight: number;
  readonly evidence: string;
}

export interface AttentionAssessment {
  readonly score: number;
  readonly level: "low" | "moderate" | "high";
  readonly signals: readonly AttentionSignal[];
  readonly boundary: "ATTENTION_SIGNAL != PROOF_OF_PROFILING";
}

const clamp = (value: number, min: number, max: number): number =>
  Math.min(max, Math.max(min, value));

export function assessAttentionSignals(
  signals: readonly AttentionSignal[],
): AttentionAssessment {
  const score = clamp(
    Math.round(signals.reduce((total, signal) => total + clamp(signal.weight, 0, 100), 0)),
    0,
    100,
  );

  const level: AttentionAssessment["level"] =
    score >= 60 ? "high" : score >= 25 ? "moderate" : "low";

  return Object.freeze({
    score,
    level,
    signals: Object.freeze([...signals]),
    boundary: "ATTENTION_SIGNAL != PROOF_OF_PROFILING",
  });
}
