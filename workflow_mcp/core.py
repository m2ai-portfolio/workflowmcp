"""Core workflow parsing, validation, and DAG generation."""

import json
from typing import Dict, List, Any, Tuple
import yaml

from workflow_mcp.models import WorkflowModel, StepModel


class WorkflowParseError(Exception):
    """Raised when workflow parsing fails."""
    pass


class WorkflowValidationError(Exception):
    """Raised when workflow validation fails."""
    pass


def parse_yaml(file_path: str) -> WorkflowModel:
    """Parse a YAML workflow file into a WorkflowModel.

    Args:
        file_path: Path to the YAML workflow file

    Returns:
        WorkflowModel instance

    Raises:
        WorkflowParseError: If parsing fails
    """
    try:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise WorkflowParseError("Workflow file must contain a YAML object")

        name = data.get('name')
        if not name:
            raise WorkflowParseError("Workflow must have a 'name' field")

        steps_data = data.get('steps', [])
        if not isinstance(steps_data, list):
            raise WorkflowParseError("Workflow 'steps' must be a list")

        steps = []
        for i, step_data in enumerate(steps_data):
            if not isinstance(step_data, dict):
                raise WorkflowParseError(f"Step {i} must be an object")

            agent = step_data.get('agent')
            if not agent:
                raise WorkflowParseError(f"Step {i} must have an 'agent' field")

            tool = step_data.get('tool')
            depends_on = step_data.get('depends_on', [])

            if not isinstance(depends_on, list):
                raise WorkflowParseError(f"Step {i} 'depends_on' must be a list")

            steps.append(StepModel(
                agent=agent,
                tool=tool,
                depends_on=depends_on
            ))

        return WorkflowModel(name=name, steps=steps)

    except FileNotFoundError:
        raise WorkflowParseError(f"File not found: {file_path}")
    except yaml.YAMLError as e:
        raise WorkflowParseError(f"YAML parsing error: {e}")
    except ValueError as e:
        raise WorkflowParseError(f"Invalid workflow data: {e}")


def validate_workflow(workflow: WorkflowModel) -> Tuple[bool, List[str]]:
    """Validate a workflow for correctness.

    Checks:
    - Step indices in depends_on are valid
    - No circular dependencies (DAG property)
    - All referenced steps exist

    Args:
        workflow: WorkflowModel to validate

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    num_steps = len(workflow.steps)

    # Check for valid step indices
    for i, step in enumerate(workflow.steps):
        for dep in step.depends_on:
            if dep < 0 or dep >= num_steps:
                errors.append(f"Step {i}: Invalid step reference {dep}")
            if dep >= i:
                errors.append(f"Step {i}: Cannot depend on step {dep} (must depend on earlier steps)")

    # Check for circular dependencies using topological sort
    if not errors:
        try:
            _topological_sort(workflow)
        except WorkflowValidationError as e:
            errors.append(str(e))

    return len(errors) == 0, errors


def _topological_sort(workflow: WorkflowModel) -> List[int]:
    """Perform topological sort to detect cycles.

    Args:
        workflow: WorkflowModel to sort

    Returns:
        List of step indices in topological order

    Raises:
        WorkflowValidationError: If a cycle is detected
    """
    num_steps = len(workflow.steps)
    in_degree = [0] * num_steps
    adj_list = [[] for _ in range(num_steps)]

    # Build adjacency list and in-degree counts
    for i, step in enumerate(workflow.steps):
        for dep in step.depends_on:
            adj_list[dep].append(i)
            in_degree[i] += 1

    # Start with nodes that have no dependencies
    queue = [i for i in range(num_steps) if in_degree[i] == 0]
    sorted_order = []

    while queue:
        node = queue.pop(0)
        sorted_order.append(node)

        for neighbor in adj_list[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(sorted_order) != num_steps:
        raise WorkflowValidationError("Circular dependency detected in workflow")

    return sorted_order


def generate_dag(workflow: WorkflowModel) -> Dict[str, Any]:
    """Generate a JSON DAG representation of the workflow.

    Args:
        workflow: WorkflowModel to convert to DAG

    Returns:
        Dictionary with 'nodes' and 'edges' keys
    """
    nodes = []
    edges = []

    for i, step in enumerate(workflow.steps):
        nodes.append({
            "id": i,
            "agent": step.agent,
            "tool": step.tool
        })

        for dep in step.depends_on:
            edges.append({
                "from": dep,
                "to": i
            })

    return {
        "name": workflow.name,
        "nodes": nodes,
        "edges": edges
    }


def generate_mermaid(workflow: WorkflowModel) -> str:
    """Generate a Mermaid diagram representation of the workflow.

    Args:
        workflow: WorkflowModel to visualize

    Returns:
        Mermaid diagram as a string
    """
    lines = ["graph TD"]

    for i, step in enumerate(workflow.steps):
        label = step.agent
        if step.tool:
            label += f"\\n[{step.tool}]"
        lines.append(f"    {i}[\"{label}\"]")

    for i, step in enumerate(workflow.steps):
        for dep in step.depends_on:
            lines.append(f"    {dep} --> {i}")

    return "\n".join(lines)
