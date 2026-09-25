"""
Auth router — login, logout, register.

Routes:
  GET  /login     Login form
  POST /login     Process login → set cookie
  GET  /logout    Clear cookie → redirect /
  GET  /register  Registration form
  POST /register  Create participant account → redirect /login
"""

import hashlib
import secrets

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.auth import get_current_user
from src.database import get_db
from src.models import User
import os

router = APIRouter()

templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "..", "templates")
)


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request, next: str = "/", db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("login.html", {
        "request": request,
        "next": next,
        "error": None,
    })


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    next: str = Form("/"),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == email).first()

    # Seeded test users have no password — any password works for them.
    if user and user.password_hash is None:
        pass  # test account, always accepted
    elif user and user.password_hash == _hash(password):
        pass  # real account, correct password
    else:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "next": next,
            "error": "Invalid email or password.",
        }, status_code=401)

    response = RedirectResponse(next or _role_home(user.role), status_code=302)
    response.set_cookie("session", user.id, httponly=True, samesite="lax")
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie("session")
    return response


@router.get("/register", response_class=HTMLResponse)
def register_form(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("register.html", {
        "request": request,
        "error": None,
    })


@router.post("/register")
def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "An account with that email already exists.",
        }, status_code=400)

    user = User(
        id=f"usr_{secrets.token_hex(6)}",
        email=email,
        name=name,
        role="participant",
        password_hash=_hash(password),
    )
    db.add(user)
    db.commit()

    response = RedirectResponse(_role_home("participant"), status_code=302)
    response.set_cookie("session", user.id, httponly=True, samesite="lax")
    return response


def _role_home(role: str) -> str:
    return {
        "organizer":   "/organizer/dashboard",
        "judge":       "/judge/dashboard",
        "participant": "/participant/dashboard",
        "admin":       "/admin/users",
    }.get(role, "/")
