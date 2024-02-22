import sys

from django.test import TestCase, tag, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from unittest.mock import Mock, patch, call
from django.contrib.messages import get_messages

import app.functions.constants as c

sys.path.append(c.FUNCTIONS_APP)

import app.views as views
from app.models import Project


def log_in(self):
    self.user = User.objects.create_user(
        id=1, username="u", password="p"
    )  # nosec B106
    self.client = Client()
    self.client.login(username="u", password="p")  # nosec B106
    return


class ProjectAccessTest(TestCase):
    def setUp(self):
        log_in(self)

    @patch("app.views.std_context")
    def test_method_not_allowed(self, mock_std_context):
        project_id = "1"

        mock_std_context.return_value = {"test": "test"}

        @views.project_access
        def mock_view(request, project_id, setup_step, *args, **kwargs):
            return HttpResponse("Success")

        request = HttpRequest()
        request.user = self.user
        request.method = "DELETE"
        response = mock_view(request, project_id)

        self.assertEqual(response.status_code, 405)

        mock_std_context.assert_called_once_with()

    @patch("app.views.std_context")
    def test_project_id_non_digit(self, mock_std_context):
        project_id = "a"

        mock_std_context.return_value = {"test": "test"}

        @views.project_access
        def mock_view(request, project_id, setup_step, *args, **kwargs):
            return HttpResponse("Success")

        request = HttpRequest()
        request.user = self.user
        request.method = "GET"
        response = mock_view(request, project_id)

        self.assertEqual(response.status_code, 404)

        mock_std_context.assert_called_once_with()

    @patch("app.decorators.messages.error")
    @patch("app.views.std_context")
    def test_project_does_not_exist(
        self,
        mock_std_context,
        mock_messages_error,
    ):
        project_id = "2"
        Project.objects.create(id=1, owner=self.user, name="Test Project")

        # mock_messages_error - here we are mocking the messages.error function
        mock_std_context.return_value = {"test": "test"}

        @views.project_access
        def mock_view(request, project_id, setup_step, *args, **kwargs):
            return HttpResponse("Success")

        request = HttpRequest()
        request.user = self.user
        request.method = "GET"
        response = mock_view(request, project_id)

        self.assertEqual(response.status_code, 404)

        mock_messages_error.assert_called_once_with(
            request, f"'Project { project_id }' does not exist"
        )
        mock_std_context.assert_called_once_with()

    @patch("app.views.user_accessible_projects")
    @patch("app.decorators.messages.error")
    @patch("app.views.std_context")
    def test_no_user_access(
        self,
        mock_std_context,
        mock_messages_error,
        mock_user_accessible_projects,
    ):
        project_id = "1"
        Project.objects.create(id=1, owner=self.user, name="Test Project")

        mock_user_accessible_projects.return_value = [{"doc_id": 2}]
        # mock_messages_error - here we are mocking the messages.error function
        mock_std_context.return_value = {"test": "test"}

        @views.project_access
        def mock_view(request, project_id, setup_step, *args, **kwargs):
            return HttpResponse("Success")

        request = HttpRequest()
        request.user = self.user
        request.method = "GET"
        response = mock_view(request, project_id)

        self.assertEqual(response.status_code, 403)

        mock_messages_error.assert_called_once_with(
            request, f"You do not have access to this project!"
        )
        mock_user_accessible_projects.assert_called_once_with(request)
        mock_std_context.assert_called_once_with()

    @patch("app.views.user_accessible_projects")
    @patch("app.decorators.ProjectBuilder")
    @patch("app.views.Path.is_dir")
    @patch("app.decorators.messages.error")
    @patch("app.views.std_context")
    def test_docs_folder_missing(
        self,
        mock_std_context,
        mock_messages_error,
        mock_is_dir,
        mock_project_builder,
        mock_user_accessible_projects,
    ):
        project_id = "1"
        project_id_int = int(project_id)
        Project.objects.create(id=1, owner=self.user, name="Test Project")

        mock_user_accessible_projects.return_value = [{"doc_id": 1}]
        mock_project_builder.return_value.configuration_get.return_value = {
            "setup_step": 2
        }
        mock_is_dir.return_value = False
        # mock_messages_error - here we are mocking the messages.error function
        mock_std_context.return_value = {"test": "test"}

        @views.project_access
        def mock_view(request, project_id, setup_step, *args, **kwargs):
            return HttpResponse("Success")

        request = HttpRequest()
        request.user = self.user
        request.method = "GET"
        response = mock_view(request, project_id)

        self.assertEqual(response.status_code, 500)

        mock_user_accessible_projects.assert_called_once_with(request)
        mock_project_builder.assert_called_once_with(project_id_int)
        mock_project_builder.return_value.configuration_get.assert_called_once_with()
        mock_messages_error.assert_called_once_with(
            request,
            f"The safety documents directory for 'project { project_id }' "
            f"does not exist. It should exist at "
            f"'{ c.CLINICAL_SAFETY_FOLDER }docs/'. Please create this folder and "
            "try again. This can either be done via setup process and importing"
            "a safety template or via the external repository and then imported.",
        )
        mock_std_context.assert_called_once_with()

    @patch("app.views.user_accessible_projects")
    @patch("app.decorators.ProjectBuilder")
    def test_allow_access(
        self,
        mock_project_builder,
        mock_user_accessible_projects,
    ):
        project_id = "1"
        project_id_int = int(project_id)

        @views.project_access
        def mock_view(request, project_id, setup_step, *args, **kwargs):
            return HttpResponse("Success")

        Project.objects.create(id=1, owner=self.user, name="Test Project")

        mock_user_accessible_projects.return_value = [{"doc_id": 1}]

        mock_project_builder.return_value.configuration_get.return_value = {
            "setup_step": 1
        }

        request = HttpRequest()
        request.user = self.user
        request.method = "GET"
        response = mock_view(request, project_id)

        self.assertEqual(response.content, b"Success")
        mock_user_accessible_projects.assert_called_once_with(request)
        mock_project_builder.assert_called_once_with(project_id_int)
        mock_project_builder.return_value.configuration_get.assert_called_once_with()
