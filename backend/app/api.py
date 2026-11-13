"""HTTP API used by the dashboard frontend."""
from __future__ import annotations

import io
from typing import Any

from pydantic import BaseModel
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .analysis import analyze, parse_now
from .drafts import generate

app = FastAPI(title="Bazarcheh Support Triage", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/analyze")
async def analyze_upload(
    file: UploadFile = File(...),
    now: str | None = Query(default=None, description="ISO-8601 UTC timestamp"),
) -> dict[str, Any]:
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="uploaded file is empty")
    try:
        reference_time = parse_now(now)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"invalid 'now': {exc}") from exc
    try:
        return analyze(io.BytesIO(content), now=reference_time, include_details=True, prefetch_drafts=False)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


class DraftRequest(BaseModel):
    message_id: str
    customer_id: str | None = None
    subject: str = ""
    body: str = ""


@app.post("/api/draft")
def draft_reply(req: DraftRequest) -> dict[str, Any]:
    return generate(req.message_id, req.subject, req.body)
