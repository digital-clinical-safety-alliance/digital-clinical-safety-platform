"""Managing Docker and Dockerhub

"""
import requests
import json
from dotenv import dotenv_values
import os
from typing import Any

import app.functions.constants as c
import app.tests.data_docker_control as d


class DockerHubController:
    def __init__(
        self,
        dockerhub_username: str = "",
        dockerhub_password: str = "",
        env_location: str = c.ENV_PATH,
    ) -> None:  # nosec B107
        """Initialise DockerHubController

        Initialise controller, getting values form .env if needed.

        Args:
            dockerhub_username (str): DockerHub username
            dockerhub_password (str): DockerHub password
            env_location (str): location of the env file
        """
        self.dockerhub_username: str = ""
        self.dockerhub_password: str = ""

        if env_location == "":
            raise ValueError(f".env location is set to empty string")

        if not os.path.isfile(env_location):
            raise ValueError(
                f"'{ env_location }' path for .env file does not exist"
            )

        dot_values = dotenv_values(env_location)

        if dockerhub_username == "":  # nosec B105
            self.dockerhub_username = str(
                dot_values.get("DOCKERHUB_USERNAME") or ""
            )
            if self.dockerhub_username == "":
                raise ValueError(
                    f"'{ c.EnvKeys.DOCKERHUB_USERNAME.value }' has not been set as an argument or in .env"
                )
        else:
            self.dockerhub_username = dockerhub_username

        if dockerhub_password == "":  # nosec B105
            self.dockerhub_password = str(
                dot_values.get("DOCKERHUB_PASSWORD") or ""
            )
            if self.dockerhub_password == "":  # nosec B105
                raise ValueError(
                    f"'{ c.EnvKeys.DOCKERHUB_PASSWORD.value }' has not been set as an argument or in .env"
                )
        else:
            self.dockerhub_password = dockerhub_password

        return

    def results(self) -> Any:
        """ """
        full_results: Any = d.RETURN_VALUE["results"]
        print(full_results)
        return full_results

    def get_tags(self, user_name: str, respository: str) -> list:
        """Get names"""
        tags: list[str] = []

        request_results = requests.get(
            f"https://hub.docker.com/v2/repositories/{ user_name }/{ respository }/tags",
            auth=(self.dockerhub_username, self.dockerhub_password),
            timeout=10,
        )
        results = json.loads(request_results.content.decode())["results"]
        for resultA in results:
            tags.append(resultA["name"])
        return tags

    def delete_image_by_tag(
        self, user_name: str, repository: str, tag_name: str
    ) -> bool:
        """ """
        print(self.dockerhub_username)
        print(self.dockerhub_password)
        request_results = requests.delete(
            f"https://hub.docker.com/v2/repositories/{ user_name }/{ repository }/tags/{ tag_name }/",
            auth=(self.dockerhub_username, self.dockerhub_password),
            timeout=10,
        )

        print(request_results.status_code)
        print(request_results.content)

        return False
