"""Workflow execution observer for real-time monitoring."""

import json
import random
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

from workflow_mcp.models import WorkflowModel
from workflow_mcp.core import _topological_sort


@dataclass
class StepMetrics:
    """Metrics for a single step execution."""
    step_id: int
    agent: str
    tool: Optional[str]
    status: str  # "running", "success", "failed"
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: int = 0
    tokens_used: int = 0
    error: Optional[str] = None


@dataclass
class WorkflowMetrics:
    """Aggregated metrics for an entire workflow run."""
    workflow_name: str
    total_steps: int
    successful_steps: int = 0
    failed_steps: int = 0
    total_duration_seconds: float = 0.0
    total_tokens: int = 0
    step_metrics: List[StepMetrics] = field(default_factory=list)


class WorkflowObserver:
    """Observes and monitors workflow execution."""

    def __init__(self, workflow: WorkflowModel, test_mode: bool = False):
        """Initialize the workflow observer.

        Args:
            workflow: WorkflowModel to monitor
            test_mode: If True, simulate a failure during execution
        """
        self.workflow = workflow
        self.test_mode = test_mode
        self.metrics = WorkflowMetrics(
            workflow_name=workflow.name,
            total_steps=len(workflow.steps)
        )

    def execute_and_monitor(self) -> WorkflowMetrics:
        """Execute the workflow and collect metrics.

        Returns:
            WorkflowMetrics with execution results

        Raises:
            Exception: If test_mode is True and a simulated failure occurs
        """
        workflow_start = time.time()

        # Get execution order via topological sort
        try:
            execution_order = _topological_sort(self.workflow)
        except Exception as e:
            raise Exception(f"Failed to determine execution order: {e}")

        # Determine which step to fail in test mode
        failure_step = None
        if self.test_mode and len(execution_order) > 1:
            # Fail at a random step (not the first one)
            failure_step = random.randint(1, len(execution_order) - 1)

        # Execute steps in topological order
        for idx, step_idx in enumerate(execution_order):
            step = self.workflow.steps[step_idx]

            # Start step execution
            start_time = datetime.now()
            self._emit_step_start(step_idx, step.agent, step.tool, start_time)

            # Simulate step execution (random duration between 50-300ms)
            execution_time_ms = random.randint(50, 300)
            time.sleep(execution_time_ms / 1000.0)

            # Check if this step should fail in test mode
            if self.test_mode and idx == failure_step:
                # Simulate failure
                end_time = datetime.now()
                error_msg = "Simulated failure for testing"

                step_metrics = StepMetrics(
                    step_id=step_idx,
                    agent=step.agent,
                    tool=step.tool,
                    status="failed",
                    start_time=start_time,
                    end_time=end_time,
                    duration_ms=execution_time_ms,
                    tokens_used=0,
                    error=error_msg
                )

                self.metrics.step_metrics.append(step_metrics)
                self.metrics.failed_steps += 1

                self._emit_step_failure(step_idx, step.agent, error_msg, execution_time_ms, end_time)
                self._emit_alert(step_idx, step.agent, error_msg, end_time)

                # Calculate total duration up to failure
                self.metrics.total_duration_seconds = time.time() - workflow_start

                raise Exception(f"Step {step_idx} failed: {error_msg}")

            # Simulate successful step completion
            end_time = datetime.now()
            tokens_used = random.randint(100, 1000)  # Simulated token usage

            step_metrics = StepMetrics(
                step_id=step_idx,
                agent=step.agent,
                tool=step.tool,
                status="success",
                start_time=start_time,
                end_time=end_time,
                duration_ms=execution_time_ms,
                tokens_used=tokens_used
            )

            self.metrics.step_metrics.append(step_metrics)
            self.metrics.successful_steps += 1
            self.metrics.total_tokens += tokens_used

            self._emit_step_completion(step_idx, step.agent, execution_time_ms, tokens_used, end_time)

        # Calculate total workflow duration
        self.metrics.total_duration_seconds = time.time() - workflow_start

        return self.metrics

    def _emit_step_start(self, step_id: int, agent: str, tool: Optional[str], timestamp: datetime):
        """Emit a JSON line for step start event."""
        event = {
            "step": step_id,
            "agent": agent,
            "tool": tool,
            "status": "running",
            "timestamp": timestamp.isoformat()
        }
        print(json.dumps(event))

    def _emit_step_completion(self, step_id: int, agent: str, duration_ms: int, tokens_used: int, timestamp: datetime):
        """Emit a JSON line for step completion event."""
        event = {
            "step": step_id,
            "agent": agent,
            "status": "success",
            "duration_ms": duration_ms,
            "tokens_used": tokens_used,
            "timestamp": timestamp.isoformat()
        }
        print(json.dumps(event))

    def _emit_step_failure(self, step_id: int, agent: str, error: str, duration_ms: int, timestamp: datetime):
        """Emit a JSON line for step failure event."""
        event = {
            "step": step_id,
            "agent": agent,
            "status": "failed",
            "error": error,
            "duration_ms": duration_ms,
            "timestamp": timestamp.isoformat()
        }
        print(json.dumps(event))

    def _emit_alert(self, step_id: int, agent: str, error: str, timestamp: datetime):
        """Emit an alert JSON line for step failure."""
        alert = {
            "alert": "step_failed",
            "step": step_id,
            "agent": agent,
            "error": error,
            "timestamp": timestamp.isoformat()
        }
        print(json.dumps(alert))

    def format_prometheus_metrics(self) -> str:
        """Format collected metrics in Prometheus format.

        Returns:
            String containing Prometheus-formatted metrics
        """
        lines = []

        # workflow_steps_total counter
        lines.append("# HELP workflow_steps_total Total number of workflow steps executed")
        lines.append("# TYPE workflow_steps_total counter")
        lines.append(f'workflow_steps_total{{workflow="{self.workflow.name}",status="success"}} {self.metrics.successful_steps}')
        lines.append(f'workflow_steps_total{{workflow="{self.workflow.name}",status="failed"}} {self.metrics.failed_steps}')

        # workflow_duration_seconds gauge
        lines.append("# HELP workflow_duration_seconds Total workflow execution duration")
        lines.append("# TYPE workflow_duration_seconds gauge")
        lines.append(f'workflow_duration_seconds{{workflow="{self.workflow.name}"}} {self.metrics.total_duration_seconds:.3f}')

        # workflow_tokens_total counter
        lines.append("# HELP workflow_tokens_total Total tokens used in workflow execution")
        lines.append("# TYPE workflow_tokens_total counter")
        lines.append(f'workflow_tokens_total{{workflow="{self.workflow.name}"}} {self.metrics.total_tokens}')

        return "\n".join(lines)
