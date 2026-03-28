"""Summarizer skill - simple text summarization."""


def execute(input_data: dict) -> dict:
    """Execute summarizer skill.

    Args:
        input_data: Dictionary with 'text' key containing text to summarize

    Returns:
        Dictionary with 'summary' and 'word_count' keys

    Raises:
        ValueError: If input_data doesn't contain 'text' key
    """
    if 'text' not in input_data:
        raise ValueError("Input must contain 'text' key")

    text = input_data['text']

    # Split into sentences (simple split on ., !, ?)
    import re
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    # Split into words
    words = text.split()

    # Truncate to first 50 words or 3 sentences, whichever is shorter
    summary_sentences = sentences[:3]
    summary_text = '. '.join(summary_sentences)

    # Also apply word limit
    summary_words = summary_text.split()[:50]
    final_summary = ' '.join(summary_words)

    # Add period if needed
    if final_summary and not final_summary.endswith(('.', '!', '?')):
        final_summary += '.'

    return {
        'summary': final_summary,
        'word_count': len(summary_words)
    }
