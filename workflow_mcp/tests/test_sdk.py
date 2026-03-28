"""Tests for SDK integration - skill loading and execution."""

import pytest
import json
from workflow_mcp.sdk import (
    SkillHandle,
    SkillRegistry,
    get_registry,
    load_skill,
    run_skill,
    list_skills,
)


class TestSkillRegistry:
    """Tests for SkillRegistry class."""

    def test_discover_skills(self):
        """Test discovering available skills."""
        registry = SkillRegistry()
        skills = registry.discover_skills()

        # Should find at least the 3 built-in skills
        assert len(skills) >= 3
        assert "summarizer" in skills
        assert "translator" in skills
        assert "planner" in skills

    def test_list_skills(self):
        """Test listing available skills."""
        registry = SkillRegistry()
        skills = registry.list_skills()

        # Should return same as discover_skills
        assert len(skills) >= 3
        assert "summarizer" in skills
        assert "translator" in skills
        assert "planner" in skills

    def test_load_skill_summarizer(self):
        """Test loading the summarizer skill."""
        registry = SkillRegistry()
        handle = registry.load_skill("summarizer")

        assert isinstance(handle, SkillHandle)
        assert handle.name == "summarizer"
        assert handle.handle_id is not None
        assert len(handle.handle_id) == 8
        assert hasattr(handle.module, 'run')

    def test_load_skill_translator(self):
        """Test loading the translator skill."""
        registry = SkillRegistry()
        handle = registry.load_skill("translator")

        assert isinstance(handle, SkillHandle)
        assert handle.name == "translator"
        assert hasattr(handle.module, 'run')

    def test_load_skill_planner(self):
        """Test loading the planner skill."""
        registry = SkillRegistry()
        handle = registry.load_skill("planner")

        assert isinstance(handle, SkillHandle)
        assert handle.name == "planner"
        assert hasattr(handle.module, 'run')

    def test_load_skill_nonexistent(self):
        """Test loading a nonexistent skill."""
        registry = SkillRegistry()

        with pytest.raises(FileNotFoundError):
            registry.load_skill("nonexistent_skill")

    def test_load_skill_caching(self):
        """Test that loading the same skill twice returns the same handle."""
        registry = SkillRegistry()
        handle1 = registry.load_skill("summarizer")
        handle2 = registry.load_skill("summarizer")

        # Should return the same handle instance
        assert handle1 is handle2
        assert handle1.handle_id == handle2.handle_id

    def test_get_handle(self):
        """Test getting a handle by ID."""
        registry = SkillRegistry()
        handle = registry.load_skill("summarizer")

        retrieved = registry.get_handle(handle.handle_id)
        assert retrieved is handle

    def test_get_handle_nonexistent(self):
        """Test getting a nonexistent handle returns None."""
        registry = SkillRegistry()
        retrieved = registry.get_handle("invalid_id")
        assert retrieved is None

    def test_run_skill_by_handle_id(self):
        """Test running a skill by handle ID."""
        registry = SkillRegistry()
        handle = registry.load_skill("summarizer")

        input_data = {"text": "This is a test. This is only a test. Please remain calm."}
        result = registry.run_skill(handle.handle_id, input_data)

        assert isinstance(result, dict)
        assert "summary" in result
        assert "original_length" in result
        assert "summary_length" in result

    def test_run_skill_invalid_handle(self):
        """Test running a skill with invalid handle ID."""
        registry = SkillRegistry()

        with pytest.raises(KeyError):
            registry.run_skill("invalid_handle_id", {})


class TestSkillHandle:
    """Tests for SkillHandle class."""

    def test_skill_handle_invoke(self):
        """Test invoking a skill through its handle."""
        registry = SkillRegistry()
        handle = registry.load_skill("summarizer")

        input_data = {"text": "Test text for summarization."}
        result = handle.invoke(input_data)

        assert isinstance(result, dict)
        assert "summary" in result

    def test_skill_handle_repr(self):
        """Test string representation of SkillHandle."""
        registry = SkillRegistry()
        handle = registry.load_skill("summarizer")

        repr_str = repr(handle)
        assert "SkillHandle" in repr_str
        assert handle.handle_id in repr_str
        assert "summarizer" in repr_str


class TestSummarizerSkill:
    """Tests for the summarizer skill."""

    def test_summarizer_basic(self):
        """Test basic summarization."""
        registry = SkillRegistry()
        handle = registry.load_skill("summarizer")

        input_data = {
            "text": "This is the first sentence. This is the second sentence. This is the third sentence. This is the fourth sentence."
        }
        result = handle.invoke(input_data)

        assert "summary" in result
        assert "original_length" in result
        assert "summary_length" in result
        assert len(result["summary"]) > 0
        assert result["original_length"] > 0
        assert result["summary_length"] <= result["original_length"]

    def test_summarizer_empty_text(self):
        """Test summarizer with empty text."""
        registry = SkillRegistry()
        handle = registry.load_skill("summarizer")

        input_data = {"text": ""}
        result = handle.invoke(input_data)

        assert result["summary"] == ""
        assert result["original_length"] == 0
        assert result["summary_length"] == 0

    def test_summarizer_no_text_key(self):
        """Test summarizer with missing text key."""
        registry = SkillRegistry()
        handle = registry.load_skill("summarizer")

        input_data = {}
        result = handle.invoke(input_data)

        assert result["summary"] == ""
        assert result["original_length"] == 0


class TestTranslatorSkill:
    """Tests for the translator skill."""

    def test_translator_basic(self):
        """Test basic translation."""
        registry = SkillRegistry()
        handle = registry.load_skill("translator")

        input_data = {
            "text": "Hello, world!",
            "target_lang": "es"
        }
        result = handle.invoke(input_data)

        assert "translated_text" in result
        assert "source_lang" in result
        assert "target_lang" in result
        assert result["target_lang"] == "es"
        assert "Hello, world!" in result["translated_text"]

    def test_translator_default_target_lang(self):
        """Test translator with default target language."""
        registry = SkillRegistry()
        handle = registry.load_skill("translator")

        input_data = {"text": "Hello"}
        result = handle.invoke(input_data)

        assert result["target_lang"] == "es"  # Default is Spanish

    def test_translator_empty_text(self):
        """Test translator with empty text."""
        registry = SkillRegistry()
        handle = registry.load_skill("translator")

        input_data = {"text": ""}
        result = handle.invoke(input_data)

        assert result["translated_text"] == ""


class TestPlannerSkill:
    """Tests for the planner skill."""

    def test_planner_basic(self):
        """Test basic planning."""
        registry = SkillRegistry()
        handle = registry.load_skill("planner")

        input_data = {"goal": "Build a web application"}
        result = handle.invoke(input_data)

        assert "plan" in result
        assert "goal" in result
        assert "num_steps" in result
        assert isinstance(result["plan"], list)
        assert len(result["plan"]) == 4
        assert result["num_steps"] == 4
        assert result["goal"] == "Build a web application"

    def test_planner_text_fallback(self):
        """Test planner with 'text' key instead of 'goal'."""
        registry = SkillRegistry()
        handle = registry.load_skill("planner")

        input_data = {"text": "Learn Python"}
        result = handle.invoke(input_data)

        assert result["goal"] == "Learn Python"
        assert len(result["plan"]) == 4

    def test_planner_empty_goal(self):
        """Test planner with empty goal."""
        registry = SkillRegistry()
        handle = registry.load_skill("planner")

        input_data = {"goal": ""}
        result = handle.invoke(input_data)

        assert result["plan"] == []
        assert result["num_steps"] == 0


class TestGlobalRegistry:
    """Tests for global registry functions."""

    def test_get_registry_singleton(self):
        """Test that get_registry returns a singleton."""
        # Reset singleton for test
        SkillRegistry._instance = None

        reg1 = get_registry()
        reg2 = get_registry()

        assert reg1 is reg2

    def test_load_skill_global(self):
        """Test load_skill convenience function."""
        # Reset singleton
        SkillRegistry._instance = None

        handle = load_skill("summarizer")
        assert isinstance(handle, SkillHandle)
        assert handle.name == "summarizer"

    def test_run_skill_global(self):
        """Test run_skill convenience function."""
        # Reset singleton
        SkillRegistry._instance = None

        handle = load_skill("summarizer")
        result = run_skill(handle.handle_id, {"text": "Test text."})

        assert isinstance(result, dict)
        assert "summary" in result

    def test_list_skills_global(self):
        """Test list_skills convenience function."""
        # Reset singleton
        SkillRegistry._instance = None

        skills = list_skills()
        assert len(skills) >= 3
        assert "summarizer" in skills
        assert "translator" in skills
        assert "planner" in skills


class TestInputValidation:
    """Tests for input validation and security."""

    def test_summarizer_invalid_input_type(self):
        """Test summarizer with invalid input type (not a dict)."""
        registry = SkillRegistry()
        handle = registry.load_skill("summarizer")

        with pytest.raises(TypeError, match="Input must be a dictionary"):
            handle.invoke("not a dict")

    def test_summarizer_invalid_text_type(self):
        """Test summarizer with invalid text type."""
        registry = SkillRegistry()
        handle = registry.load_skill("summarizer")

        with pytest.raises(TypeError, match="Expected 'text' to be str"):
            handle.invoke({"text": 123})

    def test_summarizer_input_size_limit(self):
        """Test summarizer with input exceeding size limit."""
        registry = SkillRegistry()
        handle = registry.load_skill("summarizer")

        large_text = "a" * 1_000_001  # Exceed 1MB limit
        with pytest.raises(ValueError, match="Input too large"):
            handle.invoke({"text": large_text})

    def test_translator_invalid_input_type(self):
        """Test translator with invalid input type."""
        registry = SkillRegistry()
        handle = registry.load_skill("translator")

        with pytest.raises(TypeError, match="Input must be a dictionary"):
            handle.invoke(["not", "a", "dict"])

    def test_translator_invalid_text_type(self):
        """Test translator with invalid text type."""
        registry = SkillRegistry()
        handle = registry.load_skill("translator")

        with pytest.raises(TypeError, match="Expected 'text' to be str"):
            handle.invoke({"text": None})

    def test_translator_invalid_target_lang_type(self):
        """Test translator with invalid target_lang type."""
        registry = SkillRegistry()
        handle = registry.load_skill("translator")

        with pytest.raises(TypeError, match="Expected 'target_lang' to be str"):
            handle.invoke({"text": "hello", "target_lang": 123})

    def test_translator_input_size_limit(self):
        """Test translator with input exceeding size limit."""
        registry = SkillRegistry()
        handle = registry.load_skill("translator")

        large_text = "b" * 1_000_001
        with pytest.raises(ValueError, match="Input too large"):
            handle.invoke({"text": large_text})

    def test_planner_invalid_input_type(self):
        """Test planner with invalid input type."""
        registry = SkillRegistry()
        handle = registry.load_skill("planner")

        with pytest.raises(TypeError, match="Input must be a dictionary"):
            handle.invoke(42)

    def test_planner_invalid_goal_type(self):
        """Test planner with invalid goal type."""
        registry = SkillRegistry()
        handle = registry.load_skill("planner")

        with pytest.raises(TypeError, match="Expected 'goal' or 'text' to be str"):
            handle.invoke({"goal": ["list", "of", "goals"]})

    def test_planner_input_size_limit(self):
        """Test planner with input exceeding size limit."""
        registry = SkillRegistry()
        handle = registry.load_skill("planner")

        large_goal = "c" * 1_000_001
        with pytest.raises(ValueError, match="Input too large"):
            handle.invoke({"goal": large_goal})

    def test_path_traversal_attack(self):
        """Test that path traversal in skill names is prevented."""
        registry = SkillRegistry()

        # Try various path traversal patterns
        with pytest.raises(FileNotFoundError, match="Skill '../../etc/passwd' not found"):
            registry.load_skill("../../etc/passwd")

        with pytest.raises(FileNotFoundError, match="Skill '../loader' not found"):
            registry.load_skill("../loader")

        with pytest.raises(FileNotFoundError, match="Skill '/etc/hosts' not found"):
            registry.load_skill("/etc/hosts")

    def test_error_message_no_path_disclosure(self):
        """Test that error messages don't expose internal paths."""
        registry = SkillRegistry()

        try:
            registry.load_skill("nonexistent_skill")
        except FileNotFoundError as e:
            error_msg = str(e)
            # Should not contain directory path
            assert "nonexistent_skill" in error_msg
            assert "not found" in error_msg
            # Should not expose internal directory structure
            assert "/" not in error_msg or "skills/" not in error_msg
