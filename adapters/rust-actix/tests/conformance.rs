use cmb_boundary_actix::{
    BOUNDARY_SCHEMA_VERSION, BoundaryCode, BoundaryDecision, BoundaryEvent, evaluate_boundary,
};
use serde::Deserialize;

const FIXTURE_JSON: &str =
    include_str!("../../../conformance/boundary.v1.cases.json");

#[derive(Debug, Deserialize)]
struct Fixture {
    schema_version: String,
    cases: Vec<FixtureCase>,
}

#[derive(Debug, Deserialize)]
struct FixtureCase {
    id: String,
    event: BoundaryEvent,
    expected: ExpectedDecision,
}

#[derive(Debug, Deserialize, PartialEq, Eq)]
struct ExpectedDecision {
    allowed: bool,
    authority: String,
    violations: Vec<ExpectedViolation>,
}

#[derive(Debug, Deserialize, PartialEq, Eq)]
struct ExpectedViolation {
    code: String,
    invariant: String,
}

fn normalize(decision: BoundaryDecision) -> ExpectedDecision {
    ExpectedDecision {
        allowed: decision.allowed,
        authority: decision.authority.to_owned(),
        violations: decision
            .violations
            .into_iter()
            .map(|item| ExpectedViolation {
                code: match item.code {
                    BoundaryCode::AiDisclosureRequired => "AI_DISCLOSURE_REQUIRED",
                    BoundaryCode::HumanReviewRequired => "HUMAN_REVIEW_REQUIRED",
                    BoundaryCode::ProfileIsNotPerson => "PROFILE_IS_NOT_PERSON",
                    BoundaryCode::PredictionIsNotDestiny => "PREDICTION_IS_NOT_DESTINY",
                    BoundaryCode::ConsentRequired => "CONSENT_REQUIRED",
                }
                .to_owned(),
                invariant: item.invariant.to_owned(),
            })
            .collect(),
    }
}

#[test]
fn rust_reference_engine_matches_shared_conformance_cases() {
    let fixture: Fixture = serde_json::from_str(FIXTURE_JSON).expect("valid conformance fixture");
    assert_eq!(fixture.schema_version, "cmb.boundary-conformance.v1");

    for case in fixture.cases {
        assert_eq!(case.event.schema_version, BOUNDARY_SCHEMA_VERSION);
        let actual = normalize(evaluate_boundary(&case.event).expect("valid event"));
        assert_eq!(actual, case.expected, "fixture case {}", case.id);
    }
}

#[test]
fn event_rejects_unknown_fields() {
    let invalid = r#"{
      "schema_version":"cmb.boundary-event.v1",
      "event_id":"bad-001",
      "consequential_decision":false,
      "ai_involved":false,
      "ai_disclosed":false,
      "human_review_available":false,
      "profile_treated_as_person":false,
      "prediction_treated_as_destiny":false,
      "consent_required":false,
      "consent_present":false,
      "machine_authority":true
    }"#;

    let error = serde_json::from_str::<BoundaryEvent>(invalid).expect_err("unknown field must fail");
    assert!(error.to_string().contains("unknown field"));
}

#[test]
fn event_rejects_blank_event_id() {
    let event = BoundaryEvent {
        schema_version: BOUNDARY_SCHEMA_VERSION.to_owned(),
        event_id: Some("   ".to_owned()),
        consequential_decision: false,
        ai_involved: false,
        ai_disclosed: false,
        human_review_available: false,
        profile_treated_as_person: false,
        prediction_treated_as_destiny: false,
        consent_required: false,
        consent_present: false,
    };

    let error = evaluate_boundary(&event).expect_err("blank event id must fail");
    assert!(error.to_string().contains("event_id"));
}
