"""Tests for CLI help and argument parsing — no database required."""

from click.testing import CliRunner

from tracker.cli import cli

runner = CliRunner()


class TestCLIHelp:
    """Verify all subcommands are registered and produce help text."""

    def test_root_help(self):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "project-tracker" in result.output

    def test_project_help(self):
        result = runner.invoke(cli, ["project", "--help"])
        assert result.exit_code == 0
        assert "create" in result.output
        assert "list" in result.output

    def test_member_help(self):
        result = runner.invoke(cli, ["member", "--help"])
        assert result.exit_code == 0
        assert "add" in result.output

    def test_milestone_help(self):
        result = runner.invoke(cli, ["milestone", "--help"])
        assert result.exit_code == 0
        assert "create" in result.output
        assert "close" in result.output

    def test_task_help(self):
        result = runner.invoke(cli, ["task", "--help"])
        assert result.exit_code == 0
        assert "add" in result.output
        assert "status" in result.output
        assert "log" in result.output

    def test_report_help(self):
        result = runner.invoke(cli, ["report", "--help"])
        assert result.exit_code == 0
        assert "workload" in result.output
        assert "milestones" in result.output
        assert "velocity" in result.output

    def test_task_add_validates_priority(self):
        result = runner.invoke(cli, ["task", "add", "Test", "--priority", "ultra"])
        assert result.exit_code != 0
        assert "Invalid value" in result.output or "invalid" in result.output.lower()

    def test_task_status_validates_choices(self):
        result = runner.invoke(cli, ["task", "status", "1", "invalid_status"])
        assert result.exit_code != 0
