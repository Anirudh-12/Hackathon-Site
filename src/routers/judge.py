"""
Judge router — stub for Phase 3.

Routes (all require judge role):
  GET /judge/dashboard
  GET /judge/score/{project_id}
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.auth import require_role
from src.database import get_db
from src.models import (
    Event, JudgeTrack, Project, RubricCriteria, Score, User
)
import os

router = APIRouter(prefix="/judge")

templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "..", "templates")
)


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("judge")),
):
    event = db.query(Event).first()

    # Projects in this judge's assigned tracks
    assigned_track_ids = [
        jt.track_id for jt in
        db.query(JudgeTrack).filter(JudgeTrack.judge_id == user.id).all()
    ]
    projects = (
        db.query(Project)
        .filter(Project.track_id.in_(assigned_track_ids), Project.is_draft == False)
        .all()
    ) if assigned_track_ids else []

    scored_ids = {
        s.project_id for s in
        db.query(Score).filter(Score.judge_id == user.id).all()
    }

    return templates.TemplateResponse("judge/dashboard.html", {
        "request": request,
        "user": user,
        "event": event,
        "projects": projects,
        "scored_ids": scored_ids,
        "total": len(projects),
        "completed": len(scored_ids & {p.id for p in projects}),
    })


@router.get("/score/{project_id}", response_class=HTMLResponse)
def score_form(
    project_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("judge")),
):
    event = db.query(Event).first()
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return HTMLResponse("Project not found.", status_code=404)

    criteria = db.query(RubricCriteria).filter(
        RubricCriteria.event_id == event.id
    ).all() if event else []

    existing = {
        s.criteria_id: s for s in
        db.query(Score).filter(
            Score.judge_id == user.id,
            Score.project_id == project_id,
        ).all()
    }

    # Count for the progress header
    assigned_track_ids = [
        jt.track_id for jt in
        db.query(JudgeTrack).filter(JudgeTrack.judge_id == user.id).all()
    ]
    total = db.query(Project).filter(
        Project.track_id.in_(assigned_track_ids), Project.is_draft == False
    ).count()
    scored = db.query(Score).filter(Score.judge_id == user.id).count()

    return templates.TemplateResponse("judge/score.html", {
        "request": request,
        "user": user,
        "event": event,
        "project": project,
        "criteria": criteria,
        "existing": existing,
        "total": total,
        "completed": scored,
    })
