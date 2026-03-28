"""Tests for workflow parsing, validation, and visualization."""

import pytest
import tempfile
import yaml
from pathlib import Path

from workflow_mcp.core import (
    parse_workflow,
    validate_workflow,
    visualize_workflow,
    CycleDetectedError,
)
from workflow_mcp.models import WorkflowModel, StepModel


@pytest.fixture
def valid_workflow_yaml(tmp_path):
    """Create a valid workflow YAML file."""
    workflow = {
        "name": "test-workflow",
        "steps": [
            {"agent": "researcher", "tool": "web_search", "depends_on": []},
            {"agent": "summarizer", "tool": "text_summary", "depends_on": [0]},
            {"agent": "reviewer", "tool": "quality_check", "depends_on": [1]},
        ]
    }
    file_path = tmp_path / "valid_workflow.yaml"
    with open(file_path, "w") as f:
        yaml.dump(workflow, f)
    return str(file_path)


@pytest.fixture
def invalid_workflow_yaml(tmp_path):
    """Create an invalid workflow YAML file with bad dependency."""
    workflow = {
        "name": "bad-workflow",
        "steps": [
            {"agent": "researcher", "tool": "web_search", "depends_on": [5]},
        ]
    }
    file_path = tmp_path / "invalid_workflow.yaml"
    with open(file_path, "w") as f:
        yaml.dump(workflow, f)
    return str(file_path)


@pytest.fixture
def cyclic_workflow_yaml(tmp_path):
    """Create a workflow with a cycle."""
    workflow = {
        "name": "cyclic-workflow",
        "steps": [
            {"agent": "agent1", "depends_on": [1]},
            {"agent": "agent2", "depends_on": [0]},
        ]
    }
    file_path = tmp_path / "cyclic_workflow.yaml"
    with open(file_path, "w") as f:
        yaml.dump(workflow, f)
    return str(file_path)


def test_parse_valid_workflow(valid_workflow_yaml):
    """Test parsing a valid workflow produces correct DAG."""
    dag = parse_workflow(valid_workflow_yaml)

    assert dag["name"] == "test-workflow"
    assert "nodes" in dag
    assert "execution_order" in dag
    assert len(dag["nodes"]) == 3

    # Check step 0
    assert dag["nodes"][0]["agent"] == "researcher"
    assert dag["nodes"][0]["tool"] == "web_search"
    assert dag["nodes"][0]["depends_on"] == []
    assert dag["nodes"][0]["dependents"] == [1]

    # Check step 1
    assert dag["nodes"][1]["agent"] == "summarizer"
    assert dag["nodes"][1]["depends_on"] == [0]
    assert dag["nodes"][1]["dependents"] == [2]

    # Check execution order
    assert dag["execution_order"] == [0, 1, 2]


def test_parse_nonexistent_file():
    """Test parsing a nonexistent file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        parse_workflow("nonexistent.yaml")


def test_validate_valid_workflow(valid_workflow_yaml):
    """Test validating a valid workflow returns True."""
    is_valid, errors = validate_workflow(valid_workflow_yaml)
    assert is_valid is True
    assert errors == []


def test_validate_invalid_workflow(invalid_workflow_yaml):
    """Test validating an invalid workflow returns False with errors."""
    is_valid, errors = validate_workflow(invalid_workflow_yaml)
    assert is_valid is False
    assert len(errors) > 0
    assert any("invalid dependency reference" in err.lower() for err in errors)


def test_validate_cyclic_workflow(cyclic_workflow_yaml):
    """Test validating a cyclic workflow detects the cycle."""
    is_valid, errors = validate_workflow(cyclic_workflow_yaml)
    assert is_valid is False
    assert len(errors) > 0
    assert any("cycle" in err.lower() for err in errors)


def test_validate_missing_required_fields(tmp_path):
    """Test validation catches missing required fields."""
    workflow = {"name": "missing-steps"}
    file_path = tmp_path / "missing_fields.yaml"
    with open(file_path, "w") as f:
        yaml.dump(workflow, f)

    is_valid, errors = validate_workflow(str(file_path))
    assert is_valid is False
    assert any("steps" in err.lower() for err in errors)


def test_validate_empty_steps(tmp_path):
    """Test validation catches empty steps list."""
    workflow = {"name": "empty-steps", "steps": []}
    file_path = tmp_path / "empty_steps.yaml"
    with open(file_path, "w") as f:
        yaml.dump(workflow, f)

    is_valid, errors = validate_workflow(str(file_path))
    assert is_valid is False
    assert any("at least one step" in err.lower() for err in errors)


def test_validate_self_reference(tmp_path):
    """Test validation catches self-references."""
    workflow = {
        "name": "self-ref",
        "steps": [
            {"agent": "agent1", "depends_on": [0]},
            {"agent": "agent2", "depends_on": []},
        ]
    }
    file_path = tmp_path / "self_ref.yaml"
    with open(file_path, "w") as f:
        yaml.dump(workflow, f)

    is_valid, errors = validate_workflow(str(file_path))
    assert is_valid is False
    assert any("self-reference" in err.lower() for err in errors)


def test_visualize_workflow(valid_workflow_yaml):
    """Test visualization generates valid Mermaid diagram."""
    mermaid = visualize_workflow(valid_workflow_yaml)

    assert "graph TD" in mermaid
    assert "researcher" in mermaid
    assert "summarizer" in mermaid
    assert "reviewer" in mermaid
    assert "step0" in mermaid
    assert "step1" in mermaid
    assert "step2" in mermaid
    assert "-->" in mermaid


def test_workflow_model_from_dict():
    """Test WorkflowModel.from_dict creates correct model."""
    data = {
        "name": "test",
        "steps": [
            {"agent": "agent1", "tool": "tool1", "depends_on": []},
            {"agent": "agent2", "depends_on": [0]},
        ]
    }

    workflow = WorkflowModel.from_dict(data)
    assert workflow.name == "test"
    assert len(workflow.steps) == 2
    assert workflow.steps[0].agent == "agent1"
    assert workflow.steps[0].tool == "tool1"
    assert workflow.steps[1].agent == "agent2"
    assert workflow.steps[1].tool is None


def test_step_model_to_dict():
    """Test StepModel.to_dict converts correctly."""
    step = StepModel(agent="test_agent", tool="test_tool", depends_on=[0, 1])
    data = step.to_dict()

    assert data["agent"] == "test_agent"
    assert data["tool"] == "test_tool"
    assert data["depends_on"] == [0, 1]


def test_complex_dag(tmp_path):
    """Test parsing a more complex DAG with multiple dependencies."""
    workflow = {
        "name": "complex-workflow",
        "steps": [
            {"agent": "step0", "depends_on": []},
            {"agent": "step1", "depends_on": []},
            {"agent": "step2", "depends_on": [0, 1]},
            {"agent": "step3", "depends_on": [1]},
            {"agent": "step4", "depends_on": [2, 3]},
        ]
    }
    file_path = tmp_path / "complex_workflow.yaml"
    with open(file_path, "w") as f:
        yaml.dump(workflow, f)

    dag = parse_workflow(str(file_path))
    assert len(dag["nodes"]) == 5

    # Check dependencies are preserved
    assert dag["nodes"][2]["depends_on"] == [0, 1]
    assert dag["nodes"][4]["depends_on"] == [2, 3]

    # Verify execution order is valid
    exec_order = dag["execution_order"]
    assert exec_order.index(0) < exec_order.index(2)
    assert exec_order.index(1) < exec_order.index(2)
    assert exec_order.index(1) < exec_order.index(3)
    assert exec_order.index(2) < exec_order.index(4)
    assert exec_order.index(3) < exec_order.index(4)
