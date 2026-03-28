"""Core workflow parsing, validation, and DAG generation."""

import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Any, Set
from collections import deque

from .models import WorkflowModel


class CycleDetectedError(Exception):
    """Raised when a cycle is detected in the workflow DAG."""
    pass


def parse_workflow(yaml_path: str) -> Dict[str, Any]:
    """
    Parse a YAML workflow file and return a JSON-serializable DAG representation.

    Args:
        yaml_path: Path to the YAML workflow file

    Returns:
        Dictionary containing the workflow DAG

    Raises:
        FileNotFoundError: If the YAML file doesn't exist
        yaml.YAMLError: If the YAML is malformed
        ValueError: If the workflow structure is invalid
    """
    path = Path(yaml_path)
    if not path.exists():
        raise FileNotFoundError(f"Workflow file not found: {yaml_path}")

    with open(path, 'r') as f:
        data = yaml.safe_load(f)

    if not data:
        raise ValueError("Empty workflow file")

    # Parse into WorkflowModel
    workflow = WorkflowModel.from_dict(data)

    # Generate DAG structure
    dag = _build_dag(workflow)

    return dag


def validate_workflow(yaml_path: str) -> Tuple[bool, List[str]]:
    """
    Validate a YAML workflow file.

    Args:
        yaml_path: Path to the YAML workflow file

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    try:
        path = Path(yaml_path)
        if not path.exists():
            errors.append(f"File not found: {yaml_path}")
            return False, errors

        with open(path, 'r') as f:
            data = yaml.safe_load(f)

        if not data:
            errors.append("Empty workflow file")
            return False, errors

        # Check required fields
        if "name" not in data:
            errors.append("Missing required field: name")

        if "steps" not in data:
            errors.append("Missing required field: steps")
            return False, errors

        steps = data["steps"]
        if not isinstance(steps, list):
            errors.append("Field 'steps' must be a list")
            return False, errors

        if len(steps) == 0:
            errors.append("Workflow must have at least one step")
            return False, errors

        # Validate each step
        for i, step in enumerate(steps):
            if not isinstance(step, dict):
                errors.append(f"Step {i} must be a dictionary")
                continue

            if "agent" not in step:
                errors.append(f"Step {i} missing required field: agent")

            # Validate depends_on references
            if "depends_on" in step:
                depends_on = step["depends_on"]
                if not isinstance(depends_on, list):
                    errors.append(f"Step {i} 'depends_on' must be a list")
                else:
                    for dep in depends_on:
                        if not isinstance(dep, int):
                            errors.append(f"Step {i} dependency must be an integer, got: {dep}")
                        elif dep < 0 or dep >= len(steps):
                            errors.append(f"Step {i} has invalid dependency reference: {dep} (valid range: 0-{len(steps)-1})")
                        elif dep == i:
                            errors.append(f"Step {i} cannot depend on itself (self-reference)")

        if errors:
            return False, errors

        # Check for cycles
        workflow = WorkflowModel.from_dict(data)
        try:
            _detect_cycles(workflow)
        except CycleDetectedError as e:
            errors.append(str(e))
            return False, errors

        return True, []

    except yaml.YAMLError as e:
        errors.append(f"YAML parsing error: {str(e)}")
        return False, errors
    except Exception as e:
        errors.append(f"Validation error: {str(e)}")
        return False, errors


def visualize_workflow(yaml_path: str) -> str:
    """
    Generate a Mermaid diagram representation of the workflow.

    Args:
        yaml_path: Path to the YAML workflow file

    Returns:
        Mermaid diagram as a string
    """
    path = Path(yaml_path)
    with open(path, 'r') as f:
        data = yaml.safe_load(f)

    workflow = WorkflowModel.from_dict(data)

    # Generate Mermaid diagram
    lines = ["graph TD"]

    # Add nodes
    for i, step in enumerate(workflow.steps):
        label = f"{step.agent}"
        if step.tool:
            label += f"<br/>{step.tool}"
        lines.append(f"    step{i}[\"{label}\"]")

    # Add edges based on dependencies
    for i, step in enumerate(workflow.steps):
        if step.depends_on:
            for dep in step.depends_on:
                lines.append(f"    step{dep} --> step{i}")
        else:
            # If no dependencies, it's a root node - add start marker
            if i == 0 or not any(i in s.depends_on for s in workflow.steps):
                lines.append(f"    start([Start]) --> step{i}")

    return "\n".join(lines)


def _build_dag(workflow: WorkflowModel) -> Dict[str, Any]:
    """
    Build a DAG representation from a workflow model.

    Args:
        workflow: The workflow model

    Returns:
        Dictionary representing the DAG
    """
    # Check for cycles first
    _detect_cycles(workflow)

    # Build adjacency list
    adjacency_list = {}
    for i, step in enumerate(workflow.steps):
        adjacency_list[i] = {
            "agent": step.agent,
            "tool": step.tool,
            "depends_on": step.depends_on,
            "dependents": []
        }

    # Add dependent information
    for i, step in enumerate(workflow.steps):
        for dep in step.depends_on:
            adjacency_list[dep]["dependents"].append(i)

    return {
        "name": workflow.name,
        "nodes": adjacency_list,
        "execution_order": _topological_sort(workflow)
    }


def _detect_cycles(workflow: WorkflowModel) -> None:
    """
    Detect cycles in the workflow DAG using DFS.

    Args:
        workflow: The workflow model

    Raises:
        CycleDetectedError: If a cycle is detected
    """
    n = len(workflow.steps)
    visited = [False] * n
    rec_stack = [False] * n

    def dfs(node: int, path: List[int]) -> bool:
        visited[node] = True
        rec_stack[node] = True
        path.append(node)

        for i, step in enumerate(workflow.steps):
            if node in step.depends_on:
                if not visited[i]:
                    if dfs(i, path):
                        return True
                elif rec_stack[i]:
                    # Found a cycle
                    cycle_start = path.index(i)
                    cycle = path[cycle_start:] + [i]
                    raise CycleDetectedError(f"Cycle detected: {' -> '.join(map(str, cycle))}")

        path.pop()
        rec_stack[node] = False
        return False

    for i in range(n):
        if not visited[i]:
            dfs(i, [])


def _topological_sort(workflow: WorkflowModel) -> List[int]:
    """
    Perform topological sort on the workflow DAG.

    Args:
        workflow: The workflow model

    Returns:
        List of step indices in execution order
    """
    n = len(workflow.steps)
    in_degree = [0] * n

    # Calculate in-degrees - a step's in-degree is how many steps it depends on
    for i, step in enumerate(workflow.steps):
        in_degree[i] = len(step.depends_on)

    # Find all nodes with in-degree 0 (no dependencies)
    queue = deque([i for i in range(n) if in_degree[i] == 0])
    result = []

    while queue:
        node = queue.popleft()
        result.append(node)

        # For each step that depends on this node, decrement its in-degree
        for i, step in enumerate(workflow.steps):
            if node in step.depends_on:
                in_degree[i] -= 1
                if in_degree[i] == 0:
                    queue.append(i)

    return result
