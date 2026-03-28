"""SDK Loader - dynamically load and manage agent skills."""

import importlib
import importlib.util
import uuid
from pathlib import Path
from typing import Optional


class SkillHandle:
    """Handle to a loaded skill module."""

    def __init__(self, name: str, module, config: dict = None):
        """Initialize a skill handle.

        Args:
            name: Skill name
            module: Loaded Python module containing the skill
            config: Optional configuration dictionary
        """
        self.name = name
        self.module = module
        self.config = config or {}
        self.handle_id = str(uuid.uuid4())[:8]

    def invoke(self, input_data: dict) -> dict:
        """Invoke the skill with input data.

        Args:
            input_data: Dictionary of input parameters

        Returns:
            Dictionary of output results
        """
        if not hasattr(self.module, 'run'):
            raise AttributeError(f"Skill module '{self.name}' does not have a 'run' function")

        return self.module.run(input_data)

    def __repr__(self):
        return f"<SkillHandle id={self.handle_id} name={self.name}>"


class SkillRegistry:
    """Registry for managing loaded skills."""

    # Global registry instance
    _instance = None

    def __init__(self, skills_dir: Optional[str] = None):
        """Initialize the skill registry.

        Args:
            skills_dir: Directory path containing skill modules.
                       If None, uses the built-in skills directory.
        """
        self.handles = {}  # handle_id -> SkillHandle
        self.skills_by_name = {}  # name -> SkillHandle

        if skills_dir is None:
            # Use built-in skills directory
            sdk_dir = Path(__file__).parent
            self.skills_dir = sdk_dir / "skills"
        else:
            self.skills_dir = Path(skills_dir)

    @classmethod
    def get_instance(cls, skills_dir: Optional[str] = None):
        """Get or create the global registry instance.

        Note: This is a singleton pattern. The skills_dir parameter is only
        used when creating the instance for the first time. Subsequent calls
        will return the existing instance and ignore the skills_dir parameter.

        Args:
            skills_dir: Directory path for skills (only used on first call)

        Returns:
            The singleton SkillRegistry instance
        """
        if cls._instance is None:
            cls._instance = cls(skills_dir)
        return cls._instance

    def discover_skills(self) -> list[str]:
        """Discover available skills in the skills directory.

        Returns:
            List of skill names (without .py extension)
        """
        if not self.skills_dir.exists():
            return []

        skills = []
        for path in self.skills_dir.glob("*.py"):
            # Skip __init__.py and private modules
            if path.name.startswith("_"):
                continue
            skills.append(path.stem)

        return sorted(skills)

    def load_skill(self, name: str) -> SkillHandle:
        """Load a skill by name from the skills directory.

        Args:
            name: Skill name (module name without .py)

        Returns:
            SkillHandle for the loaded skill

        Raises:
            FileNotFoundError: If skill module doesn't exist
            ImportError: If skill module can't be imported
        """
        # Sanitize skill name to prevent path traversal
        if "/" in name or "\\" in name or ".." in name:
            raise FileNotFoundError(f"Skill '{name}' not found")

        # Check if already loaded
        if name in self.skills_by_name:
            return self.skills_by_name[name]

        # Try loading from built-in skills first
        skill_path = self.skills_dir / f"{name}.py"

        if not skill_path.exists():
            raise FileNotFoundError(f"Skill '{name}' not found")

        # Load the module dynamically
        spec = importlib.util.spec_from_file_location(f"workflow_mcp.sdk.skills.{name}", skill_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load skill '{name}' from {skill_path}")

        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except SyntaxError as e:
            raise ImportError(f"Skill '{name}' has syntax errors: {e}")
        except Exception as e:
            raise ImportError(f"Skill '{name}' failed to load: {type(e).__name__}: {e}")

        # Verify the module has a run function
        if not hasattr(module, 'run'):
            raise ImportError(f"Skill module '{name}' must define a 'run' function")

        # Create handle and register
        handle = SkillHandle(name=name, module=module)
        self.handles[handle.handle_id] = handle
        self.skills_by_name[name] = handle

        return handle

    def get_handle(self, handle_id: str) -> Optional[SkillHandle]:
        """Get a loaded skill by its handle ID.

        Args:
            handle_id: The handle ID

        Returns:
            SkillHandle or None if not found
        """
        return self.handles.get(handle_id)

    def run_skill(self, handle_id: str, input_data: dict) -> dict:
        """Run a loaded skill by its handle ID.

        Args:
            handle_id: The handle ID
            input_data: Dictionary of input parameters

        Returns:
            Dictionary of output results

        Raises:
            KeyError: If handle_id doesn't exist
        """
        handle = self.handles.get(handle_id)
        if handle is None:
            raise KeyError(f"No skill loaded with handle ID '{handle_id}'")

        return handle.invoke(input_data)

    def list_skills(self) -> list[str]:
        """List all available skill names (both discovered and loaded).

        Returns:
            Sorted list of skill names
        """
        return self.discover_skills()


# Convenience functions for the global registry
def get_registry(skills_dir: Optional[str] = None) -> SkillRegistry:
    """Get the global skill registry instance."""
    return SkillRegistry.get_instance(skills_dir)


def load_skill(name: str, skills_dir: Optional[str] = None) -> SkillHandle:
    """Load a skill by name using the global registry.

    Args:
        name: Skill name
        skills_dir: Optional skills directory path

    Returns:
        SkillHandle for the loaded skill
    """
    registry = get_registry(skills_dir)
    return registry.load_skill(name)


def run_skill(handle_id: str, input_data: dict) -> dict:
    """Run a loaded skill by handle ID using the global registry.

    Args:
        handle_id: The handle ID
        input_data: Dictionary of input parameters

    Returns:
        Dictionary of output results
    """
    registry = get_registry()
    return registry.run_skill(handle_id, input_data)


def list_skills(skills_dir: Optional[str] = None) -> list[str]:
    """List all available skills using the global registry.

    Args:
        skills_dir: Optional skills directory path

    Returns:
        Sorted list of skill names
    """
    registry = get_registry(skills_dir)
    return registry.list_skills()
