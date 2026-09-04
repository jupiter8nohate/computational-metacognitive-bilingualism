from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from cmb_provenance import BoundaryContext, BoundaryRejectedError, require_boundary

app = FastAPI(title="CMB Boundary Guard Example")


class AutomatedDecisionRequest(BaseModel):
    event_id: str
    ai_involved: bool
    ai_disclosed: bool
    human_review_available: bool
    profile_treated_as_person: bool = False
    prediction_treated_as_destiny: bool = False
    consent_required: bool = False
    consent_present: bool = False


@app.post("/automated-decisions")
def automated_decision(payload: AutomatedDecisionRequest) -> dict[str, object]:
    context = BoundaryContext(
        event_id=payload.event_id,
        consequential_decision=True,
        ai_involved=payload.ai_involved,
        ai_disclosed=payload.ai_disclosed,
        human_review_available=payload.human_review_available,
        profile_treated_as_person=payload.profile_treated_as_person,
        prediction_treated_as_destiny=payload.prediction_treated_as_destiny,
        consent_required=payload.consent_required,
        consent_present=payload.consent_present,
    )

    try:
        decision = require_boundary(context)
    except BoundaryRejectedError as exc:
        raise HTTPException(status_code=422, detail=exc.decision.to_dict()) from exc

    return {
        "status": "accepted_for_application_processing",
        "boundary": decision.to_dict(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
