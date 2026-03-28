"""Skill loading and execution module for Copilot SDK."""

import importlib
import os
from dataclasses import dataclass
from typing import Dict, Any, List, Optional


@dataclass
class SkillHandle:
    """Handle for a loaded skill.

    Attributes:
        name: Name of the skill
        module: Loaded skill module
        config: Optional configuration for the skill
    """
    name: str
    module: Any
    config: Dict[str, Any]

    def __repr__(self):
        return f"SkillHandle(name='{self.name}', config={self.config})"


# Global skill registry to cache loaded skills
_skill_registry: Dict[str, SkillHandle] = {}


def load_skill(name: str, config: Optional[Dict[str, Any]] = None) -> SkillHandle:
    """Load a skill by name.

    Args:
        name: Name of the skill to load (e.g., 'summarizer', 'translator', 'planner')
        config: Optional configuration dictionary for the skill

    Returns:
        SkillHandle object representing the loaded skill

    Raises:
        ValueError: If skill cannot be found or loaded
    """
    if config is None:
        config = {}

    # Check if already loaded in registry
    cache_key = f"{name}:{str(config)}"
    if cache_key in _skill_registry:
        return _skill_registry[cache_key]

    # Try to load from built-in skills first
    try:
        module_path = f"workflow_mcp.sdk.skills.{name}"
        module = importlib.import_module(module_path)

        # Verify the module has an execute function
        if not hasattr(module, 'execute'):
            raise ValueError(f"Skill module '{name}' does not have an 'execute' function")

        handle = SkillHandle(name=name, module=module, config=config)
        _skill_registry[cache_key] = handle
        return handle

    except ImportError as e:
        raise ValueError(f"Skill '{name}' not found. Available skills: {', '.join(list_skills())}") from e


def run_skill(handle: SkillHandle, input_data: dict) -> dict:
    """Execute a skill with input data.

    Args:
        handle: SkillHandle for the skill to execute
        input_data: Input dictionary for the skill

    Returns:
        Dictionary containing the skill's output

    Raises:
        ValueError: If input is invalid or execution fails
    """
    if not isinstance(input_data, dict):
        raise ValueError("Input data must be a dictionary")

    if not hasattr(handle.module, 'execute'):
        raise ValueError(f"Skill '{handle.name}' does not have an execute function")

    try:
        # Merge config into input if needed (skill-specific behavior)
        if handle.config:
            # Don't modify original input
            merged_input = {**input_data, **handle.config}
        else:
            merged_input = input_data

        result = handle.module.execute(merged_input)

        if not isinstance(result, dict):
            raise ValueError(f"Skill '{handle.name}' must return a dictionary")

        return result

    except Exception as e:
        raise ValueError(f"Skill execution failed for '{handle.name}': {str(e)}") from e


def list_skills() -> List[str]:
    """List all available built-in skills.

    Returns:
        List of skill names
    """
    # Get the skills directory path
    import workflow_mcp.sdk.skills as skills_package
    skills_dir = os.path.dirname(skills_package.__file__)

    # Find all Python files in the skills directory
    skill_names = []
    for filename in os.listdir(skills_dir):
        if filename.endswith('.py') and not filename.startswith('_'):
            skill_name = filename[:-3]  # Remove .py extension
            skill_names.append(skill_name)

    return sorted(skill_names)


def clear_skill_cache():
    """Clear the skill registry cache.

    Useful for testing or reloading skills.
    """
    global _skill_registry
    _skill_registry.clear()
