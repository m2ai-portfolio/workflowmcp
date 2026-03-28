"""Workflow data models."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class StepModel:
    """Represents a single step in a workflow.

    Attributes:
        agent: Name of the agent to execute this step
        tool: Optional tool name to use
        depends_on: List of step indices this step depends on
    """
    agent: str
    tool: Optional[str] = None
    depends_on: List[int] = field(default_factory=list)

    def __post_init__(self):
        """Validate step data after initialization."""
        if not self.agent:
            raise ValueError("Step must have an agent")
        if not isinstance(self.depends_on, list):
            raise ValueError("depends_on must be a list")


@dataclass
class WorkflowModel:
    """Represents a complete workflow definition.

    Attributes:
        name: Name of the workflow
        steps: List of steps to execute
    """
    name: str
    steps: List[StepModel] = field(default_factory=list)

    def __post_init__(self):
        """Validate workflow data after initialization."""
        if not self.name:
            raise ValueError("Workflow must have a name")
        if not isinstance(self.steps, list):
            raise ValueError("steps must be a list")
