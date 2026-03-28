"""Planner skill - task planning and step generation."""


def execute(input_data: dict) -> dict:
    """Execute planner skill.

    Args:
        input_data: Dictionary with 'text' key containing task description

    Returns:
        Dictionary with 'plan' key containing list of step strings

    Raises:
        ValueError: If input_data doesn't contain 'text' key
    """
    if 'text' not in input_data:
        raise ValueError("Input must contain 'text' key")

    text = input_data['text']

    # Split text into sentences and convert to actionable steps
    import re
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    # Generate plan steps
    plan = []
    for i, sentence in enumerate(sentences, 1):
        # Make sentence actionable (add verb if needed)
        step = _make_actionable(sentence)
        plan.append(f"Step {i}: {step}")

    # If no sentences found, create a single step
    if not plan:
        plan.append(f"Step 1: {text.strip()}")

    return {
        'plan': plan
    }


def _make_actionable(sentence: str) -> str:
    """Convert a sentence into an actionable step.

    Args:
        sentence: Input sentence

    Returns:
        Actionable step text
    """
    sentence = sentence.strip()

    # Action verbs that indicate it's already actionable
    action_verbs = [
        'create', 'build', 'develop', 'implement', 'design', 'test',
        'verify', 'validate', 'review', 'update', 'modify', 'add',
        'remove', 'delete', 'install', 'configure', 'setup', 'initialize',
        'deploy', 'run', 'execute', 'check', 'analyze', 'research',
        'write', 'read', 'prepare', 'plan', 'organize'
    ]

    # Check if sentence starts with an action verb
    first_word = sentence.split()[0].lower() if sentence else ''

    if first_word in action_verbs:
        # Already actionable, capitalize first letter
        return sentence[0].upper() + sentence[1:] if sentence else sentence

    # Not actionable, add a generic action verb
    if sentence:
        return f"Complete: {sentence[0].upper() + sentence[1:]}"
    else:
        return "Complete the task"
