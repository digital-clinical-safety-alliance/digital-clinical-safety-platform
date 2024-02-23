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
from app.functions.custom_exceptions import RepositoryAccessException


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

        with self.assertRaises(TypeError) as error:
            ProjectBuilder(project_id)
        self.assertEqual(
            str(error.exception),
            f"'project_id' '{ project_id }' is not an integer",
        )

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
        with self.assertRaises(ValueError) as error:
            ProjectBuilder(project_id)
        self.assertEqual(
            str(error.exception),
            f"'project_id' '{ project_id }' is not a positive integer",
        )


class DecoratorTest(TestCase):
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
        with self.assertRaises(SyntaxError) as error:
            project.test_with_wrapper()
        self.assertEqual(
            str(error.exception),
            "This function is not allowed for a new-build project (with no primary key)",
        )

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

        with self.assertRaises(ValueError) as error:
            self.project.new_build(request)
        self.assertEqual(
            str(error.exception),
            "User id could not be converted to an integer",
        )

        mock_user.id.called

    def test_setup_choice_missing(self):
        factory = RequestFactory()

        # url does not matter here
        request = factory.get("/")

        middleware = SessionMiddleware(lambda req: HttpResponse())
        middleware.process_request(request)
        request.session.save()
        request.session["inputs"] = {}
        request.user = self.user_1

        with self.assertRaises(KeyError) as error:
            self.project.new_build(request)

        # Need to strip double qoutes (eg ") as KeyError adds them
        self.assertEqual(
            str(error.exception).strip('"'),
            "'setup_choice' not set",
        )

    def test_setup_choice_bad_choice(self):
        factory = RequestFactory()

        # url does not matter here
        request = factory.get("/")

        middleware = SessionMiddleware(lambda req: HttpResponse())
        middleware.process_request(request)
        request.session.save()
        request.session["inputs"] = {"setup_choice": "bad choice"}
        request.user = self.user_1

        with self.assertRaises(ValueError) as error:
            self.project.new_build(request)
        self.assertEqual(
            str(error.exception),
            "'setup_choice' is incorrectly set",
        )

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

            with self.assertRaises(KeyError) as error:
                self.project.new_build(request)
            self.assertEqual(
                str(error.exception).strip('"'),
                f"'{ repository_key }' not set",
            )

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

        with self.assertRaises(RepositoryAccessException) as error:
            self.project.new_build(request)
        self.assertEqual(
            str(error.exception),
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

        with self.assertRaises(NotImplementedError) as error:
            self.project.new_build(request)
        self.assertEqual(
            str(error.exception),
            "Code for other external repositories is not yet written.",
        )

    @patch("app.functions.project_builder.GitHubController")
    @patch("app.functions.project_builder.Path")
    def test_project_directory_already_exists(
        self, mock_path, mock_github_controller
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

        mock_path.return_value.is_dir.return_value = True

        with self.assertRaises(FileExistsError) as error:
            self.project.new_build(request)

        project_directory = (
            f"{ c.PROJECTS_FOLDER }project_{ request.session['project_id'] }/"
        )
        self.assertEqual(
            str(error.exception),
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

        self.project.new_build(request)

        mock_github_controller.assert_called_once_with(
            inputs["external_repository_username_import"],
            inputs["external_repository_password_token_import"],
        )

        mock_github_controller.return_value.repository_exists.assert_called_once_with(
            inputs["external_repository_url_import"]
        )

        self.assertEqual(mock_path.call_count, 4)
        self.assertEqual(mock_path.return_value.is_dir.call_count, 2)


class MasterTemplateGetTest(TestCase):
    @patch("app.functions.project_builder.Path")
    def test_no_templates(self, mock_path):
        project_id = 0

        mock_path_instance = Mock()
        mock_path_instance.iterdir.return_value = []
        mock_path.return_value = mock_path_instance

        project = ProjectBuilder(project_id)

        with self.assertRaises(FileNotFoundError) as error:
            project.master_template_get()
        self.assertEqual(
            str(error.exception),
            f"No templates folders found in '{ c.MASTER_TEMPLATES }' template directory",
        )

        mock_path.assert_called_once_with(c.MASTER_TEMPLATES)
        mock_path_instance.iterdir.assert_called_once_with()

    @patch("app.functions.project_builder.Path")
    def test_valid(self, mock_path):
        project_id = 0
        templates = ["template_1", "template_2"]

        mock_dir1 = Mock()
        mock_dir1.is_dir.return_value = True
        mock_dir1.name = templates[0]

        mock_dir2 = Mock()
        mock_dir2.is_dir.return_value = True
        mock_dir2.name = templates[1]

        mock_path_instance = Mock()
        mock_path_instance.iterdir.return_value = [mock_dir1, mock_dir2]
        mock_path.return_value = mock_path_instance

        project = ProjectBuilder(project_id)
        returned = project.master_template_get()

        self.assertEqual(returned, templates)

        mock_path.assert_called_once_with(c.MASTER_TEMPLATES)
        mock_path_instance.iterdir.assert_called_once_with()

        mock_dir1.is_dir.assert_called_once_with()
        mock_dir2.is_dir.assert_called_once_with()

    @patch("app.functions.project_builder.Path")
    def test_sorted_from_reverse(self, mock_path):
        project_id = 0
        templates = ["template_1", "template_2"]
        templates_reverse = ["template_2", "template_1"]

        mock_dir1 = Mock()
        mock_dir1.is_dir.return_value = True
        mock_dir1.name = templates_reverse[0]

        mock_dir2 = Mock()
        mock_dir2.is_dir.return_value = True
        mock_dir2.name = templates_reverse[1]

        mock_path_instance = Mock()
        mock_path_instance.iterdir.return_value = [mock_dir1, mock_dir2]
        mock_path.return_value = mock_path_instance

        project = ProjectBuilder(project_id)
        returned = project.master_template_get()

        self.assertEqual(returned, templates)

        mock_path.assert_called_once_with(c.MASTER_TEMPLATES)
        mock_path_instance.iterdir.assert_called_once_with()

        mock_dir1.is_dir.assert_called_once_with()
        mock_dir2.is_dir.assert_called_once_with()


class ConfigurationGetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.project_id = 1
        cls.safety_directory = f"{ c.PROJECTS_FOLDER }project_{ cls.project_id }/{ c.CLINICAL_SAFETY_FOLDER }"
        cls.configration_file = f"{  cls.safety_directory }setup.ini"

    @patch("app.functions.project_builder.Path")
    def test_folder_missing(self, mock_path):
        mock_path.return_value.is_dir.return_value = False

        config = ProjectBuilder(self.project_id)

        with self.assertRaises(FileNotFoundError) as error:
            config.configuration_get()
        self.assertEqual(
            str(error.exception), f"'{ self.safety_directory }' does not exist"
        )

        mock_path.assert_called_once_with(self.safety_directory)
        mock_path.return_value.is_dir.assert_called_once_with()

    @patch("app.functions.project_builder.Path")
    @patch("app.functions.project_builder.ENVManipulator")
    def test_non_digit(self, mock_env_manipulator, mock_path):
        mock_path.return_value.is_dir.return_value = True
        # mock_env_manipulator used here
        mock_env_manipulator.return_value.read.return_value = "not a number"

        config = ProjectBuilder(self.project_id)
        returned = config.configuration_get()
        self.assertEqual(returned, {"setup_step": 1})

        mock_path.assert_called_once_with(self.safety_directory)
        mock_path.return_value.is_dir.assert_called_once_with()
        mock_env_manipulator.assert_called_once_with(self.configration_file)

    @patch("app.functions.project_builder.Path")
    @patch("app.functions.project_builder.ENVManipulator")
    def test_valid(self, mock_env_manipulator, mock_path):
        mock_path.return_value.is_dir.return_value = True
        # mock_env_manipulator used here
        mock_env_manipulator.return_value.read.return_value = "2"

        config = ProjectBuilder(self.project_id)
        returned = config.configuration_get()
        self.assertEqual(returned, {"setup_step": 2})

        mock_path.assert_called_once_with(self.safety_directory)
        mock_path.return_value.is_dir.assert_called_once_with()
        mock_env_manipulator.assert_called_once_with(self.configration_file)


class ConfigurationSetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.project_id = 1
        cls.safety_directory = f"{ c.PROJECTS_FOLDER }project_{ cls.project_id }/{ c.CLINICAL_SAFETY_FOLDER }"
        cls.configration_file = f"{  cls.safety_directory }setup.ini"

    @patch("app.functions.project_builder.Path")
    def test_folder_missing(self, mock_path):
        mock_path.return_value.is_dir.return_value = False

        config = ProjectBuilder(self.project_id)

        with self.assertRaises(FileNotFoundError) as error:
            config.configuration_set("setup_step", 1)
        self.assertEqual(
            str(error.exception), f"'{ self.safety_directory }' does not exist"
        )

    @patch("app.functions.project_builder.Path")
    @patch("app.functions.project_builder.ENVManipulator")
    def test_valid(self, mock_env_manipulator, mock_path):
        mock_path.return_value.is_dir.return_value = True
        # mock_env_manipulator used here
        # mock_env_manipulator.return_value.add used here

        config = ProjectBuilder(self.project_id)
        self.assertTrue(config.configuration_set("setup_step", 1))

        mock_path.assert_called_once_with(self.safety_directory)
        mock_path.return_value.is_dir.assert_called_once_with()
        mock_env_manipulator.assert_called_once_with(self.configration_file)
        mock_env_manipulator.return_value.add.assert_called_once_with(
            "setup_step", "1"
        )


class CopyTemplatesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.project_id = 1

    @patch("app.functions.project_builder.Path")
    def test_folder_missing(self, mock_path):
        template = "template_1"
        template_chosen_path: str = f"{ c.MASTER_TEMPLATES }{ template }"

        mock_path.return_value.is_dir.return_value = False

        project_builder = ProjectBuilder(self.project_id)

        with self.assertRaises(FileNotFoundError) as error:
            project_builder.copy_master_template(template)
        self.assertEqual(
            str(error.exception), f"'{ template_chosen_path }' does not exist"
        )

    @patch("app.functions.project_builder.Path")
    @patch("app.functions.project_builder.shutil")
    def test_valid(self, mock_shutil, mock_path):
        template = "template_1"
        mock_path.return_value.is_dir.return_value = True

        project_builder = ProjectBuilder(self.project_id)
        project_builder.copy_master_template(template)

        mock_path.assert_called_once_with(f"{ c.MASTER_TEMPLATES}{ template }")
        mock_path.return_value.is_dir.assert_called_once_with()
        mock_shutil.copytree.assert_called_once_with(
            f"{ c.MASTER_TEMPLATES }{ template }",
            f"{ c.PROJECTS_FOLDER }project_{ self.project_id }/{ c.CLINICAL_SAFETY_FOLDER }",
            dirs_exist_ok=True,
        )


class GetPlaceholdersTest(TestCase):
    pass
