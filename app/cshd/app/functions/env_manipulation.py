"""

"""
import os
from dotenv import load_dotenv, set_key, find_dotenv, dotenv_values

import app.functions.constants as c


class ENVManipulator:
    def __init__(self, env_path: str = c.ENV_PATH) -> None:
        """ """
        self.env_path = env_path
        return

    def delete(self, variable_to_delete: str) -> bool:
        """ """
        variable_set: bool = False
        env_variables = dotenv_values(self.env_path)  # TODO need type
        key: str = ""
        # key, value

        for key in env_variables:
            if key == variable_to_delete:
                variable_set = True

        if variable_set == True:
            del env_variables[variable_to_delete]
            # TODO: may be able to delete this
            # os.environ.pop(variable_to_delete, None)
            # Clears out contents
            open(self.env_path, "w").close()

            for key, value in env_variables.items():
                set_key(self.env_path, str(key), str(value))

            # May be able to remove this.
            # load_dotenv(self.env_path)

        return variable_set

    def add(self, variable: str, value: str) -> None:
        """ """
        set_key(self.env_path, variable, value)
        return

    def read(self, key_to_read: str):
        """ """
        dot_values = dotenv_values(self.env_path)
        return dot_values.get(key_to_read)
