"""Pytest configuration and fixtures."""

import pytest
import tempfile
import os


@pytest.fixture
def valid_workflow_yaml():
    """Fixture providing a valid workflow YAML file."""
    content = """name: "Test Workflow"
steps:
  - agent: "agent1"
    tool: "tool1"
    depends_on: []

  - agent: "agent2"
    tool: "tool2"
    depends_on: [0]

  - agent: "agent3"
    depends_on: [0, 1]
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(content)
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def circular_workflow_yaml():
    """Fixture providing a workflow with circular dependency."""
    content = """name: "Circular Workflow"
steps:
  - agent: "agent1"
    depends_on: [2]

  - agent: "agent2"
    depends_on: [0]

  - agent: "agent3"
    depends_on: [1]
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(content)
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def invalid_reference_yaml():
    """Fixture providing a workflow with invalid step reference."""
    content = """name: "Invalid Reference"
steps:
  - agent: "agent1"
    depends_on: [99]

  - agent: "agent2"
    depends_on: [0]
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(content)
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)
