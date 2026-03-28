"""Translator skill - translates text (simulated)."""

SKILL_NAME = "translator"
SKILL_DESCRIPTION = "Translates text between languages"

MAX_INPUT_SIZE = 1_000_000  # 1MB limit


def run(input_data: dict) -> dict:
    """Translate text from one language to another (simulated).

    Args:
        input_data: Dictionary with:
            - text: The text to translate
            - target_lang: Target language code (default: 'es')
            - source_lang: Source language code (optional, default: 'en')

    Returns:
        Dictionary with:
            - translated_text: The translated text (simulated with language tag)
            - source_lang: Detected or provided source language
            - target_lang: Target language
    """
    if not isinstance(input_data, dict):
        raise TypeError("Input must be a dictionary")

    text = input_data.get("text", "")
    if not isinstance(text, str):
        raise TypeError(f"Expected 'text' to be str, got {type(text).__name__}")
    if len(text) > MAX_INPUT_SIZE:
        raise ValueError(f"Input too large: {len(text)} chars (max {MAX_INPUT_SIZE})")

    target_lang = input_data.get("target_lang", "es")
    if not isinstance(target_lang, str):
        raise TypeError(f"Expected 'target_lang' to be str, got {type(target_lang).__name__}")

    source_lang = input_data.get("source_lang", "en")

    if not text:
        return {
            "translated_text": "",
            "source_lang": source_lang,
            "target_lang": target_lang
        }

    # Simulated translation - prefix with language tag
    # In a real implementation, this would call a translation API
    translated_text = f"[{target_lang}] {text}"

    return {
        "translated_text": translated_text,
        "source_lang": source_lang,
        "target_lang": target_lang
    }
