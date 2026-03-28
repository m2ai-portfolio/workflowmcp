"""Agent data models."""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class AgentModel:
    """Represents an agent with configurable skills.

    Attributes:
        name: Name of the agent
        skill_path: Path to the skill module or skill name
        config: Additional configuration for the agent
    """
    name: str
    skill_path: str
    config: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate agent data after initialization."""
        if not self.name:
            raise ValueError("Agent must have a name")
        if not self.skill_path:
            raise ValueError("Agent must have a skill_path")
        if not isinstance(self.config, dict):
            raise ValueError("config must be a dictionary")
