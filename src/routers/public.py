"""
Public router — pages visible to everyone without login.

Routes:
  GET /               Landing page
  GET /projects       Gallery
  GET /projects/{id}  Project detail
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.auth import get_current_user
from src.database import get_db
from src.models import Event, Project, Track
import os

router = APIRouter()

templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "..", "templates")
)


@router.get("/", response_class=HTMLResponse)
def landing(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    event = db.query(Event).first()
    return templates.TemplateResponse("landing.html", {
        "request": request,
        "user": user,
        "event": event,
    })


@router.get("/projects", response_class=HTMLResponse)
def gallery(
    request: Request,
    track: str = None,
    q: str = None,
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    event = db.query(Event).first()

    query = db.query(Project).filter(Project.is_draft == False)
    if track:
        query = query.filter(Project.track_id == track)
    if q:
        query = query.filter(Project.title.ilike(f"%{q}%"))

    projects = query.order_by(Project.submitted_at.desc()).all()
    tracks = db.query(Track).all()

    return templates.TemplateResponse("gallery.html", {
        "request": request,
        "user": user,
        "event": event,
        "projects": projects,
        "tracks": tracks,
        "selected_track": track,
        "search_query": q or "",
    })


@router.get("/projects/{project_id}", response_class=HTMLResponse)
def project_detail(
    project_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    event = db.query(Event).first()
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        return HTMLResponse("Project not found.", status_code=404)

    return templates.TemplateResponse("project_detail.html", {
        "request": request,
        "user": user,
        "event": event,
        "project": project,
    })
