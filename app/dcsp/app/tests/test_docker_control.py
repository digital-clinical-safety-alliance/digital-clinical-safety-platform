"""Testing of Docker and Dockerhub

"""

from unittest import TestCase
from django.test import tag
import sys
import app.functions.constants as c

sys.path.append(c.FUNCTIONS_APP)
from app.functions.docker_control import DockerHubController


"""class DockerHubTest(TestCase):
    def test_print(self):
        docker_controller = DockerHubController()
        results = docker_controller.results()
        print(results)
        # for tag in results[0]:
        #    print(tag)

    # @tag("run")
    def test_get_names(self):
        docker_controller = DockerHubController()
        results = docker_controller.get_tags("cotswoldsmaker", "dcsp")
        print(results)

    @tag("run")
    def test_delete_repo_by_tag(self):
        docker_controller = DockerHubController()
        result = docker_controller.delete_image_by_tag(
            "cotswoldsmaker", "dcsp", "a_third_SHA"
        )"""
