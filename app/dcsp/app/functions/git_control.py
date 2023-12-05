"""Management of git and GitHub

If no organisation is provided, repos will be presumed to be stored under username
on Github

Classes:
    GitController

"""

# TODO - need to check all function work with username and organisations as domain_name

from dotenv import dotenv_values
import sys
from git import Repo
from github import (
    Github,
    GithubException,
    Repository,
    NamedUser,
    AuthenticatedUser,
)
import pexpect
import yaml
import requests
from requests import Response
import os
from typing import Any

sys.path.append("/dcsp/app/dcsp/")  # TODO temp
import app.functions.constants as c
from app.functions.constants import GhCredentials
from app.functions.email_functions import EmailFunctions


class GitController:
    def __init__(
        self,
        github_username: str = "",
        email: str = "",
        github_organisation: str = "",
        github_repo: str = c.REPO_NAME,
        github_token: str = "",
        repo_path_local: str = c.REPO_PATH_LOCAL,
        env_location: str = c.ENV_PATH,
    ) -> None:
        """Initialising GitController class

        Initialisation of the git and GitHub functionality.

        Args:
            github_username (str): the user's GitHub personal username.
            email (str): the user's personal email address.
            github_organisation (str): the organisation that the user wishes to
                                       associate repositories with. If this an
                                       empty string is supplied then username is
                                       used as storage location for repositories.
            github_repo (str): Name of the GitHub repository.
            github_token (str): GitHub token.
            repo_path_local (str): Local name of repository.
            env_location (str): Location of .env file. Mainly changed for unit
                                testing purposes.
        Raises:
            ValueError: if a empty string is supplied as the env_location.
            ValueError: if env_location is an invalid file path.
            ValueError: if no GitHub username is supplied as an argument or in
                        the .env file.
            ValueError: if no email is supplied as an argument or in the .env
                        file.
            ValueError: if invalid syntax of email (does not check to see if a
                        current and working email address).
            ValueError: if github_repo is set to an empty string.
            ValueError: if no github_token is supplied as an argument or in
                        the .env file.
            ValueError: if repo_path_local is set to an empty string.
            FileNotFoundError: if repo_path_local points to a invalid or non-
                               existing directory.
        """
        self.github_username: str = ""
        self.email: str = ""
        self.github_organisation: str = ""
        self.github_token: str = ""

        if env_location == "":
            raise ValueError(f".env location is set to empty string")

        if not os.path.isfile(env_location):
            raise ValueError(
                f"'{ env_location }' path for .env file does not exist"
            )

        dot_values = dotenv_values(env_location)

        if github_username == "":
            self.github_username = str(dot_values.get("GITHUB_USERNAME") or "")
            if self.github_username == "":
                raise ValueError(
                    f"'{ c.EnvKeys.GITHUB_USERNAME.value }' has not been set as an argument or in .env"
                )
        else:
            self.github_username = github_username

        if email == "":
            self.email = str(dot_values.get("EMAIL") or "")
            if self.email == "":
                raise ValueError(
                    f"'{ c.EnvKeys.EMAIL.value }' has not been set as an argument or in .env"
                )
        else:
            self.email = email

        email_function = EmailFunctions()
        if not email_function.valid_syntax(self.email):
            raise ValueError(f"Email address '{ self.email }' is invalid")

        if github_organisation == "":
            self.github_organisation = str(
                dot_values.get("GITHUB_ORGANISATION" or "")
            )

        if github_repo == "":
            raise ValueError(f"'github_repo' has not been set")
        else:
            self.github_repo = github_repo

        if github_token == "":
            self.github_token = str(dot_values.get("GITHUB_TOKEN") or "")
            if self.github_token == None or self.github_token == "":
                raise ValueError(
                    f"'{ c.EnvKeys.GITHUB_TOKEN.value }' has not been set as an argument or in .env"
                )
        else:
            self.github_token = github_token

        if repo_path_local == "":
            raise ValueError(f"'repo_path_local' has not been set")
        else:
            self.repo_path_local = repo_path_local
            if not os.path.isdir(repo_path_local):
                raise FileNotFoundError(
                    f"'{ repo_path_local }' is not a valid path for 'repo_path_local'"
                )

        return None

    def check_github_credentials(self) -> dict[str, str | bool | None]:
        """Checking Github credentials

        If no organisation is provided, then username will be used for repo storage location
        Args:
            none taken
        Returns:
            dict: a dictionary with 4 values covering the validity of the credentials supplied
                  in the initialisation of the GitController class
        """
        g: Github
        github_username_exists: bool = False
        github_organisation_exists: bool = False
        repo_exists: bool = False
        permission: str | None = None
        results: dict[str, str | bool | None] = {}
        username_request: Response
        repo_request: Response
        repo: Repository.Repository

        username_request = requests.get(
            f"https://api.github.com/users/{ self.github_username }",
            auth=(self.github_username, self.github_token),
        )

        if username_request.status_code == 200:
            github_username_exists = True
        elif username_request.status_code == 404:
            github_username_exists = False
        else:
            raise ValueError(
                f"Error with Github username checking. Returned value of: {username_request.status_code }"
            )

        github_organisation_exists = self.organisation_exists(
            self.github_organisation
        )

        # TODO this is dependent on valid credentials
        repo_request = requests.get(
            f"https://api.github.com/repos/{ self.repo_domain_name() }/{ self.github_repo }",
            auth=(self.github_organisation, self.github_token),
        )

        if repo_request.status_code == 200:
            repo_exists = True

            g = Github(self.github_username, self.github_token)
            repo = g.get_repo(
                f"{ self.repo_domain_name() }/{ self.github_repo }"
            )

            try:
                permission = repo.get_collaborator_permission(
                    self.github_username
                )
            except GithubException:
                pass
        elif repo_request.status_code == 404:
            repo_exists = False
        else:
            raise ValueError(
                f"Error with Github repo checking. Returned value of: {repo_request.status_code }"
            )

        results = {
            "github_username_exists": github_username_exists,
            "github_organisation_exists": github_organisation_exists,
            "repo_exists": repo_exists,
            "permission": permission,
        }
        return results

    def organisation_exists(self, organisation: str) -> bool:
        """Checks if the GitHub organisation exists

        Checks to see if the provided organisation name exists. This utilises
        authentification, so good credentitals are needed.

        Args:
            organisation (str): name of GitHub organisation to test.
        Returns:
            bool: True if exists, False if does not.
        Raises:
            ValueError: if bad return code from GET request
        """
        organisation_request: Response
        github_organisation_exists: bool = False

        organisation_request = requests.get(
            f"https://api.github.com/users/{ organisation }",
            auth=(self.github_organisation, self.github_token),
        )

        if organisation_request.status_code == 200:
            github_organisation_exists = True
        elif organisation_request.status_code == 404:
            github_organisation_exists = False
        else:
            raise ValueError(
                f"Error with Github organisation checking. Returned value of: {organisation_request.status_code }"
            )

        return github_organisation_exists

    def get_repos(self, github_user_org: str) -> list[str]:
        """Returns a list of repositories for a user or organisation

        Gets a list of repositories under a specified user or organisation

        Args:
            github_user_org (str): the username or organisation to look for the
                                   repositories under.
        Returns:
            list[str]: a list of repositories. Returns empty list if unsuccessful in
                       getting
        """
        g: Github
        github_user: NamedUser.NamedUser | AuthenticatedUser.AuthenticatedUser
        repos_found: list[str] = []
        repo: Repository.Repository

        g = Github(self.github_username, self.github_token)

        try:
            github_user = g.get_user(github_user_org)
        except GithubException as error:
            raise ValueError(
                f"Error with getting user / organisastion '{ github_user_org }', returned - '{ error.data['message'] }'"
            )
        else:
            for repo in github_user.get_repos():
                repos_found.append(repo.name)

        return repos_found

    def current_repo_on_github(
        self, github_use_org: str, github_repo: str
    ) -> bool:
        """ """
        current_repos_on_github: list[str] = []

        current_repos_on_github = self.get_repos(github_use_org)

        if github_repo in current_repos_on_github:
            return True
        else:
            return False

    def create_repo(self, github_use_org: str, github_repo: str) -> bool:
        """ """
        g: Github
        # github_user

        if self.current_repo_on_github(github_use_org, github_repo):
            return False

        g = Github(self.github_username, self.github_token)
        # try:
        # github_user = g.get_user(github_use_org)
        # except:
        github_user = g.get_organization(github_use_org)

        repo = github_user.create_repo(github_repo)

        return True

    def delete_repo(self, github_use_org: str, github_repo: str) -> bool:
        """ """
        g: Github
        # github_user

        if not self.current_repo_on_github(github_use_org, github_repo):
            return False

        g = Github(self.github_username, self.github_token)
        github_user = g.get_organization(github_use_org)
        repo = github_user.get_repo(github_repo)
        repo.delete()
        return True

    # TODO #20 - needs lots of testing
    # TODO - need to figure out if it failed
    # TODO - also need to make sure a push to gh pages is set on Github
    def commit_and_push(
        self,
        commit_message: str = "Automated commit",
        verbose: bool = False,
    ) -> bool:
        """Commits changes and then pushes to repo

        Initially checks if the git configs are set, and if not sets
        The username and email. Then commits the changes with the supplied
        message. If verbose is set to true, then a print out of the pexpect
        execution is given.

        Args:
            commit_message (str): message for the commit
            verbose (bool): set to True to display stdout of push.
        Returns:
            bool: currently returns False if commit fails
        """

        repo = Repo(self.repo_path_local)

        # TODO #19 - how will this work with lots of other users.
        try:
            repo.config_reader().get_value("user", "name")
            repo.config_reader().get_value("user", "email")
        except:
            os.system(
                f"git config --global user.name '{ self.github_username }'"
            )
            os.system(f"git config --global user.email '{ self.email }'")

        repo = Repo(self.repo_path_local)
        repo.git.add("--all")

        try:
            # This fails if branch is up to date
            repo.git.commit("-m", commit_message)
        except Exception as e:
            return False

        # origin = repo.remote(name="origin")

        # TODO - need to error handle this part with 'try'
        child = pexpect.spawn("git push", timeout=10)
        child.expect("Username for 'https://github.com': ")
        child.sendline(self.github_username)
        child.expect(
            f"Password for 'https://{ self.github_username }@github.com': "
        )
        child.sendline(self.github_token)

        if verbose:
            output = child.readline()
            while b"\r\n" in output:
                split = output.split(b"\r")
                for s in split:
                    print(s.decode("ascii"))
                output = child.readline()
        else:
            child.wait()
        return True

    def log_hazard(self, title: str, body: str, labels: list[str]) -> None:
        """Uses GitHub issues to log a new hazard

        Hazards are logged as issues on GitHub

        Args:
            title (str): Title for the issue.
            body (str): Body for the issue.
            labels (list[str]): a list of labels for the issue.
        Returns:
            None
        Raises:
            ValueError: if a hazard label is not valid
            ValueError: if issue with accessing the repo
        """
        g: Github
        repo: Repository.Repository

        for label in labels:
            if not self.verify_hazard_label(label):
                raise ValueError(
                    f"'{ label }' is not a valid hazard label. Please review label.yml for available values."
                )

        g = Github(self.github_username, self.github_token)

        try:
            repo = g.get_repo(
                f"{ self.repo_domain_name() }/{ self.github_repo }"
            )
            repo.create_issue(
                title=title,
                body=body,
                labels=labels,
            )
        except GithubException as error:
            raise ValueError(
                f"Error with accessing repo '{ self.repo_domain_name() }/{ self.github_repo }', return value '{ error.data['message'] }'"
            )

        return

    def available_hazard_labels(self, details: str = "full") -> list:
        """Provides a list of available hazard labels

        Reads from the labels yaml file and returns a list of valid hazard labels

        Args:
            details (str): full = all details of all hazard labels. name_only =
                           names only of all hazard labels.
        Returns:
            list: either a list[dict[str,str]] if "full" details are requested or
                  else a list[str] if names_only requested.
        Raises:
            ValueError: if details argument is not "full" or "name_only"
            FileNotFoundError: if a bad file path is given for the labels yaml.
        """
        issues_yml: list[dict[str, str]]
        issues_names_only: list[str] = []

        if details != "full" and details != "name_only":
            raise ValueError(
                f"'{ details }' is not a valid option for return values of hazard labels"
            )

        try:
            with open(c.ISSUE_LABELS_PATH, "r") as file:
                issues_yml = yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Labels.yml does not exist at '{ c.ISSUE_LABELS_PATH }'"
            )

        if details == "full":
            return issues_yml
        else:
            for label_definition in issues_yml:
                issues_names_only.append(label_definition["name"].lower())
            return issues_names_only

    def verify_hazard_label(self, label: str) -> bool:
        """Checks if a label name is valid

        Checking against all known valid hazard labels, checks if label name
        supplied is valid.

        Args:
            label (str): label to be examined.
        Returns:
            bool: True if a valid label, False if not.
        """
        issues_yml: list = self.available_hazard_labels("name_only")
        label_name: str = ""

        for label_name in issues_yml:
            if label.lower() in label_name.lower():
                return True

        return False

    def open_hazards(self) -> list[dict]:
        """Returns a list of open hazards on GitHub"""
        g: Github
        open_hazards: list[dict] = []
        label_list: list = []
        issue: Any
        open_issues: Any

        g = Github(self.github_username, self.github_token)

        try:
            repo = g.get_repo(
                f"{ self.repo_domain_name() }/{ self.github_repo }"
            )
            open_issues = repo.get_issues(state="open")
        except GithubException as error:
            raise ValueError(
                f"Error with accessing repo '{ self.repo_domain_name() }/{ self.github_repo }', return value '{ error.data['message'] }'"
            )

        for issue in open_issues:
            label_list.clear()
            for label in issue.labels:
                label_list.append(label.name)
            open_hazards.append(
                {
                    "number": issue.number,
                    "title": issue.title,
                    "body": issue.body,
                    "labels": label_list.copy(),
                }
            )
        return open_hazards

    def repo_domain_name(self) -> str:
        """ """
        repo_domain: str = ""

        if self.github_organisation == None:
            repo_domain = self.github_username
        else:
            repo_domain = self.github_organisation

        return repo_domain

    def add_comment_to_hazard(
        self,
        github_use_org: str = "",  # TODO - might need to implement
        github_repo: str = "",  # TODO - might need to implement
        hazard_number: int = 0,
        comment: str = "",
    ) -> bool:
        """ """
        issue: Any

        if hazard_number == 0:
            raise ValueError(f"No Hazard Number has been provided")

        g = Github(self.github_username, self.github_token)

        try:
            repo = g.get_repo(
                f"{ self.repo_domain_name() }/{ self.github_repo }"
            )

        except GithubException as error:
            raise ValueError(
                f"Error with accessing repo '{ self.repo_domain_name() }/{ self.github_repo }', return value '{ error.data['message'] }'"
            )
        else:
            issue = repo.get_issue(number=int(hazard_number))
            issue.create_comment(comment)

        return True
