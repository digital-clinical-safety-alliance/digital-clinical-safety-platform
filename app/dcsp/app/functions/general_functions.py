"""Some useful general functions

A collection of general functions.

functions:
    valid_partial_linux_path: Check if a path is valid in linux syntax
"""

import re
from typing import Tuple


def valid_partial_linux_path(
    path: str, extension: str = "md"
) -> Tuple[bool, list[str]]:
    """Check if a path is valid in linux syntax

    Confirms if a path is valid in linux syntax.

    Args:
        path (str): The path to check.

    Returns:
        Tuple[bool, list[str]]: Returns if a path is valid and a list of strings
                                indicating why it is not valid (if any).
    """
    valid: bool = True
    failure_reasons: list[str] = []

    if not path:
        valid = False
        failure_reasons.append("empty string")
        return valid, failure_reasons

    # Check if the string contains any backslash '\'
    if "\\" in path:
        valid = False
        failure_reasons.append("included backslash (eg '\\')")

    # Check if the string contains two or more '/' in a row
    if re.search(r"/{2,}", path):
        valid = False
        failure_reasons.append("2 or more forwards slashes in a row (eg'//')")

    # Check if the string does not end in 'extension'
    if not path.endswith(f".{ extension }"):
        valid = False
        failure_reasons.append(f"did not end in '.{ extension }'")

    if path.startswith("."):
        valid = False
        failure_reasons.append("started with a fullstop (eg '.')")

    if path.startswith("/"):
        valid = False
        failure_reasons.append("started with forward slash (eg '/')")

    return valid, failure_reasons
