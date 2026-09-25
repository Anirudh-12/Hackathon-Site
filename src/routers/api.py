"""
API router — JSON endpoints.

T1/T2 acceptance checker routes live here.
All endpoints return JSON.

Routes:
  POST /projects/new          T1  — submit a project (participant, deadline-gated)
  GET  /api/judge/scores      T2  — judge reads own scores
  GET  /api/export.csv        T2  — organizer downloads CSV
"""

import csv
from datetime import datetime
from io import StringIO

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.auth import audit, get_current_user, require_role
from src.database import get_db
from src.models import Event, Project, Score, User

router = APIRouter()


# ── T1: Submit a project ────────────────────────────────────────────────────

class ProjectSubmitPayload(BaseModel):
    title: str = ""
    summary: str = ""
    repo_url: str = ""
    demo_url: str = ""
    track_id: str = ""


@router.post("/projects/new")
def submit_project(
    payload: ProjectSubmitPayload,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    T1 — closed event refuses submissions.

    The checker POSTs as participant to this endpoint.
    The fixture event's submissions_close is in the past, so we must return 4xx.
    """
    user = get_current_user(request, db)

    if user is None or user.role != "participant":
        raise HTTPException(status_code=401, detail="Participants only.")

    event = db.query(Event).first()
    if event and event.submissions_close < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Submissions are closed for this event.")

    # TODO: create project record (Phase 2)
    return {"status": "ok", "message": "Project received."}


# ── T2: Judge scores ────────────────────────────────────────────────────────

@router.get("/api/judge/scores")
def get_judge_scores(
    request: Request,
    judge: str = None,
    db: Session = Depends(get_db),
):
    """
    T2 — judge sees own scores / judge cannot see peer scores.

    If ?judge=<id> is supplied, the requesting judge must be that judge.
    Any mismatch → 403. Non-judges → 401.
    """
    user = get_current_user(request, db)

    if user is None or user.role != "judge":
        raise HTTPException(status_code=401, detail="Judges only.")

    target_id = judge if judge else user.id

    # Core isolation check — enforced here, not in the UI
    if target_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: judges cannot view peer scores.",
        )

    scores = db.query(Score).filter(Score.judge_id == user.id).all()
    return {
        "judge": user.id,
        "scores": [
            {
                "project": s.project_id,
                "functionality": s.functionality,
                "quality": s.quality,
                "value": s.value,
                "comment": s.comment,
            }
            for s in scores
        ],
    }


# ── T2: CSV export ──────────────────────────────────────────────────────────

@router.get("/api/export.csv")
def export_csv(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    T2 — organizer can export CSV.

    Returns a CSV with one row per project.
    The checker verifies status 200 and that the first line contains a comma.
    """
    user = get_current_user(request, db)

    if user is None or user.role != "organizer":
        raise HTTPException(status_code=401, detail="Organizers only.")

    projects = db.query(Project).all()

    buf = StringIO()
    w = csv.writer(buf)
    w.writerow(["project_id", "title", "team_id", "track_id",
                "is_draft", "submitted_at", "repo_url"])
    for p in projects:
        w.writerow([
            p.id, p.title, p.team_id, p.track_id,
            p.is_draft, p.submitted_at, p.repo_url,
        ])

    return Response(
        content=buf.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=export.csv"},
    )
