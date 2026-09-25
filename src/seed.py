import json
import os
from datetime import datetime
from src.database import engine, SessionLocal
from src.models import Base, Event, Track, User, JudgeTrack, Team, TeamMember, Project, Score

def load_fixtures():
    # Only load if DB is empty
    db = SessionLocal()
    if db.query(Event).first():
        db.close()
        return

    fixture_path = os.path.join(os.path.dirname(__file__), '..', 'fixtures.json')
    if not os.path.exists(fixture_path):
        print(f"No fixtures found at {fixture_path}")
        db.close()
        return

    with open(fixture_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 1. Event
    event_data = data.get('event', {})
    if event_data:
        submissions_close = datetime.fromisoformat(event_data['submissions_close'].replace('Z', '+00:00'))
        # Using naive UTC datetime for sqlite
        submissions_close = submissions_close.replace(tzinfo=None)
        db.add(Event(
            id=event_data['id'],
            name=event_data['name'],
            submissions_close=submissions_close
        ))

    # 2. Tracks
    for t in data.get('tracks', []):
        db.add(Track(id=t['id'], name=t['name']))

    # 3. Judges
    for j in data.get('judges', []):
        db.add(User(
            id=j['id'],
            name=j['name'],
            email=j['email'],
            role='judge'
        ))
        for track_id in j.get('tracks', []):
            db.add(JudgeTrack(judge_id=j['id'], track_id=track_id))

    # Add organizer and participant for testing
    db.add(User(id='org_1', name='Organizer', email='org@example.com', role='organizer'))
    db.add(User(id='prt_1', name='Participant', email='prt@example.com', role='participant'))
    # Adding a second judge just for testing isolation
    db.add(User(id='jdg_1', name='Test Judge 1', email='jdg1@example.com', role='judge'))
    db.add(User(id='jdg_2', name='Test Judge 2', email='jdg2@example.com', role='judge'))


    # 4. Teams
    for tm in data.get('teams', []):
        db.add(Team(id=tm['id'], name=tm['name']))
        for member in tm.get('members', []):
            db.add(TeamMember(team_id=tm['id'], email=member))

    # 5. Projects
    for p in data.get('projects', []):
        submitted_at = datetime.fromisoformat(p['submitted_at'].replace('Z', '+00:00'))
        submitted_at = submitted_at.replace(tzinfo=None)
        db.add(Project(
            id=p['id'],
            team_id=p['team'],
            track_id=p['track'],
            title=p['title'],
            summary=p['summary'],
            repo_url=p['repo_url'],
            submitted_at=submitted_at
        ))

    # 6. Scores
    for s in data.get('scores', []):
        db.add(Score(
            judge_id=s['judge'],
            project_id=s['project'],
            functionality=s['criteria'].get('functionality', 0),
            quality=s['criteria'].get('quality', 0),
            comment=s.get('comment', '')
        ))

    db.commit()
    db.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    load_fixtures()
