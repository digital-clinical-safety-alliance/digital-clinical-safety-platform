"""Custom exceptions

Some custom excetions.

Functions:
    RepositoryAccessException: Exception raised when the external repository is not accessible or does not exist.
"""


class RepositoryAccessException(Exception):
    """Exception raised when the external repository is not accessible or does not exist."""

    def __init__(self, repo_url: str) -> None:
        super().__init__(
            f"The external repository '{repo_url}' does not exist or is not accessible with your credentials"
        )
