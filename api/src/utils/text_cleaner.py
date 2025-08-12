import re

import emoji


def remove_all_emojis(text: str) -> str:
    """Remove all emojis from text using the emoji library."""
    if not text:
        return text
    return emoji.replace_emoji(text, replace='')


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text by replacing multiple spaces/newlines with single space.
    
    Args:
        text: Input text to normalize
    
    Returns:
        Text with normalized whitespace
    """
    if not text:
        return text

    # Replace multiple spaces/newlines/tabs with single space
    normalized = re.sub(r'\s+', ' ', text)

    # Strip leading/trailing whitespace
    normalized = normalized.strip()

    return normalized


def normalize_text(text: str) -> str:
    """
    Generic text normalization function.
    
    Args:
        text: Input text to normalize
    
    Returns:
        Normalized text
    """
    if not text:
        return text

    # Normalize whitespace
    text = normalize_whitespace(text)

    # Remove excessive punctuation
    text = re.sub(r'[!]{2,}', '!', text)
    text = re.sub(r'[?]{2,}', '?', text)
    text = re.sub(r'[.]{3,}', '...', text)

    return text
