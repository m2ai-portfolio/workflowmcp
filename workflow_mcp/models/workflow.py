"""Workflow and Step data models."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class StepModel:
    """Represents a single step in a workflow."""

    agent: str
    tool: Optional[str] = None
    depends_on: List[int] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StepModel":
        """Create a StepModel from a dictionary."""
        return cls(
            agent=data["agent"],
            tool=data.get("tool"),
            depends_on=data.get("depends_on", [])
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert StepModel to a dictionary."""
        result = {
            "agent": self.agent,
            "depends_on": self.depends_on
        }
        if self.tool is not None:
            result["tool"] = self.tool
        return result


@dataclass
class WorkflowModel:
    """Represents a complete workflow definition."""

    name: str
    steps: List[StepModel] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowModel":
        """Create a WorkflowModel from a dictionary."""
        steps = [StepModel.from_dict(step) for step in data.get("steps", [])]
        return cls(
            name=data["name"],
            steps=steps
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert WorkflowModel to a dictionary."""
        return {
            "name": self.name,
            "steps": [step.to_dict() for step in self.steps]
        }
