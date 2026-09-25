"""
Hackforge — DOGFOOD 2026 Platform
FastAPI application entry point.

Startup sequence:
  1. Create DB tables (SQLAlchemy metadata)
  2. Seed fixtures.json if the DB is empty
  3. Print test session tokens to stdout

Running:
  uvicorn src.main:app --port 8080
"""

import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.database import engine
from src.models import Base
from src.seed import load_fixtures

from src.routers import api, auth, judge, organizer, participant, public

app = FastAPI(
    title="Hackforge",
    description="Open-source hackathon submission and judging platform.",
    version="1.0.0",
)

# ── Static files ────────────────────────────────────────────────────────────
_static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=_static_dir), name="static")

# ── Routers ─────────────────────────────────────────────────────────────────
app.include_router(public.router)
app.include_router(auth.router)
app.include_router(participant.router)
app.include_router(judge.router)
app.include_router(organizer.router)
app.include_router(api.router)  # /projects/new, /api/judge/scores, /api/export.csv


# ── Startup ──────────────────────────────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    load_fixtures()
    print(" ")
    print("seeded. test logins:")
    print("  organizer    Cookie: session=org_1")
    print("  judge_a      Cookie: session=jdg_1")
    print("  judge_b      Cookie: session=jdg_2")
    print("  participant  Cookie: session=prt_1")
    print(" ")
