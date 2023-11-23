"""

"""
import os
from dotenv import load_dotenv, set_key, find_dotenv, dotenv_values

import app.functions.constants as c


class ENVManipulator:
    def __init__(self) -> None:
        """ """
        return

    def delete(self, variable_to_delete: str) -> bool:
        """ """
        variable_set: bool = False
        env_variables = dotenv_values(find_dotenv())  # TODO need type
        key: str = ""
        # key, value

        for key in env_variables:
            if key == variable_to_delete:
                variable_set = True

        if variable_set == True:
            del env_variables[variable_to_delete]
            os.environ.pop("MYVAR", None)
            # Clears out contents
            open(c.ENV_PATH, "w").close()

            for key, value in env_variables.items():
                set_key(find_dotenv(), str(key), str(value))

            # May be able to remove this.
            load_dotenv(find_dotenv())

        return variable_set

    def add(self, variable: str, value: str) -> None:
        """ """
        set_key(find_dotenv(), variable, value)
        return

    def read(self):
        """ """
        return dotenv_values(find_dotenv())
