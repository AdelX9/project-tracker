# project-tracker

CLI + REST API + Streamlit dashboard for tracking project milestones, tasks, and team workload.

Built for engineering managers and tech leads who want lightweight project visibility without the bloat of enterprise tools.

## Features

- **CLI** — manage projects, tasks, milestones, and team from the terminal
- **REST API** — FastAPI backend with auto-generated Swagger docs
- **Dashboard** — Streamlit visual overview with KPIs, kanban board, and workload heatmap
- **Analytics** — milestone progress, team utilization, velocity tracking
- **PostgreSQL** — proper relational schema with indexes and constraints
- **Docker Compose** — one command to spin up the database with sample data

## Architecture

```
tracker/
├── models.py       # Domain models (dataclasses, enums — no ORM in domain layer)
├── db.py           # SQLAlchemy 2.0 CRUD + analytics queries
├── cli.py          # Click CLI with Rich terminal output
├── api.py          # FastAPI REST endpoints
└── dashboard.py    # Streamlit visual dashboard
```

The domain layer (`models.py`) is pure Python — no framework dependency.
The database layer (`db.py`) uses SQLAlchemy 2.0 with `text()` queries and context-managed connections.
CLI and API are thin wrappers over the same `db` module.

## Quick Start

```bash
# 1. Start PostgreSQL with sample data
docker compose up -d

# 2. Install
pip install -e ".[dev]"

# 3. Use the CLI
tracker project list
tracker task list
tracker task add "Fix login bug" --priority high --assignee 1
tracker task status 1 in_progress
tracker task log 1 --hours 2.5
tracker report workload
tracker report milestones

# 4. Start the API
uvicorn tracker.api:app --reload
# Open http://localhost:8000/docs

# 5. Launch the dashboard
streamlit run tracker/dashboard.py
```

## CLI Commands

| Command | Description |
|---|---|
| `tracker project create/list` | Manage projects |
| `tracker member add/list` | Manage team members |
| `tracker milestone create/list/close` | Manage milestones |
| `tracker task add/list/status/log` | Full task lifecycle |
| `tracker report workload` | Team hours vs capacity |
| `tracker report milestones` | Completion % per milestone |
| `tracker report velocity` | Tasks done per week |

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST/GET | `/projects` | Create / list projects |
| POST/GET | `/members` | Add / list team members |
| POST/GET | `/milestones` | Create / list milestones |
| POST | `/milestones/{id}/close` | Close a milestone |
| POST/GET | `/tasks` | Create / list tasks (filter by status, assignee, milestone) |
| PATCH | `/tasks/{id}/status` | Update task status |
| POST | `/tasks/{id}/log` | Log hours |
| GET | `/reports/workload` | Team utilization |
| GET | `/reports/milestones` | Milestone progress |
| GET | `/reports/velocity` | Weekly velocity |

## Sample Data

The Docker setup auto-loads a "Website Redesign" project with:
- 5 team members (Frontend Lead, Backend Engineer, Designer, QA, PM)
- 3 milestones (MVP Launch, Beta Feedback, Full Launch)
- 15 tasks across all statuses and priorities

## Tech Stack

- Python 3.10+
- PostgreSQL 16
- SQLAlchemy 2.0 (raw SQL via `text()`, context-managed connections)
- Click + Rich (CLI)
- FastAPI + Pydantic (REST API)
- Streamlit (dashboard)
- Docker Compose
- pytest + ruff (testing & linting)

## License

MIT
