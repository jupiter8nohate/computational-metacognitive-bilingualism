# FastAPI CMB Boundary Guard

This example shows how a web application can convert **explicit, server-known facts** into a CMB boundary decision before allowing a consequential operation.

It intentionally does not inspect prose and guess whether a person was "profiled." The application supplies auditable booleans.

## Install

```bash
python -m pip install -e .
python -m pip install "fastapi>=0.115,<1" "uvicorn>=0.30,<1"
python examples/06_fastapi_boundary/app.py
```

Then submit a POST request to `/automated-decisions`.

## Why the boundary is structured this way

A production service should derive these facts from authenticated application state, configured policy, and verified user choices. Do not trust arbitrary client headers to declare consent or human-review availability.

The engine can enforce:

- AI disclosure;
- human review for consequential decisions;
- profile/person separation;
- prediction/destiny separation;
- explicit consent requirements.

It cannot prove philosophical propositions from arbitrary text, determine a person's mental state, or replace legal review.
