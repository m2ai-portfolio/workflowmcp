"""Summarizer skill - summarizes text input."""

import re

SKILL_NAME = "summarizer"
SKILL_DESCRIPTION = "Summarizes text content"

MAX_INPUT_SIZE = 1_000_000  # 1MB limit


def run(input_data: dict) -> dict:
    """Summarize text input using simple extractive summarization.

    Args:
        input_data: Dictionary with 'text' key containing the text to summarize

    Returns:
        Dictionary with:
            - summary: Extracted summary (first 3 sentences)
            - original_length: Length of original text
            - summary_length: Length of summary
    """
    if not isinstance(input_data, dict):
        raise TypeError("Input must be a dictionary")

    text = input_data.get("text", "")
    if not isinstance(text, str):
        raise TypeError(f"Expected 'text' to be str, got {type(text).__name__}")
    if len(text) > MAX_INPUT_SIZE:
        raise ValueError(f"Input too large: {len(text)} chars (max {MAX_INPUT_SIZE})")

    if not text:
        return {
            "summary": "",
            "original_length": 0,
            "summary_length": 0
        }

    # Simple extractive summary: first few sentences
    # Split on sentence-ending punctuation followed by whitespace
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    # Filter out empty strings
    sentences = [s for s in sentences if s]

    # Take first 3 sentences
    summary_sentences = sentences[:3]
    summary = " ".join(summary_sentences)

    # Ensure summary ends with period if it doesn't
    if summary and not summary.endswith('.'):
        summary += '.'

    return {
        "summary": summary,
        "original_length": len(text),
        "summary_length": len(summary)
    }
