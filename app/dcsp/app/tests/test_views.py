import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

from django.test import TestCase, tag, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from unittest.mock import Mock, patch, call
from app.models import ProjectGroup
from django.contrib.messages import get_messages
from django.db.models import F
from django.utils import timezone

import app.functions.constants as c

sys.path.append(c.FUNCTIONS_APP)

# from app.decorators import project_access
import app.views as views
from app.models import Project, UserProjectAttribute, ViewAccess
import app.tests.data_views as d
from app.functions.text_manipulation import snake_to_sentense


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


class indexTest(TestCase):
    @patch("app.views.std_context")
    def test_show_public_view(self, mock_std_context):
        mock_std_context.return_value = {"test": "test"}

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")

        mock_std_context.assert_called_once_with()

    @patch("app.views.std_context")
    def test_bad_request(self, mock_std_context):
        mock_std_context.return_value = {"test": "test"}

        response = self.client.delete("/")
        self.assertEqual(response.status_code, 405)
        self.assertTemplateUsed(response, "error_handler.html")

        mock_std_context.assert_called_once_with()

    def test_authenticated(self):
        log_in(self)
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)


class MemberLandingPageTest(TestCase):
    def setUp(self):
        log_in(self)

    @patch("app.views.user_accessible_projects", return_value=[{"doc_id": 1}])
    @patch("app.views.std_context")
    def test_members_page(
        self, mock_std_context, mock_user_accessible_projects
    ):
        mock_std_context.return_value = {"test": "test"}

        response = self.client.get("/member")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "member_landing_page.html")

        request = response.wsgi_request
        mock_user_accessible_projects.assert_called_once_with(request)
        mock_std_context.assert_called_once_with()

    @patch("app.views.std_context")
    def test_bad_request(self, mock_std_context):
        mock_std_context.return_value = {"test": "test"}

        response = self.client.delete("/member")
        self.assertEqual(response.status_code, 405)
        self.assertTemplateUsed(response, "error_handler.html")

        mock_std_context.assert_called_once_with()

    @patch("app.views.user_accessible_projects", return_value=[])
    @patch("app.views.std_context")
    def test_no_projects(
        self, mock_std_context, mock_user_accessible_projects
    ):
        mock_std_context.return_value = {"test": "test"}
        response = self.client.get("/member")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "member_landing_page.html")

        request = response.wsgi_request
        mock_user_accessible_projects.assert_called_once_with(request)
        mock_std_context.assert_called_once_with()


class StartNewProjectTest(TestCase):
    def setUp(self):
        ProjectGroup.objects.create(id=1, name="Test Group")
        log_in(self)

    @patch("app.views.std_context")
    def test_bad_request(self, mock_std_context):
        mock_std_context.return_value = {"test": "test"}

        response = self.client.delete("/start_new_project")
        self.assertEqual(response.status_code, 405)
        self.assertTemplateUsed(response, "error_handler.html")

        mock_std_context.assert_called_once_with()

    @patch("app.views.std_context")
    def test_get(self, mock_std_context):
        mock_std_context.return_value = {"test": "test"}

        s = self.client.session
        s.update(
            {
                "repository_type": "test state",
                "project_setup_step": 0,
                "inputs": {"test_key": "test_value"},
            }
        )
        s.save()

        response = self.client.get("/start_new_project")

        self.assertNotIn("repository_type", dir(self.client.session))
        self.assertEqual(self.client.session["project_setup_step"], 1)
        self.assertEqual(self.client.session["inputs"], {})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "start_new_project.html")

        mock_std_context.assert_called_once_with()

    def test_post_setup_step_1_None(self):
        response = self.client.post("/start_new_project")
        self.assertEqual(response.status_code, 302)

    @patch("app.views.std_context")
    def test_post_setup_step_1_import(self, mock_std_context):
        mock_std_context.return_value = {"test": "test"}

        repo_types = {
            "github.com/": "github",
            "gitlab.com/": "gitlab",
            "gitbucket": "gitbucket",
            "random_name": "other",
        }

        for repo_type, returned_value in repo_types.items():
            s = self.client.session
            s.update(
                {
                    "project_setup_step": 1,
                    "inputs": {"repository_type": ""},
                    "project_setup_1_form_data": {},
                }
            )
            s.save()

            setup_1_form_data = d.START_NEW_PROJECT_STEP_1_IMPORT.copy()
            setup_1_form_data["external_repository_url_import"] = repo_type
            post_data = d.START_NEW_PROJECT_STEP_1_IMPORT.copy()
            post_data["external_repository_url_import"] = repo_type

            response = self.client.post(
                "/start_new_project",
                post_data,
            )

            self.assertEqual(self.client.session.get("project_setup_step"), 2)
            self.assertEqual(
                self.client.session["inputs"]["repository_type"],
                returned_value,
            )
            self.assertEqual(
                self.client.session["project_setup_1_form_data"],
                setup_1_form_data,
            )
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "start_new_project.html")

        self.assertEqual(mock_std_context.call_count, 4)

    @patch("app.views.std_context")
    def test_post_setup_step_1_start_anew(self, mock_std_context):
        mock_std_context.return_value = {"test": "test"}

        s = self.client.session
        s.update({"project_setup_step": 1})
        s.save()

        response = self.client.post(
            "/start_new_project",
            d.START_NEW_PROJECT_STEP_1_START_ANEW,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "start_new_project.html")

        mock_std_context.assert_called_once_with()

    @patch("app.views.ProjectSetupInitialForm")
    @patch("app.views.std_context")
    def test_post_setup_step_1_invalid(
        self, mock_std_context, mock_project_setup_initial_form
    ):
        mock_std_context.return_value = {"test": "test"}

        s = self.client.session
        s.update({"project_setup_step": 1, "inputs": {"repository_type": ""}})
        s.save()

        mock_project_setup_initial_form.return_value.is_valid.return_value = (
            False
        )
        response = self.client.post(
            "/start_new_project",
            {},
        )

        self.assertEqual(self.client.session["project_setup_step"], 1)
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, "start_new_project.html")

        request = response.wsgi_request
        mock_project_setup_initial_form.assert_called_once_with(request.POST)
        mock_project_setup_initial_form.return_value.is_valid.assert_called_once_with()
        mock_std_context.assert_called_once_with()

    @patch("app.views.ProjectSetupStepTwoForm")
    @patch("app.views.std_context")
    def test_post_setup_step_2_wrong_setup_choice(
        self, mock_std_context, mock_form
    ):
        mock_form.return_value.is_valid.return_value = True
        mock_std_context.return_value = {"test": "test"}

        s = self.client.session
        s.update(
            {
                "project_setup_step": 2,
                "project_setup_1_form_data": d.START_NEW_PROJECT_STEP_1_IMPORT_WRONG_CHOICE,
                "inputs": {},
            }
        )
        s.save()

        response = self.client.post(
            "/start_new_project",
            d.START_NEW_PROJECT_STEP_2,
        )

        self.assertEqual(response.status_code, 500)
        self.assertTemplateUsed(response, "error_handler.html")

        request = response.wsgi_request
        mock_form.assert_called_once_with(request.POST)
        mock_form.return_value.is_valid.assert_called_once_with()
        mock_std_context.assert_called_once_with()

    @patch("app.views.ProjectSetupStepTwoForm")
    @patch("app.views.start_new_project_step_2_input_GUI")
    @patch("app.views.std_context")
    def test_post_setup_step_2_import(
        self, mock_std_context, mock_input_GUI, mock_form
    ):
        test_dict_1 = {"test_1": "test_1"}

        mock_form.return_value.is_valid.return_value = True
        mock_form.return_value.cleaned_data = d.START_NEW_PROJECT_STEP_2
        # mock_input_GUI - used here
        mock_std_context.return_value = test_dict_1

        s = self.client.session
        s.update(
            {
                "project_setup_step": 2,
                "project_setup_1_form_data": d.START_NEW_PROJECT_STEP_1_IMPORT,
                "project_setup_2_form_data": {},
                "repository_type": "github",
                "inputs": {},
            }
        )
        s.save()

        response = self.client.post(
            "/start_new_project",
            d.START_NEW_PROJECT_STEP_2,
        )

        self.assertEqual(self.client.session["project_setup_step"], 3)
        self.assertEqual(
            self.client.session["project_setup_2_form_data"],
            d.START_NEW_PROJECT_STEP_2,
        )
        self.assertEqual(
            self.client.session.get("inputs"),
            d.START_NEW_PROJECT_STEP_2_IMPORT_INPUTS,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "start_new_project.html")

        request = response.wsgi_request
        mock_form.assert_called_once_with(request.POST)
        mock_form.return_value.is_valid.assert_called_once_with()
        mock_input_GUI.assert_called_once_with(
            d.START_NEW_PROJECT_STEP_2_IMPORT_INPUTS
        )
        mock_std_context.assert_called_once_with()

    @patch("app.views.ProjectSetupStepTwoForm")
    @patch("app.views.start_new_project_step_2_input_GUI")
    @patch("app.views.std_context")
    def test_post_setup_step_2_start_anew(
        self, mock_std_context, mock_input_GUI, mock_form
    ):
        test_dict_1 = {"test_1": "test_1"}

        mock_form.return_value.is_valid.return_value = True
        mock_form.return_value.cleaned_data = d.START_NEW_PROJECT_STEP_2
        # mock_input_GUI - used here
        mock_std_context.return_value = test_dict_1

        s = self.client.session
        s.update(
            {
                "project_setup_step": 2,
                "project_setup_1_form_data": d.START_NEW_PROJECT_STEP_1_START_ANEW,
                "inputs": {},
            }
        )
        s.save()

        response = self.client.post(
            "/start_new_project",
            d.START_NEW_PROJECT_STEP_2,
        )

        self.assertEqual(self.client.session["project_setup_step"], 3)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "start_new_project.html")

        request = response.wsgi_request
        mock_form.assert_called_once_with(request.POST)
        mock_form.return_value.is_valid.assert_called_once_with()
        mock_input_GUI.assert_called_once_with(
            d.START_NEW_PROJECT_STEP_2_START_ANEW_INPUTS
        )
        mock_std_context.assert_called_once_with()

    @patch("app.views.ProjectSetupStepTwoForm")
    @patch("app.views.std_context")
    def test_post_setup_step_2_post_invalid(
        self, mock_std_context, mock_project_setup_step_two_form
    ):
        mock_std_context.return_value = {"test": "test"}
        mock_project_setup_step_two_form.return_value.is_valid.return_value = (
            False
        )

        s = self.client.session
        s.update({"project_setup_step": 2})
        s.save()

        response = self.client.post(
            "/start_new_project",
            {},
        )

        self.assertEqual(self.client.session["project_setup_step"], 2)
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, "start_new_project.html")

        request = response.wsgi_request
        mock_project_setup_step_two_form.assert_called_once_with(request.POST)
        mock_project_setup_step_two_form.return_value.is_valid.assert_called_once_with()

        mock_std_context.assert_called_once_with()

    @patch("app.views.ProjectBuilder")
    @patch("app.views.std_context")
    def test_post_setup_step_3(self, mock_std_context, mock_project_builder):
        mock_std_context.return_value = {"test": "test"}

        mock_project_builder.return_value.new_build.return_value = (
            True,
            "All passed",
        )

        s = self.client.session
        s.update(
            {
                "project_setup_step": 3,
                "inputs": d.START_NEW_PROJECT_STEP_2_START_ANEW_INPUTS,
                "project_id": 1,
            }
        )
        s.save()

        response = self.client.post(
            "/start_new_project",
            {},
        )

        self.assertEqual(self.client.session["project_setup_step"], 4)
        self.assertNotIn("project_id", dir(self.client.session))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "start_new_project.html")

        request = response.wsgi_request
        mock_project_builder.assert_called_once_with()
        mock_project_builder.return_value.new_build.assert_called_once_with(
            request
        )

        mock_std_context.assert_called_once_with()

    @patch("app.views.ProjectBuilder", return_value=Mock())
    @patch("app.views.std_context")
    def test_post_setup_step_3_build_fail(
        self, mock_std_context, mock_project_builder
    ):
        mock_std_context.return_value = {"test": "test"}
        mock_project_builder.return_value.new_build.return_value = (
            False,
            "Some error",
        )

        s = self.client.session
        s.update(
            {
                "project_setup_step": 3,
                "inputs": d.START_NEW_PROJECT_STEP_2_START_ANEW_INPUTS,
                "project_id": 0,
            }
        )
        s.save()

        response = self.client.post(
            "/start_new_project",
            {},
        )

        self.assertEqual(self.client.session["project_setup_step"], 4)
        self.assertEqual(self.client.session["project_id"], 0)

        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, "start_new_project.html")

        request = response.wsgi_request
        mock_project_builder.assert_called_once_with()
        mock_project_builder.return_value.new_build.assert_called_once_with(
            request
        )

        mock_std_context.assert_called_once_with()

    def test_post_setup_step_4(self):
        s = self.client.session
        s.update(
            {
                "project_setup_step": 4,
            }
        )
        s.save()

        response = self.client.post(
            "/start_new_project",
            {},
        )

        self.assertEqual(response.status_code, 302)


class SetupDocumentsTest(TestCase):
    def setUp(self):
        log_in(self)
        Project.objects.create(id=1, owner=self.user, name="Test Project")

    @patch("app.decorators._project_access")
    @patch("app.views.TemplateSelectForm")
    @patch("app.views.std_context")
    def test_setup_step_1_get(
        self,
        mock_std_context,
        mock_template_select_form,
        mock_project_access,
    ):
        project_id = 1
        setup_step = 1

        mock_project_access.return_value = (
            True,
            HttpResponse(),
            project_id,
            setup_step,
        )

        mock_std_context.return_value = {"test": "test"}

        response = self.client.get(f"/setup_documents/{ project_id }")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "setup_documents_template_select.html"
        )
        request = response.wsgi_request
        mock_project_access.assert_called_once_with(request, str(project_id))
        mock_template_select_form.assert_called_once_with(project_id)
        mock_std_context.assert_called_once_with(project_id)

    @patch("app.decorators._project_access")
    @patch("app.views.ProjectBuilder")
    @patch("app.views.TemplateSelectForm")
    @patch("app.views.PlaceholdersForm")
    @patch("app.views.std_context")
    def test_setup_step_1_post(
        self,
        mock_std_context,
        mock_placeholders_form,
        mock_template_select_form,
        mock_project_builder,
        mock_project_access,
    ):
        project_id = 1
        setup_step = 1
        test_template = "test_template_1"

        mock_project_access.return_value = (
            True,
            HttpResponse(),
            project_id,
            setup_step,
        )
        mock_template_select_form.return_value.is_valid.return_value = True
        mock_project_builder.return_value.configuration_set.return_value = None
        mock_template_select_form.return_value.cleaned_data = {
            "template_choice": test_template
        }
        mock_project_builder.return_value.copy_templates.return_value = None
        mock_std_context.return_value = {"test": "test"}

        response = self.client.post(f"/setup_documents/{ project_id }")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "setup_documents_placeholders_show.html"
        )

        request = response.wsgi_request
        mock_project_access.assert_called_once_with(request, str(project_id))
        mock_project_builder.assert_has_calls(
            [
                call(project_id),
                call().configuration_set("setup_step", 2),
                call().copy_templates(test_template),
            ]
        )
        mock_template_select_form.assert_called_once_with(
            project_id, request.POST
        )
        mock_template_select_form.return_value.is_valid.assert_called_once_with()
        mock_placeholders_form.assert_called_once_with(project_id)
        mock_std_context.assert_called_once_with(project_id)

    @patch("app.decorators._project_access")
    @patch("app.views.ProjectBuilder")
    @patch("app.views.TemplateSelectForm")
    @patch("app.views.std_context")
    def test_setup_step_1_post_invalid(
        self,
        mock_std_context,
        mock_template_select_form,
        mock_project_builder,
        mock_project_access,
    ):
        project_id = 1
        setup_step = 1

        mock_project_access.return_value = (
            True,
            HttpResponse(),
            project_id,
            setup_step,
        )
        mock_template_select_form.return_value.is_valid.return_value = False
        mock_std_context.return_value = {"test": "test"}

        response = self.client.post(f"/setup_documents/{ project_id }")

        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(
            response, "setup_documents_template_select.html"
        )

        request = response.wsgi_request
        mock_project_access.assert_called_once_with(request, str(project_id))
        mock_project_builder.assert_called_once_with(project_id)
        mock_template_select_form.assert_called_once_with(
            project_id, request.POST
        )
        mock_template_select_form.return_value.is_valid.assert_called_once_with()
        mock_std_context.assert_called_once_with(project_id)

    @patch("app.decorators._project_access")
    @patch("app.views.PlaceholdersForm")
    @patch("app.views.std_context")
    def test_setup_step_2_get(
        self,
        mock_std_context,
        mock_placeholders_form,
        mock_project_access,
    ):
        project_id = 1
        setup_step = 2

        mock_project_access.return_value = (
            True,
            HttpResponse(),
            project_id,
            setup_step,
        )

        mock_std_context.return_value = {"test": "test"}

        response = self.client.get(f"/setup_documents/{ project_id }")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "setup_documents_placeholders_show.html"
        )
        request = response.wsgi_request
        mock_project_access.assert_called_once_with(request, str(project_id))
        mock_placeholders_form.assert_called_once_with(project_id)
        mock_std_context.assert_called_once_with(project_id)

    @patch("app.decorators._project_access")
    @patch("app.views.ProjectBuilder")
    @patch("app.views.PlaceholdersForm")
    @patch("app.views.project_timestamp")
    @patch("app.views.std_context")
    def test_setup_step_2_post(
        self,
        mock_std_context,
        mock_project_timestamp,
        mock_placeholders_form,
        mock_project_builder,
        mock_project_access,
    ):
        project_id = 1
        setup_step = 2

        mock_project_access.return_value = (
            True,
            HttpResponse(),
            project_id,
            setup_step,
        )
        mock_placeholders_form.return_value.is_valid.return_value = True
        mock_project_builder.return_value.configuration_set.return_value = None
        mock_project_builder.return_value.save_placeholders_from_form.return_value = (
            None
        )
        mock_project_timestamp.return_value = None
        mock_std_context.return_value = {"test": "test"}

        response = self.client.post(f"/setup_documents/{ project_id }")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "setup_documents_placeholders_saved.html"
        )

        request = response.wsgi_request
        mock_project_access.assert_called_once_with(request, str(project_id))
        mock_project_builder.assert_has_calls(
            [
                call(project_id),
                call().configuration_set("setup_step", setup_step + 1),
                call().save_placeholders_from_form(mock_placeholders_form()),
            ]
        )
        # This test fails if put in front of mock_project_builder.assert_has_calls()
        mock_placeholders_form.assert_has_calls(
            [call(project_id, request.POST), call().is_valid(), call()]
        )
        mock_project_timestamp.assert_called_once_with(project_id)
        mock_std_context.assert_called_once_with(project_id)

    @patch("app.decorators._project_access")
    @patch("app.views.ProjectBuilder")
    @patch("app.views.PlaceholdersForm")
    @patch("app.views.std_context")
    def test_setup_step_2_post_invalid(
        self,
        mock_std_context,
        mock_placeholders_form,
        mock_project_builder,
        mock_project_access,
    ):
        project_id = 1
        setup_step = 2

        mock_project_access.return_value = (
            True,
            HttpResponse(),
            project_id,
            setup_step,
        )
        mock_placeholders_form.return_value.is_valid.return_value = False
        mock_std_context.return_value = {"test": "test"}

        response = self.client.post("/setup_documents/1")

        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(
            response, "setup_documents_placeholders_show.html"
        )

        request = response.wsgi_request
        mock_project_access.assert_called_once_with(request, str(project_id))
        mock_project_builder.assert_has_calls(
            [
                call(project_id),
            ]
        )
        # This test fails if put in front of mock_project_builder.assert_has_calls()
        mock_placeholders_form.assert_has_calls(
            [call(project_id, request.POST), call().is_valid()]
        )
        mock_std_context.assert_called_once_with(project_id)


class ProjectBuildASAPTest(TestCase):
    def setUp(self):
        log_in(self)
        Project.objects.create(id=1, owner=self.user, name="Test Project")

    @patch("app.decorators._project_access")
    @patch("app.views.MkdocsControl")
    @patch("app.views.std_context")
    def test_get(
        self, mock_std_context, mock_mkdocs_control, mock_project_access
    ):
        project_id = 1
        setup_step = 2

        mock_project_access.return_value = (
            True,
            HttpResponse(),
            project_id,
            setup_step,
        )
        mock_std_context.return_value = {"test": "test"}

        response = self.client.get(f"/project_build_asap/{ project_id }")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "project_build_asap.html")

        request = response.wsgi_request
        mock_project_access.assert_called_once_with(request, str(project_id))
        mock_mkdocs_control.assert_called_once_with(project_id)
        mock_std_context.assert_called_once_with(project_id)

    @patch("app.decorators._project_access")
    @patch("app.views.MkdocsControl")
    @patch("app.views.std_context")
    def test_post(
        self, mock_std_context, mock_mkdocs_control, mock_project_access
    ):
        project_id = 1
        setup_step = 2

        mock_project_access.return_value = (
            True,
            HttpResponse(),
            project_id,
            setup_step,
        )
        mock_mkdocs_control.return_value.build_documents.return_value = (
            True,
            "All passed",
        )
        mock_std_context.return_value = {"test": "test"}

        response = self.client.post(f"/project_build_asap/{ project_id }")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "project_build_asap.html")

        request = response.wsgi_request
        mock_project_access.assert_called_once_with(request, str(project_id))
        mock_mkdocs_control.assert_called_once_with(project_id)
        mock_mkdocs_control.return_value.build_documents.assert_called_once_with(
            force=True
        )
        mock_std_context.assert_called_once_with(project_id)


class ProjectDocumentsTest(TestCase):
    def setUp(self):
        log_in(self)
        project = Project.objects.create(
            id=1, owner=self.user, name="Test Project"
        )
        project.member.set([self.user])
        project_group = ProjectGroup.objects.create(id=1, name="Test Group")
        project_group.project_access.set([project])

    @patch("app.decorators._project_access")
    @patch("app.views.std_context")
    def test_wrong_method(self, mock_std_context, mock_project_access):
        project_id = 1
        setup_step = 2

        mock_project_access.return_value = (
            True,
            HttpResponse(),
            project_id,
            setup_step,
        )
        mock_std_context.return_value = {"test": "test"}

        response = self.client.delete(f"/project_documents/{ project_id}")

        self.assertEqual(response.status_code, 405)
        self.assertTemplateUsed(response, "error_handler.html")

        request = response.wsgi_request
        mock_project_access.assert_called_once_with(request, str(project_id))
        mock_std_context.assert_called_once_with()

    @patch("app.decorators._project_access")
    @patch("app.views.std_context")
    def test_get(self, mock_std_context, mock_project_access):
        project_id = 1
        setup_step = 2

        mock_project_access.return_value = (
            True,
            HttpResponse(),
            project_id,
            setup_step,
        )
        mock_std_context.return_value = {"test": "test"}

        response = self.client.get(f"/project_documents/{ project_id }")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "project_documents.html")

        request = response.wsgi_request
        mock_project_access.assert_called_once_with(request, str(project_id))
        mock_std_context.assert_called_once_with(project_id)


class ViewDocsTest(TestCase):
    @patch("app.views.std_context")
    def test_not_digit(self, mock_std_context):
        mock_std_context.return_value = {"test": "test"}

        response = self.client.get("/view_docs/a/test_page.html")

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "error_handler.html")

        mock_std_context.assert_called_once_with()

    @patch("app.views.std_context")
    def test_project_nonexistent(self, mock_std_context):
        project_id = 1
        mock_std_context.return_value = {"test": "test"}

        response = self.client.get(f"/view_docs/{ project_id }/test_page.html")

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "error_handler.html")

        request = response.wsgi_request
        messages = list(get_messages(request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), f"'Project { project_id }' does not exist"
        )

        mock_std_context.assert_called_once_with()

    @patch("app.views.std_context")
    def test_members_user_not_authenticated(self, mock_std_context):
        project_id = 1
        self.user = User.objects.create_user(
            id=1, username="u", password="p"
        )  # nosec B106
        Project.objects.create(
            id=project_id,
            owner=self.user,
            name="Test Project",
            access=ViewAccess.MEMBERS,
        )
        mock_std_context.return_value = {"test": "test"}

        response = self.client.get(f"/view_docs/{ project_id }/test_page.html")

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "error_handler.html")

        request = response.wsgi_request
        messages = list(get_messages(request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            f"You do not have access to 'project { project_id }'. "
            "This is a members only project.",
        )
        mock_std_context.assert_called_once_with()

    @patch("app.views.std_context")
    def test_private_with_no_access(self, mock_std_context):
        project_id = 1
        self.user1 = User.objects.create_user(
            id=1, username="user1", password="password1"
        )  # nosec B106
        self.user2 = User.objects.create_user(
            id=2, username="user2", password="password2"
        )  # nosec B106
        Project.objects.create(
            id=project_id,
            owner=self.user1,
            name="Test Project",
            access=ViewAccess.PRIVATE,
        )

        self.client = Client()
        self.client.login(username="user2", password="password2")  # nosec B106

        mock_std_context.return_value = {"test": "test"}

        response = self.client.get(f"/view_docs/{ project_id }/test_page.html")

        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "error_handler.html")

        request = response.wsgi_request
        messages = list(get_messages(request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            f"You do not have access to 'project { project_id }'.",
        )
        mock_std_context.assert_called_once_with()

    @patch("app.views.MkdocsControl")
    @patch("app.views.Path.is_file")
    @patch("app.views.std_context")
    def test_public_file_nonexistent(
        self, mock_std_context, mock_is_file, mock_mkdocs_control
    ):
        project_id = 1
        test_page = "test_page.html"

        self.user = User.objects.create_user(
            id=1, username="user", password="password"
        )  # nosec B106
        Project.objects.create(
            id=project_id,
            owner=self.user,
            name="Test Project",
            access=ViewAccess.PUBLIC,
        )

        mock_mkdocs_control.return_value.build_documents.return_value = Mock()

        mock_is_file.return_value = False

        mock_std_context.return_value = {"test": "test"}

        response = self.client.get(f"/view_docs/{ project_id }/{ test_page }")

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "error_handler.html")

        request = response.wsgi_request
        messages = list(get_messages(request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            f"File '{ test_page }' does not exist.",
        )
        mock_mkdocs_control.assert_called_once_with(str(project_id))
        mock_mkdocs_control.return_value.build_documents.assert_called_once_with()
        mock_is_file.assert_called_once_with()
        mock_std_context.assert_called_once_with()

    @patch("app.views.MkdocsControl")
    @patch("app.views.Path.is_file")
    @patch("app.views.open")
    @patch("app.views.std_context")
    def test_public_html_file(
        self, mock_std_context, mock_open, mock_is_file, mock_mkdocs_control
    ):
        project_id = 1
        test_page = "test_page.html"
        self.user = User.objects.create_user(
            id=1, username="user", password="password"
        )  # nosec B106
        Project.objects.create(
            id=project_id,
            owner=self.user,
            name="Test Project",
            access=ViewAccess.PUBLIC,
        )

        mock_mkdocs_control.return_value.build_documents.return_value = Mock()

        mock_is_file.return_value = True

        mock_open.return_value.read.return_value = "Some test html"

        mock_std_context.return_value = {"test": "test"}

        response = self.client.get(f"/view_docs/{ project_id }/{ test_page }")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "document_serve.html")

        mock_mkdocs_control.assert_called_once_with(str(project_id))
        mock_mkdocs_control.return_value.build_documents.assert_called_once_with()
        mock_is_file.assert_called_once_with()
        mock_open.assert_called_once_with(
            str(
                Path(c.DOCUMENTATION_PAGES)
                / f"project_{ project_id }"
                / test_page
            ),
            "r",
        )
        mock_open.return_value.read.assert_called_once_with()
        mock_std_context.assert_called_once_with(project_id)

    @patch("app.views.Path.is_file")
    def test_public_non_html_file(self, mock_is_file):
        project_id = 1
        test_image = "test_image.jpeg"
        self.user = User.objects.create_user(
            id=1, username="user", password="password"
        )  # nosec B106
        Project.objects.create(
            id=project_id,
            owner=self.user,
            name="Test Project",
            access=ViewAccess.PUBLIC,
        )

        mock_is_file.return_value = True

        response = self.client.get(f"/view_docs/{ project_id }/{ test_image }")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/jpeg")
        self.assertEqual(
            response["X-Accel-Redirect"],
            "/documentation-pages/project_1/test_image.jpeg",
        )

        mock_is_file.assert_called_once_with()


class DocumentNewTest(TestCase):
    def setUp(self):
        log_in(self)
        project = Project.objects.create(
            id=1, owner=self.user, name="Test Project"
        )
        project.member.set([self.user])
        project_group = ProjectGroup.objects.create(id=1, name="Test Group")
        project_group.project_access.set([project])

    @patch("app.decorators._project_access")
    def test_setup_step_1(self, mock_project_access):
        project_id = 1
        setup_step = 1

        mock_project_access.return_value = (
            True,
            HttpResponse(),
            project_id,
            setup_step,
        )

        response = self.client.get(f"/document_new/{ project_id }")

        self.assertEqual(response.status_code, 302)

        request = response.wsgi_request
        mock_project_access.assert_called_once_with(request, str(project_id))

    @patch("app.decorators._project_access")
    @patch("app.views.DocumentNewForm")
    @patch("app.views.std_context")
    def test_get(
        self, mock_std_context, mock_document_new_form, mock_project_access
    ):
        project_id = 1
        setup_step = 2

        mock_project_access.return_value = (
            True,
            HttpResponse(),
            project_id,
            setup_step,
        )
        # mock_document_new_form - used here
        mock_std_context.return_value = {"test": "test"}

        response = self.client.get(f"/document_new/{ project_id }")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "document_new.html")

        request = response.wsgi_request
        mock_project_access.assert_called_once_with(request, str(project_id))
        mock_document_new_form.assert_called_once_with(project_id)
        mock_std_context.assert_called_once_with(project_id)

    @patch("app.decorators._project_access")
    @patch("app.views.DocumentNewForm")
    @patch("app.views.ProjectBuilder")
    @patch("app.views.std_context")
    def test_post(
        self,
        mock_std_context,
        mock_project_builder,
        mock_document_new_form,
        mock_project_access,
    ):
        project_id = 1
        setup_step = 2
        document_dict = {"document_name": "test_name"}

        mock_project_access.return_value = (
            True,
            HttpResponse(),
            project_id,
            setup_step,
        )
        mock_document_new_form.return_value.is_valid.return_value = True
        mock_document_new_form.return_value.cleaned_data = {
            "document_name": "test_name"
        }
        mock_std_context.return_value = {"test": "test"}

        response = self.client.post(f"/document_new/{ project_id }", {})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "document_new.html")

        request = response.wsgi_request
        mock_project_access.assert_called_once_with(request, str(project_id))
        mock_document_new_form.assert_called_once_with(
            project_id, request.POST
        )
        mock_document_new_form.return_value.is_valid.assert_called_once_with()
        mock_project_builder.assert_called_once_with(project_id)
        mock_project_builder.return_value.document_create.assert_called_once_with(
            document_dict["document_name"]
        )
        messages = list(get_messages(request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            f"Document '{ document_dict['document_name'] }' has been created",
        )
        mock_std_context.assert_called_once_with(project_id)

    @patch("app.decorators._project_access")
    @patch("app.views.DocumentNewForm")
    @patch("app.views.std_context")
    def test_post_invalid(
        self, mock_std_context, mock_document_new_form, mock_project_access
    ):
        project_id = 1
        setup_step = 2

        mock_project_access.return_value = (
            True,
            HttpResponse(),
            project_id,
            setup_step,
        )
        mock_document_new_form.return_value.is_valid.return_value = False

        mock_std_context.return_value = {"test": "test"}

        response = self.client.post(f"/document_new/{ project_id }", {})

        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, "document_new.html")

        request = response.wsgi_request
        mock_project_access.assert_called_once_with(request, str(project_id))
        mock_std_context.assert_called_once_with(project_id)


class DocumentUpdateTest(TestCase):
    def setUp(self):
        log_in(self)
        project = Project.objects.create(
            id=1, owner=self.user, name="Test Project"
        )
        project.member.set([self.user])
        project_group = ProjectGroup.objects.create(id=1, name="Test Group")
        project_group.project_access.set([project])

    @patch("app.decorators._project_access")
    def test_setup_step_1(self, mock_project_access):
        project_id = 1
        setup_step = 1

        mock_project_access.return_value = (
            True,
            HttpResponse(),
            project_id,
            setup_step,
        )

        response = self.client.get(f"/document_update/{ project_id }")

        self.assertEqual(response.status_code, 302)

        request = response.wsgi_request
        mock_project_access.assert_called_once_with(request, str(project_id))

    @patch("app.decorators._project_access")
    @patch("app.views.DocumentUpdateForm")
    @patch("app.views.placeholders")
    @patch("app.views.std_context")
    def test_get(
        self,
        mock_std_context,
        mock_placeholders,
        mock_form,
        mock_project_access,
    ):
        project_id = 1
        setup_step = 2

        mock_project_access.return_value = (
            True,
            HttpResponse(),
            project_id,
            setup_step,
        )
        # mock_form - used here
        # mock_placeholders - used here
        mock_std_context.return_value = {"test": "test"}

        response = self.client.get(f"/document_update/{ project_id }")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "document_update.html")

        request = response.wsgi_request
        mock_project_access.assert_called_once_with(request, str(project_id))
        mock_form.assert_called_once_with(project_id)
        mock_placeholders.assert_called_once_with(project_id)
        mock_std_context.assert_called_once_with(project_id)

    @patch("app.decorators._project_access")
    @patch("app.views.DocumentUpdateForm")
    @patch("app.views.open")
    @patch("app.views.placeholders")
    @patch("app.views.std_context")
    def test_post_document_changed(
        self,
        mock_std_context,
        mock_placeholders,
        mock_open,
        mock_form,
        mock_project_access,
    ):
        project_id = 1
        setup_step = 2
        docs_dir: str = f"{ c.PROJECTS_FOLDER }project_{ project_id }/{ c.CLINICAL_SAFETY_FOLDER }docs/"
        updated_form_data = {
            "document_name": "another_name.md",
            "document_markdown": "Some safety information",
        }

        mock_project_access.return_value = (
            True,
            HttpResponse(),
            project_id,
            setup_step,
        )
        # mock_form - used here
        mock_form.return_value.is_valid.return_value = True
        mock_form.return_value.cleaned_data = {
            "document_name_initial": "one_name.md",
            "document_name": "another_name.md",
            "document_markdown_initial": "test_same",
            "document_markdown": "test_same",
        }
        # mock_open - used here
        mock_open.return_value.__enter__.return_value.read.return_value = (
            "Some safety information"
        )
        mock_std_context.return_value = {"test": "test"}

        response = self.client.post(f"/document_update/{ project_id }")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "document_update.html")

        request = response.wsgi_request
        mock_project_access.assert_called_once_with(request, str(project_id))
        mock_form.assert_any_call(project_id, request.POST)
        mock_form.return_value.is_valid.assert_called_once()
        mock_open.assert_called_once_with(
            Path(docs_dir) / "another_name.md", "r"
        )
        mock_open.return_value.__enter__.return_value.read.assert_called_once_with()
        mock_form.assert_any_call(project_id, initial=updated_form_data)
        mock_placeholders.assert_called_once_with(project_id)
        mock_std_context.assert_called_once_with(project_id)

    @patch("app.decorators._project_access")
    @patch("app.views.DocumentUpdateForm")
    @patch("app.views.project_timestamp")
    @patch("app.views.open")
    @patch("app.views.placeholders")
    @patch("app.views.std_context")
    def test_post_text_changed(
        self,
        mock_std_context,
        mock_placeholders,
        mock_open,
        mock_project_timestamp,
        mock_form,
        mock_project_access,
    ):
        project_id = 1
        setup_step = 2
        document_name = "same_name.md"
        new_text = "new text"
        docs_dir: str = f"{ c.PROJECTS_FOLDER }project_{ project_id }/{ c.CLINICAL_SAFETY_FOLDER }docs/"
        updated_form_data = {
            "document_name": document_name,
            "document_markdown": "new text",
        }

        mock_project_access.return_value = (
            True,
            HttpResponse(),
            project_id,
            setup_step,
        )
        # mock_form - used here
        mock_form.return_value.is_valid.return_value = True
        mock_form.return_value.cleaned_data = {
            "document_name_initial": document_name,
            "document_name": document_name,
            "document_markdown_initial": "initial text",
            "document_markdown": new_text,
        }
        # mock_open - used here
        # mock_open / write - used here
        # mock_project_timestamp - used here
        mock_std_context.return_value = {"test": "test"}

        response = self.client.post(f"/document_update/{ project_id }")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "document_update.html")

        request = response.wsgi_request
        mock_project_access.assert_called_once_with(request, str(project_id))
        mock_form.assert_any_call(project_id, request.POST)
        mock_form.return_value.is_valid.assert_called_once()
        mock_open.assert_called_once_with(Path(docs_dir) / document_name, "r")
        mock_open.return_value.__enter__.return_value.write.assert_called_once_with(
            new_text
        )
        mock_project_timestamp.assert_called_once_with(project_id)
        messages = list(get_messages(request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            f"Mark down file '{ document_name }' has been successfully saved",
        )
        mock_form.assert_any_call(project_id, initial=updated_form_data)
        mock_placeholders.assert_called_once_with(project_id)
        mock_std_context.assert_called_once_with(project_id)

    @patch("app.decorators._project_access")
    @patch("app.views.DocumentUpdateForm")
    @patch("app.views.placeholders")
    @patch("app.views.std_context")
    def test_post_no_changes(
        self,
        mock_std_context,
        mock_placeholders,
        mock_form,
        mock_project_access,
    ):
        project_id = 1
        setup_step = 2
        old_document_name = "same_name.md"
        old_text = "old text"

        mock_project_access.return_value = (
            True,
            HttpResponse(),
            project_id,
            setup_step,
        )
        # mock_form - used here
        mock_form.return_value.is_valid.return_value = True
        mock_form.return_value.cleaned_data = {
            "document_name_initial": old_document_name,
            "document_name": old_document_name,
            "document_markdown_initial": old_text,
            "document_markdown": old_text,
        }

        mock_std_context.return_value = {"test": "test"}

        response = self.client.post(f"/document_update/{ project_id }")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "document_update.html")

        request = response.wsgi_request
        mock_project_access.assert_called_once_with(request, str(project_id))
        mock_form.assert_any_call(project_id, request.POST)
        mock_form.return_value.is_valid.assert_called_once()
        messages = list(get_messages(request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "As no changes have been made, no save has been made",
        )
        mock_placeholders.assert_called_once_with(project_id)
        mock_std_context.assert_called_once_with(project_id)

    @patch("app.decorators._project_access")
    @patch("app.views.DocumentUpdateForm")
    @patch("app.views.placeholders")
    @patch("app.views.std_context")
    def test_post_invalid(
        self,
        mock_std_context,
        mock_placeholders,
        mock_form,
        mock_project_access,
    ):
        project_id = 1
        setup_step = 2

        mock_project_access.return_value = (
            True,
            HttpResponse(),
            project_id,
            setup_step,
        )
        # mock_form - used here
        mock_form.return_value.is_valid.return_value = False

        mock_std_context.return_value = {"test": "test"}

        response = self.client.post(f"/document_update/{ project_id }")

        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, "document_update.html")

        request = response.wsgi_request
        mock_project_access.assert_called_once_with(request, str(project_id))
        mock_form.assert_any_call(project_id, request.POST)
        mock_form.return_value.is_valid.assert_called_once()
        mock_placeholders.assert_called_once_with(project_id)
        mock_std_context.assert_called_once_with(project_id)


class EntryUpdateTest(TestCase):
    def setUp(self):
        log_in(self)
        project = Project.objects.create(
            id=1, owner=self.user, name="Test Project"
        )
        project.member.set([self.user])
        project_group = ProjectGroup.objects.create(id=1, name="Test Group")
        project_group.project_access.set([project])

    @patch("app.decorators._project_access")
    @patch("app.views.ProjectBuilder")
    def test_setup_step_1(self, mock_project_builder, mock_project_access):
        project_id = 1
        setup_step = 1
        entry_type = "hazard"
        entry_number = 1

        mock_project_access.return_value = (
            True,
            HttpResponse(),
            project_id,
            setup_step,
        )
        # mock_project_builder - used here

        response = self.client.get(
            f"/entry_update/{ project_id }/{ entry_type }/{ entry_number}"
        )

        self.assertEqual(response.status_code, 302)

        request = response.wsgi_request
        mock_project_access.assert_called_once_with(request, str(project_id))
        mock_project_builder.assert_called_once_with(project_id)

    @patch("app.decorators._project_access")
    @patch("app.views.ProjectBuilder")
    @patch("app.views.std_context")
    def test_entry_nonexistent(
        self, mock_std_context, mock_project_builder, mock_project_access
    ):
        project_id = 1
        setup_step = 2
        entry_type = "hazard"
        entry_number = 1

        mock_project_access.return_value = (
            True,
            HttpResponse(),
            project_id,
            setup_step,
        )
        # mock_project_builder - used here
        mock_project_builder.return_value.entry_exists.return_value = False
        mock_std_context.return_value = {"test": "test"}

        response = self.client.get(
            f"/entry_update/{ project_id }/{ entry_type }/{ entry_number}"
        )

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "error_handler.html")

        request = response.wsgi_request
        mock_project_access.assert_called_once_with(request, str(project_id))
        mock_project_builder.assert_called_once_with(project_id)
        mock_project_builder.return_value.entry_exists.assert_called_once_with(
            entry_type, str(project_id)
        )
        mock_std_context.assert_called_once_with()

    @patch("app.decorators._project_access")
    @patch("app.views.ProjectBuilder")
    @patch("app.views.std_context")
    def test_entry_type_nonexistent(
        self, mock_std_context, mock_project_builder, mock_project_access
    ):
        project_id = 1
        setup_step = 2
        entry_type = "nonexistent_type"
        entry_number = 1

        mock_project_access.return_value = (
            True,
            HttpResponse(),
            project_id,
            setup_step,
        )
        # mock_project_builder - used here
        mock_project_builder.return_value.entry_exists.return_value = True
        mock_project_builder.return_value.entry_type_exists.return_value = (
            False
        )
        mock_std_context.return_value = {"test": "test"}

        response = self.client.get(
            f"/entry_update/{ project_id }/{ entry_type }/{ entry_number}"
        )

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "error_handler.html")

        request = response.wsgi_request
        mock_project_access.assert_called_once_with(request, str(project_id))
        mock_project_builder.assert_called_once_with(project_id)
        mock_project_builder.return_value.entry_exists.assert_called_once_with(
            entry_type, str(project_id)
        )
        mock_project_builder.return_value.entry_type_exists.assert_called_once_with(
            entry_type
        )
        mock_std_context.assert_called_once_with()

    @patch("app.decorators._project_access")
    @patch("app.views.ProjectBuilder")
    @patch("app.views.kebab_to_sentense")
    @patch("app.views.EntryUpdateForm")
    @patch("app.views.std_context")
    def test_get_new(
        self,
        mock_std_context,
        mock_form,
        mock_kebab_to_sentense,
        mock_project_builder,
        mock_project_access,
    ):
        project_id = 1
        setup_step = 2
        entry_type = "nonexistent_type"
        entry_number = "new"

        mock_project_access.return_value = (
            True,
            HttpResponse(),
            project_id,
            setup_step,
        )
        # mock_project_builder - used here
        mock_project_builder.return_value.entry_type_exists.return_value = True
        # mock_kebab_to_sentense - used here
        # mock_form - used here
        mock_std_context.return_value = {"test": "test"}

        response = self.client.get(
            f"/entry_update/{ project_id }/{ entry_type }/{ entry_number}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "entry_update.html")

        request = response.wsgi_request
        mock_project_access.assert_called_once_with(request, str(project_id))
        mock_project_builder.assert_called_once_with(project_id)
        mock_project_builder.return_value.entry_type_exists.assert_called_once_with(
            entry_type
        )
        mock_kebab_to_sentense.assert_called_once_with(entry_type)
        mock_form.assert_called_once_with(project_id, entry_type)
        mock_std_context.assert_called_once_with(project_id)

    @patch("app.decorators._project_access")
    @patch("app.views.ProjectBuilder")
    @patch("app.views.kebab_to_sentense")
    @patch("app.views.EntryUpdateForm")
    @patch("app.views.std_context")
    def test_get_entry_1(
        self,
        mock_std_context,
        mock_form,
        mock_kebab_to_sentense,
        mock_project_builder,
        mock_project_access,
    ):
        project_id = 1
        setup_step = 2
        entry_type = "nonexistent_type"
        entry_number = 1
        form_initial = {"test": "test"}

        mock_project_access.return_value = (
            True,
            HttpResponse(),
            project_id,
            setup_step,
        )
        # mock_project_builder - used here
        mock_project_builder.return_value.entry_exists.return_value = True
        mock_project_builder.return_value.entry_type_exists.return_value = True
        mock_project_builder.return_value.form_initial.return_value = (
            form_initial
        )
        # mock_kebab_to_sentense - used here
        # mock_form - used here
        mock_std_context.return_value = {"test": "test"}

        response = self.client.get(
            f"/entry_update/{ project_id }/{ entry_type }/{ entry_number}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "entry_update.html")

        request = response.wsgi_request
        mock_project_access.assert_called_once_with(request, str(project_id))
        mock_project_builder.assert_called_once_with(project_id)
        mock_project_builder.return_value.entry_exists.assert_called_once_with(
            entry_type, str(project_id)
        )
        mock_project_builder.return_value.entry_type_exists.assert_called_once_with(
            entry_type
        )
        mock_project_builder.return_value.form_initial.assert_called_once_with(
            entry_type, entry_number
        )
        mock_kebab_to_sentense.assert_called_once_with(entry_type)
        mock_form.assert_called_once_with(
            project_id, entry_type, initial=form_initial
        )
        mock_std_context.assert_called_once_with(project_id)

    @patch("app.decorators._project_access")
    @patch("app.views.ProjectBuilder")
    @patch("app.views.EntryUpdateForm")
    @patch("app.views.project_timestamp")
    @patch("app.views.kebab_to_sentense")
    @patch("app.views.std_context")
    def test_get_post(
        self,
        mock_std_context,
        mock_kebab_to_sentense,
        mock_project_timestamp,
        mock_form,
        mock_project_builder,
        mock_project_access,
    ):
        project_id = 1
        setup_step = 2
        entry_type = "nonexistent_type"
        entry_number = 1
        form_initial = {"test": "test"}

        mock_project_access.return_value = (
            True,
            HttpResponse(),
            project_id,
            setup_step,
        )
        # mock_project_builder - used here
        mock_project_builder.return_value.entry_exists.return_value = True
        mock_project_builder.return_value.entry_type_exists.return_value = True
        # mock_form - used here
        mock_form.return_value.is_valid.return_value = True
        # mock_project_timestamp - used here
        mock_project_builder.return_value.entry_update.return_value = {
            "test": "test"
        }
        mock_form.return_value.cleaned_data = form_initial
        # mock_kebab_to_sentense - used here
        mock_std_context.return_value = {"test": "test"}

        response = self.client.post(
            f"/entry_update/{ project_id }/{ entry_type }/{ entry_number}",
            form_initial,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "entry_saved.html")

        request = response.wsgi_request
        mock_project_access.assert_called_once_with(request, str(project_id))
        mock_project_builder.assert_called_once_with(project_id)
        mock_project_builder.return_value.entry_exists.assert_called_once_with(
            entry_type, str(project_id)
        )
        mock_project_builder.return_value.entry_type_exists.assert_called_once_with(
            entry_type
        )

        mock_form.assert_any_call(project_id, entry_type, request.POST)
        mock_form.return_value.is_valid.assert_called_once_with()
        mock_project_timestamp.assert_called_once_with(project_id)
        mock_project_builder.return_value.entry_update.assert_called_once_with(
            form_initial, entry_type, str(entry_number)
        )
        mock_kebab_to_sentense.assert_called_once_with(entry_type)
        mock_std_context.assert_called_once_with(project_id)

    @patch("app.decorators._project_access")
    @patch("app.views.ProjectBuilder")
    @patch("app.views.EntryUpdateForm")
    @patch("app.views.kebab_to_sentense")
    @patch("app.views.std_context")
    def test_get_post_invalid_entry_number_1(
        self,
        mock_std_context,
        mock_kebab_to_sentense,
        mock_form,
        mock_project_builder,
        mock_project_access,
    ):
        project_id = 1
        setup_step = 2
        entry_type = "nonexistent_type"
        entry_number = 1
        form_initial = {"test": "test"}

        mock_project_access.return_value = (
            True,
            HttpResponse(),
            project_id,
            setup_step,
        )
        # mock_project_builder - used here
        mock_project_builder.return_value.entry_exists.return_value = True
        mock_project_builder.return_value.entry_type_exists.return_value = True
        # mock_form - used here
        mock_form.return_value.is_valid.return_value = False
        # mock_kebab_to_sentense - used here
        mock_std_context.return_value = {"test": "test"}

        response = self.client.post(
            f"/entry_update/{ project_id }/{ entry_type }/{ entry_number}",
            form_initial,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "entry_update.html")

        request = response.wsgi_request
        mock_project_access.assert_called_once_with(request, str(project_id))
        mock_project_builder.assert_called_once_with(project_id)
        mock_project_builder.return_value.entry_exists.assert_called_once_with(
            entry_type, str(project_id)
        )
        mock_project_builder.return_value.entry_type_exists.assert_called_once_with(
            entry_type
        )

        mock_form.assert_any_call(project_id, entry_type, request.POST)
        mock_form.return_value.is_valid.assert_called_once_with()
        mock_kebab_to_sentense.assert_called_once_with(entry_type)
        mock_std_context.assert_called_once_with(project_id)

    @patch("app.decorators._project_access")
    @patch("app.views.ProjectBuilder")
    @patch("app.views.EntryUpdateForm")
    @patch("app.views.kebab_to_sentense")
    @patch("app.views.std_context")
    def test_get_post_invalid_entry_new(
        self,
        mock_std_context,
        mock_kebab_to_sentense,
        mock_form,
        mock_project_builder,
        mock_project_access,
    ):
        project_id = 1
        setup_step = 2
        entry_type = "nonexistent_type"
        entry_number = "new"
        form_initial = {"test": "test"}

        mock_project_access.return_value = (
            True,
            HttpResponse(),
            project_id,
            setup_step,
        )
        # mock_project_builder - used here
        mock_project_builder.return_value.entry_type_exists.return_value = True
        # mock_form - used here
        mock_form.return_value.is_valid.return_value = False
        # mock_kebab_to_sentense - used here
        mock_std_context.return_value = {"test": "test"}

        response = self.client.post(
            f"/entry_update/{ project_id }/{ entry_type }/{ entry_number}",
            form_initial,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "entry_update.html")

        request = response.wsgi_request
        mock_project_access.assert_called_once_with(request, str(project_id))
        mock_project_builder.assert_called_once_with(project_id)
        mock_project_builder.return_value.entry_exists.assert_not_called()
        mock_project_builder.return_value.entry_type_exists.assert_called_once_with(
            entry_type
        )

        mock_form.assert_any_call(project_id, entry_type, request.POST)
        mock_form.return_value.is_valid.assert_called_once_with()
        mock_kebab_to_sentense.assert_called_once_with(entry_type)
        mock_std_context.assert_called_once_with(project_id)


class EntrySelectTest(TestCase):
    def setUp(self):
        log_in(self)
        project = Project.objects.create(
            id=1, owner=self.user, name="Test Project"
        )
        project.member.set([self.user])
        project_group = ProjectGroup.objects.create(id=1, name="Test Group")
        project_group.project_access.set([project])

    @patch("app.decorators._project_access")
    @patch("app.views.ProjectBuilder")
    def test_setup_step_1(self, mock_project_builder, mock_project_access):
        project_id = 1
        setup_step = 1
        entry_type = "hazard"

        mock_project_access.return_value = (
            True,
            HttpResponse(),
            project_id,
            setup_step,
        )
        # mock_project_builder - used here

        response = self.client.get(
            f"/entry_select/{ project_id }/{ entry_type }"
        )

        self.assertEqual(response.status_code, 302)

        request = response.wsgi_request
        mock_project_access.assert_called_once_with(request, str(project_id))
        mock_project_builder.assert_called_once_with(project_id)

    @patch("app.decorators._project_access")
    @patch("app.views.ProjectBuilder")
    def test_wrong_method(self, mock_project_builder, mock_project_access):
        project_id = 1
        setup_step = 2
        entry_type = "hazard"

        mock_project_access.return_value = (
            True,
            HttpResponse(),
            project_id,
            setup_step,
        )
        # mock_project_builder - used here

        response = self.client.post(
            f"/entry_select/{ project_id }/{ entry_type }", {}
        )

        self.assertEqual(response.status_code, 405)
        self.assertTemplateUsed(response, "error_handler.html")

        request = response.wsgi_request
        mock_project_access.assert_called_once_with(request, str(project_id))
        mock_project_builder.assert_called_once_with(project_id)

    @patch("app.decorators._project_access")
    @patch("app.views.ProjectBuilder")
    @patch("app.views.std_context")
    def test_entry_type_nonexistent(
        self, mock_std_context, mock_project_builder, mock_project_access
    ):
        project_id = 1
        setup_step = 2
        entry_type = "nonexistent_type"

        mock_project_access.return_value = (
            True,
            HttpResponse(),
            project_id,
            setup_step,
        )
        # mock_project_builder - used here
        mock_project_builder.return_value.entry_type_exists.return_value = (
            False
        )
        mock_std_context.return_value = {"test": "test"}

        response = self.client.get(
            f"/entry_select/{ project_id }/{ entry_type }"
        )

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "error_handler.html")

        request = response.wsgi_request
        mock_project_access.assert_called_once_with(request, str(project_id))
        mock_project_builder.assert_called_once_with(project_id)
        mock_project_builder.return_value.entry_type_exists.assert_called_once_with(
            entry_type
        )
        mock_std_context.assert_called_once_with()

    @patch("app.decorators._project_access")
    @patch("app.views.ProjectBuilder")
    @patch("app.views.kebab_to_sentense")
    @patch("app.views.std_context")
    def test_get(
        self,
        mock_std_context,
        mock_kebab_to_sentense,
        mock_project_builder,
        mock_project_access,
    ):
        project_id = 1
        setup_step = 2
        entry_type = "hazard"

        mock_project_access.return_value = (
            True,
            HttpResponse(),
            project_id,
            setup_step,
        )
        # mock_project_builder - used here
        mock_project_builder.return_value.entry_type_exists.return_value = True
        # mock_project_builder.return_value.entries_all_get.return_value - used here
        # mock_kebab_to_sentense - used here
        mock_std_context.return_value = {"test": "test"}

        response = self.client.get(
            f"/entry_select/{ project_id }/{ entry_type }"
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "entry_select.html")

        request = response.wsgi_request
        mock_project_access.assert_called_once_with(request, str(project_id))
        mock_project_builder.assert_called_once_with(project_id)
        mock_project_builder.return_value.entry_type_exists.assert_called_once_with(
            entry_type
        )
        mock_project_builder.return_value.entries_all_get.assert_called_once_with(
            entry_type
        )
        mock_kebab_to_sentense.assert_called_once_with(entry_type)
        mock_std_context.assert_called_once_with(project_id)


class UnderConstructionViewTest(TestCase):
    def test_valid(self):
        response = self.client.get("/under_construction/test_page")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test_page")
        self.assertContains(response, "Under contruction")


class StdContextTest(TestCase):
    @patch("app.views.ProjectBuilder")
    def test_std_context(self, mock_project_builder):
        project_id = 1
        entry_templates = ["template1", "template2"]

        mock_project_builder.return_value.entry_template_names.return_value = (
            entry_templates
        )

        result = views.std_context(project_id)

        self.assertEqual(result["entry_templates"], entry_templates)

        mock_project_builder.assert_called_once_with(project_id)
        mock_project_builder.return_value.entry_template_names.assert_called_once_with()

    @patch("app.views.ProjectBuilder")
    def test_std_context_with_project_id_0(self, mock_project_builder):
        mock_project_builder.return_value.entry_template_names.return_value = (
            []
        )

        result = views.std_context(0)

        self.assertEqual(result["entry_templates"], [])
        mock_project_builder.assert_not_called()


class UserAccessibleProjectsTest(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create_user(
            id=1, username="user_1", password="password_1"
        )  # nosec B106
        self.user_2 = User.objects.create_user(
            id=2, username="user_2", password="password_2"
        )  # nosec B106
        self.client = Client()
        self.client.login(
            username="user1", password="password_1"
        )  # nosec B106

    def test_no_records(self):
        request = HttpRequest()
        request.user = self.user_1

        documents = views.user_accessible_projects(request)

        self.assertEqual(documents, [])

    def test_user_has_no_access(self):
        project_id_1 = 1
        project_id_2 = 2
        project_name_1 = "Project 1"
        project_name_2 = "Project 2"
        project_1 = Project.objects.create(
            id=project_id_1, owner=self.user_2, name=project_name_1
        )
        project_2 = Project.objects.create(
            id=project_id_2, owner=self.user_2, name=project_name_2
        )
        UserProjectAttribute.objects.create(
            id=1,
            user=self.user_2,
            project=project_1,
            # last_accessed is set automatically
        )
        UserProjectAttribute.objects.create(
            id=2,
            user=self.user_2,
            project=project_2,
            # last_accessed is set automatically
        )

        request = HttpRequest()
        request.user = self.user_1

        documents = views.user_accessible_projects(request)

        self.assertEqual(documents, [])

    def test_owner(self):
        project_id_1 = 1
        project_id_2 = 2
        project_name_1 = "Project 1"
        project_name_2 = "Project 2"
        project_1 = Project.objects.create(
            id=project_id_1, owner=self.user_1, name=project_name_1
        )
        project_2 = Project.objects.create(
            id=project_id_2, owner=self.user_2, name=project_name_2
        )
        UserProjectAttribute.objects.create(
            id=1,
            user=self.user_2,
            project=project_1,
            # last_accessed is set automatically
        )
        UserProjectAttribute.objects.create(
            id=2,
            user=self.user_2,
            project=project_2,
            # last_accessed is set automatically
        )

        request = HttpRequest()
        request.user = self.user_1

        documents = views.user_accessible_projects(request)

        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0]["doc_id"], project_id_1)
        self.assertEqual(documents[0]["project_name"], project_name_1)
        current_datetime = datetime.now()
        difference = current_datetime - documents[0]["doc_last_accessed"]
        self.assertLess(difference, timedelta(minutes=5))

    def test_member(self):
        project_id_1 = 1
        project_id_2 = 2
        project_name_1 = "Project 1"
        project_name_2 = "Project 2"
        project_1 = Project.objects.create(
            id=project_id_1, owner=self.user_2, name=project_name_1
        )
        project_1.member.set([self.user_1])
        project_2 = Project.objects.create(
            id=project_id_2, owner=self.user_2, name=project_name_2
        )
        UserProjectAttribute.objects.create(
            id=1,
            user=self.user_1,
            project=project_1,
            # last_accessed is set automatically
        )
        UserProjectAttribute.objects.create(
            id=2,
            user=self.user_2,
            project=project_2,
            # last_accessed is set automatically
        )

        request = HttpRequest()
        request.user = self.user_1

        documents = views.user_accessible_projects(request)

        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0]["doc_id"], project_id_1)
        self.assertEqual(documents[0]["project_name"], project_name_1)
        current_datetime = datetime.now()
        difference = current_datetime - documents[0]["doc_last_accessed"]
        self.assertLess(difference, timedelta(minutes=5))

    def test_project_group_member(self):
        project_id_1 = 1
        project_id_2 = 2
        project_name_1 = "Project 1"
        project_name_2 = "Project 2"
        project_1 = Project.objects.create(
            id=project_id_1, owner=self.user_2, name=project_name_1
        )
        project_2 = Project.objects.create(
            id=project_id_2, owner=self.user_2, name=project_name_2
        )
        UserProjectAttribute.objects.create(
            id=1,
            user=self.user_1,
            project=project_1,
            # last_accessed is set automatically
        )
        UserProjectAttribute.objects.create(
            id=2,
            user=self.user_2,
            project=project_2,
            # last_accessed is set automatically
        )
        group_1 = ProjectGroup.objects.create(id=1, name="Test Group")
        group_1.project_access.set([project_1])
        group_1.member.set([self.user_1])

        request = HttpRequest()
        request.user = self.user_1

        documents = views.user_accessible_projects(request)

        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0]["doc_id"], project_id_1)
        self.assertEqual(documents[0]["project_name"], project_name_1)
        current_datetime = datetime.now()
        difference = current_datetime - documents[0]["doc_last_accessed"]
        self.assertLess(difference, timedelta(minutes=5))


class StartNewProjectStep2InputGUITestCase(TestCase):
    def setUp(self):
        self.group1 = ProjectGroup.objects.create(id=1, name="Group 1")
        self.group2 = ProjectGroup.objects.create(id=2, name="Group 2")
        self.user_1 = User.objects.create(
            id=1, username="user_1", first_name="John", last_name="Smith"
        )
        self.user_2 = User.objects.create(
            id=2, username="user_2", first_name="Jane", last_name="Doe"
        )

    @tag("run")
    def test_import(self):
        inputs = d.START_NEW_PROJECT_STEP_2_IMPORT_INPUTS

        expected_output = {
            "Setup choice": "Import",
            "External repository url": "www.github.com/test",
            "External repository username": "test_username",
            "External repository password / token": "***",
            "Project name": "Test project",
            "Description": "A test project",
            "Groups": "Group 1",
            "Members": "John Smith",
        }

        output = views.start_new_project_step_2_input_GUI(inputs)
        self.assertEqual(output, expected_output)

    def test_start_anew(self):
        inputs = d.START_NEW_PROJECT_STEP_2_START_ANEW_INPUTS

        expected_output = {
            "Setup choice": "Start anew",
            "Project name": "Test project",
            "Description": "A test project",
            "Groups": "Group 1",
            "Members": "John Smith",
        }

        output = views.start_new_project_step_2_input_GUI(inputs)
        self.assertEqual(output, expected_output)

    def test_start_anew_no_members_or_groups(self):
        inputs = {
            "setup_choice": "start_anew",
            "project_name": "Test project",
            "description": "A test project",
            "groups": [],
            "members": [],
        }

        expected_output = {
            "Setup choice": "Start anew",
            "Project name": "Test project",
            "Description": "A test project",
            "Groups": "<i>none selected</i>",
            "Members": "<i>none selected</i>",
        }

        output = views.start_new_project_step_2_input_GUI(inputs)
        self.assertEqual(output, expected_output)


class PlaceholdersTest(TestCase):
    def test_not_int(self):
        project_id = "not_int"

        result = views.placeholders(project_id)
        self.assertEquals(result, "")

    def test_project_nonexistent(self):
        project_id_1 = 1
        project_id_2 = 2
        project_name_1 = "Project 1"

        self.user_1 = User.objects.create_user(
            id=1, username="user_1", password="password_1"
        )  # nosec B106

        Project.objects.create(
            id=project_id_1, owner=self.user_1, name=project_name_1
        )

        result = views.placeholders(project_id_2)
        self.assertEquals(result, "")

    @patch("app.views.ProjectBuilder")
    def test_get_placeholders(self, mock_project_builder):
        project_id_1 = 1
        project_name_1 = "Project 1"
        placeholders = {
            "placeholder_1": "test_text",
            "placeholder_2": "test_text",
        }

        self.user_1 = User.objects.create_user(
            id=1, username="user_1", password="password_1"
        )  # nosec B106

        Project.objects.create(
            id=project_id_1, owner=self.user_1, name=project_name_1
        )

        # mock_project_builder - used here
        mock_project_builder.return_value.get_placeholders.return_value = (
            placeholders.copy()
        )

        result = views.placeholders(project_id_1)
        self.assertEquals(result, json.dumps(placeholders))

        mock_project_builder.assert_called_once_with(project_id_1)
        mock_project_builder.return_value.get_placeholders.assert_called_once_with()

    @patch("app.views.ProjectBuilder")
    def test_no_placeholders(self, mock_project_builder):
        project_id_1 = 1
        project_name_1 = "Project 1"
        placeholders = {}

        self.user_1 = User.objects.create_user(
            id=1, username="user_1", password="password_1"
        )  # nosec B106

        Project.objects.create(
            id=project_id_1, owner=self.user_1, name=project_name_1
        )

        # mock_project_builder - used here
        mock_project_builder.return_value.get_placeholders.return_value = (
            placeholders.copy()
        )
        result = views.placeholders(project_id_1)
        self.assertEquals(result, json.dumps(placeholders))

        mock_project_builder.assert_called_once_with(project_id_1)
        mock_project_builder.return_value.get_placeholders.assert_called_once_with()

    @patch("app.views.ProjectBuilder")
    def test_one_empty_placeholder(self, mock_project_builder):
        project_id_1 = 1
        project_name_1 = "Project 1"
        placeholders = {
            "placeholder_1": "test_text",
            "placeholder_empty": "",
        }
        placeholders_returned = {
            "placeholder_1": "test_text",
            "placeholder_empty": "[placeholder_empty undefined]",
        }

        self.user_1 = User.objects.create_user(
            id=1, username="user_1", password="password_1"
        )  # nosec B106

        Project.objects.create(
            id=project_id_1, owner=self.user_1, name=project_name_1
        )

        # mock_project_builder - used here
        mock_project_builder.return_value.get_placeholders.return_value = (
            placeholders.copy()
        )

        result = views.placeholders(project_id_1)

        self.assertEquals(result, json.dumps(placeholders_returned))

        mock_project_builder.assert_called_once_with(project_id_1)
        mock_project_builder.return_value.get_placeholders.assert_called_once_with()


class ProjectTimestampTest(TestCase):
    def test_nonexistent(self):
        project_id_1 = 1
        project_id_2 = 2
        project_name_1 = "Project 1"

        user_1 = User.objects.create_user(
            id=1, username="user_1", password="password_1"
        )  # nosec B106

        Project.objects.create(
            id=project_id_1, owner=user_1, name=project_name_1
        )

        result = views.project_timestamp(project_id_2)
        self.assertFalse(result)

    def test_exists(self):
        project_id_1 = 1
        project_name_1 = "Project 1"

        user_1 = User.objects.create_user(
            id=1, username="user_1", password="password_1"
        )  # nosec B106

        Project.objects.create(
            id=project_id_1,
            owner=user_1,
            name=project_name_1,
            last_modified=timezone.now() - timedelta(minutes=10),
        )

        project_before = Project.objects.get(id=project_id_1)
        timestamp_before = project_before.last_modified

        result = views.project_timestamp(project_id_1)
        self.assertTrue(result)

        project_after = Project.objects.get(id=project_id_1)
        timestamp_after = project_after.last_modified

        self.assertNotEqual(timestamp_before, timestamp_after)


@tag("run")
class Custom400Test(TestCase):
    @patch("app.views.std_context")
    def test_valid(self, mock_std_context):
        mock_std_context.return_value = {"test": "test"}

        response = views.custom_400(HttpRequest(), Exception())

        self.assertEqual(response.status_code, 400)
        self.assertTrue("400 - Bad request" in str(response.content))

        mock_std_context.assert_called_once_with()


@tag("run")
class Custom403Test(TestCase):
    @patch("app.views.std_context")
    def test_valid(self, mock_std_context):
        mock_std_context.return_value = {"test": "test"}

        response = views.custom_403(HttpRequest(), Exception())

        self.assertEqual(response.status_code, 403)
        self.assertTrue("403 - Forbidden access" in str(response.content))

        mock_std_context.assert_called_once_with()


@tag("run")
class Custom403CRSFTest(TestCase):
    @patch("app.views.std_context")
    def test_valid(self, mock_std_context):
        mock_std_context.return_value = {"test": "test"}

        response = views.custom_403_csrf(HttpRequest(), Exception())

        self.assertEqual(response.status_code, 403)
        self.assertTrue("403 - Forbidden access" in str(response.content))

        mock_std_context.assert_called_once_with()


@tag("run")
class Custom404Test(TestCase):
    @patch("app.views.std_context")
    def test_valid(self, mock_std_context):
        mock_std_context.return_value = {"test": "test"}

        response = views.custom_404(HttpRequest(), Exception())

        self.assertEqual(response.status_code, 404)
        self.assertTrue("404 - Page not found" in str(response.content))

        mock_std_context.assert_called_once_with()


@tag("run")
class Custom405Test(TestCase):
    @patch("app.views.std_context")
    def test_valid(self, mock_std_context):
        mock_std_context.return_value = {"test": "test"}

        response = views.custom_405(HttpRequest(), Exception())

        self.assertEqual(response.status_code, 405)
        self.assertTrue("405 - method not allowed" in str(response.content))

        mock_std_context.assert_called_once_with()


@tag("run")
class Custom500Test(TestCase):
    @patch("app.views.std_context")
    def test_valid(self, mock_std_context):
        mock_std_context.return_value = {"test": "test"}

        response = views.custom_500(HttpRequest(), Exception())

        self.assertEqual(response.status_code, 500)
        self.assertTrue("500 - Internal Server Error" in str(response.content))

        mock_std_context.assert_called_once_with()
