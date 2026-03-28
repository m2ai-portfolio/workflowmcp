"""Translator skill - simple text transformations."""


def execute(input_data: dict) -> dict:
    """Execute translator skill.

    Args:
        input_data: Dictionary with 'text' and optional 'mode' keys
                   mode can be 'upper', 'reverse', or 'pig_latin' (default: 'upper')

    Returns:
        Dictionary with 'translated' key containing transformed text

    Raises:
        ValueError: If input_data doesn't contain 'text' key or mode is invalid
    """
    if 'text' not in input_data:
        raise ValueError("Input must contain 'text' key")

    text = input_data['text']
    mode = input_data.get('mode', 'upper')

    if mode == 'upper':
        result = text.upper()
    elif mode == 'reverse':
        result = text[::-1]
    elif mode == 'pig_latin':
        result = _to_pig_latin(text)
    else:
        raise ValueError(f"Invalid mode: {mode}. Must be 'upper', 'reverse', or 'pig_latin'")

    return {
        'translated': result
    }


def _to_pig_latin(text: str) -> str:
    """Convert text to pig latin.

    Simple implementation:
    - Words starting with consonants: move first letter to end and add 'ay'
    - Words starting with vowels: add 'way' to end
    """
    vowels = 'aeiouAEIOU'
    words = text.split()
    pig_latin_words = []

    for word in words:
        # Preserve non-alphabetic characters
        if not word or not word[0].isalpha():
            pig_latin_words.append(word)
            continue

        # Check if starts with vowel
        if word[0] in vowels:
            pig_latin_words.append(word + 'way')
        else:
            # Find first vowel position
            first_vowel = 0
            for i, char in enumerate(word):
                if char in vowels:
                    first_vowel = i
                    break
            else:
                # No vowels found, just add 'ay'
                pig_latin_words.append(word + 'ay')
                continue

            # Move consonant cluster to end
            if first_vowel > 0:
                pig_latin_words.append(word[first_vowel:] + word[:first_vowel] + 'ay')
            else:
                pig_latin_words.append(word + 'way')

    return ' '.join(pig_latin_words)
