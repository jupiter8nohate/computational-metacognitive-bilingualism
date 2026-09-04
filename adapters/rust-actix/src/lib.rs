use actix_web::{HttpResponse, web};
use serde::{Deserialize, Serialize};
use std::error::Error;
use std::fmt::{Display, Formatter};

pub const BOUNDARY_SCHEMA_VERSION: &str = "cmb.boundary-event.v1";
pub const BOUNDARY_AUTHORITY: &str = "HUMAN_FINAL";

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum BoundaryCode {
    AiDisclosureRequired,
    HumanReviewRequired,
    ProfileIsNotPerson,
    PredictionIsNotDestiny,
    ConsentRequired,
}

impl BoundaryCode {
    pub const fn as_str(self) -> &'static str {
        match self {
            Self::AiDisclosureRequired => "AI_DISCLOSURE_REQUIRED",
            Self::HumanReviewRequired => "HUMAN_REVIEW_REQUIRED",
            Self::ProfileIsNotPerson => "PROFILE_IS_NOT_PERSON",
            Self::PredictionIsNotDestiny => "PREDICTION_IS_NOT_DESTINY",
            Self::ConsentRequired => "CONSENT_REQUIRED",
        }
    }
}

impl Display for BoundaryCode {
    fn fmt(&self, formatter: &mut Formatter<'_>) -> std::fmt::Result {
        formatter.write_str(self.as_str())
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct BoundaryEvent {
    pub schema_version: String,
    pub event_id: Option<String>,
    pub consequential_decision: bool,
    pub ai_involved: bool,
    pub ai_disclosed: bool,
    pub human_review_available: bool,
    pub profile_treated_as_person: bool,
    pub prediction_treated_as_destiny: bool,
    pub consent_required: bool,
    pub consent_present: bool,
}

impl BoundaryEvent {
    pub fn validate(&self) -> Result<(), BoundaryInputError> {
        if self.schema_version != BOUNDARY_SCHEMA_VERSION {
            return Err(BoundaryInputError::InvalidSchemaVersion);
        }

        if self
            .event_id
            .as_ref()
            .is_some_and(|value| value.trim().is_empty())
        {
            return Err(BoundaryInputError::BlankEventId);
        }

        Ok(())
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct BoundaryViolation {
    pub code: BoundaryCode,
    pub invariant: &'static str,
    pub message: &'static str,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct BoundaryDecision {
    allowed: bool,
    authority: &'static str,
    violations: Vec<BoundaryViolation>,
}

impl BoundaryDecision {
    fn new(violations: Vec<BoundaryViolation>) -> Self {
        Self {
            allowed: violations.is_empty(),
            authority: BOUNDARY_AUTHORITY,
            violations,
        }
    }

    pub const fn allowed(&self) -> bool {
        self.allowed
    }

    pub const fn authority(&self) -> &'static str {
        self.authority
    }

    pub fn violations(&self) -> &[BoundaryViolation] {
        &self.violations
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum BoundaryInputError {
    InvalidSchemaVersion,
    BlankEventId,
}

impl Display for BoundaryInputError {
    fn fmt(&self, formatter: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::InvalidSchemaVersion => {
                write!(
                    formatter,
                    "schema_version must equal {BOUNDARY_SCHEMA_VERSION}"
                )
            }
            Self::BlankEventId => write!(formatter, "event_id must be non-empty when supplied"),
        }
    }
}

impl Error for BoundaryInputError {}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct BoundaryRejectedError {
    pub decision: BoundaryDecision,
}

impl Display for BoundaryRejectedError {
    fn fmt(&self, formatter: &mut Formatter<'_>) -> std::fmt::Result {
        let codes = self
            .decision
            .violations
            .iter()
            .map(|item| item.code.to_string())
            .collect::<Vec<_>>()
            .join(", ");
        write!(formatter, "CMB boundary rejected event: {codes}")
    }
}

impl Error for BoundaryRejectedError {}

pub fn evaluate_boundary(event: &BoundaryEvent) -> Result<BoundaryDecision, BoundaryInputError> {
    event.validate()?;
    let mut violations = Vec::new();

    if event.ai_involved && !event.ai_disclosed {
        violations.push(BoundaryViolation {
            code: BoundaryCode::AiDisclosureRequired,
            invariant: "CAPABILITY != AUTHORITY",
            message: "AI involvement must be disclosed when this boundary policy requires transparency.",
        });
    }

    if event.consequential_decision && !event.human_review_available {
        violations.push(BoundaryViolation {
            code: BoundaryCode::HumanReviewRequired,
            invariant: "HUMAN_AGENCY > MACHINE_AUTHORITY",
            message: "Consequential automated decisions require an available human review path.",
        });
    }

    if event.profile_treated_as_person {
        violations.push(BoundaryViolation {
            code: BoundaryCode::ProfileIsNotPerson,
            invariant: "PROFILE != PERSON",
            message: "A profile may inform a workflow but must not be treated as the person itself.",
        });
    }

    if event.prediction_treated_as_destiny {
        violations.push(BoundaryViolation {
            code: BoundaryCode::PredictionIsNotDestiny,
            invariant: "PREDICTION != DESTINY",
            message: "A prediction must not be treated as an inevitable human outcome.",
        });
    }

    if event.consent_required && !event.consent_present {
        violations.push(BoundaryViolation {
            code: BoundaryCode::ConsentRequired,
            invariant: "ATTENTION != CONSENT",
            message: "The declared operation requires consent before it may proceed.",
        });
    }

    Ok(BoundaryDecision::new(violations))
}

pub fn require_boundary(
    event: &BoundaryEvent,
) -> Result<BoundaryDecision, Box<dyn Error + Send + Sync>> {
    let decision = evaluate_boundary(event)?;
    if decision.allowed() {
        Ok(decision)
    } else {
        Err(Box::new(BoundaryRejectedError { decision }))
    }
}

pub async fn boundary_handler(payload: web::Json<BoundaryEvent>) -> HttpResponse {
    match evaluate_boundary(payload.as_ref()) {
        Ok(decision) if decision.allowed() => HttpResponse::Ok().json(decision),
        Ok(decision) => HttpResponse::UnprocessableEntity().json(decision),
        Err(error) => HttpResponse::BadRequest().json(serde_json::json!({
            "error": "INVALID_BOUNDARY_EVENT",
            "message": error.to_string(),
        })),
    }
}

pub fn configure(config: &mut web::ServiceConfig) {
    config.route("/cmb/boundary/v1", web::post().to(boundary_handler));
}
