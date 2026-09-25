# Data Model

Our schema is designed for flexibility and integrity. It is implemented in `src/models.py` using SQLAlchemy.

## Tables

### `events`
Holds event metadata, such as `name` and `submissions_close`. The deadline is enforced strictly against `submissions_close`.

### `tracks`
Hackathons often feature multiple tracks (e.g., Security, Accessibility). Tracks are stored independently and referenced by projects and judges.

### `users`
A unified table for all roles.
- `id`: Unique string (from fixtures).
- `email`: Unique email.
- `role`: One of `organizer`, `judge`, or `participant`. This simplifies authentication checks since roles are tied directly to the identity.

### `teams` & `team_members`
A team can have multiple members. `team_members` maps emails to a `team_id`.

### `projects`
Stores submissions.
- Foreign keys to `team_id` and `track_id`.
- Stores `title`, `summary`, `repo_url`, and `submitted_at`.

### `scores`
Records judge evaluations.
- Foreign keys to `judge_id` (from users) and `project_id`.
- Criteria scores: `functionality` and `quality`.
- Optional text `comment`.
- By keeping scores normalized and linked to judges, we ensure that a judge cannot modify or view peer scores without explicit database queries allowing it (which our API restricts).

## Import & Export
- **Import**: On startup, `src/seed.py` parses `fixtures.json` and loads it cleanly into this relational structure.
- **Export**: The organizer can export all projects and their metadata via the `/api/export.csv` route, natively generating CSV from the `projects` table.
