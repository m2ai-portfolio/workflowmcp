"""Planner skill - creates action plans from goals."""

SKILL_NAME = "planner"
SKILL_DESCRIPTION = "Creates action plans from goals"

MAX_INPUT_SIZE = 1_000_000  # 1MB limit


def run(input_data: dict) -> dict:
    """Create an action plan from a goal.

    Args:
        input_data: Dictionary with:
            - goal: The goal to plan for (or 'text' as fallback)

    Returns:
        Dictionary with:
            - plan: List of action steps
            - goal: The original goal
            - num_steps: Number of steps in the plan
    """
    if not isinstance(input_data, dict):
        raise TypeError("Input must be a dictionary")

    goal = input_data.get("goal", input_data.get("text", ""))
    if not isinstance(goal, str):
        raise TypeError(f"Expected 'goal' or 'text' to be str, got {type(goal).__name__}")
    if len(goal) > MAX_INPUT_SIZE:
        raise ValueError(f"Input too large: {len(goal)} chars (max {MAX_INPUT_SIZE})")

    if not goal:
        return {
            "plan": [],
            "goal": "",
            "num_steps": 0
        }

    # Generate a simple 4-step plan
    steps = [
        f"Analyze: {goal}",
        f"Research: {goal}",
        f"Implement: {goal}",
        f"Review: {goal}"
    ]

    return {
        "plan": steps,
        "goal": goal,
        "num_steps": len(steps)
    }
