"""Tests for agent model."""

import pytest
from workflow_mcp.models import AgentModel


def test_agent_model_from_dict():
    """Test AgentModel.from_dict creates correct model."""
    data = {
        "name": "test_agent",
        "skill_path": "/path/to/skill",
        "config": {"key": "value"}
    }

    agent = AgentModel.from_dict(data)
    assert agent.name == "test_agent"
    assert agent.skill_path == "/path/to/skill"
    assert agent.config == {"key": "value"}


def test_agent_model_to_dict():
    """Test AgentModel.to_dict converts correctly."""
    agent = AgentModel(
        name="test_agent",
        skill_path="/path/to/skill",
        config={"key": "value"}
    )
    data = agent.to_dict()

    assert data["name"] == "test_agent"
    assert data["skill_path"] == "/path/to/skill"
    assert data["config"] == {"key": "value"}


def test_agent_model_default_config():
    """Test AgentModel with default empty config."""
    agent = AgentModel(name="test", skill_path="/path")
    assert agent.config == {}
