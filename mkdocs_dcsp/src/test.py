import re


class EmailFunctions:
    _valid_email_regex: str = (
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    )

    def __init__(self) -> None:
        """Gets and prints the spreadsheet's header columns

        :param file_loc: The file location of the spreadsheet
        :type file_loc: str
        :param print_cols: A flag used to print the columns to the console
            (default is False)
        :type print_cols: bool
        :returns: a list of strings representing the header columns
        :rtype: list
        """
        return

    def valid_syntax(self, email: str) -> bool:
        """Gets and prints the spreadsheet's header columns

        :param file_loc: The file location of the spreadsheet
        :type file_loc: str
        :param print_cols: A flag used to print the columns to the console
            (default is False)
        :type print_cols: bool
        :returns: a list of strings representing the header columns
        :rtype: list
        """
        if re.fullmatch(self._valid_email_regex, email):
            return True

        else:
            return False
