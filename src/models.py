"""
SQLAlchemy models for Hackforge.

Tables:
  events          — One event per portal instance
  tracks          — Competition tracks (Security, Climate, etc.)
  users           — All roles: organizer, judge, participant, admin
  judge_tracks    — Many-to-many: which tracks a judge is assigned to
  teams           — Participant teams
  team_members    — Many-to-many: users in teams (by email)
  projects        — Hackathon submissions
  rubric_criteria — Configurable scoring criteria with weights
  scores          — Judge scores per project per criterion
  audit_log       — Human-readable event log
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime,
    ForeignKey, Text, Float, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class Event(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    submissions_open = Column(DateTime, nullable=True)
    submissions_close = Column(DateTime, nullable=False)
    judging_open = Column(DateTime, nullable=True)
    judging_close = Column(DateTime, nullable=True)
    results_published = Column(Boolean, default=False)

    tracks = relationship("Track", back_populates="event", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="event", cascade="all, delete-orphan")
    criteria = relationship("RubricCriteria", back_populates="event", cascade="all, delete-orphan")


class Track(Base):
    __tablename__ = "tracks"

    id = Column(String, primary_key=True)
    event_id = Column(String, ForeignKey("events.id"), nullable=False)
    name = Column(String, nullable=False)

    event = relationship("Event", back_populates="tracks")
    projects = relationship("Project", back_populates="track")
    judge_assignments = relationship("JudgeTrack", back_populates="track")


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=True)  # null = seeded test user
    role = Column(String, nullable=False)  # organizer | judge | participant | admin

    judge_tracks = relationship("JudgeTrack", back_populates="judge")
    scores = relationship("Score", back_populates="judge")
    audit_entries = relationship("AuditLog", back_populates="actor")


class JudgeTrack(Base):
    """Which tracks a judge is assigned to review."""
    __tablename__ = "judge_tracks"

    judge_id = Column(String, ForeignKey("users.id"), primary_key=True)
    track_id = Column(String, ForeignKey("tracks.id"), primary_key=True)

    judge = relationship("User", back_populates="judge_tracks")
    track = relationship("Track", back_populates="judge_assignments")


class Team(Base):
    __tablename__ = "teams"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    invite_token = Column(String, unique=True, nullable=True)

    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    project = relationship("Project", back_populates="team", uselist=False)


class TeamMember(Base):
    __tablename__ = "team_members"

    team_id = Column(String, ForeignKey("teams.id"), primary_key=True)
    email = Column(String, primary_key=True)

    team = relationship("Team", back_populates="members")


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True)
    event_id = Column(String, ForeignKey("events.id"), nullable=False)
    team_id = Column(String, ForeignKey("teams.id"), nullable=True)
    track_id = Column(String, ForeignKey("tracks.id"), nullable=True)
    title = Column(String, nullable=False)
    summary = Column(Text, default="")
    repo_url = Column(String, default="")
    demo_url = Column(String, default="")
    is_draft = Column(Boolean, default=True)
    is_disqualified = Column(Boolean, default=False)
    disqualified_reason = Column(Text, default="")
    submitted_at = Column(DateTime, nullable=True)

    event = relationship("Event", back_populates="projects")
    team = relationship("Team", back_populates="project")
    track = relationship("Track", back_populates="projects")
    scores = relationship("Score", back_populates="project", cascade="all, delete-orphan")


class RubricCriteria(Base):
    """Organizer-configured scoring criteria for an event."""
    __tablename__ = "rubric_criteria"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String, ForeignKey("events.id"), nullable=False)
    name = Column(String, nullable=False)       # e.g. "Functionality"
    description = Column(Text, default="")
    weight = Column(Integer, nullable=False)    # integer, sum of all = 100

    event = relationship("Event", back_populates="criteria")
    scores = relationship("Score", back_populates="criteria")


class Score(Base):
    """One judge's score for one project on one rubric criterion."""
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    judge_id = Column(String, ForeignKey("users.id"), nullable=False)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    criteria_id = Column(Integer, ForeignKey("rubric_criteria.id"), nullable=True)

    # Fallback integer fields for fixture compatibility (pre-rubric)
    functionality = Column(Integer, nullable=True)
    quality = Column(Integer, nullable=True)

    value = Column(Integer, nullable=True)      # score for this criterion (1–5)
    comment = Column(Text, default="")
    is_draft = Column(Boolean, default=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    judge = relationship("User", back_populates="scores")
    project = relationship("Project", back_populates="scores")
    criteria = relationship("RubricCriteria", back_populates="scores")

    __table_args__ = (
        UniqueConstraint("judge_id", "project_id", "criteria_id", name="uq_score_per_criteria"),
    )


class AuditLog(Base):
    """Human-readable log of all significant actions."""
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    actor_id = Column(String, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)     # e.g. "scored_project"
    message = Column(Text, nullable=False)      # plain English sentence
    target_type = Column(String, nullable=True) # "project" | "judge" | "event"
    target_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    actor = relationship("User", back_populates="audit_entries")
