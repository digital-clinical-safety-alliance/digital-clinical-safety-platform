from unittest.mock import Mock, patch, call, MagicMock

from django.test import TestCase, tag, Client
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware

from app.functions.project_builder import ProjectBuilder
import app.functions.constants as c
import app.tests.data_project_builder as d
from app.models import ProjectGroup, Project


def log_in(self):
    self.user_1 = User.objects.create_user(
        id=1, username="user_1", password="password_1"
    )  # nosec B106
    self.user_2 = User.objects.create_user(
        id=2, username="user_2", password="password_2"
    )  # nosec B106
    self.client = Client()
    self.client.login(username="user_1", password="password_1")  # nosec B106
    return


class InitialisationTest(TestCase):
    def test_initialise_string(self):
        project_id = "one"
        with self.assertRaises(TypeError):
            ProjectBuilder(project_id)

    def test_initialise_0(self):
        project_id = 0
        project = ProjectBuilder(project_id)
        self.assertTrue(project.new_build_flag)

    def test_initialise_1(self):
        project_id = 1
        project = ProjectBuilder(project_id)
        self.assertFalse(project.new_build_flag)

    def test_initialise_minus_1(self):
        project_id = -1
        with self.assertRaises(ValueError):
            ProjectBuilder(project_id)

    def test_no_wrapper_new_build(self):
        project_id = 0
        project = ProjectBuilder(project_id)
        project.test_no_wrapper()

    def test_no_wrapper_old_build(self):
        project_id = 1
        project = ProjectBuilder(project_id)
        project.new_build_flag = False
        try:
            project.test_no_wrapper()
        except SyntaxError:
            self.fail("Raised SyntaxError unexpectedly!")

    def test_with_wrapper_new_build(self):
        project_id = 0
        project = ProjectBuilder(project_id)
        project.new_build_flag = True
        with self.assertRaises(SyntaxError):
            project.test_with_wrapper()

    def test_with_wrapper_old_build(self):
        project_id = 1
        project = ProjectBuilder(project_id)
        project.new_build_flag = False
        try:
            project.test_with_wrapper()
        except SyntaxError:
            self.fail("Raised SyntaxError unexpectedly!")


class NewBuildTest(TestCase):
    def setUp(self):
        log_in(self)

        self.project_id = 0
        self.project = ProjectBuilder(self.project_id)

        ProjectGroup.objects.create(id=1, name="Test Group")

    def test_id_is_string(self):
        factory = RequestFactory()
        # url does not matter here
        request = factory.get("/")

        middleware = SessionMiddleware(lambda req: HttpResponse())
        middleware.process_request(request)
        request.session.save()

        request.session["inputs"] = {}

        mock_user = MagicMock()
        mock_user.id = MagicMock(return_value="non-integer-id")
        request.user = mock_user

        pass_result, message = self.project.new_build(request)

        self.assertFalse(pass_result)
        self.assertEqual(
            message, "User id could not be converted to an integer"
        )

        mock_user.id.called

    def test_setup_choice_bad(self):
        factory = RequestFactory()

        # url does not matter here
        request = factory.get("/")

        middleware = SessionMiddleware(lambda req: HttpResponse())
        middleware.process_request(request)
        request.session.save()
        request.session["inputs"] = {"setup_choice": "bad choice"}
        request.user = self.user_1

        pass_result, message = self.project.new_build(request)

        self.assertFalse(pass_result)
        self.assertEqual(message, "'setup_choice' is incorrectly set")

    def test_input_data_missing(self):
        for repository_key in d.REPO_INPUTS_1:
            factory = RequestFactory()

            # url does not matter here
            request = factory.get("/")

            middleware = SessionMiddleware(lambda req: HttpResponse())
            middleware.process_request(request)
            request.session.save()
            inputs = d.REPO_INPUTS_1.copy()
            inputs.pop(repository_key)
            request.session["inputs"] = inputs
            request.user = self.user_1

            pass_result, message = self.project.new_build(request)

            self.assertFalse(pass_result)
            self.assertEqual(message, f"'{ repository_key }' not set")

    @patch("app.functions.project_builder.GitHubController")
    def test_setup_external_respository_url_bad(self, mock_github_controller):
        factory = RequestFactory()

        # url does not matter here
        request = factory.get("/")

        middleware = SessionMiddleware(lambda req: HttpResponse())
        middleware.process_request(request)
        request.session.save()
        inputs = d.REPO_INPUTS_1.copy()
        inputs.update(d.REPO_INPUTS_2.copy())

        request.session["inputs"] = inputs
        request.user = self.user_1

        # mock_github_controller used here
        mock_github_controller.return_value.repository_exists.return_value = (
            False
        )

        pass_result, message = self.project.new_build(request)

        self.assertFalse(pass_result)
        self.assertEqual(
            message,
            (
                "The external repository "
                f"'{ inputs['external_repository_url_import'] }' "
                "does not exist or is not accessible with your credentials"
            ),
        )

        mock_github_controller.assert_called_once_with(
            inputs["external_repository_username_import"],
            inputs["external_repository_password_token_import"],
        )

        mock_github_controller.return_value.repository_exists.assert_called_once_with(
            inputs["external_repository_url_import"]
        )

    def test_external_repository_not_github(self):
        factory = RequestFactory()

        # url does not matter here
        request = factory.get("/")

        middleware = SessionMiddleware(lambda req: HttpResponse())
        middleware.process_request(request)
        request.session.save()
        inputs = d.REPO_INPUTS_1.copy()
        inputs.update(d.REPO_INPUTS_2.copy())
        inputs["repository_type"] = "not_github"

        request.session["inputs"] = inputs
        request.user = self.user_1

        pass_result, message = self.project.new_build(request)

        self.assertFalse(pass_result)
        self.assertEqual(
            message,
            ("Code for other external repositories is not yet written."),
        )

    @tag("run")
    @patch("app.functions.project_builder.GitHubController")
    @patch("app.functions.project_builder.Path")
    def test_project_directory_already_exists(
        self, mock_path, mock_github_controller
    ):
        project_id = 1

        factory = RequestFactory()

        # url does not matter here
        request = factory.get("/")

        middleware = SessionMiddleware(lambda req: HttpResponse())
        middleware.process_request(request)
        request.session.save()
        inputs = d.REPO_INPUTS_1.copy()
        inputs.update(d.REPO_INPUTS_2.copy())

        request.session["inputs"] = inputs
        request.user = self.user_1

        # mock_github_controller used here
        mock_github_controller.return_value.repository_exists.return_value = (
            True
        )

        mock_path.return_value.is_dir.return_value = True

        pass_result, message = self.project.new_build(request)
        project_directory = (
            f"{ c.PROJECTS_FOLDER }project_{ request.session['project_id'] }/"
        )
        self.assertFalse(pass_result)
        self.assertEqual(
            message,
            f"'{ project_directory }' already exists",
        )

        mock_github_controller.assert_called_once_with(
            inputs["external_repository_username_import"],
            inputs["external_repository_password_token_import"],
        )

        mock_github_controller.return_value.repository_exists.assert_called_once_with(
            inputs["external_repository_url_import"]
        )

        mock_path.assert_called_once_with(project_directory)
        mock_path.return_value.is_dir.assert_called_once_with()

    @patch("app.functions.project_builder.GitHubController")
    @patch("app.functions.project_builder.Path")
    @patch("app.functions.project_builder.GitController")
    def test_all_valid(
        self, mock_git_controller, mock_path, mock_github_controller
    ):
        factory = RequestFactory()

        # url does not matter here
        request = factory.get("/")

        middleware = SessionMiddleware(lambda req: HttpResponse())
        middleware.process_request(request)
        request.session.save()
        inputs = d.REPO_INPUTS_1.copy()
        inputs.update(d.REPO_INPUTS_2.copy())

        request.session["inputs"] = inputs
        request.user = self.user_1

        # mock_github_controller used here
        mock_github_controller.return_value.repository_exists.return_value = (
            True
        )

        # mock_path.return_value.is_dir used here
        # mock_path.return_value.mkdir used here

        mock_path.return_value.is_dir.side_effect = [False, False]

        # mock_git_controller used here
        # mock_git_controller.return_value.clone.return_value used here

        pass_result, message = self.project.new_build(request)

        self.assertTrue(pass_result)
        self.assertEqual(message, "All passed")

        mock_github_controller.assert_called_once_with(
            inputs["external_repository_username_import"],
            inputs["external_repository_password_token_import"],
        )

        mock_github_controller.return_value.repository_exists.assert_called_once_with(
            inputs["external_repository_url_import"]
        )

        self.assertEqual(mock_path.call_count, 4)
        self.assertEqual(mock_path.return_value.is_dir.call_count, 2)


@tag("run")
class DocumentTemplatesGetTest(TestCase):
    pass
