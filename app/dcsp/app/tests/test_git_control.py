"""Testing of git_control.py

    Maybe used in async mode

"""

from unittest import TestCase
from django.test import tag
import sys
import os
from dotenv import load_dotenv, set_key, find_dotenv, dotenv_values
from git import Repo
from github import Github, Issue, Auth, GithubException

import app.functions.constants as c

sys.path.append(c.FUNCTIONS_APP)
from app.functions.git_control import GitController

import app.tests.data_git_control as d


def close_all_issues():
    dot_values = dotenv_values(c.TESTING_ENV_PATH_GIT)
    g = Github(
        dot_values.get("GITHUB_USERNAME"), dot_values.get("GITHUB_TOKEN")
    )
    repo = g.get_repo(f"{d.ORGANISATION_NAME_GOOD}/{ d.REPO_NAME_CURRENT }")
    open_issues = repo.get_issues(state="open")
    for issue in open_issues:
        issue.edit(state="closed")

    return


@tag("git")
class GitControllerTest(TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.path.isfile(c.TESTING_ENV_PATH_GIT):
            raise FileNotFoundError(
                ".env file for GitControllerTest class is missing"
            )
            sys.exit(1)

        for key in c.EnvKeys:
            file_name_temp = (
                f"{c.TESTING_ENV_PATH_GIT_DIR_ONLY}env_no_{ key.value }"
            )
            f = open(file_name_temp, "w")
            for key_again in c.EnvKeys:
                if key == key_again:
                    f.write(f"{ key_again.value }=''\n")
                else:
                    if key_again.value == c.EnvKeys.EMAIL.value:
                        f.write(f"{ key_again.value }='john.doe@domain.com'\n")
                    else:
                        f.write(f"{ key_again.value }='some test data'\n")
            f.close()

        close_all_issues()

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
        for key in c.EnvKeys:
            if (
                key.value != c.EnvKeys.GITHUB_REPO.value
                and key.value != c.EnvKeys.GITHUB_ORGANISATION.value
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

    def test_init_github_repo_empty(self):
        with self.assertRaises(ValueError) as error:
            GitController(
                github_repo="",
                env_location=c.TESTING_ENV_PATH_GIT,
            )
        self.assertEqual(
            str(error.exception), "'github_repo' has not been set"
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

    def test_check_github_credentials(self):
        gc = GitController(
            github_repo=d.REPO_NAME_CURRENT,
            env_location=c.TESTING_ENV_PATH_GIT,
        )

        self.assertEqual(
            gc.check_github_credentials(), d.CREDENTIALS_CHECK_REPO_EXISTS
        )

    def test_check_github_credentials_repo_does_not_exist(self):
        gc = GitController(
            github_repo="test_repo_does_not_exist",
            env_location=c.TESTING_ENV_PATH_GIT,
        )
        self.assertEqual(
            gc.check_github_credentials(),
            d.CREDENTIALS_CHECK_REPO_DOES_NOT_EXIST,
        )

    def test_check_github_credentials_username_bad(self):
        gc = GitController(
            github_username="111222333444abccba",
            github_repo=d.REPO_NAME_CURRENT,
            env_location=c.TESTING_ENV_PATH_GIT,
        )

        self.assertEqual(
            gc.check_github_credentials(), d.CREDENTIALS_CHECK_USERNAME_BAD
        )

    def test_check_github_credentials_organisation_bad(self):
        gc = GitController(
            github_organisation="111222333444abccba",
            github_repo=d.REPO_NAME_CURRENT,
            env_location=c.TESTING_ENV_PATH_GIT,
        )
        self.assertEqual(
            gc.check_github_credentials(), d.CREDENTIALS_CHECK_ORGANISATION_BAD
        )

    def test_organisation_exists(self):
        gc = GitController(env_location=c.TESTING_ENV_PATH_GIT)
        self.assertTrue(gc.organisation_exists(d.ORGANISATION_NAME_GOOD))

    def test_get_repos(self):
        gc = GitController(env_location=c.TESTING_ENV_PATH_GIT)
        self.assertTrue(
            gc.get_repos(d.ORGANISATION_NAME_GOOD), d.GET_REPOS_RETURN
        )

    def test_get_repos_bad(self):
        gc = GitController(env_location=c.TESTING_ENV_PATH_GIT)
        with self.assertRaises(ValueError) as error:
            gc.get_repos(d.ORGANISATION_NAME_BAD), d.GET_REPOS_RETURN

        self.assertEqual(
            str(error.exception),
            f"Error with getting user / organisastion '{ d.ORGANISATION_NAME_BAD }', returned - 'Not Found'",
        )

    def test_current_repo_on_github(self):
        gc = GitController(env_location=c.TESTING_ENV_PATH_GIT)
        self.assertTrue(
            gc.current_repo_on_github(
                d.ORGANISATION_NAME_GOOD, d.REPO_NAME_CURRENT
            )
        )

    def test_create_repo(self):
        gc = GitController(env_location=c.TESTING_ENV_PATH_GIT)
        if gc.current_repo_on_github(
            d.ORGANISATION_NAME_GOOD, d.REPO_NAME_NEW
        ):
            gc.delete_repo(d.ORGANISATION_NAME_GOOD, d.REPO_NAME_NEW)

        self.assertFalse(
            gc.current_repo_on_github(
                d.ORGANISATION_NAME_GOOD, d.REPO_NAME_NEW
            )
        )

        gc.create_repo(d.ORGANISATION_NAME_GOOD, d.REPO_NAME_NEW)
        self.assertTrue(
            gc.current_repo_on_github(
                d.ORGANISATION_NAME_GOOD, d.REPO_NAME_NEW
            )
        )

    def test_delete_repo(self):
        gc = GitController(env_location=c.TESTING_ENV_PATH_GIT)
        if not gc.current_repo_on_github(
            d.ORGANISATION_NAME_GOOD, d.REPO_NAME_NEW
        ):
            gc.create_repo(d.ORGANISATION_NAME_GOOD, d.REPO_NAME_NEW)

        self.assertTrue(
            gc.current_repo_on_github(
                d.ORGANISATION_NAME_GOOD, d.REPO_NAME_NEW
            )
        )

        gc.delete_repo(d.ORGANISATION_NAME_GOOD, d.REPO_NAME_NEW)

        self.assertFalse(
            gc.current_repo_on_github(
                d.ORGANISATION_NAME_GOOD, d.REPO_NAME_NEW
            )
        )

    # TODO #21 - needs testing of test_commit_and_push
    def test_commit_and_push(self):
        pass

    def test_commit_and_push_already_committed(self):
        pass

    def test_log_hazard(self):
        gc = GitController(
            github_repo=d.REPO_NAME_CURRENT,
            env_location=c.TESTING_ENV_PATH_GIT,
        )
        gc.log_hazard("title", "body", ["hazard"])
        close_all_issues()

    def test_log_hazard_label_bad(self):
        gc = GitController(
            github_repo=d.REPO_NAME_CURRENT,
            env_location=c.TESTING_ENV_PATH_GIT,
        )
        with self.assertRaises(ValueError) as error:
            gc.log_hazard("title", "body", [d.LABEL_NAME_BAD])

        self.assertEqual(
            str(error.exception),
            f"'{ d.LABEL_NAME_BAD}' is not a valid hazard label. Please review label.yml for available values.",
        )

    def test_log_hazard_repo_bad(self):
        gc = GitController(
            github_repo=d.REPO_BAD_NAME,
            env_location=c.TESTING_ENV_PATH_GIT,
        )
        with self.assertRaises(ValueError) as error:
            gc.log_hazard("title", "body", ["hazard"])

        dot_values = dotenv_values(c.TESTING_ENV_PATH_GIT)
        self.assertEqual(
            str(error.exception),
            f"Error with accessing repo '{ dot_values.get(c.EnvKeys.GITHUB_ORGANISATION.value) }/{ d.REPO_BAD_NAME }', return value 'Not Found'",
        )

    def test_available_hazard_labels_full(self):
        gc = GitController(env_location=c.TESTING_ENV_PATH_GIT)
        self.assertEqual(
            gc.available_hazard_labels(), d.AVAILABLE_HAZARD_LABELS_FULL
        )

    def test_available_hazard_labels_name_only(self):
        gc = GitController(env_location=c.TESTING_ENV_PATH_GIT)
        self.assertEqual(
            gc.available_hazard_labels("name_only"),
            d.AVAILABLE_HAZARD_LABELS_NAME_ONLY,
        )

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

    def test_open_hazards(self):
        gc = GitController(
            github_repo=d.REPO_NAME_CURRENT,
            env_location=c.TESTING_ENV_PATH_GIT,
        )
        gc.log_hazard("title", "body", ["hazard"])

        open_hazard = gc.open_hazards()[0]
        self.assertTrue(open_hazard["title"], "title")
        self.assertTrue(open_hazard["body"], "body")
        self.assertTrue(open_hazard["labels"], {"hazard"})
        close_all_issues()

    def test_open_hazards_repo_bad(self):
        gc = GitController(
            github_repo=d.REPO_BAD_NAME,
            env_location=c.TESTING_ENV_PATH_GIT,
        )

        with self.assertRaises(ValueError) as error:
            gc.log_hazard("title", "body", ["hazard"])

        dot_values = dotenv_values(c.TESTING_ENV_PATH_GIT)
        self.assertEqual(
            str(error.exception),
            f"Error with accessing repo '{ dot_values.get(c.EnvKeys.GITHUB_ORGANISATION.value) }/{ d.REPO_BAD_NAME }', return value 'Not Found'",
        )
        close_all_issues()

    def test_repo_domain_name(self):
        gc = GitController(
            github_repo=d.REPO_NAME_CURRENT,
            env_location=c.TESTING_ENV_PATH_GIT,
        )
        self.assertTrue(gc.repo_domain_name(), d.ORGANISATION_NAME_GOOD)

    def test_add_comment_to_hazard(self):
        gc = GitController(
            github_repo=d.REPO_NAME_CURRENT,
            env_location=c.TESTING_ENV_PATH_GIT,
        )
        gc.log_hazard("title", "body", ["hazard"])

        hazard_number = gc.open_hazards()[0]["number"]
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

    @classmethod
    def tearDownClass(cls):
        gc = GitController(env_location=c.TESTING_ENV_PATH_GIT)
        if gc.current_repo_on_github(
            d.ORGANISATION_NAME_GOOD, d.REPO_NAME_NEW
        ):
            gc.delete_repo(d.ORGANISATION_NAME_GOOD, d.REPO_NAME_NEW)

        close_all_issues()
