""" env manipulator

Better live env manipulation than standard python library.

Classes:
    ENVManipulator: placeholder
"""
from dotenv import set_key, dotenv_values

import app.functions.constants as c


class ENVManipulator:
    def __init__(self, env_path: str = c.ENV_PATH) -> None:
        """Initialise the env path

        Initialise the env path

        Args:
            env_path (str): location of the env file. Sets to c.ENV_PATH if not
                            sets.
        """
        self.env_path = env_path
        return

    def delete(self, variable_to_delete: str) -> bool:
        """Remove a variable from the env file

        Removes the variable from the env file.

        Args:
            variable_to_delete (str): as name.

        Returns:
            bool: True if was present and deleted, False if was never present.
        """
        variable_set: bool = False
        env_variables = dotenv_values(self.env_path)  # TODO need type
        key: str = ""
        value2: str | None = ""
        key2: str | None = ""

        for key in env_variables:
            if key == variable_to_delete:
                variable_set = True

        if variable_set == True:
            del env_variables[variable_to_delete]
            open(self.env_path, "w").close()

            for key2, value2 in env_variables.items():
                set_key(self.env_path, str(key2), str(value2))

        return variable_set

    def delete_all(self) -> None:
        """Remove all variables from env file

        Removes all the variables from the env file, keeping the file itself
        however.
        """
        open(self.env_path, "w").close()
        return

    def add(self, variable: str, value: str) -> None:
        """Add or change a variable in the env file

        Add or change a variable in the env file

        Args:
            variable (str): name of variable.
            value (str): value to set.

        Returns:
            None
        """
        set_key(self.env_path, variable, value)
        return

    def read(self, key_to_read: str) -> str:
        """Reads a variable from env file

        Reads a variable from an env file

        Args:
            key_to_read (str): the variable to read.

        Returns:
            str: value of the variable. This will return empty string ("")
                 if the variable has not been set.
        """
        dot_values: dict[str, str | None] = dotenv_values(self.env_path)
        return str(dot_values.get(key_to_read) or "")

    def read_all(self) -> dict[str, str]:
        """Reads all variables from env file

        Reads all variable from an env file and returns with keys in alphabetical
        order.

        Returns:
            dict[str, str]: returns all variables in the env file. This will
                            return empty string ("") if the variable has not been
                            set.
        """
        dot_values_raw: dict[str, str | None] = dotenv_values(self.env_path)
        dot_values_clean: dict[str, str] = {}
        key: str = ""
        value: str | None = ""
        sorted_dict: dict[str, str]

        for key, value in dot_values_raw.items():
            dot_values_clean[key] = str(value or "")

        keys_list = list(dot_values_clean.keys())
        keys_list.sort(key=str.lower)
        sorted_dict = {i: dot_values_clean[i] for i in keys_list}
        return sorted_dict
