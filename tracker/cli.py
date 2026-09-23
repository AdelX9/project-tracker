"""Click CLI — manage projects, tasks, milestones, and team from the terminal.

Usage:
    tracker project create "Website Redesign"
    tracker member add "Alice" --role "Frontend" --email alice@corp.com
    tracker milestone create "MVP Launch" --date 2025-03-01
    tracker task add "Build login page" --priority high --assignee 1 --milestone 1
    tracker task list
    tracker task status 1 in_progress
    tracker task log 1 --hours 3.5
    tracker report workload
    tracker report milestones
    tracker report velocity
"""

from __future__ import annotations

from datetime import date

import click
from rich.console import Console
from rich.table import Table

from tracker import db
from tracker.models import Priority, Status

console = Console()


# ---------------------------------------------------------------------------
# Root group
# ---------------------------------------------------------------------------

@click.group()
def cli() -> None:
    """project-tracker: track milestones, tasks, and team workload."""


# ---------------------------------------------------------------------------
# Project commands
# ---------------------------------------------------------------------------

@cli.group()
def project() -> None:
    """Manage projects."""


@project.command("create")
@click.argument("name")
@click.option("--desc", default="", help="Project description")
def project_create(name: str, desc: str) -> None:
    """Create a new project."""
    with db.connect() as conn:
        p = db.create_project(conn, name, desc)
    console.print(f"[green]Created project #{p.id}:[/] {p.name}")


@project.command("list")
def project_list() -> None:
    """List all projects."""
    with db.connect() as conn:
        projects = db.list_projects(conn)
    if not projects:
        console.print("[dim]No projects yet.[/]")
        return
    table = Table(title="Projects")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Name", style="bold")
    table.add_column("Description")
    table.add_column("Created")
    for p in projects:
        table.add_row(str(p.id), p.name, p.description,
                      p.created_at.strftime("%Y-%m-%d"))
    console.print(table)


# ---------------------------------------------------------------------------
# Team member commands
# ---------------------------------------------------------------------------

@cli.group()
def member() -> None:
    """Manage team members."""


@member.command("add")
@click.argument("name")
@click.option("--role", default="", help="Job role")
@click.option("--email", default="", help="Email address")
@click.option("--capacity", default=40.0, help="Weekly hours (default 40)")
def member_add(name: str, role: str, email: str, capacity: float) -> None:
    """Add a team member."""
    with db.connect() as conn:
        m = db.add_member(conn, name, role, email, capacity)
    console.print(f"[green]Added member #{m.id}:[/] {m.name} ({m.role})")


@member.command("list")
def member_list() -> None:
    """List team members."""
    with db.connect() as conn:
        members = db.list_members(conn)
    if not members:
        console.print("[dim]No team members yet.[/]")
        return
    table = Table(title="Team Members")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Name", style="bold")
    table.add_column("Role")
    table.add_column("Email")
    table.add_column("Capacity (h/wk)", justify="right")
    for m in members:
        table.add_row(str(m.id), m.name, m.role, m.email,
                      f"{m.capacity_hours:.0f}")
    console.print(table)


# ---------------------------------------------------------------------------
# Milestone commands
# ---------------------------------------------------------------------------

@cli.group()
def milestone() -> None:
    """Manage milestones."""


@milestone.command("create")
@click.argument("title")
@click.option("--desc", default="", help="Description")
@click.option("--date", "target", default=None, help="Target date (YYYY-MM-DD)")
def milestone_create(title: str, desc: str, target: str | None) -> None:
    """Create a milestone."""
    target_date = date.fromisoformat(target) if target else None
    with db.connect() as conn:
        ms = db.create_milestone(conn, title, desc, target_date)
    console.print(f"[green]Created milestone #{ms.id}:[/] {ms.title}")


@milestone.command("list")
def milestone_list() -> None:
    """List milestones."""
    with db.connect() as conn:
        milestones = db.list_milestones(conn)
    if not milestones:
        console.print("[dim]No milestones yet.[/]")
        return
    table = Table(title="Milestones")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Title", style="bold")
    table.add_column("Status")
    table.add_column("Target Date")
    for ms in milestones:
        status_style = "green" if ms.status.value == "closed" else "yellow"
        overdue = " [red](OVERDUE)[/]" if ms.is_overdue else ""
        table.add_row(
            str(ms.id), ms.title,
            f"[{status_style}]{ms.status.value}[/]{overdue}",
            str(ms.target_date) if ms.target_date else "-",
        )
    console.print(table)


@milestone.command("close")
@click.argument("milestone_id", type=int)
def milestone_close(milestone_id: int) -> None:
    """Close a milestone."""
    with db.connect() as conn:
        db.close_milestone(conn, milestone_id)
    console.print(f"[green]Milestone #{milestone_id} closed.[/]")


# ---------------------------------------------------------------------------
# Task commands
# ---------------------------------------------------------------------------

@cli.group()
def task() -> None:
    """Manage tasks."""


@task.command("add")
@click.argument("title")
@click.option("--desc", default="", help="Description")
@click.option("--priority", type=click.Choice(["low", "medium", "high", "critical"]),
              default="medium")
@click.option("--assignee", type=int, default=None, help="Team member ID")
@click.option("--milestone", "ms_id", type=int, default=None, help="Milestone ID")
@click.option("--estimate", type=float, default=0.0, help="Estimated hours")
@click.option("--due", default=None, help="Due date (YYYY-MM-DD)")
@click.option("--tags", default="", help="Comma-separated tags")
def task_add(title: str, desc: str, priority: str, assignee: int | None,
             ms_id: int | None, estimate: float, due: str | None, tags: str) -> None:
    """Add a task."""
    due_date = date.fromisoformat(due) if due else None
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    with db.connect() as conn:
        t = db.create_task(
            conn, title, desc, Priority(priority),
            assignee, ms_id, estimate, due_date, tag_list,
        )
    console.print(f"[green]Created task #{t.id}:[/] {t.title} [{t.priority.value}]")


@task.command("list")
@click.option("--status", type=click.Choice([s.value for s in Status]), default=None)
@click.option("--assignee", type=int, default=None)
@click.option("--milestone", "ms_id", type=int, default=None)
def task_list(status: str | None, assignee: int | None, ms_id: int | None) -> None:
    """List tasks with optional filters."""
    s = Status(status) if status else None
    with db.connect() as conn:
        tasks = db.list_tasks(conn, s, assignee, ms_id)
    if not tasks:
        console.print("[dim]No matching tasks.[/]")
        return
    table = Table(title="Tasks")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Title", style="bold", max_width=40)
    table.add_column("Status")
    table.add_column("Priority")
    table.add_column("Assignee", justify="right")
    table.add_column("Est (h)", justify="right")
    table.add_column("Act (h)", justify="right")
    table.add_column("Due")
    for t in tasks:
        pri_colors = {"critical": "red bold", "high": "red", "medium": "yellow", "low": "dim"}
        status_colors = {
            "done": "green", "in_progress": "blue", "in_review": "magenta",
            "blocked": "red", "todo": "white", "backlog": "dim",
        }
        overdue = " [red]![/]" if t.is_overdue else ""
        table.add_row(
            str(t.id), t.title,
            f"[{status_colors.get(t.status.value, '')}]{t.status.value}[/]",
            f"[{pri_colors.get(t.priority.value, '')}]{t.priority.value}[/]",
            str(t.assignee_id or "-"),
            f"{t.estimated_hours:.1f}", f"{t.actual_hours:.1f}",
            f"{t.due_date}{overdue}" if t.due_date else "-",
        )
    console.print(table)


@task.command("status")
@click.argument("task_id", type=int)
@click.argument("new_status", type=click.Choice([s.value for s in Status]))
def task_status(task_id: int, new_status: str) -> None:
    """Update a task's status."""
    with db.connect() as conn:
        db.update_task_status(conn, task_id, Status(new_status))
    console.print(f"[green]Task #{task_id} -> {new_status}[/]")


@task.command("log")
@click.argument("task_id", type=int)
@click.option("--hours", type=float, required=True, help="Hours to log")
def task_log(task_id: int, hours: float) -> None:
    """Log hours against a task."""
    with db.connect() as conn:
        db.log_hours(conn, task_id, hours)
    console.print(f"[green]Logged {hours:.1f}h on task #{task_id}[/]")


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

@cli.group()
def report() -> None:
    """Analytics and reports."""


@report.command("workload")
def report_workload() -> None:
    """Show team workload — assigned hours vs capacity."""
    with db.connect() as conn:
        rows = db.workload_summary(conn)
    if not rows:
        console.print("[dim]No data.[/]")
        return
    table = Table(title="Team Workload")
    table.add_column("Name", style="bold")
    table.add_column("Active Tasks", justify="right")
    table.add_column("Assigned (h)", justify="right")
    table.add_column("Logged (h)", justify="right")
    table.add_column("Capacity (h)", justify="right")
    table.add_column("Utilization", justify="right")
    for r in rows:
        util = (r["assigned_hours"] / r["capacity_hours"] * 100
                if r["capacity_hours"] > 0 else 0)
        util_style = "red" if util > 100 else ("yellow" if util > 80 else "green")
        table.add_row(
            r["name"], str(r["active_tasks"]),
            f"{r['assigned_hours']:.1f}", f"{r['logged_hours']:.1f}",
            f"{r['capacity_hours']:.0f}",
            f"[{util_style}]{util:.0f}%[/]",
        )
    console.print(table)


@report.command("milestones")
def report_milestones() -> None:
    """Show milestone progress."""
    with db.connect() as conn:
        rows = db.milestone_progress(conn)
    if not rows:
        console.print("[dim]No open milestones.[/]")
        return
    table = Table(title="Milestone Progress")
    table.add_column("Milestone", style="bold")
    table.add_column("Target Date")
    table.add_column("Tasks", justify="right")
    table.add_column("Done", justify="right")
    table.add_column("Progress", justify="right")
    for r in rows:
        pct = float(r["pct_complete"])
        bar_len = 20
        filled = int(pct / 100 * bar_len)
        bar = f"[green]{'█' * filled}[/][dim]{'░' * (bar_len - filled)}[/]"
        table.add_row(
            r["title"],
            str(r["target_date"]) if r["target_date"] else "-",
            str(r["total_tasks"]), str(r["done_tasks"]),
            f"{bar} {pct:.0f}%",
        )
    console.print(table)


@report.command("velocity")
@click.option("--weeks", default=4, help="Number of past weeks")
def report_velocity(weeks: int) -> None:
    """Show tasks completed per week."""
    with db.connect() as conn:
        rows = db.velocity_last_n_weeks(conn, weeks)
    if not rows:
        console.print("[dim]No completed tasks in the last {weeks} weeks.[/]")
        return
    table = Table(title=f"Velocity (Last {weeks} Weeks)")
    table.add_column("Week Starting", style="bold")
    table.add_column("Tasks Done", justify="right")
    table.add_column("Hours Logged", justify="right")
    for r in rows:
        table.add_row(str(r["week_start"]), str(r["tasks_completed"]),
                      f"{r['hours_logged']:.1f}")
    console.print(table)


if __name__ == "__main__":
    cli()
