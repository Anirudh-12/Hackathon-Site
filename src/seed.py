"""
Fixture seeder for Hackforge.

Loads fixtures.json into the database on first boot.
Safe to call multiple times — idempotent (checks if event already exists).

Seeded test sessions (printed to stdout at startup):
  organizer    → org_1
  judge_a      → jdg_1   (assigned to trk_01)
  judge_b      → jdg_2   (assigned to trk_01)
  participant  → prt_1
"""

import json
import os
import secrets
from datetime import datetime

from src.database import SessionLocal, engine
from src.models import (
    Base, Event, Track, User, JudgeTrack, Team, TeamMember,
    Project, Score, RubricCriteria
)

FIXTURE_PATH = os.path.join(os.path.dirname(__file__), "..", "fixtures.json")


def _parse_dt(s: str) -> datetime:
    """Parse ISO 8601 UTC string to naive datetime (SQLite has no TZ support)."""
    return datetime.fromisoformat(s.replace("Z", "+00:00")).replace(tzinfo=None)


def load_fixtures():
    db = SessionLocal()
    try:
        # Idempotent: only seed once
        if db.query(Event).first():
            return

        if not os.path.exists(FIXTURE_PATH):
            print(f"[seed] fixtures.json not found at {FIXTURE_PATH} — skipping.")
            return

        with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        # ── Event ──────────────────────────────────────────────────────────────
        ev = data["event"]
        event = Event(
            id=ev["id"],
            name=ev["name"],
            description="",
            submissions_close=_parse_dt(ev["submissions_close"]),
            results_published=False,
        )
        db.add(event)
        db.flush()  # ensure event.id exists before FK references

        # ── Tracks ─────────────────────────────────────────────────────────────
        for t in data.get("tracks", []):
            db.add(Track(id=t["id"], event_id=event.id, name=t["name"]))
        db.flush()

        # ── Default rubric (3 criteria, weights sum to 100) ───────────────────
        default_criteria = [
            RubricCriteria(event_id=event.id, name="Functionality",
                           description="Does it work? Does it solve the problem?", weight=40),
            RubricCriteria(event_id=event.id, name="Quality",
                           description="Code quality, architecture, documentation.", weight=30),
            RubricCriteria(event_id=event.id, name="Innovation",
                           description="Is this a novel approach? Is it creative?", weight=30),
        ]
        for c in default_criteria:
            db.add(c)
        db.flush()

        # ── Judges from fixture ────────────────────────────────────────────────
        for j in data.get("judges", []):
            db.add(User(id=j["id"], email=j["email"], name=j["name"],
                        role="judge", password_hash=None))
            for track_id in j.get("tracks", []):
                db.add(JudgeTrack(judge_id=j["id"], track_id=track_id))

        # ── Seeded test accounts (printed at startup) ─────────────────────────
        test_accounts = [
            User(id="org_1",  email="organizer@hackforge.dev",
                 name="Organizer",    role="organizer",   password_hash=None),
            User(id="prt_1",  email="participant@hackforge.dev",
                 name="Participant",  role="participant",  password_hash=None),
            User(id="jdg_1",  email="judge_a@hackforge.dev",
                 name="Judge Alpha",  role="judge",        password_hash=None),
            User(id="jdg_2",  email="judge_b@hackforge.dev",
                 name="Judge Beta",   role="judge",        password_hash=None),
        ]
        for u in test_accounts:
            db.add(u)
        db.flush()

        # Assign test judges to first track
        first_track = data["tracks"][0]["id"] if data.get("tracks") else None
        if first_track:
            db.add(JudgeTrack(judge_id="jdg_1", track_id=first_track))
            db.add(JudgeTrack(judge_id="jdg_2", track_id=first_track))

        # ── Teams ──────────────────────────────────────────────────────────────
        for tm in data.get("teams", []):
            token = secrets.token_urlsafe(16)
            db.add(Team(id=tm["id"], name=tm["name"], invite_token=token))
            for email in tm.get("members", []):
                db.add(TeamMember(team_id=tm["id"], email=email))

        # ── Projects ───────────────────────────────────────────────────────────
        for p in data.get("projects", []):
            db.add(Project(
                id=p["id"],
                event_id=event.id,
                team_id=p["team"],
                track_id=p["track"],
                title=p["title"],
                summary=p.get("summary", ""),
                repo_url=p.get("repo_url", ""),
                demo_url=p.get("demo_url", ""),
                is_draft=False,
                submitted_at=_parse_dt(p["submitted_at"]),
            ))

        # ── Scores (fixture format uses flat criteria dict) ────────────────────
        for s in data.get("scores", []):
            criteria = s.get("criteria", {})
            db.add(Score(
                judge_id=s["judge"],
                project_id=s["project"],
                functionality=criteria.get("functionality"),
                quality=criteria.get("quality"),
                value=None,          # not linked to a RubricCriteria row
                comment=s.get("comment", ""),
                is_draft=False,
            ))

        db.commit()
        print("[seed] fixtures loaded.")

    except Exception as e:
        db.rollback()
        print(f"[seed] ERROR: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    load_fixtures()
