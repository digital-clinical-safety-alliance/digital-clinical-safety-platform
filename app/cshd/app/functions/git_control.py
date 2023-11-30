"""
    If no organisation is provided, repos will be presumed to be stored under username
    on Github

"""
from dotenv import load_dotenv, set_key, find_dotenv, dotenv_values
import sys
from git import Repo
from github import Github, Issue, Auth
import configparser
import pexpect
import yaml
import requests
import os

import constants as c
from constants import GhCredentials


class GitController:
    def __init__(
        self,
        github_username: str | None = None,
        email: str | None = None,
        github_organisation: str | None = None,
        github_repo: str | None = c.REPO_NAME,
        github_token: str | None = None,
        repo_path_local: str | None = c.REPO_PATH_LOCAL,
        env_location: str | None = c.ENV_PATH,
    ) -> None:
        """Initialising GitController class"""

        if env_location == None or env_location == "":
            if self.github_username == None or self.github_username == "":
                raise ValueError(f".env location is invalid")

        dot_values = dotenv_values(env_location)

        if github_username == None or github_username == "":
            self.github_username = dot_values.get("GITHUB_USERNAME")
            if self.github_username == None or self.github_username == "":
                raise ValueError(
                    f"Github username is not set either as an arguement or in .env"
                )
        else:
            self.github_username = github_username

        if email == None or email == "":
            self.email = dot_values.get("EMAIL")
            if self.email == None or self.email == "":
                raise ValueError(
                    f"'Email' has not been set as an argument or in .env"
                )
        else:
            self.email = email

        if github_organisation == None:
            self.github_organisation = dot_values.get("GITHUB_ORGANISATION")
            if (
                self.github_organisation == None
                or self.github_organisation == ""
            ):
                raise ValueError(
                    f"'Organisation' has not been set as an argument or in .env"
                )
        else:
            self.github_organisation = github_organisation

        if github_repo == None or github_repo == "":
            raise ValueError(f"'github_repo' has not been set")
        else:
            self.github_repo = str(github_repo)

        if github_token == None:
            self.github_token = dot_values.get("GITHUB_TOKEN")
            if self.github_token == None or self.github_token == "":
                raise ValueError(
                    f"'Github token' is not set either as an arguement or in .env"
                )
        else:
            self.github_token = github_token

        if repo_path_local == None or repo_path_local == "":
            raise ValueError(f"'repo_path_local' has not been set")
        else:
            self.repo_path_local = str(repo_path_local)

        return None

    def check_github_credentials(self) -> dict[str, str | bool | None]:
        """Checking Github credentials
        If no organisation is provided, then username will be used for repo storage location
        """
        g: Github
        github_username_exists: bool = False
        github_organisation_exists: bool = False
        repo_domain: str = ""
        repo_exists: bool = False
        permission: str | None = None
        results: dict[str, str | bool | None] = {}
        # username_request
        # organisation_request
        # repo_request

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

        if self.github_organisation == None:
            repo_domain = self.github_username
        else:
            repo_domain = self.github_organisation

        repo_request = requests.get(
            f"https://api.github.com/repos/{ repo_domain }/{ self.github_repo }"
        )

        if repo_request.status_code == 200:
            repo_exists = True

            g = Github(self.github_username, self.github_token)
            repo = g.get_repo(f"{ repo_domain }/{ self.github_repo }")

            try:
                permission = repo.get_collaborator_permission(
                    self.github_username
                )
            except GithubException as error:
                # print(f"Error - { error.data['message'] }")
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
        """ """
        # organisation_request
        # github_organisation_exists

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
        """ """
        repos_found: list[str] = []

        g = Github(self.github_username, self.github_token)
        try:
            github_ctrl = g.get_user(github_user_org)
        except GithubException as error:
            # print(f"- Fail, repo was '{ error.data['message'] }'")
            pass
        else:
            for repo in github_ctrl.get_repos():
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

    def create_repo(self, github_repo: str) -> bool:
        """ """
        g: Github
        # github_ctrl

        if self.current_repo_on_github(github_repo):
            return False

        g = Github(self.user_org, self.github_token)
        github_ctrl = g.get_organization(self.user_org)
        repo = github_ctrl.create_repo(github_repo)

        return True

    def delete_repo(self, github_repo: str) -> bool:
        """ """
        g: Github
        # github_ctrl

        if not self.current_repo_on_github(github_repo):
            return False

        g = Github(self.user_org, self.github_token)
        github_ctrl = g.get_organization(self.user_org)
        repo = github_ctrl.get_repo(github_repo)
        repo.delete()
        return True

    # TODO - need to figure out if it failed
    def commit_and_push(
        self,
        commit_message: str = "No message supplied",
        verbose: bool = False,
    ) -> bool:
        """ """

        repo = Repo(self.repo_path_local)

        try:
            repo.config_reader().get_value("user", "name")
            repo.config_reader().get_value("user", "email")
        except configparser.NoOptionError:
            os.system(
                f"git config --global user.name '{ self.github_username }'"
            )
            os.system(f"git config --global user.email '{ self.email }'")

        repo = Repo(self.repo_path_local)
        repo.git.add("--all")

        try:
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

    def log_hazard(self, title: str, body: str, labels: list[str]) -> bool:
        g: Github
        # repo

        for label in labels:
            print(label)
            if not self.verify_hazard_label(label):
                raise ValueError(
                    f"'{ label } is not a valid hazard label. Please review label.yml for available values."
                )

        g = Github(self.user_org, self.github_token)
        repo = g.get_repo(f"{ self.user_org }/{ self.github_repo }")
        repo.create_issue(
            title=title,
            body=body,
            labels=labels,
        )

        return True

    def available_hazard_labels(
        self, details: str = "full"
    ) -> list[dict[str, str]] | list[str]:
        issues_yml: list[dict[str, str]]
        issues_names_only: list[str] = []

        if details != "full" and details != "name_only":
            raise ValueError(f"'{ details } is not a valid option")

        with open(c.ISSUE_LABELS_PATH, "r") as file:
            issues_yml = yaml.safe_load(file)

        # for label in issues_yml:
        #    print(label)

        if details == "full":
            return issues_yml
        else:
            for label_definition in issues_yml:
                issues_names_only.append(label_definition["name"].lower())
            return issues_names_only  # TODO - need to test if works

    def verify_hazard_label(self, label: str) -> bool:
        issues_yml: list[dict[str, str]]

        issues_yml = self.available_hazard_labels()

        for label_definition in issues_yml:
            if label.lower() in label_definition["name"].lower():
                return True

        return False

    def open_hazards(self) -> list[dict]:
        """ """
        g: Github
        open_hazards: list[dict] = []
        label_list: list = []

        g = Github(self.github_token)
        repo = g.get_repo(f"{ self.user_org }/{ self.github_repo }")
        open_issues = repo.get_issues(state="open")

        for issue in open_issues:
            print(issue)
            label_list.clear()
            for label in issue.labels:
                label_list.append(label.name)
                # print(label.split('"')[1].split('"')[0])
            open_hazards.append(
                {
                    "number": issue.number,
                    "title": issue.title,
                    "body": issue.body,
                    "labels": label_list.copy(),
                }
            )
        return open_hazards


if __name__ == "__main__":
    print("Starting...")
    # gc = GitController()
    gc = GitController(
        github_username="CotswoldsMaker",
        github_organisation="clinicians-who-code",
        github_repo="clinical-safety-hazard-documentation",
    )
    """gc = GitController(
        github_username="CotswoldsMaker",
        github_repo="QuickSpiritum",
    )"""
    # print(gc.check_github_credentials())
    # print(gc.get_repos("clinicians-who-code"))
    """print(
        gc.current_repo_on_github(
            "clinicians-who-code", "clinical-safety-hazard-documentation"
        )
    )"""
    print(gc.commit_and_push("A commit with a new function"))
    # print(gc.get_repos())
    # gc.log_hazard("Test title 3", "This is a test body of issue 3", ["hazard"])
    # gc.available_hazard_labels()
    # print(gc.verify_hazard_label("hazard"))
    # gc.open_issues()
    # print(gc.create_repo("abc"))
    # print(gc.delete_repo("abc"))
    # gc.open_hazards()
