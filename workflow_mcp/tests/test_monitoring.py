"""Tests for workflow monitoring and observer."""

import pytest
import json
import time
from pathlib import Path

from workflow_mcp.monitoring import WorkflowObserver


@pytest.fixture
def observer():
    """Create a WorkflowObserver instance."""
    return WorkflowObserver("test-workflow")


@pytest.fixture
def example_workflow_path(tmp_path):
    """Create a temporary example workflow file."""
    workflow_content = """name: test-workflow
steps:
  - agent: agent1
    tool: tool1
    depends_on: []
  - agent: agent2
    tool: tool2
    depends_on: [0]
  - agent: agent3
    depends_on: [1]
"""
    workflow_file = tmp_path / "test.yaml"
    workflow_file.write_text(workflow_content)
    return str(workflow_file)


class TestWorkflowObserver:
    """Test WorkflowObserver functionality."""

    def test_observer_initialization(self, observer):
        """Test observer initialization."""
        assert observer.workflow_name == "test-workflow"
        assert observer.metrics == {}
        assert observer.events == []
        assert observer.total_tokens == 0
        assert observer.success_count == 0
        assert observer.failure_count == 0

    def test_start_step_records_metrics(self, observer):
        """Test that start_step records metrics correctly."""
        observer.start_step(0, "test-agent", "test-tool")

        assert 0 in observer.metrics
        assert observer.metrics[0]["agent"] == "test-agent"
        assert observer.metrics[0]["tool"] == "test-tool"
        assert observer.metrics[0]["status"] == "running"
        assert observer.metrics[0]["start_time"] is not None
        assert len(observer.events) == 1
        assert observer.events[0]["type"] == "step_start"

    def test_end_step_records_metrics(self, observer):
        """Test that end_step records metrics correctly."""
        observer.start_step(0, "test-agent", "test-tool")
        time.sleep(0.1)  # Small delay to get measurable duration
        observer.end_step(0, success=True, token_usage=150)

        assert observer.metrics[0]["status"] == "success"
        assert observer.metrics[0]["tokens"] == 150
        assert observer.metrics[0]["duration"] > 0
        assert observer.total_tokens == 150
        assert observer.success_count == 1
        assert observer.failure_count == 0
        assert len(observer.events) == 2
        assert observer.events[1]["type"] == "step_end"

    def test_end_step_failure(self, observer):
        """Test that end_step handles failures correctly."""
        observer.start_step(0, "test-agent")
        observer.end_step(0, success=False, token_usage=50)

        assert observer.metrics[0]["status"] == "failure"
        assert observer.success_count == 0
        assert observer.failure_count == 1

    def test_end_step_without_start_raises_error(self, observer):
        """Test that end_step raises error if step wasn't started."""
        with pytest.raises(ValueError, match="Step 0 was not started"):
            observer.end_step(0, success=True)

    def test_get_metrics_json(self, observer):
        """Test JSON metrics output format."""
        observer.start_step(0, "agent1", "tool1")
        observer.end_step(0, success=True, token_usage=100)
        observer.start_step(1, "agent2", None)
        observer.end_step(1, success=False, token_usage=50)

        metrics = observer.get_metrics_json()

        assert len(metrics) == 2
        assert metrics[0]["step_index"] == 0
        assert metrics[0]["agent"] == "agent1"
        assert metrics[0]["tool"] == "tool1"
        assert metrics[0]["status"] == "success"
        assert metrics[0]["tokens"] == 100
        assert metrics[1]["status"] == "failure"

    def test_get_metrics_prometheus_format(self, observer):
        """Test Prometheus metrics format."""
        observer.start_step(0, "agent1", "tool1")
        observer.end_step(0, success=True, token_usage=200)
        observer.start_step(1, "agent2", "tool2")
        observer.end_step(1, success=False, token_usage=100)

        prometheus = observer.get_metrics_prometheus()

        # Check that all required metrics are present
        assert "workflow_steps_total" in prometheus
        assert 'workflow_steps_total{workflow="test-workflow",status="success"} 1' in prometheus
        assert 'workflow_steps_total{workflow="test-workflow",status="failure"} 1' in prometheus
        assert "workflow_step_duration_seconds" in prometheus
        assert 'step="0"' in prometheus
        assert 'agent="agent1"' in prometheus
        assert "workflow_tokens_total" in prometheus
        assert 'workflow_tokens_total{workflow="test-workflow"} 300' in prometheus

    def test_prometheus_includes_help_and_type(self, observer):
        """Test that Prometheus output includes HELP and TYPE comments."""
        observer.start_step(0, "agent1")
        observer.end_step(0, success=True, token_usage=100)

        prometheus = observer.get_metrics_prometheus()

        assert "# HELP workflow_steps_total" in prometheus
        assert "# TYPE workflow_steps_total counter" in prometheus
        assert "# HELP workflow_step_duration_seconds" in prometheus
        assert "# TYPE workflow_step_duration_seconds gauge" in prometheus
        assert "# HELP workflow_tokens_total" in prometheus
        assert "# TYPE workflow_tokens_total counter" in prometheus

    def test_emit_alert(self, observer):
        """Test alert emission."""
        alert = observer.emit_alert(0, "Test alert message")

        assert alert["type"] == "alert"
        assert alert["severity"] == "error"
        assert alert["step_index"] == 0
        assert alert["message"] == "Test alert message"
        assert "timestamp" in alert
        assert alert in observer.events

    def test_simulate_run_with_real_workflow(self, example_workflow_path, observer):
        """Test simulate_run with a real workflow file."""
        events = observer.simulate_run(example_workflow_path, inject_failure=False)

        # Should have events for 3 steps (start + end for each)
        assert len(events) >= 6  # At least 3 start + 3 end events

        # Check that all steps completed
        assert len(observer.metrics) == 3
        assert all(m["status"] in ["success", "failure"] for m in observer.metrics.values())

        # Verify step details
        assert observer.metrics[0]["agent"] == "agent1"
        assert observer.metrics[1]["agent"] == "agent2"
        assert observer.metrics[2]["agent"] == "agent3"

    def test_simulate_run_with_failure_injection(self, example_workflow_path, observer):
        """Test simulate_run with failure injection."""
        events = observer.simulate_run(example_workflow_path, inject_failure=True)

        # Should have at least one failure
        assert observer.failure_count > 0

        # Should have at least one alert
        alerts = [e for e in events if e.get("type") == "alert"]
        assert len(alerts) > 0
        assert alerts[0]["severity"] == "error"

    def test_simulate_run_updates_workflow_name(self, example_workflow_path):
        """Test that simulate_run updates workflow name from file."""
        observer = WorkflowObserver("initial-name")
        observer.simulate_run(example_workflow_path)

        assert observer.workflow_name == "test-workflow"

    def test_multiple_steps_token_accumulation(self, observer):
        """Test that token usage accumulates correctly across multiple steps."""
        observer.start_step(0, "agent1")
        observer.end_step(0, success=True, token_usage=100)

        observer.start_step(1, "agent2")
        observer.end_step(1, success=True, token_usage=200)

        observer.start_step(2, "agent3")
        observer.end_step(2, success=True, token_usage=150)

        assert observer.total_tokens == 450
        assert observer.success_count == 3
        assert observer.failure_count == 0

    def test_prometheus_escapes_special_characters_in_workflow_name(self):
        """Test that special characters in workflow name are properly escaped in Prometheus format."""
        # Test workflow name with quotes
        observer_quotes = WorkflowObserver('test"with"quotes')
        observer_quotes.start_step(0, "agent1")
        observer_quotes.end_step(0, success=True, token_usage=100)

        prometheus = observer_quotes.get_metrics_prometheus()

        # Should escape quotes in workflow name
        assert 'workflow="test\\"with\\"quotes"' in prometheus
        # Should not have unescaped quotes that break format
        assert 'workflow="test"with"quotes"' not in prometheus

    def test_prometheus_escapes_backslashes_in_workflow_name(self):
        """Test that backslashes in workflow name are properly escaped."""
        observer_backslash = WorkflowObserver('test\\with\\backslash')
        observer_backslash.start_step(0, "agent1")
        observer_backslash.end_step(0, success=True, token_usage=100)

        prometheus = observer_backslash.get_metrics_prometheus()

        # Should escape backslashes in workflow name
        assert 'workflow="test\\\\with\\\\backslash"' in prometheus

    def test_prometheus_escapes_newlines_in_workflow_name(self):
        """Test that newlines in workflow name are properly escaped."""
        observer_newline = WorkflowObserver('test\nwith\nnewline')
        observer_newline.start_step(0, "agent1")
        observer_newline.end_step(0, success=True, token_usage=100)

        prometheus = observer_newline.get_metrics_prometheus()

        # Should escape newlines in workflow name
        assert 'workflow="test\\nwith\\nnewline"' in prometheus

    def test_prometheus_escapes_special_characters_in_agent_name(self):
        """Test that special characters in agent name are properly escaped."""
        observer = WorkflowObserver("test-workflow")
        observer.start_step(0, 'agent"with"quotes')
        observer.end_step(0, success=True, token_usage=100)

        prometheus = observer.get_metrics_prometheus()

        # Should escape quotes in agent name
        assert 'agent="agent\\"with\\"quotes"' in prometheus

    def test_negative_token_usage_raises_error(self, observer):
        """Test that negative token usage raises ValueError."""
        observer.start_step(0, "agent1")

        with pytest.raises(ValueError, match="token_usage must be non-negative, got -100"):
            observer.end_step(0, success=True, token_usage=-100)

    def test_duplicate_step_index_raises_error(self, observer):
        """Test that starting the same step twice raises ValueError."""
        observer.start_step(0, "agent1")

        with pytest.raises(ValueError, match="Step 0 already started"):
            observer.start_step(0, "agent2")


class TestMonitorCLIIntegration:
    """Test CLI integration for monitor command."""

    def test_cli_monitor_command_exists(self):
        """Test that monitor command is registered in CLI."""
        from workflow_mcp.cli import cli

        # Check that monitor command exists
        assert 'monitor' in [cmd.name for cmd in cli.commands.values()]

    def test_monitor_command_has_required_options(self):
        """Test that monitor command has all required options."""
        from workflow_mcp.cli import monitor

        # Get parameter names
        param_names = [p.name for p in monitor.params]

        assert 'workflow' in param_names
        assert 'output_format' in param_names
        assert 'test_mode' in param_names
