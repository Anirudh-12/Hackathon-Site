# DOGFOOD 2026 - Premium Platform

This is our submission for the DOGFOOD 2026 hackathon. We built a beautiful, premium, self-hostable submission and judging platform.

## Features Claimed
We have completed **T1 Core** and **T2 Judging**.
- **T1**: Authentication (via headers/cookies), event closure enforcement, participant submissions, and a beautifully designed public gallery.
- **T2**: Judge score tracking, backend-enforced role isolation (judges cannot see peers' scores), and CSV export for organizers.

## Tech Stack
- **Backend**: Python 3.11 with FastAPI (High performance, simple to host).
- **Database**: SQLite (Zero external dependencies).
- **Frontend**: Jinja2 Templates with Vanilla CSS for a premium glassmorphism aesthetic.
- **ORM**: SQLAlchemy.

## Running Locally

To run the application with the exact fixture data, ensure you have Docker installed and simply run:

```bash
docker compose up
```

The server will start on port 8080 and automatically seed the database with `fixtures.json`.
You can view the gallery at: `http://localhost:8080/projects`

## Acceptance Checker

To run the checker:

```bash
python3 run.py .dogfood.toml > acceptance-report.txt
```

## Honest Limitations
- The frontend currently focuses mainly on the public gallery view (`/projects`).
- The login flow is currently API-based using headers (Cookie), as per the spec. A fully interactive login UI would be the next step for T3.
- Normalization (T2/Stretch) is not yet mathematically implemented for cross-judge score adjustment, though the data structure supports it.
