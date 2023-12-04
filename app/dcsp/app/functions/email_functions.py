"""Basic email testing

This module needs building out further, but at the moment can test if the syntax
of a given email address is correct.

Classes:
    EmailFunctions
"""
import re


class EmailFunctions:
    _valid_email_regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"

    def __init__(self) -> None:
        """Init

        Nothing is done in the initialisation phase
        """
        return

    def valid_syntax(self, email: str) -> bool:
        """Checks if the syntax of an email string is corrent

        This function only checks if the syntax of an email is correct. It does
        not confirm if the email exists or that the end-server is able to
        process the email

        Args:
            email (str): the email address to be assesed
        Returns:
            bool: True if a valid email, otherwise False
        """
        if re.fullmatch(self._valid_email_regex, email):
            return True

        else:
            return False
