"""
Participant router — stub for Phase 2.

Routes (all require participant role):
  GET  /participant/dashboard
  GET  /participant/team
  GET  /participant/submit
  POST /participant/submit
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.auth import get_current_user, require_role
from src.database import get_db
from src.models import Event, Project, Team, TeamMember, Track, User
import os

router = APIRouter(prefix="/participant")

templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "..", "templates")
)


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("participant")),
):
    event = db.query(Event).first()

    # Find the team this participant is on
    member = db.query(TeamMember).filter(TeamMember.email == user.email).first()
    team = db.query(Team).filter(Team.id == member.team_id).first() if member else None
    project = db.query(Project).filter(Project.team_id == team.id).first() if team else None

    return templates.TemplateResponse("participant/dashboard.html", {
        "request": request,
        "user": user,
        "event": event,
        "team": team,
        "project": project,
    })


@router.get("/submit", response_class=HTMLResponse)
def submit_form(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("participant")),
):
    event = db.query(Event).first()
    tracks = db.query(Track).all()
    member = db.query(TeamMember).filter(TeamMember.email == user.email).first()
    team = db.query(Team).filter(Team.id == member.team_id).first() if member else None
    project = db.query(Project).filter(Project.team_id == team.id).first() if team else None

    from datetime import datetime
    is_closed = event and event.submissions_close < datetime.utcnow()

    return templates.TemplateResponse("participant/submit.html", {
        "request": request,
        "user": user,
        "event": event,
        "tracks": tracks,
        "team": team,
        "project": project,
        "is_closed": is_closed,
    })
