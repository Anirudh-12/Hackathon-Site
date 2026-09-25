from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Event(Base):
    __tablename__ = 'events'
    id = Column(String, primary_key=True)
    name = Column(String)
    submissions_close = Column(DateTime)

class Track(Base):
    __tablename__ = 'tracks'
    id = Column(String, primary_key=True)
    name = Column(String)

class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    role = Column(String) # 'organizer', 'judge', 'participant'

class JudgeTrack(Base):
    __tablename__ = 'judge_tracks'
    judge_id = Column(String, ForeignKey('users.id'), primary_key=True)
    track_id = Column(String, ForeignKey('tracks.id'), primary_key=True)

class Team(Base):
    __tablename__ = 'teams'
    id = Column(String, primary_key=True)
    name = Column(String)

class TeamMember(Base):
    __tablename__ = 'team_members'
    team_id = Column(String, ForeignKey('teams.id'), primary_key=True)
    email = Column(String, primary_key=True)

class Project(Base):
    __tablename__ = 'projects'
    id = Column(String, primary_key=True)
    team_id = Column(String, ForeignKey('teams.id'))
    track_id = Column(String, ForeignKey('tracks.id'))
    title = Column(String)
    summary = Column(Text)
    repo_url = Column(String)
    submitted_at = Column(DateTime)

    team = relationship("Team")
    track = relationship("Track")

class Score(Base):
    __tablename__ = 'scores'
    id = Column(Integer, primary_key=True, autoincrement=True)
    judge_id = Column(String, ForeignKey('users.id'))
    project_id = Column(String, ForeignKey('projects.id'))
    functionality = Column(Integer)
    quality = Column(Integer)
    comment = Column(Text)

    judge = relationship("User")
    project = relationship("Project")
