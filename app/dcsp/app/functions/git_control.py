"""Management of git and GitHub

If no organisation is provided, repos will be presumed to be stored under username
on Github

Classes:
    GitController: handle git and GitHub functionality
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
    Organization,
    PaginatedList,
)
from github.Issue import Issue

import pexpect
import yaml
import requests
from requests import Response, exceptions
import os
import subprocess  # nosec B404
from typing import Any
from pathlib import Path

sys.path.append("/dcsp/app/dcsp/")  # TODO temp
import app.functions.constants as c
from app.functions.constants import GhCredentials
from app.functions.email_functions import (
    EmailFunctions,
)


class GitHubController:
    def __init__(self, username: str, password_token: str):
        """ """
        if username == "":
            raise ValueError("'username' cannot be empty")
        if password_token == "":  # nosec B105
            raise ValueError("'password_token' cannot be empty")

        self.username: str = username
        self.password_token: str = password_token

    def exists(self, repo_url: str) -> bool:
        """ """
        g = Github(self.username, self.password_token)

        # Find the index of the second-to-last forward slash
        index_of_second_last_slash = repo_url.rfind(
            "/", 0, repo_url.rfind("/")
        )

        # Retrieve the substring after the second-to-last forward slash
        repo_path = repo_url[index_of_second_last_slash + 1 :]

        try:
            repo = g.get_repo(repo_path)
        except GithubException:
            return False
        return True


if __name__ == "__main__":
    gh = GitHubController("", "")

    url = "https://github.com/digital-clinical-safety-alliance/digital-clinical-safety-platform"

    # print(gh.exists(url))


class GitController:
    def __init__(
        self,
        github_username: str = "",
        email: str = "",
        github_organisation: str = "",
        github_repo: str = c.REPO_NAME,
        default_external_repository_token: str = "",
        repo_path_local: str = c.REPO_PATH_LOCAL,
        env_location: str = c.ENV_PATH_PLACEHOLDERS,
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
            default_external_repository_token (str): GitHub token.
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
            ValueError: if no default_external_repository_token is supplied as an argument or in
                        the .env file.
            ValueError: if repo_path_local is set to an empty string.
            FileNotFoundError: if repo_path_local points to a invalid or non-
                               existing directory.
        """
        self.github_username: str = ""
        self.email: str = ""
        self.github_organisation: str = ""
        self.default_external_repository_token: str = ""

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
                    f"'{ c.EnvKeysPH.GITHUB_USERNAME.value }' has not been set as an argument or in .env"
                )
        else:
            self.github_username = github_username

        if email == "":
            self.email = str(dot_values.get("EMAIL") or "")
            if self.email == "":
                raise ValueError(
                    f"'{ c.EnvKeysPH.EMAIL.value }' has not been set as an argument or in .env"
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
        else:
            self.github_organisation = github_organisation

        if github_repo == "":
            self.github_repo = str(dot_values.get("GITHUB_REPO") or "")
            if self.github_repo == "":
                raise ValueError(
                    f"'{ c.EnvKeysPH.GITHUB_REPO.value }' has not been set as an argument or in .env"
                )
        else:
            self.github_repo = github_repo

        if default_external_repository_token == "":  # nosec B105, B107
            self.default_external_repository_token = str(
                dot_values.get("GITHUB_TOKEN") or ""
            )
            if (
                self.default_external_repository_token == None
                or self.default_external_repository_token == ""  # nosec B105
            ):  # nosec B105, B107
                raise ValueError(
                    f"'{ c.EnvKeysPH.GITHUB_TOKEN.value }' has not been set as an argument or in .env"
                )
        else:
            self.default_external_repository_token = (
                default_external_repository_token
            )

        if repo_path_local == "":
            raise ValueError(f"'repo_path_local' has not been set")
        else:
            self.repo_path_local = repo_path_local
            if not os.path.isdir(repo_path_local):
                raise FileNotFoundError(
                    f"'{ repo_path_local }' is not a valid path for 'repo_path_local'"
                )
        return None

    # TODO #28 - need to find a good way to see if github token and username pair is valid
    # TODO #29 - need to handle 404, 500, Timeout and connection errors
    def check_github_credentials(
        self,
    ) -> dict[str, str | bool | None]:
        """Checking Github credentials

        If no organisation is provided, then username will be used for repo storage location

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

        # TODO ? manage rate limiters

        try:
            username_request = requests.get(
                f"https://api.github.com/users/{ self.github_username }",
                auth=(
                    self.github_username,
                    self.default_external_repository_token,
                ),
                timeout=10,
            )
        except requests.exceptions.ConnectionError:
            raise requests.exceptions.ConnectionError(
                "No connection available to GitHub API"
            )
        except requests.exceptions.Timeout:
            raise requests.exceptions.Timeout(
                "Timeout while connecting to GitHub API"
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

        try:
            repo_request = requests.get(
                f"https://api.github.com/repos/{ self.repo_domain_name() }/{ self.github_repo }",
                auth=(
                    self.github_organisation,
                    self.default_external_repository_token,
                ),
                timeout=10,
            )
        except requests.exceptions.ConnectionError:
            raise requests.exceptions.ConnectionError(
                "No connection available to GitHub API"
            )
        except requests.exceptions.Timeout:
            raise requests.exceptions.Timeout(
                "Timeout while connecting to GitHub API"
            )

        if repo_request.status_code == 200:
            repo_exists = True

            # patch
            g = Github(
                self.github_username,
                self.default_external_repository_token,
            )
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

        # TODO will need to manage other errors like time outs and rate limiters
        try:
            organisation_request = requests.get(
                f"https://api.github.com/users/{ organisation }",
                auth=(
                    self.github_organisation,
                    self.default_external_repository_token,
                ),
                timeout=10,
            )
        except requests.exceptions.ConnectionError:
            raise requests.exceptions.ConnectionError(
                "No connection available to GitHub API"
            )
        except requests.exceptions.Timeout:
            raise requests.exceptions.Timeout(
                "Timeout while connecting to GitHub API"
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
                       getting.

        Raises:
            ValueError: if unable to get user or organisation.
        """
        g: Github
        github_user: NamedUser.NamedUser | AuthenticatedUser.AuthenticatedUser
        repos_found: list[str] = []
        repo: Repository.Repository

        g = Github(
            self.github_username,
            self.default_external_repository_token,
        )

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
        self,
        github_user_org: str,
        github_repo: str,
    ) -> bool:
        """Checks if supplied repository is on GitHub

        Checks if the supplied repository name is on GitHub, in the format
        "github_user_org/github_repo".

        Args:
            github_user_org (str): the username or organisation that the
                                   repository is stored under.
            github_repo (str): the name of the GitHub repository.

        Returns:
            bool: True if is a current repository under the user/organisation
                  or False if not.
        """
        current_repos_on_github: list[str] = self.get_repos(github_user_org)
        # print("")
        # print(str(current_repos_on_github))
        if github_repo in current_repos_on_github:
            return True
        else:
            return False

    def create_repo(
        self,
        github_use_org: str,
        github_repo: str,
    ) -> bool:
        """Create a new repository on GitHub

        If does not already exist, this function will create a new repository
        on GitHub.

        Args:
            github_use_org (str): username or organisation to create the new
                                  repository under.
            github_repo (str): name of new repository.

        Returns:
            bool: False if already exists. True if created.

        Raises:
            ValueError: if invalid credentials supplied to
                        'current_repo_on_github'.
        """
        g: Github
        github_get: Organization.Organization

        try:
            if self.current_repo_on_github(github_use_org, github_repo):
                return False
        except ValueError as error:
            raise ValueError(f"{ error }")

        g = Github(
            self.github_username,
            self.default_external_repository_token,
        )
        github_get = g.get_organization(github_use_org)
        github_get.create_repo(github_repo)
        return True

    def delete_repo(
        self,
        github_use_org: str,
        github_repo: str,
    ) -> bool:
        """Delete a repository on GitHub

        If in existence, then deletes repository on GitHub.

        Args:
            github_use_org (str): username or organisation where repository
                                  is stored.
            github_repo (str): name of repository to delete.

        Returns:
            bool: False if does not exist. True if exists and deleted.
        """
        g: Github
        github_get: Organization.Organization
        repo: Repository.Repository

        if not self.current_repo_on_github(github_use_org, github_repo):
            return False

        g = Github(
            self.github_username,
            self.default_external_repository_token,
        )
        github_get = g.get_organization(github_use_org)
        repo = github_get.get_repo(github_repo)
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
            subprocess.Popen(
                [
                    "/usr/bin/git",
                    "config",
                    "--global",
                    "user.name",
                    self.github_username,
                ],
                shell=False,
            ).wait()  # nosec B603

            subprocess.Popen(
                [
                    "/usr/bin/git",
                    "config",
                    "--global",
                    "user.email",
                    self.email,
                ],
                shell=False,
            ).wait()  # nosec B603

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
        child.sendline(self.default_external_repository_token)

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

    def entry_update(
        self,
        title: str,
        body: str,
        labels: list[str],
    ) -> None:
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

        g = Github(
            self.github_username,
            self.default_external_repository_token,
        )

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

    def available_hazard_labels(
        self, details: str = "full"
    ) -> list[dict[str, str]] | list[str]:
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
        issues_yml: list[dict[str, str]] | list[
            str
        ] = self.available_hazard_labels("name_only")
        label_name: str | dict[str, str] = ""

        for label_name in issues_yml:
            if (
                isinstance(label_name, str)
                and label.lower() in label_name.lower()
            ):
                return True
            elif isinstance(label_name, dict):
                pass

        return False

    def hazards_open(
        self,
    ) -> list[dict[str, Any]]:
        """Returns a list of open hazards on GitHub

        Grabs open hazards (which are actually GitHub Issues) from GitHub

        Returns:
            list[dict[str, Any]]: list of dictionaries of open hazards.

        Raises:
            ValueError: if error with accessing the repository
        """
        g: Github
        hazards_open: list[dict[str, Any]] = []
        label_list: list[str] = []
        issue: Any
        open_issues: PaginatedList.PaginatedList[Issue]
        repo: Repository.Repository

        g = Github(
            self.github_username,
            self.default_external_repository_token,
        )

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
            hazards_open.append(
                {
                    "number": issue.number,
                    "title": issue.title,
                    "body": issue.body,
                    "labels": label_list.copy(),
                }
            )
        return hazards_open

    def repo_domain_name(self) -> str:
        """Domain name set

        If organisational name is not set then use username is used as the
        "domain" name for the repository.

        Returns:
            str: name of domain (organisation or username)
        """
        repo_domain: str = ""

        if self.github_organisation == "":
            repo_domain = self.github_username
        else:
            repo_domain = self.github_organisation

        return repo_domain

    def add_comment_to_hazard(
        self,
        hazard_number: int = 0,
        comment: str = "",
    ) -> None:
        """Add a comment to a hazard

        As a comment to an already open hazard (stored as an issue on GitHub).

        Args:
            hazard_number (int): hazard (issue) number to add comment to.
            comment (str): comment to add to hazard.

        Returns:
            None

        Raises:
            ValueError: if no hazard number is provided.
            ValueError: if no comment if provided.
            ValueError: if issue with accessing the repository.
        """
        g: Github
        repo: Repository.Repository
        issue: Issue

        if hazard_number == 0:
            raise ValueError("No Hazard Number has been provided")

        if comment == "":
            raise ValueError("No comment has been provided")

        g = Github(
            self.github_username,
            self.default_external_repository_token,
        )

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
        return
