from django.test import TestCase, tag, override_settings
from django.urls import reverse
from django.conf import settings
from unittest.mock import Mock, patch, call

import time as t
import sys
import os
import shutil
from dotenv import dotenv_values

import app.functions.constants as c

"""settings.ENV_LOCATION = c.TESTING_ENV_PATH_DJANGO
settings.GITHUB_REPO = c.TESTING_GITHUB_REPO
settings.MKDOCS_LOCATION = c.TESTING_MKDOCS
settings.MKDOCS_DOCS_LOCATION = c.TESTING_MKDOCS_DOCS
settings.TESTING = True
settings.START_AFRESH = True"""


sys.path.append(c.FUNCTIONS_APP)

from app.functions.env_manipulation import ENVManipulator
from app.views import std_context
import app.tests.data_views as d


@patch("app.forms.GitController")
def setup_level(self, level, mock_git_controller):
    if not isinstance(level, int):
        raise ValueError("Supplied level is not convertable into an integer")
        sys.exit(1)

    if level > 3 or level < 1:
        raise ValueError("Supplied level must be between 1 and 3")
        sys.exit(1)

    if level >= 1:
        mock_git_controller_instance = Mock()
        mock_git_controller.return_value = mock_git_controller_instance
        mock_git_controller_instance.check_github_credentials.return_value = (
            d.CREDENTIALS_CHECK_REPO_EXISTS
        )

        response = self.client.post("/", installation_variables())
        self.assertEqual(response.status_code, 200)
    if level >= 2:
        response1 = self.client.post("/", d.TEMPLATE_GOOD_DATA)
        self.assertEqual(response1.status_code, 200)
    if level >= 3:
        response3 = self.client.post("/", d.PLACEHOLDERS_GOOD_DATA)
        self.assertEqual(response3.status_code, 200)
    return


def installation_variables():
    em = ENVManipulator(c.TESTING_ENV_PATH_GIT)
    all_variables = em.read_all()

    env_for_post = {
        "installation_type": "SA",
        "github_username_SA": all_variables["GITHUB_USERNAME"],
        "github_organisation_SA": all_variables["GITHUB_ORGANISATION"],
        "email_SA": all_variables["EMAIL"],
        "github_token_SA": all_variables["GITHUB_TOKEN"],
        "github_repo_SA": all_variables["GITHUB_REPO"],
    }

    return env_for_post


def env_variables():
    em = ENVManipulator(c.TESTING_ENV_PATH_GIT)
    all_variables = em.read_all()

    return_values = {
        "github_username": all_variables["GITHUB_USERNAME"],
        "github_organisation": all_variables["GITHUB_ORGANISATION"],
        "email": all_variables["EMAIL"],
        "github_token": all_variables["GITHUB_TOKEN"],
        "github_repo": all_variables["GITHUB_REPO"],
    }

    return return_values


# TODO - add some messages tests


@tag("run")
class IndexTest(TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.path.isfile(c.TESTING_ENV_PATH_GIT):
            raise FileNotFoundError(
                ".env file for GitControllerTest class is missing"
            )
            sys.exit(1)

        if not os.path.isfile(c.ENV_PATH_PLACEHOLDERS):
            open(c.ENV_PATH_PLACEHOLDERS, "w").close()

    def setUp(self):
        self.client.get("/start_afresh")

    def test_method_bad(self):
        response = self.client.delete("/")
        self.assertEqual(response.status_code, 405)

    def test_installation_setup_get(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_installation_setup_get_template_correct(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "installation_method.html")

    @patch("app.forms.GitController")
    def test_installation_post_good_data(self, mock_git_controller):
        mock_git_controller_instance = Mock()
        mock_git_controller.return_value = mock_git_controller_instance
        mock_git_controller_instance.check_github_credentials.return_value = (
            d.CREDENTIALS_CHECK_REPO_EXISTS
        )

        response = self.client.post("/", installation_variables())
        self.assertEqual(response.status_code, 200)

        mock_git_controller.assert_called_once()
        _, calls_git_controller = mock_git_controller.call_args
        self.assertEqual(calls_git_controller, env_variables())

        mock_git_controller_instance.check_github_credentials.assert_called_once()
        (
            _,
            calls_git_controller_instance,
        ) = mock_git_controller_instance.check_github_credentials.call_args

        self.assertEqual(calls_git_controller_instance, {})

    """def test_installation_post_template_correct(self):
        response = self.client.post("/", installation_variables())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "template_select.html")"""

    #
    @patch("app.forms.GitController")
    def test_installation_post_template_correct(self, mock_git_controller):
        mock_git_controller_instance = Mock()
        mock_git_controller.return_value = mock_git_controller_instance
        mock_git_controller_instance.check_github_credentials.return_value = (
            d.CREDENTIALS_CHECK_REPO_EXISTS
        )

        response = self.client.post("/", installation_variables())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "template_select.html")

    # TODO
    def test_installation_post_good_data_message(self):
        pass

    def test_installation_post_stand_alone_data_bad(self):
        pass
        """response = self.client.post(
            "/", d.INSTALLATION_POST_STAND_ALONE_DATA_BAD
        )
        print(response.content)
        self.assertContains(response, "Invalid URL")
        self.assertEqual(response.status_code, 200)"""

    def test_installation_post_integrated_data_bad(self):
        response = self.client.post(
            "/", d.INSTALLATION_POST_INTEGRATED_DATA_BAD
        )
        self.assertContains(response, "Invalid path")
        self.assertEqual(response.status_code, 200)

    def test_template_select_get(self):
        setup_level(self, 1)
        response1 = self.client.get("/")
        self.assertEqual(response1.status_code, 200)

    def test_template_select_get_template_correct(self):
        setup_level(self, 1)
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        # print(response.content)
        self.assertTemplateUsed(response, "template_select.html")

    def test_template_post_good_data(self):
        self.test_installation_post_good_data()
        response = self.client.post("/", d.TEMPLATE_GOOD_DATA)
        self.assertEqual(response.status_code, 200)

    # TODO
    def test_template_post_good_data_message(self):
        pass

    def test_template_post_bad_data(self):
        self.test_installation_post_good_data()
        response = self.client.post("/", d.TEMPLATE_BAD_DATA)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select a valid choice.")

    def test_template_post_template_correct(self):
        self.test_installation_post_good_data()
        response = self.client.post("/", d.TEMPLATE_GOOD_DATA)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "placeholders_show.html")

    def test_placeholders_get(self):
        self.test_template_post_good_data()
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_placeholders_get_template_correct(self):
        self.test_template_post_good_data()
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "placeholders_show.html")

    def test_placeholders_post_good_data(self):
        self.test_template_post_good_data()
        response = self.client.post("/", d.PLACEHOLDERS_GOOD_DATA)
        self.assertEqual(response.status_code, 200)

    # TODO
    def test_post_good_data_message(self):
        pass

    # TODO - no cleaning check for placeholders yet, but will need a test
    # function if cleaning is implemented.

    @classmethod
    def tearDownClass(cls):
        pass


@tag("run")
# TODO: Need to see if could use IndexViewTest to reduce code here
class MdEditTest(TestCase):
    def setUp(self):
        self.client.get("/start_afresh")

    def test_md_edit_wrong_method(self):
        setup_level(self, 2)
        """response = self.client.post("/", installation_variables())
        self.assertEqual(response.status_code, 200)
        response1 = self.client.post("/", d.TEMPLATE_GOOD_DATA)
        self.assertEqual(response1.status_code, 200)"""
        response2 = self.client.delete("/md_edit")
        self.assertEqual(response2.status_code, 405)

    def test_md_edit_setup_step_none(self):
        self.client.post("/start_afresh")
        response = self.client.get("/md_edit")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("index"))

    def test_md_edit_setup_step_1(self):
        setup_level(self, 1)
        response1 = self.client.get("/md_edit")
        self.assertEqual(response1.status_code, 302)
        self.assertRedirects(response1, reverse("index"))

    def test_md_edit_setup_step_2(self):
        setup_level(self, 2)
        """response = self.client.post("/", installation_variables())
        self.assertEqual(response.status_code, 200)
        response1 = self.client.post("/", d.TEMPLATE_GOOD_DATA)
        self.assertEqual(response1.status_code, 200)"""
        response2 = self.client.get("/md_edit")
        self.assertEqual(response2.status_code, 200)

    def test_md_edit_template_correct(self):
        setup_level(self, 2)
        """response = self.client.post("/", installation_variables())
        self.assertEqual(response.status_code, 200)
        response1 = self.client.post("/", d.TEMPLATE_GOOD_DATA)
        self.assertEqual(response1.status_code, 200)"""
        response2 = self.client.get("/md_edit")
        self.assertEqual(response2.status_code, 200)
        self.assertTemplateUsed(response2, "md_edit.html")

    def test_md_edit_post_good_data(self):
        setup_level(self, 2)
        """response = self.client.post("/", installation_variables())
        self.assertEqual(response.status_code, 200)
        response1 = self.client.post("/", d.TEMPLATE_GOOD_DATA)
        self.assertEqual(response1.status_code, 200)"""
        response2 = self.client.post("/md_edit", d.MD_EDIT_GOOD_DATA)
        self.assertEqual(response2.status_code, 200)
        self.assertTemplateUsed(response2, "md_edit.html")

    # TODO - no clean method for md_edit form yet, will need testing for this once implemented wth bad data


@tag("run")
class MdSavedTest(TestCase):
    def setUp(self):
        self.client.get("/start_afresh")

    def test_md_edit_wrong_method(self):
        response = self.client.delete("/md_saved")
        self.assertEqual(response.status_code, 405)

    def test_get_setup_None(self):
        response = self.client.get("/md_saved")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("md_edit"), target_status_code=302
        )

    """def setup_2_initialise(self):
        response = self.client.post("/", installation_variables())
        self.assertEqual(response.status_code, 200)
        response1 = self.client.post("/", d.TEMPLATE_GOOD_DATA)
        self.assertEqual(response1.status_code, 200)"""

    # @tag("run")
    def test_get_setup_2_good_data(self):
        setup_level(self, 2)
        response2 = self.client.post("/md_saved", d.MD_SAVED_GOOD_DATA)
        self.assertEqual(response2.status_code, 200)
        f = open(d.MD_SAVED_TEMPLATE_FILE_PATH, "r")
        self.assertEqual(f.read(), d.MD_SAVED_GOOD_DATA["md_text"])

    def test_get_setup_2_good_data_template_correct(self):
        setup_level(self, 2)
        response2 = self.client.post("/md_saved", d.MD_SAVED_GOOD_DATA)
        self.assertEqual(response2.status_code, 200)
        self.assertTemplateUsed(response2, "md_edit.html")

    # TODO
    def test_post_good_data_message(self):
        pass

    # @tag("run")
    def test_post_bad_filename(self):
        # self.setup_2_initialise()
        setup_level(self, 3)
        response2 = self.client.post("/md_saved", d.MD_SAVED_BAD_FILENAME)
        self.assertEqual(response2.status_code, 500)

    # TODO - there is no markdown validity checker yet. But will need a test when in place


class MdNewTest(TestCase):
    pass


@tag("run")
class HazardLogTest(TestCase):
    def setUp(self):
        self.client.get("/start_afresh")

    def test_hazard_log_bad_method(self):
        response = self.client.delete("/hazard_log")
        self.assertEqual(response.status_code, 405)

    def test_hazard_log_get(self):
        pass  # TODO - needs finishing

    def test_hazard_log_get_template_correct(self):
        shutil.copyfile(c.TESTING_ENV_PATH_GIT, c.TESTING_ENV_PATH_DJANGO)
        response = self.client.get("/hazard_log")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hazard_log.html")

    def test_hazard_log_post(self):
        pass


@tag("git")
class HazardCommentTest(TestCase):
    def setUp(self):
        setup_level(self, 3)

    def test_hazard_comment_method_bad(self):
        response = self.client.delete("/hazard_comment/1")
        self.assertEqual(response.status_code, 405)

    def test_hazard_comment_method_bad_corrent_template(self):
        response = self.client.delete("/hazard_comment/1")
        self.assertEqual(response.status_code, 405)
        self.assertTemplateUsed(response, "405.html")

    def test_hazard_comment_parameter_bad(self):
        response = self.client.get("/hazard_comment/a")
        self.assertEqual(response.status_code, 400)

    def test_hazard_comment_parameter_bad_corrent_template(self):
        response = self.client.get("/hazard_comment/a")
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, "400.html")

    def test_hazard_comment_get(self):
        response = self.client.get(
            f"/hazard_comment/{ c.TESTING_CURRENT_ISSUE  }"
        )
        self.assertEqual(response.status_code, 200)

    def test_hazard_comment_get_template_correct(self):
        response = self.client.get(
            f"/hazard_comment/{ c.TESTING_CURRENT_ISSUE  }"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hazard_comment.html")

    def test_hazard_comment_issue_number_nonexistent(self):
        response = self.client.get(
            f"/hazard_comment/{ d.ISSUE_NUMBER_NONEXISTENT }"
        )
        self.assertEqual(response.status_code, 400)

    def test_hazard_comment_issue_number_nonexistent_corrent_template(self):
        response = self.client.get(
            f"/hazard_comment/{ d.ISSUE_NUMBER_NONEXISTENT }"
        )
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, "400.html")

    def test_hazard_comment_post(self):
        pass


class HazardsOpenTest(TestCase):
    pass


class MkdocsRedirectTest(TestCase):
    def setUp(self):
        self.client.get("/start_afresh")

    def test_bad_method(self):
        response = self.client.delete("/mkdoc_redirect/home")
        self.assertEqual(response.status_code, 405)

    def test_get_home(self):
        response = self.client.get("/mkdoc_redirect/home")
        self.assertEqual(response.status_code, 302)


class UpLoadToGithubTest(TestCase):
    pass


class SetupStepTest(TestCase):
    pass


@tag("git")
class StdContectTest(TestCase):
    def setUp(self):
        self.client.get("/start_afresh")

    def test_setup_None(self):
        self.assertEqual(std_context(), d.STD_CONTEXT_SETUP_NONE)

    def test_setup_1(self):
        setup_level(self, 1)
        self.assertEqual(std_context(), d.STD_CONTEXT_SETUP_1)

    def test_setup_2(self):
        setup_level(self, 2)
        self.assertEqual(std_context(), d.STD_CONTEXT_SETUP_2)

    # @tag("run")
    def test_setup_3(self):
        setup_level(self, 3)
        self.assertEqual(std_context(), d.STD_CONTEXT_SETUP_3)


@tag("git")
class StartAfreshEnabledTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.start_fresh_previous_state = settings.START_AFRESH
        settings.START_AFRESH = True
        cls.testing_previous_state = settings.TESTING
        settings.TESTING = True
        # TODO might not need this as already set at top of module
        cls.env_location_previous = settings.ENV_LOCATION
        settings.ENV_LOCATION = c.TESTING_ENV_PATH_DJANGO

    def setUp(self):
        self.client.get("/start_afresh")

    def test_bad_method(self):
        response = self.client.delete("/start_afresh")
        self.assertEqual(response.status_code, 405)

    def test_start_afresh_with_nothing_running(self):
        if not os.path.isfile(c.TESTING_ENV_PATH_DJANGO):
            self.assertTrue(False)

        f = open(c.TESTING_ENV_PATH_DJANGO, "r")
        self.assertEqual(f.read(), "")

    def test_start_afresh_with_everything_running(self):
        setup_level(self, 3)
        if not os.path.isfile(c.TESTING_ENV_PATH_DJANGO):
            self.assertTrue(False)

        em_django = ENVManipulator(c.TESTING_ENV_PATH_DJANGO)
        em_git = ENVManipulator(c.TESTING_ENV_PATH_GIT)
        git_env_dict = em_git.read_all()
        git_env_dict["setup_step"] = "3"
        self.assertEqual(em_django.read_all(), git_env_dict)

    @classmethod
    def tearDownClass(cls):
        settings.START_AFRESH = cls.start_fresh_previous_state
        settings.TESTING = cls.testing_previous_state
        settings.ENV_LOCATION = cls.env_location_previous


@tag("git")
class StartAfreshDisabledTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.start_fresh_previous_state = settings.START_AFRESH
        settings.START_AFRESH = False
        cls.testing_previous_state = settings.TESTING
        settings.TESTING = False

    def setUp(self):
        settings.TESTING = True
        self.client.get("/start_afresh")
        settings.TESTING = False

    def test_bad_method(self):
        response = self.client.delete("/start_afresh")
        self.assertEqual(response.status_code, 405)

    def test_start_afresh_with_nothing_running(self):
        if not os.path.isfile(c.TESTING_ENV_PATH_DJANGO):
            self.assertTrue(False)

        f = open(c.TESTING_ENV_PATH_DJANGO, "r")
        self.assertEqual(f.read(), "")

    def test_start_afresh_with_everything_running(self):
        setup_level(self, 3)
        if not os.path.isfile(c.TESTING_ENV_PATH_DJANGO):
            self.assertTrue(False)

        em_django = ENVManipulator(c.TESTING_ENV_PATH_DJANGO)
        em_git = ENVManipulator(c.TESTING_ENV_PATH_GIT)
        git_env_dict = em_git.read_all()
        git_env_dict["setup_step"] = "3"
        self.assertEqual(em_django.read_all(), git_env_dict)

    @classmethod
    def tearDownClass(cls):
        settings.START_AFRESH = cls.start_fresh_previous_state
        settings.TESTING = cls.testing_previous_state


class Custum404(TestCase):
    def test_(self):
        pass


class Custum405(TestCase):
    def test_(self):
        pass
