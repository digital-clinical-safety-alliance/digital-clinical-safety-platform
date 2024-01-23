"""Testing of git_control.py

    Maybe used in async mode

"""

from unittest import TestCase
from django.test import tag
import sys
import os
from dotenv import load_dotenv, set_key, find_dotenv, dotenv_values
import requests
from requests import exceptions
from git import Repo
from github import Github, Issue, Auth, GithubException
from unittest.mock import Mock, patch, call
from unittest.mock import create_autospec
import time as t

import app.functions.constants as c

sys.path.append(c.FUNCTIONS_APP)
from app.functions.git_control import GitController

import app.tests.data_git_control as d


# @tag("git")
class GitControllerTest(TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.path.isfile(c.TESTING_ENV_PATH_GIT):
            raise FileNotFoundError(
                ".env file for GitControllerTest class is missing"
            )
            sys.exit(1)

        if not os.path.isfile(c.ENV_PATH_PLACEHOLDERS):
            open(c.ENV_PATH_PLACEHOLDERS, "w").close()

        for key in c.EnvKeysPH:
            file_name_temp = (
                f"{c.TESTING_ENV_PATH_GIT_DIR_ONLY}env_no_{ key.value }"
            )
            f = open(file_name_temp, "w")
            for key_again in c.EnvKeysPH:
                if key == key_again:
                    f.write(f"{ key_again.value }=''\n")
                else:
                    if key_again.value == c.EnvKeysPH.EMAIL.value:
                        f.write(f"{ key_again.value }='john.doe@domain.com'\n")
                    else:
                        f.write(f"{ key_again.value }='some test data'\n")
            f.close()

    def test_init(self):
        GitController(env_location=c.TESTING_ENV_PATH_GIT)

    def test_init_env_location_empty(self):
        with self.assertRaises(ValueError) as error:
            GitController(env_location="")
        self.assertEqual(
            str(error.exception), f".env location is set to empty string"
        )

    def test_init_env_location_bad(self):
        with self.assertRaises(ValueError) as error:
            GitController(env_location=d.ENV_PATH_BAD)
        self.assertEqual(
            str(error.exception),
            f"'{ d.ENV_PATH_BAD }' path for .env file does not exist",
        )

    def test_init_single_empty_fields(self):
        for key in c.EnvKeysPH:
            if (
                key.value != c.EnvKeysPH.GITHUB_REPO.value
                and key.value != c.EnvKeysPH.GITHUB_ORGANISATION.value
            ):
                with self.assertRaises(ValueError) as error:
                    GitController(
                        env_location=f"{c.TESTING_ENV_PATH_GIT_DIR_ONLY}env_no_{ key.value }"
                    )
                self.assertEqual(
                    str(error.exception),
                    f"'{ key.value }' has not been set as an argument or in .env",
                )

    def test_init_email_bad(self):
        with self.assertRaises(ValueError) as error:
            GitController(
                email=d.EMAIL_BAD,
                env_location=c.TESTING_ENV_PATH_GIT,
            )
        self.assertEqual(
            str(error.exception), f"Email address '{ d.EMAIL_BAD }' is invalid"
        )

    def test_init_repo_path_local_empty(self):
        with self.assertRaises(ValueError) as error:
            GitController(
                repo_path_local="",
                env_location=c.TESTING_ENV_PATH_GIT,
            )
        self.assertEqual(
            str(error.exception),
            "'repo_path_local' has not been set",
        )

    def test_init_repo_path_local_path_bad(self):
        with self.assertRaises(FileNotFoundError) as error:
            GitController(
                repo_path_local=d.VALUE_BAD,
                env_location=c.TESTING_ENV_PATH_GIT,
            )
        self.assertEqual(
            str(error.exception),
            f"'{ d.VALUE_BAD }' is not a valid path for 'repo_path_local'",
        )

    # @tag("run")
    @patch("app.functions.git_control.requests.get")
    @patch("app.functions.git_control.Github")
    def test_check_github_credentials(self, mock_github, mock_get):
        mock_get.side_effect = iter(
            [
                Mock(status_code=200),
                Mock(status_code=200),
                Mock(status_code=200),
            ]
        )

        mock_github_instance = Mock()
        mock_github.return_value = mock_github_instance
        mock_repo_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo_instance
        mock_repo_instance.get_collaborator_permission.return_value = "admin"

        gc = GitController(**d.git_contoller_args)

        self.assertEqual(
            gc.check_github_credentials(), d.CREDENTIALS_CHECK_REPO_EXISTS
        )

        calls = mock_get.call_args_list
        self.assertEqual(calls, d.CHECK_CREDENTIALS_GET_CALLS)

        mock_github.assert_called_once()
        calls_github = mock_github.call_args_list
        self.assertEqual(calls_github[0].args, d.CHECK_CREDENTIALS_GITHUB_CALL)

        mock_github_instance.get_repo.assert_called_once()
        calls_get_repo = mock_github_instance.get_repo.call_args_list
        self.assertEqual(
            calls_get_repo[0].args[0],
            d.CHECK_CREDENTIALS_REPO_CALL,
        )

        mock_repo_instance.get_collaborator_permission.assert_called_once()
        calls_permission = (
            mock_repo_instance.get_collaborator_permission.call_args_list
        )
        self.assertEqual(
            calls_permission[0].args[0],
            d.git_contoller_args["github_username"],
        )

    # @tag("run")
    @patch("app.functions.git_control.requests.get")
    @patch("app.functions.git_control.Github")
    def test_check_github_credentials_no_connection(
        self, mock_github, mock_get
    ):
        mock_get.side_effect = requests.exceptions.ConnectionError(
            "Test Connection Error"
        )

        gc = GitController(**d.git_contoller_args)

        mock_github_instance = Mock()
        mock_github.return_value = mock_github_instance

        with self.assertRaises(requests.exceptions.ConnectionError) as error:
            gc.check_github_credentials()

        self.assertEqual(str(error.exception), d.NO_CONNECTION_ERROR_MESSAGE)

        self.assertEqual(mock_get.call_count, 1)
        calls = mock_get.call_args_list
        self.assertEqual(calls[0], d.CHECK_CREDENTIALS_GET_CALLS[0])

        self.assertEqual(mock_github.call_count, 0)

    # @tag("run")
    @patch("app.functions.git_control.requests.get")
    @patch("app.functions.git_control.Github")
    def test_check_github_credentials_timeout(self, mock_github, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout(
            "Test Timeout Error"
        )

        gc = GitController(**d.git_contoller_args)

        mock_github_instance = Mock()
        mock_github.return_value = mock_github_instance

        with self.assertRaises(requests.exceptions.Timeout) as error:
            gc.check_github_credentials()

        self.assertEqual(str(error.exception), d.TIME_ERROR_MESSAGE)

        self.assertEqual(mock_get.call_count, 1)
        calls = mock_get.call_args_list
        self.assertEqual(calls[0], d.CHECK_CREDENTIALS_GET_CALLS[0])

        self.assertEqual(mock_github.call_count, 0)

    # TODO #30 may need to catch time outs and no connections in different request places

    # @tag("run")
    @patch("app.functions.git_control.requests.get")
    @patch("app.functions.git_control.Github")
    def test_check_github_credentials_repo_does_not_exist(
        self, mock_github, mock_get
    ):
        mock_get.side_effect = iter(
            [
                Mock(status_code=200),
                Mock(status_code=200),
                Mock(status_code=404),
            ]
        )

        mock_github_instance = Mock()
        mock_github.return_value = mock_github_instance

        gc = GitController(**d.git_contoller_args)

        self.assertEqual(
            gc.check_github_credentials(),
            d.CREDENTIALS_CHECK_REPO_DOES_NOT_EXIST,
        )

        self.assertEqual(mock_get.call_count, 3)
        calls = mock_get.call_args_list
        self.assertEqual(calls, d.CHECK_CREDENTIALS_GET_CALLS)

        self.assertEqual(mock_github.call_count, 0)

    # @tag("run")
    @patch("app.functions.git_control.requests.get")
    @patch("app.functions.git_control.Github")
    def test_check_github_credentials_username_bad(
        self, mock_github, mock_get
    ):
        mock_get.side_effect = iter(
            [
                Mock(status_code=404),
                Mock(status_code=200),
                Mock(status_code=200),
            ]
        )

        mock_github_instance = Mock()
        mock_github.return_value = mock_github_instance
        mock_repo_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo_instance
        mock_repo_instance.get_collaborator_permission.side_effect = (
            GithubException("No permission for repo")
        )

        gc = GitController(**d.git_contoller_args)

        self.assertEqual(
            gc.check_github_credentials(), d.CREDENTIALS_CHECK_USERNAME_BAD
        )

        self.assertEqual(mock_get.call_count, 3)
        calls_get = mock_get.call_args_list
        self.assertEqual(calls_get, d.CHECK_CREDENTIALS_GET_CALLS)

        mock_github.assert_called_once()
        calls_github = mock_github.call_args_list
        self.assertEqual(calls_github[0].args, d.CHECK_CREDENTIALS_GITHUB_CALL)

        mock_github_instance.get_repo.assert_called_once()
        calls_get_repo = mock_github_instance.get_repo.call_args_list
        self.assertEqual(
            calls_get_repo[0].args[0],
            d.CHECK_CREDENTIALS_REPO_CALL,
        )

        mock_repo_instance.get_collaborator_permission.assert_called_once()
        calls_permission = (
            mock_repo_instance.get_collaborator_permission.call_args_list
        )
        self.assertEqual(
            calls_permission[0].args[0],
            d.git_contoller_args["github_username"],
        )

    # @tag("run")
    @patch("app.functions.git_control.requests.get")
    @patch("app.functions.git_control.Github")
    def test_check_github_credentials_organisation_bad(
        self, mock_github, mock_get
    ):
        mock_get.side_effect = iter(
            [
                Mock(status_code=200),
                Mock(status_code=404),
                Mock(status_code=404),
            ]
        )

        mock_github_instance = Mock()
        mock_github.return_value = mock_github_instance

        gc = GitController(**d.git_contoller_args)

        self.assertEqual(
            gc.check_github_credentials(), d.CREDENTIALS_CHECK_ORGANISATION_BAD
        )

        self.assertEqual(mock_get.call_count, 3)
        calls = mock_get.call_args_list
        self.assertEqual(calls, d.CHECK_CREDENTIALS_GET_CALLS)

        self.assertEqual(mock_github.call_count, 0)

    # @tag("run")
    @patch("app.functions.git_control.requests.get")
    def test_organisation_exists(self, mock_get):
        mock_get.return_value = Mock(status_code=200)
        gc = GitController(**d.git_contoller_args)
        self.assertTrue(
            gc.organisation_exists(d.git_contoller_args["github_organisation"])
        )
        mock_get.assert_called_once()
        calls = mock_get.call_args_list
        self.assertEqual(calls[0], d.CHECK_CREDENTIALS_GET_CALLS[1])

    # @tag("run")
    @patch("app.functions.git_control.requests.get")
    def test_organisation_does_not_exists(self, mock_get):
        mock_get.return_value = Mock(status_code=404)
        gc = GitController(**d.git_contoller_args)
        self.assertFalse(
            gc.organisation_exists(d.git_contoller_args["github_organisation"])
        )
        mock_get.assert_called_once()
        calls = mock_get.call_args_list
        self.assertEqual(calls[0], d.CHECK_CREDENTIALS_GET_CALLS[1])

    # @tag("run")
    @patch("app.functions.git_control.Github")
    def test_get_repos(self, mock_github):
        mock_github_instance = Mock()
        mock_github.return_value = mock_github_instance
        mock_repo_instance = Mock()
        mock_github_instance.get_user.return_value = mock_repo_instance
        mock_name0 = Mock()
        setattr(mock_name0, "name", d.GET_REPOS[0])
        mock_name1 = Mock()
        setattr(mock_name1, "name", d.GET_REPOS[1])
        mock_repo_instance.get_repos.return_value = iter(
            [mock_name0, mock_name1]
        )

        gc = GitController(**d.git_contoller_args)
        self.assertTrue(
            gc.get_repos(d.git_contoller_args["github_organisation"]),
            d.GET_REPOS,
        )

        mock_github.assert_called_once()
        calls_github = mock_github.call_args_list
        self.assertEqual(calls_github[0].args, d.CHECK_CREDENTIALS_GITHUB_CALL)

        mock_github_instance.get_user.assert_called_once()
        calls_get_user = mock_github_instance.get_user.call_args_list
        self.assertEqual(
            calls_get_user[0].args[0],
            d.git_contoller_args["github_organisation"],
        )

        mock_repo_instance.get_repos.assert_called_once()
        calls_repos = mock_github_instance.get_repos.call_args_list
        self.assertEqual(calls_repos, [])

    # @tag("run")
    @patch("app.functions.git_control.Github")
    def test_get_repos_domain_nonexist(self, mock_github):
        mock_github_instance = Mock()
        mock_github.return_value = mock_github_instance
        mock_github_instance.get_user.side_effect = GithubException(
            "User / organisation not found", data={"message": "Not Found"}
        )

        gc = GitController(**d.git_contoller_args)
        with self.assertRaises(ValueError) as error:
            gc.get_repos(d.git_contoller_args["github_organisation"])

        self.assertEqual(
            str(error.exception),
            f"Error with getting user / organisastion '{ d.git_contoller_args['github_organisation'] }', returned - 'Not Found'",
        )

        mock_github.assert_called_once()
        calls_github = mock_github.call_args_list
        self.assertEqual(calls_github[0].args, d.CHECK_CREDENTIALS_GITHUB_CALL)

        mock_github_instance.get_user.assert_called_once()
        calls_get_user = mock_github_instance.get_user.call_args_list
        self.assertEqual(
            calls_get_user[0].args[0],
            d.git_contoller_args["github_organisation"],
        )

    # @tag("run")
    @patch("app.functions.git_control.Github")
    def test_current_repo_on_github(self, mock_github):
        mock_github_instance = Mock()
        mock_github.return_value = mock_github_instance
        mock_repo_instance = Mock()
        mock_github_instance.get_user.return_value = mock_repo_instance
        mock_name0 = Mock()
        setattr(mock_name0, "name", d.GET_REPOS[0])
        mock_name1 = Mock()
        setattr(mock_name1, "name", d.GET_REPOS[1])
        mock_repo_instance.get_repos.return_value = iter(
            [mock_name0, mock_name1]
        )

        gc = GitController(**d.git_contoller_args)
        self.assertTrue(
            gc.current_repo_on_github(
                d.git_contoller_args["github_organisation"], d.GET_REPOS[0]
            )
        )

        mock_github.assert_called_once()
        calls_github = mock_github.call_args_list
        self.assertEqual(calls_github[0].args, d.CHECK_CREDENTIALS_GITHUB_CALL)

        mock_github_instance.get_user.assert_called_once()
        calls_get_user = mock_github_instance.get_user.call_args_list
        self.assertEqual(
            calls_get_user[0].args[0],
            d.git_contoller_args["github_organisation"],
        )

        mock_repo_instance.get_repos.assert_called_once()
        calls_repos = mock_github_instance.get_repos.call_args_list
        self.assertEqual(calls_repos, [])

    @tag("git")
    def test_create_repo(self):
        gc = GitController(env_location=c.TESTING_ENV_PATH_GIT)
        if gc.current_repo_on_github(
            d.git_contoller_args["github_organisation"], d.REPO_NAME_NEW
        ):
            gc.delete_repo(
                d.git_contoller_args["github_organisation"], d.REPO_NAME_NEW
            )

        self.assertFalse(
            gc.current_repo_on_github(
                d.git_contoller_args["github_organisation"], d.REPO_NAME_NEW
            )
        )

        gc.create_repo(
            d.git_contoller_args["github_organisation"], d.REPO_NAME_NEW
        )
        self.assertTrue(
            gc.current_repo_on_github(
                d.git_contoller_args["github_organisation"], d.REPO_NAME_NEW
            )
        )

    @tag("git")
    def test_create_repo_organisation_bad(self):
        gc = GitController(env_location=c.TESTING_ENV_PATH_GIT)
        with self.assertRaises(ValueError) as error:
            gc.create_repo(d.ORGANISATION_NAME_BAD, d.REPO_NAME_NEW)
        self.assertEqual(
            str(error.exception),
            f"Error with getting user / organisastion '{ d.ORGANISATION_NAME_BAD }', returned - 'Not Found'",
        )

    @tag("git")
    def test_delete_repo(self):
        gc = GitController(env_location=c.TESTING_ENV_PATH_GIT)
        if not gc.current_repo_on_github(
            d.git_contoller_args["github_organisation"], d.REPO_NAME_NEW
        ):
            gc.create_repo(
                d.git_contoller_args["github_organisation"], d.REPO_NAME_NEW
            )

        self.assertTrue(
            gc.current_repo_on_github(
                d.git_contoller_args["github_organisation"], d.REPO_NAME_NEW
            )
        )

        gc.delete_repo(
            d.git_contoller_args["github_organisation"], d.REPO_NAME_NEW
        )

        self.assertFalse(
            gc.current_repo_on_github(
                d.git_contoller_args["github_organisation"], d.REPO_NAME_NEW
            )
        )

    # TODO #21 - needs testing of test_commit_and_push
    def test_commit_and_push(self):
        pass

    def test_commit_and_push_already_committed(self):
        pass

    @tag("git")
    def test_hazard_new(self):
        gc = GitController(
            github_repo=d.REPO_NAME_CURRENT,
            env_location=c.TESTING_ENV_PATH_GIT,
        )
        gc.hazard_new("title", "body", ["hazard"])
        # TODO - should really check hazard was created
        close_all_issues()

    @tag("git")
    def test_hazard_new_label_bad(self):
        gc = GitController(
            github_repo=d.REPO_NAME_CURRENT,
            env_location=c.TESTING_ENV_PATH_GIT,
        )
        with self.assertRaises(ValueError) as error:
            gc.hazard_new("title", "body", [d.LABEL_NAME_BAD])

        self.assertEqual(
            str(error.exception),
            f"'{ d.LABEL_NAME_BAD}' is not a valid hazard label. Please review label.yml for available values.",
        )

    @tag("git")
    def test_hazard_new_repo_bad(self):
        gc = GitController(
            github_repo=d.REPO_BAD_NAME,
            env_location=c.TESTING_ENV_PATH_GIT,
        )
        with self.assertRaises(ValueError) as error:
            gc.hazard_new("title", "body", ["hazard"])

        dot_values = dotenv_values(c.TESTING_ENV_PATH_GIT)
        self.assertEqual(
            str(error.exception),
            f"Error with accessing repo '{ dot_values.get(c.EnvKeysPH.GITHUB_ORGANISATION.value) }/{ d.REPO_BAD_NAME }', return value 'Not Found'",
        )

    @tag("git")
    def test_available_hazard_labels_full(self):
        gc = GitController(env_location=c.TESTING_ENV_PATH_GIT)
        self.assertEqual(
            gc.available_hazard_labels(), d.AVAILABLE_HAZARD_LABELS_FULL
        )

    @tag("git")
    def test_available_hazard_labels_name_only(self):
        gc = GitController(env_location=c.TESTING_ENV_PATH_GIT)
        self.assertEqual(
            gc.available_hazard_labels("name_only"),
            d.AVAILABLE_HAZARD_LABELS_NAME_ONLY,
        )

    @tag("git")
    def test_available_hazard_labels_details_wrong(self):
        gc = GitController(env_location=c.TESTING_ENV_PATH_GIT)
        with self.assertRaises(ValueError) as error:
            self.assertEqual(
                gc.available_hazard_labels(d.VALUE_BAD),
                d.AVAILABLE_HAZARD_LABELS_NAME_ONLY,
            )
        self.assertEqual(
            str(error.exception),
            f"'{ d.VALUE_BAD }' is not a valid option for return values of hazard labels",
        )

    def test_available_hazard_labels_yaml_missing(self):
        label_yaml_previous_value = c.ISSUE_LABELS_PATH
        c.ISSUE_LABELS_PATH = d.ISSUES_LABELS_PATH_BAD
        gc = GitController(env_location=c.TESTING_ENV_PATH_GIT)
        with self.assertRaises(FileNotFoundError) as error:
            self.assertEqual(
                gc.available_hazard_labels(),
                d.AVAILABLE_HAZARD_LABELS_NAME_ONLY,
            )

        self.assertEqual(
            str(error.exception),
            f"Labels.yml does not exist at '{ d.ISSUES_LABELS_PATH_BAD }'",
        )

        c.ISSUE_LABELS_PATH = label_yaml_previous_value

    def test_verify_hazard_label(self):
        gc = GitController(env_location=c.TESTING_ENV_PATH_GIT)
        self.assertTrue(gc.verify_hazard_label("hazard"))

    def test_verify_hazard_label_bad(self):
        gc = GitController(env_location=c.TESTING_ENV_PATH_GIT)
        self.assertFalse(gc.verify_hazard_label("hazard2"))

    @tag("git")
    def test_hazards_open(self):
        gc = GitController(
            github_repo=d.REPO_NAME_CURRENT,
            env_location=c.TESTING_ENV_PATH_GIT,
        )
        gc.hazard_new("title", "body", ["hazard"])

        open_hazard = gc.hazards_open()[0]
        self.assertTrue(open_hazard["title"], "title")
        self.assertTrue(open_hazard["body"], "body")
        self.assertTrue(open_hazard["labels"], {"hazard"})
        close_all_issues()

    @tag("git")
    def test_hazards_open_repo_bad(self):
        gc = GitController(
            github_repo=d.REPO_BAD_NAME,
            env_location=c.TESTING_ENV_PATH_GIT,
        )

        with self.assertRaises(ValueError) as error:
            gc.hazard_new("title", "body", ["hazard"])

        dot_values = dotenv_values(c.TESTING_ENV_PATH_GIT)
        self.assertEqual(
            str(error.exception),
            f"Error with accessing repo '{ dot_values.get(c.EnvKeysPH.GITHUB_ORGANISATION.value) }/{ d.REPO_BAD_NAME }', return value 'Not Found'",
        )
        close_all_issues()

    def test_repo_domain_name(self):
        gc = GitController(
            github_repo=d.REPO_NAME_CURRENT,
            env_location=c.TESTING_ENV_PATH_GIT,
        )
        self.assertTrue(
            gc.repo_domain_name(), d.git_contoller_args["github_organisation"]
        )

    @tag("git")
    def test_add_comment_to_hazard(self):
        gc = GitController(
            github_repo=d.REPO_NAME_CURRENT,
            env_location=c.TESTING_ENV_PATH_GIT,
        )
        gc.hazard_new("title", "body", ["hazard"])

        hazard_number = gc.hazards_open()[0]["number"]
        gc.add_comment_to_hazard(
            hazard_number=hazard_number, comment="a comment"
        )
        close_all_issues()

    def test_add_comment_to_hazard_number_missing(self):
        gc = GitController(
            github_repo=d.REPO_NAME_CURRENT,
            env_location=c.TESTING_ENV_PATH_GIT,
        )
        with self.assertRaises(ValueError) as error:
            gc.add_comment_to_hazard(comment="a comment")
        self.assertEqual(
            str(error.exception), "No Hazard Number has been provided"
        )

    def test_add_comment_to_hazard_comment_missing(self):
        gc = GitController(
            github_repo=d.REPO_NAME_CURRENT,
            env_location=c.TESTING_ENV_PATH_GIT,
        )
        with self.assertRaises(ValueError) as error:
            gc.add_comment_to_hazard(hazard_number=1)
        self.assertEqual(str(error.exception), "No comment has been provided")

    @classmethod
    def tearDownClass(cls):
        # gc = GitController(env_location=c.TESTING_ENV_PATH_GIT)
        # if gc.current_repo_on_github(
        #    d.git_contoller_args["github_organisation"], d.REPO_NAME_NEW
        # ):
        #    gc.delete_repo(d.git_contoller_args["github_organisation"], d.REPO_NAME_NEW)

        # close_all_issues()
        pass
