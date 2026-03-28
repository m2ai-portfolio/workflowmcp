"""Tests for workflow monitoring and observability."""

import pytest
import json
from io import StringIO
import sys

from workflow_mcp.core import parse_yaml
from workflow_mcp.monitoring import WorkflowObserver
from workflow_mcp.models import WorkflowModel, StepModel


class TestWorkflowObserver:
    """Test WorkflowObserver functionality."""

    def test_observer_creation(self, valid_workflow_yaml):
        """Test creating a WorkflowObserver."""
        workflow = parse_yaml(valid_workflow_yaml)
        observer = WorkflowObserver(workflow, test_mode=False)

        assert observer.workflow == workflow
        assert observer.test_mode is False
        assert observer.metrics.workflow_name == "Test Workflow"
        assert observer.metrics.total_steps == 3

    def test_execute_and_monitor_success(self, valid_workflow_yaml, capsys):
        """Test successful workflow execution monitoring."""
        workflow = parse_yaml(valid_workflow_yaml)
        observer = WorkflowObserver(workflow, test_mode=False)

        metrics = observer.execute_and_monitor()

        # Check metrics
        assert metrics.successful_steps == 3
        assert metrics.failed_steps == 0
        assert metrics.total_duration_seconds > 0
        assert metrics.total_tokens > 0
        assert len(metrics.step_metrics) == 3

        # Check that all steps completed successfully
        for step_metric in metrics.step_metrics:
            assert step_metric.status == "success"
            assert step_metric.duration_ms > 0
            assert step_metric.tokens_used > 0

        # Check stdout for JSON events
        captured = capsys.readouterr()
        lines = captured.out.strip().split('\n')

        # Should have 2 events per step (start + completion) = 6 events
        assert len(lines) == 6

        # Verify JSON format
        for line in lines:
            event = json.loads(line)
            assert 'step' in event
            assert 'agent' in event
            assert 'status' in event
            assert 'timestamp' in event

    def test_execute_and_monitor_failure(self, valid_workflow_yaml, capsys):
        """Test workflow execution with simulated failure."""
        workflow = parse_yaml(valid_workflow_yaml)
        observer = WorkflowObserver(workflow, test_mode=True)

        # Should raise exception due to simulated failure
        with pytest.raises(Exception, match="Step .* failed"):
            observer.execute_and_monitor()

        # Check metrics
        assert observer.metrics.failed_steps >= 1
        assert observer.metrics.total_duration_seconds > 0

        # Check stdout for alert
        captured = capsys.readouterr()
        lines = captured.out.strip().split('\n')

        # Should have alert in output
        alert_found = False
        for line in lines:
            event = json.loads(line)
            if 'alert' in event:
                assert event['alert'] == "step_failed"
                assert 'error' in event
                assert event['error'] == "Simulated failure for testing"
                alert_found = True
                break

        assert alert_found, "Alert should be emitted on failure"

    def test_prometheus_format(self, valid_workflow_yaml):
        """Test Prometheus metrics formatting."""
        workflow = parse_yaml(valid_workflow_yaml)
        observer = WorkflowObserver(workflow, test_mode=False)

        metrics = observer.execute_and_monitor()
        prometheus_output = observer.format_prometheus_metrics()

        # Check for required Prometheus elements
        assert "# HELP workflow_steps_total" in prometheus_output
        assert "# TYPE workflow_steps_total counter" in prometheus_output
        assert 'workflow_steps_total{workflow="Test Workflow",status="success"}' in prometheus_output
        assert 'workflow_steps_total{workflow="Test Workflow",status="failed"}' in prometheus_output

        assert "# HELP workflow_duration_seconds" in prometheus_output
        assert "# TYPE workflow_duration_seconds gauge" in prometheus_output
        assert 'workflow_duration_seconds{workflow="Test Workflow"}' in prometheus_output

        assert "# HELP workflow_tokens_total" in prometheus_output
        assert "# TYPE workflow_tokens_total counter" in prometheus_output
        assert 'workflow_tokens_total{workflow="Test Workflow"}' in prometheus_output

        # Verify metric values
        lines = prometheus_output.split('\n')
        for line in lines:
            if line.startswith('workflow_steps_total') and 'status="success"' in line:
                # Extract value
                value = int(line.split()[-1])
                assert value == 3

    def test_step_metrics_details(self, valid_workflow_yaml):
        """Test that step metrics contain detailed information."""
        workflow = parse_yaml(valid_workflow_yaml)
        observer = WorkflowObserver(workflow, test_mode=False)

        metrics = observer.execute_and_monitor()

        # Check first step metrics
        step_0 = metrics.step_metrics[0]
        assert step_0.step_id == 0
        assert step_0.agent == "agent1"
        assert step_0.tool == "tool1"
        assert step_0.status == "success"
        assert step_0.start_time is not None
        assert step_0.end_time is not None
        assert step_0.duration_ms > 0
        assert step_0.tokens_used > 0
        assert step_0.error is None

    def test_json_event_format(self, valid_workflow_yaml, capsys):
        """Test that JSON events have correct format."""
        workflow = parse_yaml(valid_workflow_yaml)
        observer = WorkflowObserver(workflow, test_mode=False)

        observer.execute_and_monitor()

        captured = capsys.readouterr()
        lines = captured.out.strip().split('\n')

        # Check start event (first line)
        start_event = json.loads(lines[0])
        assert start_event['status'] == 'running'
        assert 'step' in start_event
        assert 'agent' in start_event
        assert 'tool' in start_event
        assert 'timestamp' in start_event

        # Check completion event (second line)
        complete_event = json.loads(lines[1])
        assert complete_event['status'] == 'success'
        assert 'step' in complete_event
        assert 'agent' in complete_event
        assert 'duration_ms' in complete_event
        assert 'tokens_used' in complete_event
        assert 'timestamp' in complete_event

    def test_simple_workflow_execution(self):
        """Test monitoring a simple single-step workflow."""
        workflow = WorkflowModel(
            name="Simple Test",
            steps=[StepModel(agent="test_agent", tool="test_tool")]
        )

        observer = WorkflowObserver(workflow, test_mode=False)
        metrics = observer.execute_and_monitor()

        assert metrics.total_steps == 1
        assert metrics.successful_steps == 1
        assert metrics.failed_steps == 0
        assert len(metrics.step_metrics) == 1

    def test_multi_dependency_workflow(self, valid_workflow_yaml):
        """Test monitoring workflow with dependencies executes in correct order."""
        workflow = parse_yaml(valid_workflow_yaml)
        observer = WorkflowObserver(workflow, test_mode=False)

        metrics = observer.execute_and_monitor()

        # All steps should complete
        assert len(metrics.step_metrics) == 3

        # Steps should be executed in topological order
        # Step 0 should execute first, then step 1, then step 2
        step_ids = [m.step_id for m in metrics.step_metrics]
        # Due to dependencies, step 0 must come before steps 1 and 2
        assert step_ids[0] == 0

    def test_failure_mode_alert_format(self, valid_workflow_yaml, capsys):
        """Test that failure alert has correct format."""
        workflow = parse_yaml(valid_workflow_yaml)
        observer = WorkflowObserver(workflow, test_mode=True)

        with pytest.raises(Exception):
            observer.execute_and_monitor()

        captured = capsys.readouterr()
        lines = captured.out.strip().split('\n')

        # Find the alert
        alert = None
        for line in lines:
            event = json.loads(line)
            if 'alert' in event:
                alert = event
                break

        assert alert is not None
        assert alert['alert'] == 'step_failed'
        assert 'step' in alert
        assert 'agent' in alert
        assert 'error' in alert
        assert 'timestamp' in alert
        assert alert['error'] == 'Simulated failure for testing'
