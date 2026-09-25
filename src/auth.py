"""
Authentication helpers for Hackforge.

get_current_user  — extracts the session cookie and returns the User or None
require_role      — factory that returns a FastAPI dependency raising 401/403
                    if the user is missing or has the wrong role

The checker sends:  Cookie: session=<user_id>
FastAPI parses this automatically via request.cookies.
We fall back to parsing the raw Cookie header for any client that sends it
without the standard cookie jar (e.g. urllib in run.py).
"""

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.database import get_db
from src.models import AuditLog, User
from datetime import datetime


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    """Return the logged-in User or None (unauthenticated)."""
    session_id = request.cookies.get("session")

    # urllib (used by run.py) sends the Cookie header as a plain string.
    # FastAPI parses it correctly, but if the cookie jar is missing we
    # fall back to a manual parse.
    if not session_id:
        raw = request.headers.get("cookie", "")
        for part in raw.split(";"):
            part = part.strip()
            if part.startswith("session="):
                session_id = part[len("session="):]
                break

    if not session_id:
        return None

    return db.query(User).filter(User.id == session_id).first()


def require_role(*roles: str):
    """
    FastAPI dependency factory.

    Usage:
        @router.get("/organizer/dashboard")
        def dashboard(user: User = Depends(require_role("organizer"))):
            ...

    Returns the authenticated user if their role is in `roles`.
    Raises 401 if not logged in, 403 if wrong role.
    """
    def dependency(
        request: Request,
        db: Session = Depends(get_db),
    ) -> User:
        user = get_current_user(request, db)
        if user is None:
            raise HTTPException(status_code=401, detail="Authentication required.")
        if user.role not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required role: {' or '.join(roles)}.",
            )
        return user

    return dependency


def audit(db: Session, actor: User | None, action: str, message: str,
          target_type: str = None, target_id: str = None):
    """Write a plain-English audit log entry."""
    entry = AuditLog(
        actor_id=actor.id if actor else None,
        action=action,
        message=message,
        target_type=target_type,
        target_id=target_id,
        created_at=datetime.utcnow(),
    )
    db.add(entry)
    # Caller is responsible for db.commit()
