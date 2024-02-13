"""Basic email testing

This module needs building out further, but at the moment can test if the syntax
of a given email address is correct.

Classes:
    EmailFunctions: placeholder
"""

import os
from dotenv import load_dotenv
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()


class EmailFunctions:
    _valid_email_regex: str = (
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    )

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
            email (str): the email address to be assesed.

        Returns:
            bool: True if a valid email, otherwise False.
        """
        if re.fullmatch(self._valid_email_regex, email):
            return True

        else:
            return False


def email_gmail() -> None:
    message = MIMEMultipart()
    message["To"] = os.getenv("Mark 1")
    message["From"] = os.getenv("Mark 2")
    message["Subject"] = "Subject line here."

    title = "<b> Title line here. </b>"
    messageText = MIMEText("""Message body goes here.""", "html")
    message.attach(messageText)

    email: str = os.getenv("EMAIL_HOST_USER") or ""
    password: str = os.getenv("EMAIL_HOST_PASSWORD") or ""

    server = smtplib.SMTP("smtp.gmail.com:587")
    server.ehlo("Gmail")
    server.starttls()
    server.login(email, password)
    fromaddr: str = os.getenv("EMAIL_HOST_USER") or ""
    toaddrs = os.getenv("EMAIL_HOST_USER") or ""
    server.sendmail(fromaddr, toaddrs, message.as_string())

    server.quit()

    return


if __name__ == "__main__":
    email_gmail()
