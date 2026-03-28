"""Tests for Copilot SDK functionality."""

import pytest
import json

from workflow_mcp.sdk import load_skill, run_skill, list_skills, SkillHandle
from workflow_mcp.sdk.loader import clear_skill_cache
from workflow_mcp.models import AgentModel


class TestSkillLoading:
    """Test skill loading functionality."""

    def setup_method(self):
        """Clear skill cache before each test."""
        clear_skill_cache()

    def test_load_summarizer_skill(self):
        """Test loading the summarizer skill."""
        handle = load_skill('summarizer')

        assert isinstance(handle, SkillHandle)
        assert handle.name == 'summarizer'
        assert hasattr(handle.module, 'execute')
        assert handle.config == {}

    def test_load_translator_skill(self):
        """Test loading the translator skill."""
        handle = load_skill('translator')

        assert isinstance(handle, SkillHandle)
        assert handle.name == 'translator'
        assert hasattr(handle.module, 'execute')

    def test_load_planner_skill(self):
        """Test loading the planner skill."""
        handle = load_skill('planner')

        assert isinstance(handle, SkillHandle)
        assert handle.name == 'planner'
        assert hasattr(handle.module, 'execute')

    def test_load_skill_with_config(self):
        """Test loading a skill with custom config."""
        config = {'mode': 'upper'}
        handle = load_skill('translator', config)

        assert handle.config == config

    def test_load_nonexistent_skill(self):
        """Test loading a skill that doesn't exist."""
        with pytest.raises(ValueError, match="Skill 'nonexistent' not found"):
            load_skill('nonexistent')

    def test_skill_caching(self):
        """Test that skills are cached after first load."""
        handle1 = load_skill('summarizer')
        handle2 = load_skill('summarizer')

        # Should be the same object (cached)
        assert handle1 is handle2


class TestSkillExecution:
    """Test skill execution functionality."""

    def setup_method(self):
        """Clear skill cache before each test."""
        clear_skill_cache()

    def test_run_summarizer(self):
        """Test executing summarizer skill."""
        handle = load_skill('summarizer')
        input_data = {
            'text': 'This is a long article about technology. It contains many sentences. Each sentence has valuable information. We want to summarize this text. The summary should be shorter.'
        }

        result = run_skill(handle, input_data)

        assert 'summary' in result
        assert 'word_count' in result
        assert isinstance(result['summary'], str)
        assert isinstance(result['word_count'], int)
        assert len(result['summary']) < len(input_data['text'])

    def test_run_translator_upper(self):
        """Test executing translator skill with upper mode."""
        handle = load_skill('translator')
        input_data = {
            'text': 'hello world',
            'mode': 'upper'
        }

        result = run_skill(handle, input_data)

        assert 'translated' in result
        assert result['translated'] == 'HELLO WORLD'

    def test_run_translator_reverse(self):
        """Test executing translator skill with reverse mode."""
        handle = load_skill('translator')
        input_data = {
            'text': 'hello',
            'mode': 'reverse'
        }

        result = run_skill(handle, input_data)

        assert 'translated' in result
        assert result['translated'] == 'olleh'

    def test_run_translator_pig_latin(self):
        """Test executing translator skill with pig latin mode."""
        handle = load_skill('translator')
        input_data = {
            'text': 'hello world',
            'mode': 'pig_latin'
        }

        result = run_skill(handle, input_data)

        assert 'translated' in result
        assert 'way' in result['translated'] or 'ay' in result['translated']

    def test_run_planner(self):
        """Test executing planner skill."""
        handle = load_skill('planner')
        input_data = {
            'text': 'Create a new feature. Test the feature. Deploy to production.'
        }

        result = run_skill(handle, input_data)

        assert 'plan' in result
        assert isinstance(result['plan'], list)
        assert len(result['plan']) >= 1
        # Check that steps are numbered
        assert all('Step' in step for step in result['plan'])

    def test_run_skill_invalid_input(self):
        """Test running skill with invalid input."""
        handle = load_skill('summarizer')

        with pytest.raises(ValueError, match="Input data must be a dictionary"):
            run_skill(handle, "not a dict")

    def test_run_skill_missing_required_field(self):
        """Test running skill with missing required field."""
        handle = load_skill('summarizer')
        input_data = {'wrong_key': 'value'}

        with pytest.raises(ValueError, match="must contain 'text'"):
            run_skill(handle, input_data)


class TestListSkills:
    """Test listing available skills."""

    def test_list_skills(self):
        """Test listing all available skills."""
        skills = list_skills()

        assert isinstance(skills, list)
        assert 'summarizer' in skills
        assert 'translator' in skills
        assert 'planner' in skills
        assert len(skills) >= 3

    def test_list_skills_returns_sorted(self):
        """Test that list_skills returns sorted results."""
        skills = list_skills()

        assert skills == sorted(skills)


class TestSkillModules:
    """Test individual skill modules."""

    def test_summarizer_truncates_to_50_words(self):
        """Test that summarizer truncates to 50 words."""
        handle = load_skill('summarizer')

        # Create text with more than 50 words
        words = ['word'] * 100
        long_text = ' '.join(words)

        result = run_skill(handle, {'text': long_text})

        assert result['word_count'] <= 50

    def test_summarizer_truncates_to_3_sentences(self):
        """Test that summarizer truncates to 3 sentences."""
        handle = load_skill('summarizer')

        # Create text with more than 3 sentences
        text = 'First sentence. Second sentence. Third sentence. Fourth sentence. Fifth sentence.'

        result = run_skill(handle, {'text': text})

        # Should have at most 3 sentence endings
        summary = result['summary']
        sentence_count = summary.count('.') + summary.count('!') + summary.count('?')
        assert sentence_count <= 4  # 3 sentences + potential period at end

    def test_translator_invalid_mode(self):
        """Test translator with invalid mode."""
        handle = load_skill('translator')

        with pytest.raises(ValueError, match="Invalid mode"):
            run_skill(handle, {'text': 'hello', 'mode': 'invalid'})

    def test_planner_empty_text(self):
        """Test planner with empty text."""
        handle = load_skill('planner')

        result = run_skill(handle, {'text': ''})

        assert 'plan' in result
        assert len(result['plan']) >= 1

    def test_planner_single_sentence(self):
        """Test planner with single sentence."""
        handle = load_skill('planner')

        result = run_skill(handle, {'text': 'Build a new feature.'})

        assert 'plan' in result
        assert len(result['plan']) >= 1
        assert 'Step 1' in result['plan'][0]


class TestAgentModel:
    """Test AgentModel dataclass."""

    def test_agent_model_creation(self):
        """Test creating an AgentModel."""
        agent = AgentModel(
            name='test_agent',
            skill_path='summarizer',
            config={'mode': 'test'}
        )

        assert agent.name == 'test_agent'
        assert agent.skill_path == 'summarizer'
        assert agent.config == {'mode': 'test'}

    def test_agent_model_defaults(self):
        """Test AgentModel default values."""
        agent = AgentModel(name='test', skill_path='summarizer')

        assert agent.config == {}

    def test_agent_model_validation_empty_name(self):
        """Test that AgentModel validates name."""
        with pytest.raises(ValueError, match="must have a name"):
            AgentModel(name='', skill_path='summarizer')

    def test_agent_model_validation_empty_skill_path(self):
        """Test that AgentModel validates skill_path."""
        with pytest.raises(ValueError, match="must have a skill_path"):
            AgentModel(name='test', skill_path='')

    def test_agent_model_validation_invalid_config(self):
        """Test that AgentModel validates config type."""
        with pytest.raises(ValueError, match="config must be a dictionary"):
            AgentModel(name='test', skill_path='summarizer', config='invalid')


class TestIntegration:
    """Integration tests for SDK."""

    def setup_method(self):
        """Clear skill cache before each test."""
        clear_skill_cache()

    def test_end_to_end_workflow(self):
        """Test complete workflow: load, execute, verify."""
        # List available skills
        skills = list_skills()
        assert 'summarizer' in skills

        # Load skill
        handle = load_skill('summarizer')
        assert handle.name == 'summarizer'

        # Execute skill
        input_data = {'text': 'This is a test document. It has multiple sentences. We will summarize it.'}
        result = run_skill(handle, input_data)

        # Verify result
        assert 'summary' in result
        assert 'word_count' in result
        assert isinstance(result['summary'], str)

    def test_multiple_skills_execution(self):
        """Test executing multiple different skills."""
        # Execute summarizer
        summarizer_handle = load_skill('summarizer')
        summary_result = run_skill(summarizer_handle, {
            'text': 'Long article with many words and sentences.'
        })
        assert 'summary' in summary_result

        # Execute translator
        translator_handle = load_skill('translator')
        translator_result = run_skill(translator_handle, {
            'text': 'hello',
            'mode': 'upper'
        })
        assert translator_result['translated'] == 'HELLO'

        # Execute planner
        planner_handle = load_skill('planner')
        planner_result = run_skill(planner_handle, {
            'text': 'Implement feature. Test feature.'
        })
        assert len(planner_result['plan']) >= 1
