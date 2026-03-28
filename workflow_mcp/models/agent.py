"""Agent data model."""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class AgentModel:
    """Represents an agent configuration."""

    name: str
    skill_path: str
    config: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentModel":
        """Create an AgentModel from a dictionary."""
        return cls(
            name=data["name"],
            skill_path=data["skill_path"],
            config=data.get("config", {})
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert AgentModel to a dictionary."""
        return {
            "name": self.name,
            "skill_path": self.skill_path,
            "config": self.config
        }
