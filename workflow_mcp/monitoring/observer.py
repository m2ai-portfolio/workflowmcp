"""Workflow execution observer for metrics collection and monitoring."""

import time
import random
from typing import Dict, List, Any, Optional
from pathlib import Path

from ..core import parse_workflow


def _escape_prometheus_label_value(value: str) -> str:
    """
    Escape special characters in Prometheus label values.

    According to Prometheus specification, label values must escape:
    - Backslash (\) -> \\
    - Double quote (") -> \"
    - Newline (\n) -> \\n

    Args:
        value: Raw label value string

    Returns:
        Escaped string safe for Prometheus format
    """
    # Order matters: escape backslashes first to avoid double-escaping
    value = value.replace("\\", "\\\\")
    value = value.replace("\"", "\\\"")
    value = value.replace("\n", "\\n")
    return value


class WorkflowObserver:
    """Observes workflow execution, collects metrics, emits events."""

    def __init__(self, workflow_name: str):
        """
        Initialize the observer.

        Args:
            workflow_name: Name of the workflow being observed
        """
        self.workflow_name = workflow_name
        self.metrics: Dict[int, Dict[str, Any]] = {}  # step_index -> metrics
        self.events: List[Dict[str, Any]] = []  # event log
        self.total_tokens = 0
        self.success_count = 0
        self.failure_count = 0

    def start_step(self, step_index: int, agent: str, tool: Optional[str] = None) -> None:
        """
        Record step start with timestamp.

        Args:
            step_index: Index of the step
            agent: Agent name
            tool: Optional tool name

        Raises:
            ValueError: If step has already been started
        """
        if step_index in self.metrics:
            raise ValueError(f"Step {step_index} already started")

        self.metrics[step_index] = {
            "step_index": step_index,
            "agent": agent,
            "tool": tool,
            "start_time": time.time(),
            "end_time": None,
            "duration": None,
            "status": "running",
            "tokens": 0
        }

        event = {
            "type": "step_start",
            "step_index": step_index,
            "agent": agent,
            "tool": tool,
            "timestamp": time.time()
        }
        self.events.append(event)

    def end_step(self, step_index: int, success: bool, token_usage: int = 0) -> None:
        """
        Record step end with timestamp, status, token usage.

        Args:
            step_index: Index of the step
            success: Whether the step succeeded
            token_usage: Number of tokens used

        Raises:
            ValueError: If step was not started or token_usage is negative
        """
        if step_index not in self.metrics:
            raise ValueError(f"Step {step_index} was not started")

        if token_usage < 0:
            raise ValueError(f"token_usage must be non-negative, got {token_usage}")

        end_time = time.time()
        start_time = self.metrics[step_index]["start_time"]
        duration = end_time - start_time

        self.metrics[step_index].update({
            "end_time": end_time,
            "duration": duration,
            "status": "success" if success else "failure",
            "tokens": token_usage
        })

        self.total_tokens += token_usage

        if success:
            self.success_count += 1
        else:
            self.failure_count += 1

        event = {
            "type": "step_end",
            "step_index": step_index,
            "agent": self.metrics[step_index]["agent"],
            "status": "success" if success else "failure",
            "duration": duration,
            "tokens": token_usage,
            "timestamp": end_time
        }
        self.events.append(event)

    def get_metrics_json(self) -> List[Dict[str, Any]]:
        """
        Return metrics as JSON-serializable list (for JSON lines output).

        Returns:
            List of metric dictionaries
        """
        return [
            {
                "step_index": metric["step_index"],
                "agent": metric["agent"],
                "tool": metric["tool"],
                "status": metric["status"],
                "duration": metric["duration"],
                "tokens": metric["tokens"]
            }
            for metric in self.metrics.values()
        ]

    def get_metrics_prometheus(self) -> str:
        """
        Return metrics in Prometheus exposition format.

        Returns:
            Prometheus format metrics as string
        """
        lines = []

        # Escape workflow name for use in labels
        escaped_workflow_name = _escape_prometheus_label_value(self.workflow_name)

        # workflow_steps_total metric
        lines.append("# HELP workflow_steps_total Total number of workflow steps by status")
        lines.append("# TYPE workflow_steps_total counter")
        lines.append(f'workflow_steps_total{{workflow="{escaped_workflow_name}",status="success"}} {self.success_count}')
        lines.append(f'workflow_steps_total{{workflow="{escaped_workflow_name}",status="failure"}} {self.failure_count}')

        # workflow_step_duration_seconds metric
        lines.append("")
        lines.append("# HELP workflow_step_duration_seconds Duration of each workflow step in seconds")
        lines.append("# TYPE workflow_step_duration_seconds gauge")
        for metric in self.metrics.values():
            if metric["duration"] is not None:
                escaped_agent = _escape_prometheus_label_value(metric["agent"])
                lines.append(
                    f'workflow_step_duration_seconds{{workflow="{escaped_workflow_name}",'
                    f'step="{metric["step_index"]}",agent="{escaped_agent}"}} '
                    f'{metric["duration"]:.3f}'
                )

        # workflow_tokens_total metric
        lines.append("")
        lines.append("# HELP workflow_tokens_total Total number of tokens used in workflow")
        lines.append("# TYPE workflow_tokens_total counter")
        lines.append(f'workflow_tokens_total{{workflow="{escaped_workflow_name}"}} {self.total_tokens}')

        return "\n".join(lines)

    def emit_alert(self, step_index: int, message: str) -> Dict[str, Any]:
        """
        Emit an alert event for failures.

        Args:
            step_index: Index of the failed step
            message: Alert message

        Returns:
            Alert event dictionary
        """
        alert = {
            "type": "alert",
            "severity": "error",
            "step_index": step_index,
            "message": message,
            "timestamp": time.time()
        }
        self.events.append(alert)
        return alert

    def simulate_run(self, workflow_path: str, inject_failure: bool = False) -> List[Dict[str, Any]]:
        """
        Simulate a workflow run for testing/demo purposes.

        Args:
            workflow_path: Path to the workflow YAML file
            inject_failure: Whether to inject a failure in a random step

        Returns:
            List of events/metrics
        """
        # Parse the workflow
        dag = parse_workflow(workflow_path)
        workflow_name = dag["name"]
        nodes = dag["nodes"]
        execution_order = dag["execution_order"]

        # Update workflow name
        self.workflow_name = workflow_name

        # Determine which step to fail if injecting failure
        failure_step = None
        if inject_failure and len(execution_order) > 0:
            failure_step = random.choice(execution_order)

        # Simulate each step in execution order
        for step_index in execution_order:
            node = nodes[step_index]
            agent = node["agent"]
            tool = node["tool"]

            # Start step
            self.start_step(step_index, agent, tool)

            # Simulate execution time (50-200ms)
            time.sleep(random.uniform(0.05, 0.2))

            # Determine if this step should fail
            should_fail = (step_index == failure_step)

            # Simulate token usage (100-500 tokens)
            tokens = random.randint(100, 500) if not should_fail else random.randint(50, 150)

            # End step
            self.end_step(step_index, success=not should_fail, token_usage=tokens)

            # Emit alert if failed
            if should_fail:
                self.emit_alert(
                    step_index,
                    f"Step {step_index} ({agent}) failed during execution"
                )

        return self.events
