"""
Organizer router — stub for Phase 4.

Routes (all require organizer role):
  GET /organizer/dashboard
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.auth import require_role
from src.database import get_db
from src.models import Event, Project, Score, User, JudgeTrack
import os

router = APIRouter(prefix="/organizer")

templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "..", "templates")
)


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("organizer")),
):
    event = db.query(Event).first()

    total_projects = db.query(Project).filter(Project.is_draft == False).count()
    draft_projects = db.query(Project).filter(Project.is_draft == True).count()
    total_judges = db.query(User).filter(User.role == "judge").count()

    # Judges with progress
    judges = db.query(User).filter(User.role == "judge").all()
    judge_progress = []
    for j in judges:
        assigned = db.query(JudgeTrack).filter(JudgeTrack.judge_id == j.id).count()
        # Count distinct projects scored
        scored = db.query(Score.project_id).filter(
            Score.judge_id == j.id
        ).distinct().count()
        judge_progress.append({
            "judge": j,
            "assigned": assigned,
            "scored": scored,
            "pct": int(scored / assigned * 100) if assigned else 0,
        })

    return templates.TemplateResponse("organizer/dashboard.html", {
        "request": request,
        "user": user,
        "event": event,
        "total_projects": total_projects,
        "draft_projects": draft_projects,
        "total_judges": total_judges,
        "judge_progress": judge_progress,
    })
