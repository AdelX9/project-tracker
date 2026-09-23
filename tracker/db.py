"""Database layer — SQLAlchemy 2.0 with context-managed connections.

Tables are created via raw SQL migrations (see migrations/).
This module handles connections and CRUD operations.
"""

from __future__ import annotations

import os
from collections.abc import Generator
from contextlib import contextmanager
from datetime import date, datetime, timezone

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection, Engine

from tracker.models import (
    Milestone,
    MilestoneStatus,
    Priority,
    Project,
    Status,
    Task,
    TeamMember,
)

# ---------------------------------------------------------------------------
# Connection helpers
# ---------------------------------------------------------------------------

_engine: Engine | None = None


def get_engine(url: str | None = None) -> Engine:
    """Return a singleton engine, creating it on first call."""
    global _engine  # noqa: PLW0603
    if _engine is None:
        db_url = url or os.getenv(
            "DATABASE_URL", "postgresql://tracker:tracker@localhost:5432/tracker"
        )
        _engine = create_engine(db_url, pool_pre_ping=True)
    return _engine


def reset_engine() -> None:
    """Dispose current engine (useful in tests)."""
    global _engine  # noqa: PLW0603
    if _engine is not None:
        _engine.dispose()
        _engine = None


@contextmanager
def connect(url: str | None = None) -> Generator[Connection, None, None]:
    """Yield a transactional connection; commits on clean exit, rolls back on error."""
    engine = get_engine(url)
    with engine.connect() as conn, conn.begin():
        yield conn


# ---------------------------------------------------------------------------
# Project CRUD
# ---------------------------------------------------------------------------


def create_project(conn: Connection, name: str, description: str = "") -> Project:
    row = conn.execute(
        text(
            "INSERT INTO projects (name, description) VALUES (:name, :desc) "
            "RETURNING id, created_at"
        ),
        {"name": name, "desc": description},
    ).mappings().one()
    return Project(id=row["id"], name=name, description=description, created_at=row["created_at"])


def list_projects(conn: Connection) -> list[Project]:
    rows = conn.execute(
        text("SELECT id, name, description, created_at FROM projects ORDER BY id")
    ).mappings().all()
    return [Project(id=r["id"], name=r["name"], description=r["description"],
                    created_at=r["created_at"]) for r in rows]


# ---------------------------------------------------------------------------
# Team member CRUD
# ---------------------------------------------------------------------------


def add_member(conn: Connection, name: str, role: str = "",
               email: str = "", capacity: float = 40.0) -> TeamMember:
    row = conn.execute(
        text(
            "INSERT INTO team_members (name, role, email, capacity_hours) "
            "VALUES (:name, :role, :email, :cap) RETURNING id, created_at"
        ),
        {"name": name, "role": role, "email": email, "cap": capacity},
    ).mappings().one()
    return TeamMember(id=row["id"], name=name, role=role, email=email,
                      capacity_hours=capacity, created_at=row["created_at"])


def list_members(conn: Connection) -> list[TeamMember]:
    rows = conn.execute(
        text("SELECT id, name, role, email, capacity_hours, created_at "
             "FROM team_members ORDER BY id")
    ).mappings().all()
    return [
        TeamMember(id=r["id"], name=r["name"], role=r["role"],
                   email=r["email"], capacity_hours=r["capacity_hours"],
                   created_at=r["created_at"])
        for r in rows
    ]


# ---------------------------------------------------------------------------
# Milestone CRUD
# ---------------------------------------------------------------------------


def create_milestone(conn: Connection, title: str, description: str = "",
                     target_date: date | None = None) -> Milestone:
    row = conn.execute(
        text(
            "INSERT INTO milestones (title, description, target_date) "
            "VALUES (:title, :desc, :target) RETURNING id, created_at"
        ),
        {"title": title, "desc": description, "target": target_date},
    ).mappings().one()
    return Milestone(id=row["id"], title=title, description=description,
                     target_date=target_date, created_at=row["created_at"])


def list_milestones(conn: Connection) -> list[Milestone]:
    rows = conn.execute(
        text("SELECT id, title, description, status, target_date, created_at "
             "FROM milestones ORDER BY target_date NULLS LAST, id")
    ).mappings().all()
    return [
        Milestone(id=r["id"], title=r["title"], description=r["description"],
                  status=MilestoneStatus(r["status"]), target_date=r["target_date"],
                  created_at=r["created_at"])
        for r in rows
    ]


def close_milestone(conn: Connection, milestone_id: int) -> None:
    conn.execute(
        text("UPDATE milestones SET status = 'closed' WHERE id = :id"),
        {"id": milestone_id},
    )


# ---------------------------------------------------------------------------
# Task CRUD
# ---------------------------------------------------------------------------


def create_task(
    conn: Connection,
    title: str,
    description: str = "",
    priority: Priority = Priority.MEDIUM,
    assignee_id: int | None = None,
    milestone_id: int | None = None,
    estimated_hours: float = 0.0,
    due_date: date | None = None,
    tags: list[str] | None = None,
) -> Task:
    row = conn.execute(
        text(
            "INSERT INTO tasks "
            "(title, description, priority, assignee_id, milestone_id, "
            " estimated_hours, due_date, tags) "
            "VALUES (:title, :desc, :pri, :assignee, :ms, :est, :due, :tags) "
            "RETURNING id, created_at, updated_at"
        ),
        {
            "title": title, "desc": description, "pri": priority.value,
            "assignee": assignee_id, "ms": milestone_id,
            "est": estimated_hours, "due": due_date,
            "tags": ",".join(tags) if tags else "",
        },
    ).mappings().one()
    return Task(
        id=row["id"], title=title, description=description,
        priority=priority, assignee_id=assignee_id, milestone_id=milestone_id,
        estimated_hours=estimated_hours, due_date=due_date,
        tags=tags or [], created_at=row["created_at"], updated_at=row["updated_at"],
    )


def update_task_status(conn: Connection, task_id: int, status: Status) -> None:
    conn.execute(
        text("UPDATE tasks SET status = :status, updated_at = :now WHERE id = :id"),
        {"status": status.value, "now": datetime.now(timezone.utc), "id": task_id},
    )


def log_hours(conn: Connection, task_id: int, hours: float) -> None:
    conn.execute(
        text(
            "UPDATE tasks SET actual_hours = actual_hours + :hours, "
            "updated_at = :now WHERE id = :id"
        ),
        {"hours": hours, "now": datetime.now(timezone.utc), "id": task_id},
    )


def list_tasks(
    conn: Connection,
    status: Status | None = None,
    assignee_id: int | None = None,
    milestone_id: int | None = None,
) -> list[Task]:
    query = (
        "SELECT id, title, description, status, priority, assignee_id, "
        "milestone_id, estimated_hours, actual_hours, due_date, tags, "
        "created_at, updated_at FROM tasks WHERE 1=1"
    )
    params: dict = {}
    if status:
        query += " AND status = :status"
        params["status"] = status.value
    if assignee_id:
        query += " AND assignee_id = :assignee"
        params["assignee"] = assignee_id
    if milestone_id:
        query += " AND milestone_id = :ms"
        params["ms"] = milestone_id
    query += " ORDER BY CASE priority "
    query += "WHEN 'critical' THEN 0 WHEN 'high' THEN 1 "
    query += "WHEN 'medium' THEN 2 WHEN 'low' THEN 3 END, due_date NULLS LAST"

    rows = conn.execute(text(query), params).mappings().all()
    return [
        Task(
            id=r["id"], title=r["title"], description=r["description"],
            status=Status(r["status"]), priority=Priority(r["priority"]),
            assignee_id=r["assignee_id"], milestone_id=r["milestone_id"],
            estimated_hours=r["estimated_hours"], actual_hours=r["actual_hours"],
            due_date=r["due_date"],
            tags=[t for t in (r["tags"] or "").split(",") if t],
            created_at=r["created_at"], updated_at=r["updated_at"],
        )
        for r in rows
    ]


# ---------------------------------------------------------------------------
# Analytics queries
# ---------------------------------------------------------------------------


def workload_summary(conn: Connection) -> list[dict]:
    """Hours assigned vs capacity per team member (active tasks only)."""
    rows = conn.execute(
        text(
            "SELECT m.id, m.name, m.capacity_hours, "
            "  COALESCE(SUM(t.estimated_hours), 0) AS assigned_hours, "
            "  COALESCE(SUM(t.actual_hours), 0)    AS logged_hours, "
            "  COUNT(t.id)                          AS active_tasks "
            "FROM team_members m "
            "LEFT JOIN tasks t ON t.assignee_id = m.id "
            "  AND t.status NOT IN ('done', 'backlog') "
            "GROUP BY m.id, m.name, m.capacity_hours "
            "ORDER BY assigned_hours DESC"
        )
    ).mappings().all()
    return [dict(r) for r in rows]


def milestone_progress(conn: Connection) -> list[dict]:
    """Completion percentage per open milestone."""
    rows = conn.execute(
        text(
            "SELECT ms.id, ms.title, ms.target_date, "
            "  COUNT(t.id) AS total_tasks, "
            "  COUNT(t.id) FILTER (WHERE t.status = 'done') AS done_tasks, "
            "  ROUND(100.0 * COUNT(t.id) FILTER (WHERE t.status = 'done') "
            "    / GREATEST(COUNT(t.id), 1), 1) AS pct_complete "
            "FROM milestones ms "
            "LEFT JOIN tasks t ON t.milestone_id = ms.id "
            "WHERE ms.status = 'open' "
            "GROUP BY ms.id, ms.title, ms.target_date "
            "ORDER BY ms.target_date NULLS LAST"
        )
    ).mappings().all()
    return [dict(r) for r in rows]


def velocity_last_n_weeks(conn: Connection, weeks: int = 4) -> list[dict]:
    """Tasks completed per week over the last N weeks."""
    rows = conn.execute(
        text(
            "SELECT date_trunc('week', updated_at)::date AS week_start, "
            "  COUNT(*) AS tasks_completed, "
            "  COALESCE(SUM(actual_hours), 0) AS hours_logged "
            "FROM tasks "
            "WHERE status = 'done' "
            "  AND updated_at >= NOW() - MAKE_INTERVAL(weeks => :n) "
            "GROUP BY week_start ORDER BY week_start"
        ),
        {"n": weeks},
    ).mappings().all()
    return [dict(r) for r in rows]
