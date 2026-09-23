"""Domain models — pure Python dataclasses, no ORM dependency in the domain layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Status(str, Enum):
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
    BLOCKED = "blocked"


class MilestoneStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"


@dataclass
class TeamMember:
    """A person who can be assigned tasks."""

    id: int | None = None
    name: str = ""
    role: str = ""
    email: str = ""
    capacity_hours: float = 40.0  # weekly hours available
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("TeamMember name is required")


@dataclass
class Task:
    """A unit of work within a project."""

    id: int | None = None
    title: str = ""
    description: str = ""
    status: Status = Status.BACKLOG
    priority: Priority = Priority.MEDIUM
    assignee_id: int | None = None
    milestone_id: int | None = None
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    due_date: date | None = None
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.title:
            raise ValueError("Task title is required")

    @property
    def is_overdue(self) -> bool:
        if self.due_date and self.status != Status.DONE:
            return date.today() > self.due_date
        return False

    @property
    def effort_ratio(self) -> float | None:
        """Actual / Estimated — >1.0 means over budget."""
        if self.estimated_hours > 0:
            return round(self.actual_hours / self.estimated_hours, 2)
        return None


@dataclass
class Milestone:
    """A deadline grouping related tasks."""

    id: int | None = None
    title: str = ""
    description: str = ""
    status: MilestoneStatus = MilestoneStatus.OPEN
    target_date: date | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.title:
            raise ValueError("Milestone title is required")

    @property
    def is_overdue(self) -> bool:
        if self.target_date and self.status == MilestoneStatus.OPEN:
            return date.today() > self.target_date
        return False


@dataclass
class Project:
    """Top-level container for milestones, tasks, and team members."""

    id: int | None = None
    name: str = ""
    description: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Project name is required")
