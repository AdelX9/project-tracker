"""Tests for domain models — no database required."""

from datetime import date, timedelta

import pytest

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
# Validation
# ---------------------------------------------------------------------------


class TestValidation:
    def test_task_requires_title(self):
        with pytest.raises(ValueError, match="title"):
            Task()

    def test_project_requires_name(self):
        with pytest.raises(ValueError, match="name"):
            Project()

    def test_milestone_requires_title(self):
        with pytest.raises(ValueError, match="title"):
            Milestone()

    def test_member_requires_name(self):
        with pytest.raises(ValueError, match="name"):
            TeamMember()

    def test_valid_task_creates(self):
        t = Task(title="Build login page")
        assert t.title == "Build login page"
        assert t.status == Status.BACKLOG
        assert t.priority == Priority.MEDIUM

    def test_valid_project_creates(self):
        p = Project(name="Website Redesign")
        assert p.name == "Website Redesign"


# ---------------------------------------------------------------------------
# Task properties
# ---------------------------------------------------------------------------


class TestTaskProperties:
    def test_not_overdue_when_no_due_date(self):
        t = Task(title="No deadline")
        assert t.is_overdue is False

    def test_not_overdue_when_done(self):
        t = Task(title="Finished", status=Status.DONE,
                 due_date=date.today() - timedelta(days=5))
        assert t.is_overdue is False

    def test_overdue_when_past_due(self):
        t = Task(title="Late", status=Status.IN_PROGRESS,
                 due_date=date.today() - timedelta(days=1))
        assert t.is_overdue is True

    def test_not_overdue_when_future_due(self):
        t = Task(title="On time", status=Status.TODO,
                 due_date=date.today() + timedelta(days=7))
        assert t.is_overdue is False

    def test_effort_ratio_none_when_no_estimate(self):
        t = Task(title="Unestimated")
        assert t.effort_ratio is None

    def test_effort_ratio_calculation(self):
        t = Task(title="Tracked", estimated_hours=10, actual_hours=12)
        assert t.effort_ratio == 1.2

    def test_effort_ratio_under_budget(self):
        t = Task(title="Fast", estimated_hours=8, actual_hours=4)
        assert t.effort_ratio == 0.5


# ---------------------------------------------------------------------------
# Milestone properties
# ---------------------------------------------------------------------------


class TestMilestoneProperties:
    def test_open_and_past_due_is_overdue(self):
        ms = Milestone(title="Late milestone",
                       target_date=date.today() - timedelta(days=1))
        assert ms.is_overdue is True

    def test_closed_is_not_overdue(self):
        ms = Milestone(title="Done", status=MilestoneStatus.CLOSED,
                       target_date=date.today() - timedelta(days=5))
        assert ms.is_overdue is False

    def test_no_target_is_not_overdue(self):
        ms = Milestone(title="Open-ended")
        assert ms.is_overdue is False


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class TestEnums:
    def test_status_values(self):
        assert len(Status) == 6
        assert Status("in_progress") == Status.IN_PROGRESS

    def test_priority_values(self):
        assert len(Priority) == 4
        assert Priority("critical") == Priority.CRITICAL

    def test_milestone_status_values(self):
        assert len(MilestoneStatus) == 2
