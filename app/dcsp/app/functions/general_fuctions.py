"""Some useful general functions
"""

import re
from typing import Tuple


def snake_to_title(snake_text):
    """ """
    words = snake_text.split("_")
    title_text = " ".join(words).capitalize()
    title_text = title_text.strip()
    return title_text


def kebab_to_title(kebab_text):
    """ """
    words = kebab_text.split("-")
    title_text = " ".join(words).capitalize()
    title_text = title_text.strip()
    return title_text


def valid_linux_path(s) -> Tuple[bool, list[str]]:
    """Check if a path is valid in linux syntax"""
    valid: bool = True
    failure_reasons: list[str] = []
    failure_reasons_str: str = ""

    # Check if the string contains any backslash '\'
    if "\\" in s:
        valid = False
        failure_reasons.append("included backslash (eg '\\')")

    # Check if the string contains two or more '/' in a row
    if re.search(r"/{2,}", s):
        valid = False
        failure_reasons.append("2 or more forwards slashes in a row (eg'//')")

    # Check if the string does not end in '.md'
    if not s.endswith(".md"):
        valid = False
        failure_reasons.append("did not end in '.md'")

    if s.startswith("."):
        valid = False
        failure_reasons.append("started with a fullstop (eg '.')")

    if s.startswith("/"):
        valid = False
        failure_reasons.append("started with forward slash (eg '/')")

    return valid, failure_reasons


def list_to_string(list_to_convert: list) -> str:
    """ """
    return_string: str = ""

    if len(list_to_convert) == 0:
        return_string = ""
    elif len(list_to_convert) == 1:
        return_string = list_to_convert[0]
    else:
        return_string = (
            ", ".join(list_to_convert[:-1]) + ", and " + list_to_convert[-1]
        )
    return return_string
