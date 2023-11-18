"""

"""
import os
from dotenv import load_dotenv, set_key, find_dotenv, dotenv_values


ENV_PATH = "/cshd/.env"


class ENVManipulator:
    def __init__(self):
        return

    def delete(self, variable_to_delete) -> bool:
        variable_set: bool = False
        env_variables = dotenv_values(find_dotenv())
        # print(env_variables)

        for key in env_variables:
            if key == variable_to_delete:
                variable_set = True

        if variable_set == True:
            del env_variables[variable_to_delete]
            os.environ.pop("MYVAR", None)
            open(ENV_PATH, "w").close()

            for key, value in env_variables.items():
                set_key(find_dotenv(), key, value)

            # May be able to remove this.
            load_dotenv(find_dotenv())

        # env_variables = dotenv_values(find_dotenv())
        # print(env_variables)

        return variable_set

    def add(self, variable, value) -> None:
        set_key(find_dotenv(), variable, value)
        return

    """EMAIL_USERNAME = 'mark.bailey5@nhs.net'
    EMAIL_PASSWORD = 'Ashtre135!'
    GITHUB_USERNAME = 'CotswoldsMaker'
    GITHUB_TOKEN = 'testtest'
    MY_VARIABLE = 'new_value'
    MY_VARIABLE1='new_value'"""
