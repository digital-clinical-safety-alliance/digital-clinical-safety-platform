from unittest.mock import Mock, patch, call, MagicMock
from pathlib import Path

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
    @classmethod
    def setUpTestData(cls):
        cls.project_id = 1
        cls.project = ProjectBuilder(cls.project_id)
        cls.docs_dir = f"{ c.PROJECTS_FOLDER }project_{ cls.project_id }/{ c.CLINICAL_SAFETY_FOLDER }docs/"

    @patch("app.functions.project_builder.Path")
    def test_no_files_found(self, mock_path):
        mock_path.return_value.rglob.return_value = []

        with self.assertRaises(FileNotFoundError) as error:
            self.project.get_placeholders()
        self.assertEqual(
            str(error.exception),
            f"No files found in mkdocs '{ self.docs_dir }' folder",
        )

        mock_path.return_value.rglob.assert_called_once_with("*.md")

    @patch("app.functions.project_builder.Path")
    @patch("app.functions.project_builder.open")
    @patch("app.functions.project_builder.ProjectBuilder.read_placeholders")
    def test_no_placeholders_found(
        self, mock_read_placeholders, mock_open, mock_path
    ):
        mock_path.return_value.rglob.return_value = [
            "file1.md",
            "file2.md",
            "file3.md",
        ]

        # mock_open used here

        mock_open.return_value.read.side_effect = [
            "no placeholders",
            "no placeholders",
            "no placeholders",
        ]

        mock_path.return_value.exists.return_value = True

        mock_read_placeholders.return_value = d.GET_PLACEHOLDERS_STORED

        returned = self.project.get_placeholders()

        self.assertEqual(returned, {})

        mock_path.return_value.rglob.assert_called_once_with("*.md")
        self.assertEqual(
            mock_open.call_args_list,
            [
                call("file1.md", "r"),
                call("file2.md", "r"),
                call("file3.md", "r"),
            ],
        )
        self.assertEqual(
            mock_open.return_value.read.call_args_list,
            [call(), call(), call()],
        )
        mock_path.return_value.exists.assert_called_once_with()
        mock_read_placeholders.assert_called_once_with()

    @patch("app.functions.project_builder.Path")
    @patch("app.functions.project_builder.open")
    @patch("app.functions.project_builder.ProjectBuilder.read_placeholders")
    def test_no_stored_placeholders(
        self, mock_read_placeholders, mock_open, mock_path
    ):
        mock_path.return_value.rglob.return_value = [
            "file1.md",
            "file2.md",
            "file3.md",
        ]

        # mock_open used here

        mock_open.return_value.read.side_effect = [
            "{{placeholder1}} {{placeholder2}}",
            "{{placeholder3}} {{placeholder4}}",
            "{{placeholder5}} {{placeholder6}}",
        ]

        mock_path.return_value.exists.return_value = False

        # mock_read_placeholders not read here

        returned = self.project.get_placeholders()

        self.assertEqual(returned, d.PLACEHOLDERS_EMPTY)

        mock_path.return_value.rglob.assert_called_once_with("*.md")
        self.assertEqual(
            mock_open.call_args_list,
            [
                call("file1.md", "r"),
                call("file2.md", "r"),
                call("file3.md", "r"),
            ],
        )
        self.assertEqual(
            mock_open.return_value.read.call_args_list,
            [call(), call(), call()],
        )
        mock_path.return_value.exists.assert_called_once_with()
        mock_read_placeholders.assert_not_called()

    @patch("app.functions.project_builder.Path")
    @patch("app.functions.project_builder.open")
    @patch("app.functions.project_builder.ProjectBuilder.read_placeholders")
    def test_valid(self, mock_read_placeholders, mock_open, mock_path):
        mock_path.return_value.rglob.return_value = [
            "file1.md",
            "file2.md",
            "file3.md",
        ]

        # mock_open used here

        mock_open.return_value.read.side_effect = [
            "{{placeholder1}} {{placeholder2}}",
            "{{placeholder3}} {{placeholder4}}",
            "{{placeholder5}} {{placeholder6}}",
        ]

        mock_path.return_value.exists.return_value = True

        mock_read_placeholders.return_value = d.GET_PLACEHOLDERS_STORED

        returned = self.project.get_placeholders()

        self.assertEqual(returned, d.GET_PLACEHOLDERS_STORED)

        mock_path.return_value.rglob.assert_called_once_with("*.md")
        self.assertEqual(
            mock_open.call_args_list,
            [
                call("file1.md", "r"),
                call("file2.md", "r"),
                call("file3.md", "r"),
            ],
        )
        self.assertEqual(
            mock_open.return_value.read.call_args_list,
            [call(), call(), call()],
        )
        mock_path.return_value.exists.assert_called_once_with()
        mock_read_placeholders.assert_called_once_with()


class SavePlaceholdersTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.project_id = 1
        cls.safety_directory = f"{ c.PROJECTS_FOLDER }project_{ cls.project_id }/{ c.CLINICAL_SAFETY_FOLDER }"
        cls.placeholders_yaml = f"{ cls.safety_directory }placeholders.yml"

        cls.project_builder = ProjectBuilder(cls.project_id)

    @patch("app.functions.project_builder.Path")
    def test_folder_missing(self, mock_path):
        mock_path.return_value.is_dir.return_value = False

        with self.assertRaises(FileNotFoundError) as error:
            self.project_builder.save_placeholders({})
        self.assertEqual(
            str(error.exception),
            f"'{ self.safety_directory }' does not exist",
        )

        mock_path.assert_called_once_with(self.safety_directory)
        mock_path.return_value.is_dir.assert_called_once_with()

    @patch("app.functions.project_builder.Path")
    @patch("app.functions.project_builder.open")
    @patch("app.functions.project_builder.yaml")
    def test_valid(self, mock_yaml, mock_open, mock_path):
        mock_path.return_value.is_dir.return_value = True

        mock_instance = Mock()

        mock_open.return_value.__enter__.return_value = mock_instance

        # mock_yaml used here

        self.project_builder.save_placeholders(d.GET_PLACEHOLDERS_STORED)

        mock_path.assert_called_once_with(self.safety_directory)
        mock_path.return_value.is_dir.assert_called_once_with()
        mock_open.assert_called_once_with(self.placeholders_yaml, "w")
        mock_yaml.dump.assert_called_once_with(
            {"extra": d.GET_PLACEHOLDERS_STORED}, mock_instance
        )


class SavePlaceholdersFromFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.project_id = 1
        cls.safety_directory = f"{ c.PROJECTS_FOLDER }project_{ cls.project_id }/{ c.CLINICAL_SAFETY_FOLDER }"
        cls.placeholders_yaml = f"{ cls.safety_directory }placeholders.yml"

        cls.project_builder = ProjectBuilder(cls.project_id)

    @patch("app.functions.project_builder.ProjectBuilder.get_placeholders")
    @patch("app.functions.project_builder.ProjectBuilder.save_placeholders")
    def test_valid(self, mock_save_placeholders, mock_get_placeholders):
        mock_get_placeholders.return_value = d.GET_PLACEHOLDERS_STORED

        mock_form = MagicMock()
        mock_form.cleaned_data = d.GET_PLACEHOLDERS_STORED

        self.project_builder.save_placeholders_from_form(mock_form)

        mock_get_placeholders.assert_called_once_with()
        mock_save_placeholders.assert_called_once_with(
            d.GET_PLACEHOLDERS_STORED
        )


class ReadPlaceholdersFromFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.project_id = 1
        cls.safety_directory = f"{ c.PROJECTS_FOLDER }project_{ cls.project_id }/{ c.CLINICAL_SAFETY_FOLDER }"
        cls.placeholders_yaml = f"{ cls.safety_directory }placeholders.yml"

        cls.project_builder = ProjectBuilder(cls.project_id)

    @patch("app.functions.project_builder.Path")
    def test_yaml_file_missing(self, mock_path):
        mock_path.return_value.is_file.return_value = False

        with self.assertRaises(FileNotFoundError) as error:
            self.project_builder.read_placeholders()
        self.assertEqual(
            str(error.exception),
            f"'{ self.placeholders_yaml }' is not a valid path",
        )

        mock_path.assert_called_once_with(self.placeholders_yaml)
        mock_path.return_value.is_file.assert_called_once_with()

    @patch("app.functions.project_builder.Path")
    @patch("app.functions.project_builder.open")
    @patch("app.functions.project_builder.yaml")
    def test_yaml_bad_contents(self, mock_yaml, mock_open, mock_path):
        mock_path.return_value.is_file.return_value = True

        mock_instance = Mock()
        mock_open.return_value.__enter__.return_value = mock_instance

        mock_yaml.safe_load.return_value = {}

        with self.assertRaises(ValueError) as error:
            self.project_builder.read_placeholders()
        self.assertEqual(
            str(error.exception),
            "Error with placeholders yaml file, likely 'extra' missing from file",
        )

        mock_path.assert_called_once_with(self.placeholders_yaml)
        mock_path.return_value.is_file.assert_called_once_with()
        mock_open.assert_called_once_with(self.placeholders_yaml, "r")
        mock_yaml.safe_load.assert_called_once_with(mock_instance)

    @patch("app.functions.project_builder.Path")
    @patch("app.functions.project_builder.open")
    @patch("app.functions.project_builder.yaml")
    def test_yaml_valid(self, mock_yaml, mock_open, mock_path):
        mock_path.return_value.is_file.return_value = True

        mock_instance = Mock()
        mock_open.return_value.__enter__.return_value = mock_instance

        mock_yaml.safe_load.return_value = {"extra": d.GET_PLACEHOLDERS_STORED}

        return_values = self.project_builder.read_placeholders()

        self.assertEqual(return_values, d.GET_PLACEHOLDERS_STORED)

        mock_path.assert_called_once_with(self.placeholders_yaml)
        mock_path.return_value.is_file.assert_called_once_with()
        mock_open.assert_called_once_with(self.placeholders_yaml, "r")
        mock_yaml.safe_load.assert_called_once_with(mock_instance)


class EntryExistsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.project_id = 1
        cls.safety_directory = f"{ c.PROJECTS_FOLDER }project_{ cls.project_id }/{ c.CLINICAL_SAFETY_FOLDER }"
        cls.placeholders_yaml = f"{ cls.safety_directory }placeholders.yml"

        cls.entry_type = "hazard"

        cls.project_builder = ProjectBuilder(cls.project_id)

    def test_id_is_string(self):
        entry_id = "one"

        with self.assertRaises(ValueError) as error:
            self.project_builder.entry_exists(self.entry_type, entry_id)
        self.assertEqual(
            str(error.exception),
            f"'id' '{ entry_id }' is not an integer",
        )

    def test_id_is_zero(self):
        entry_id = 0

        with self.assertRaises(ValueError) as error:
            self.project_builder.entry_exists(self.entry_type, entry_id)
        self.assertEqual(
            str(error.exception),
            f"'id' '{ entry_id }' is not a positive integer",
        )

    @patch("app.functions.project_builder.Path")
    def test_exists(self, mock_path):
        entry_id = 1
        file_to_find: str = f"{ self.entry_type }-{ entry_id }.md"

        mock_path.return_value.rglob.return_value = [file_to_find]

        self.assertTrue(
            self.project_builder.entry_exists(self.entry_type, entry_id)
        )
        mock_path.assert_called_once_with(
            f"{ c.PROJECTS_FOLDER }project_{ self.project_id }/{ c.CLINICAL_SAFETY_FOLDER }docs/{ self.entry_type }s/{ self.entry_type }s/"
        )
        mock_path.return_value.rglob.assert_called_once_with(file_to_find)

    @patch("app.functions.project_builder.Path")
    def test_does_not_exist(self, mock_path):
        entry_id = 1
        file_to_find: str = f"{ self.entry_type }-{ entry_id }.md"

        mock_path.return_value.rglob.return_value = []

        self.assertFalse(
            self.project_builder.entry_exists(self.entry_type, entry_id)
        )
        mock_path.assert_called_once_with(
            f"{ c.PROJECTS_FOLDER }project_{ self.project_id }/{ c.CLINICAL_SAFETY_FOLDER }docs/{ self.entry_type }s/{ self.entry_type }s/"
        )
        mock_path.return_value.rglob.assert_called_once_with(file_to_find)


class EntryFileReadTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.project_id = 1
        cls.safety_directory = f"{ c.PROJECTS_FOLDER }project_{ cls.project_id }/{ c.CLINICAL_SAFETY_FOLDER }"
        cls.placeholders_yaml = f"{ cls.safety_directory }placeholders.yml"

        cls.entry_type = "hazard"
        cls.template_path = f"{ cls.safety_directory }templates/{ cls.entry_type }{ c.ENTRY_TEMPLATE_SUFFIX }"

        cls.project_builder = ProjectBuilder(cls.project_id)

    @patch("app.functions.project_builder.Path")
    def test_path_nonexistent_template(self, mock_path):
        file_path = "nonexistent.md"
        mock_path.return_value.is_file.return_value = False

        with self.assertRaises(FileNotFoundError) as error:
            self.project_builder.entry_file_read(self.entry_type, file_path)

        mock_path.assert_called_once_with(file_path)
        mock_path.return_value.is_file.assert_called_once_with()

    @patch("app.functions.project_builder.Path")
    def test_path_nonexistent_instance(self, mock_path):
        mock_path.return_value.is_file.return_value = False

        with self.assertRaises(FileNotFoundError) as error:
            self.project_builder.entry_file_read(self.entry_type)

        mock_path.assert_called_once_with(self.template_path)
        mock_path.return_value.is_file.assert_called_once_with()

    @patch("app.functions.project_builder.Path")
    @patch("app.functions.project_builder.open")
    def test_path_nonexistent_instance(self, mock_open, mock_path):
        mock_path.return_value.is_file.return_value = True

        mock_open.return_value.read.return_value = d.TEMPLATE_CONTENTS

        return_values = self.project_builder.entry_file_read(self.entry_type)

        self.assertEqual(return_values, d.TEMPLATE_LIST)

        mock_path.assert_called_once_with(self.template_path)
        mock_path.return_value.is_file.assert_called_once_with()


class EntryReadWithFieldTypesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.project_id = 1
        cls.entry_type = "hazard"
        cls.project_builder = ProjectBuilder(cls.project_id)

    @patch.object(ProjectBuilder, "entry_file_read")
    def test_valid(self, mock_entry_file_read):
        entry_file_path = "test_path.md"

        mock_entry_file_read.side_effect = [
            d.ENTRY_INSRTANCE,
            d.ENTRY_TEMPLATE,
        ]

        result = self.project_builder.entry_read_with_field_types(
            self.entry_type, entry_file_path
        )

        self.assertEqual(result, d.EXPECTED_FIELD_ADDED_RESULT)

        mock_entry_file_read.assert_any_call(self.entry_type, entry_file_path)
        mock_entry_file_read.assert_any_call(self.entry_type)


class HeadingNumberingTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.project_id = 1
        cls.entry_type = "hazard"
        cls.project_builder = ProjectBuilder(cls.project_id)

    def test_heading_numbering_no_duplicate(self):
        heading = "Test Heading"
        content_list = [{"heading": "Different Heading"}]
        expected_result = "Test Heading"
        result = self.project_builder._heading_numbering(heading, content_list)
        self.assertEqual(result, expected_result)

    def test_heading_numbering_with_duplicate(self):
        heading = "Test Heading"
        content_list = [{"heading": "Test Heading"}]
        expected_result = "Test Heading [2]"
        result = self.project_builder._heading_numbering(heading, content_list)
        self.assertEqual(result, expected_result)

    def test_heading_numbering_with_multiple_duplicates(self):
        heading = "Test Heading"
        content_list = [
            {"heading": "Test Heading"},
            {"heading": "Test Heading [2]"},
        ]
        expected_result = "Test Heading [3]"
        result = self.project_builder._heading_numbering(heading, content_list)
        self.assertEqual(result, expected_result)

    def test_heading_numbering_exceeds_max_loop(self):
        heading = "Test Heading"
        content_list = [{"heading": "Test Heading"}]
        content_list_2 = [
            {"heading": f"Test Heading [{i}]"}
            for i in range(2, c.HEADING_MAX_LOOP + 1)
        ]

        content_list.extend(content_list_2)

        with self.assertRaises(ValueError) as error:
            self.project_builder._heading_numbering(heading, content_list)
        self.assertEqual(
            str(error.exception), f"For loop over {c.HEADING_MAX_LOOP}!"
        )


class CreateGuiLabelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.project_id = 1
        cls.project_builder = ProjectBuilder(cls.project_id)

    def test_valid(self):
        initial_label = "## Test label"

        result = self.project_builder._create_gui_label(initial_label)

        self.assertEqual(result, "Test label")


class EntryUpdateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.project_id = 1
        cls.project_builder = ProjectBuilder(cls.project_id)
