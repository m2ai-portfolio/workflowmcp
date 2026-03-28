"""Tests for workflow parsing, validation, and DAG generation."""

import pytest
import json
import tempfile
import os

from workflow_mcp.core import (
    parse_yaml,
    validate_workflow,
    generate_dag,
    generate_mermaid,
    WorkflowParseError,
)
from workflow_mcp.models import WorkflowModel, StepModel


class TestParsing:
    """Test workflow parsing."""

    def test_parse_valid_workflow(self, valid_workflow_yaml):
        """Test parsing a valid workflow file."""
        workflow = parse_yaml(valid_workflow_yaml)

        assert workflow.name == "Test Workflow"
        assert len(workflow.steps) == 3
        assert workflow.steps[0].agent == "agent1"
        assert workflow.steps[0].tool == "tool1"
        assert workflow.steps[1].depends_on == [0]
        assert workflow.steps[2].depends_on == [0, 1]

    def test_parse_missing_file(self):
        """Test parsing a non-existent file."""
        with pytest.raises(WorkflowParseError, match="File not found"):
            parse_yaml("/nonexistent/file.yaml")

    def test_parse_invalid_yaml(self):
        """Test parsing invalid YAML syntax."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("name: [invalid: yaml: syntax")
            temp_path = f.name

        try:
            with pytest.raises(WorkflowParseError, match="YAML parsing error"):
                parse_yaml(temp_path)
        finally:
            os.unlink(temp_path)

    def test_parse_missing_name(self):
        """Test parsing workflow without name."""
        content = """steps:
  - agent: "agent1"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            with pytest.raises(WorkflowParseError, match="must have a 'name'"):
                parse_yaml(temp_path)
        finally:
            os.unlink(temp_path)


class TestValidation:
    """Test workflow validation."""

    def test_validate_valid_workflow(self, valid_workflow_yaml):
        """Test validation of a valid workflow."""
        workflow = parse_yaml(valid_workflow_yaml)
        is_valid, errors = validate_workflow(workflow)

        assert is_valid
        assert len(errors) == 0

    def test_validate_circular_dependency(self, circular_workflow_yaml):
        """Test validation detects circular dependencies."""
        workflow = parse_yaml(circular_workflow_yaml)
        is_valid, errors = validate_workflow(workflow)

        assert not is_valid
        assert len(errors) > 0
        assert any("Circular dependency" in err or "Cannot depend on step" in err for err in errors)

    def test_validate_invalid_reference(self, invalid_reference_yaml):
        """Test validation detects invalid step references."""
        workflow = parse_yaml(invalid_reference_yaml)
        is_valid, errors = validate_workflow(workflow)

        assert not is_valid
        assert len(errors) > 0
        assert any("Invalid step reference" in err for err in errors)


class TestDAGGeneration:
    """Test DAG generation."""

    def test_generate_dag(self, valid_workflow_yaml):
        """Test generating a DAG from a workflow."""
        workflow = parse_yaml(valid_workflow_yaml)
        dag = generate_dag(workflow)

        assert "name" in dag
        assert "nodes" in dag
        assert "edges" in dag
        assert dag["name"] == "Test Workflow"
        assert len(dag["nodes"]) == 3
        assert len(dag["edges"]) == 3  # edges: 0->1, 0->2, 1->2

        # Check nodes
        assert dag["nodes"][0]["agent"] == "agent1"
        assert dag["nodes"][0]["tool"] == "tool1"

        # Check edges
        edges = dag["edges"]
        assert {"from": 0, "to": 1} in edges
        assert {"from": 0, "to": 2} in edges
        assert {"from": 1, "to": 2} in edges

    def test_generate_dag_json_serializable(self, valid_workflow_yaml):
        """Test that DAG can be serialized to JSON."""
        workflow = parse_yaml(valid_workflow_yaml)
        dag = generate_dag(workflow)

        # Should not raise
        json_str = json.dumps(dag)
        assert json_str is not None


class TestVisualization:
    """Test Mermaid diagram generation."""

    def test_generate_mermaid(self, valid_workflow_yaml):
        """Test generating a Mermaid diagram."""
        workflow = parse_yaml(valid_workflow_yaml)
        mermaid = generate_mermaid(workflow)

        assert "graph TD" in mermaid
        assert "agent1" in mermaid
        assert "agent2" in mermaid
        assert "agent3" in mermaid
        assert "-->" in mermaid

    def test_mermaid_includes_tools(self, valid_workflow_yaml):
        """Test that Mermaid diagram includes tool names."""
        workflow = parse_yaml(valid_workflow_yaml)
        mermaid = generate_mermaid(workflow)

        assert "tool1" in mermaid
        assert "tool2" in mermaid


class TestModels:
    """Test data models."""

    def test_step_model_creation(self):
        """Test creating a StepModel."""
        step = StepModel(agent="test_agent", tool="test_tool", depends_on=[0, 1])

        assert step.agent == "test_agent"
        assert step.tool == "test_tool"
        assert step.depends_on == [0, 1]

    def test_step_model_defaults(self):
        """Test StepModel default values."""
        step = StepModel(agent="test_agent")

        assert step.agent == "test_agent"
        assert step.tool is None
        assert step.depends_on == []

    def test_workflow_model_creation(self):
        """Test creating a WorkflowModel."""
        steps = [
            StepModel(agent="agent1"),
            StepModel(agent="agent2", depends_on=[0])
        ]
        workflow = WorkflowModel(name="test", steps=steps)

        assert workflow.name == "test"
        assert len(workflow.steps) == 2

    def test_step_validation_empty_agent(self):
        """Test that StepModel validates agent name."""
        with pytest.raises(ValueError, match="must have an agent"):
            StepModel(agent="")
