"""FastAPI REST backend — serves the same data the CLI manages.

Run:  uvicorn tracker.api:app --reload
Docs: http://localhost:8000/docs  (auto-generated Swagger UI)
"""

from __future__ import annotations

from datetime import date

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from tracker import db
from tracker.models import Priority, Status

app = FastAPI(
    title="project-tracker API",
    version="0.1.0",
    description="REST API for project milestones, tasks, and team workload",
)


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class ProjectIn(BaseModel):
    name: str
    description: str = ""


class MemberIn(BaseModel):
    name: str
    role: str = ""
    email: str = ""
    capacity_hours: float = 40.0


class MilestoneIn(BaseModel):
    title: str
    description: str = ""
    target_date: date | None = None


class TaskIn(BaseModel):
    title: str
    description: str = ""
    priority: str = "medium"
    assignee_id: int | None = None
    milestone_id: int | None = None
    estimated_hours: float = 0.0
    due_date: date | None = None
    tags: list[str] = []


class StatusUpdate(BaseModel):
    status: str


class HoursLog(BaseModel):
    hours: float


# ---------------------------------------------------------------------------
# Project endpoints
# ---------------------------------------------------------------------------

@app.post("/projects", status_code=201)
def create_project(body: ProjectIn):
    with db.connect() as conn:
        p = db.create_project(conn, body.name, body.description)
    return {"id": p.id, "name": p.name}


@app.get("/projects")
def get_projects():
    with db.connect() as conn:
        return [{"id": p.id, "name": p.name, "description": p.description}
                for p in db.list_projects(conn)]


# ---------------------------------------------------------------------------
# Team endpoints
# ---------------------------------------------------------------------------

@app.post("/members", status_code=201)
def add_member(body: MemberIn):
    with db.connect() as conn:
        m = db.add_member(conn, body.name, body.role, body.email, body.capacity_hours)
    return {"id": m.id, "name": m.name}


@app.get("/members")
def get_members():
    with db.connect() as conn:
        return [{"id": m.id, "name": m.name, "role": m.role,
                 "capacity_hours": m.capacity_hours}
                for m in db.list_members(conn)]


# ---------------------------------------------------------------------------
# Milestone endpoints
# ---------------------------------------------------------------------------

@app.post("/milestones", status_code=201)
def create_milestone(body: MilestoneIn):
    with db.connect() as conn:
        ms = db.create_milestone(conn, body.title, body.description, body.target_date)
    return {"id": ms.id, "title": ms.title}


@app.get("/milestones")
def get_milestones():
    with db.connect() as conn:
        return [{"id": ms.id, "title": ms.title, "status": ms.status.value,
                 "target_date": str(ms.target_date) if ms.target_date else None}
                for ms in db.list_milestones(conn)]


@app.post("/milestones/{milestone_id}/close")
def close_milestone(milestone_id: int):
    with db.connect() as conn:
        db.close_milestone(conn, milestone_id)
    return {"status": "closed"}


# ---------------------------------------------------------------------------
# Task endpoints
# ---------------------------------------------------------------------------

@app.post("/tasks", status_code=201)
def create_task(body: TaskIn):
    with db.connect() as conn:
        t = db.create_task(
            conn, body.title, body.description,
            Priority(body.priority), body.assignee_id,
            body.milestone_id, body.estimated_hours,
            body.due_date, body.tags,
        )
    return {"id": t.id, "title": t.title}


@app.get("/tasks")
def get_tasks(status: str | None = None, assignee_id: int | None = None,
              milestone_id: int | None = None):
    s = Status(status) if status else None
    with db.connect() as conn:
        tasks = db.list_tasks(conn, s, assignee_id, milestone_id)
    return [
        {
            "id": t.id, "title": t.title, "status": t.status.value,
            "priority": t.priority.value, "assignee_id": t.assignee_id,
            "milestone_id": t.milestone_id,
            "estimated_hours": t.estimated_hours,
            "actual_hours": t.actual_hours,
            "due_date": str(t.due_date) if t.due_date else None,
            "is_overdue": t.is_overdue,
        }
        for t in tasks
    ]


@app.patch("/tasks/{task_id}/status")
def update_status(task_id: int, body: StatusUpdate):
    try:
        s = Status(body.status)
    except ValueError:
        raise HTTPException(400, f"Invalid status: {body.status}") from None
    with db.connect() as conn:
        db.update_task_status(conn, task_id, s)
    return {"task_id": task_id, "status": s.value}


@app.post("/tasks/{task_id}/log")
def log_hours(task_id: int, body: HoursLog):
    with db.connect() as conn:
        db.log_hours(conn, task_id, body.hours)
    return {"task_id": task_id, "hours_added": body.hours}


# ---------------------------------------------------------------------------
# Report endpoints
# ---------------------------------------------------------------------------

@app.get("/reports/workload")
def get_workload():
    with db.connect() as conn:
        return db.workload_summary(conn)


@app.get("/reports/milestones")
def get_milestone_progress():
    with db.connect() as conn:
        return db.milestone_progress(conn)


@app.get("/reports/velocity")
def get_velocity(weeks: int = 4):
    with db.connect() as conn:
        return db.velocity_last_n_weeks(conn, weeks)
