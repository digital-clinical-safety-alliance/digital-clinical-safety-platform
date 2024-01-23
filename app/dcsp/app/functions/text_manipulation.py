"""

"""


def snake_to_title(snake_text: str) -> str:
    """ """
    words = snake_text.split("_")
    title_text = " ".join(words).capitalize()
    title_text = title_text.strip()
    return title_text


def kebab_to_title(kebab_text: str) -> str:
    """ """
    words = kebab_text.split("-")
    title_text = " ".join(words).capitalize()
    title_text = title_text.strip()
    return title_text
