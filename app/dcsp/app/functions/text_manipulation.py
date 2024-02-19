"""Module for text manipulation functions.

This module contains functions for manipulating text.

functions:
    snake_to_sentense(snake_text: str) -> str: snake to title conversion
    kebab_to_sentense(kebab_text: str) -> str: kebab to title conversion
    list_to_string(list_to_convert: list[str]) -> str: list to string conversion
"""


def snake_to_sentense(snake_text: str) -> str:
    """Convert snake case text to title case text.

    Convert snake case text to title case text. The first letter of the first
    word is capitalized and the rest of the words are in lower case.

    Args:
        snake_text (str): The snake case text to convert to title case.

    Returns:
        str: The title case text.
    """
    if snake_text.startswith("_"):
        snake_text = snake_text[1:]

    snake_text = snake_text.replace("__", "_")
    words = snake_text.split("_")
    title_text = " ".join(words).capitalize()
    title_text = title_text.strip()
    return title_text


def kebab_to_sentense(kebab_text: str) -> str:
    """Convert kebab case text to title case text.

    Convert kebab case text to title case text. The first letter of the first
    word is capitalized and the rest of the words are in lower case.

    Args:
        kebab_text (str): The kebab case text to convert to title case.

    Returns:
        str: The title case text.
    """
    if kebab_text.startswith("-"):
        kebab_text = kebab_text[1:]

    kebab_text = kebab_text.replace("--", "-")

    words = kebab_text.split("-")
    title_text = " ".join(words).capitalize()
    title_text = title_text.strip()
    return title_text


def list_to_string(list_to_convert: list[str]) -> str:
    """Convert a list to a string

    Take a list of strings and convert it to a string.

    Args:
        list_to_convert (list[str]): The list to convert to a string.

    Returns:
        str: String of the list items.
    """
    if len(list_to_convert) == 0:
        return ""
    elif len(list_to_convert) == 1:
        return list_to_convert[0]
    else:
        return ", ".join(list_to_convert[:-1]) + " and " + list_to_convert[-1]
