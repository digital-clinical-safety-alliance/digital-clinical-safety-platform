"""

"""
from dotenv import load_dotenv, set_key, find_dotenv, dotenv_values
import sys
from git import Repo
from github import Github, Issue
import pexpect
import yaml

import constants as c


class GitController:
    def __init__(
        self,
        repo_path_local: str | None = c.REPO_PATH_LOCAL,
        repo_name: str | None = c.REPO_NAME,
        user_org: str | None = None,
        token: str | None = None,
        env_location: str | None = c.ENV_PATH,
    ) -> None:
        dot_values = dotenv_values(env_location)

        if user_org == None:
            self.user_org = dot_values.get("GITHUB_USERNAME_ORG")
            if self.user_org == None:
                raise ValueError(
                    f"Github username / org is not set either as an arguement or in .env"
                )
        if token == None:
            self.token = dot_values.get("GITHUB_TOKEN")
            if self.token == None:
                raise ValueError(
                    f"Github token is not set either as an arguement or in .env"
                )

        if repo_path_local == None:
            raise ValueError(f"'repo_path_local' has not been set")

        if repo_name == None:
            raise ValueError(f"'repo_name' has not been set")

        self.repo_path_local = str(repo_path_local)
        self.repo_name = str(repo_name)
        return

    def get_repos(self) -> list[str]:
        """ """
        repos_found: list[str] = []

        g = Github(self.token)
        github_ctrl = g.get_user(self.user_org)

        for repo in github_ctrl.get_repos():
            repos_found.append(repo.name)

        return repos_found

    def current_repo_on_github(self, repo_name: str) -> bool:
        """ """
        current_repos_on_github: list[str] = []

        current_repos_on_github = self.get_repos()

        if repo_name in current_repos_on_github:
            return True
        else:
            return False

    def create_repo(self, repo_name: str) -> bool:
        """ """
        g: Github
        # github_ctrl

        if self.current_repo_on_github(repo_name):
            return False

        g = Github(self.user_org, self.token)
        github_ctrl = g.get_organization(self.user_org)
        repo = github_ctrl.create_repo(repo_name)

        return True

    def delete_repo(self, repo_name: str) -> bool:
        """ """
        g: Github
        # github_ctrl

        if not self.current_repo_on_github(repo_name):
            return False

        g = Github(self.user_org, self.token)
        github_ctrl = g.get_organization(self.user_org)
        repo = github_ctrl.get_repo(repo_name)
        repo.delete()
        return True

    def commit_and_push(
        self,
        commit_message: str = "No message supplied",
        verbose: bool = False,
    ) -> bool:
        repo = Repo(self.repo_path_local)
        repo.git.add("--all")

        repo.git.commit("-m", commit_message)

        origin = repo.remote(name="origin")
        # TODO - need to erro handle this part with 'try'
        child = pexpect.spawn("git push", timeout=10)
        child.expect("Username for 'https://github.com': ")
        child.sendline(self.user_org)
        child.expect(f"Password for 'https://{ self.user_org }@github.com': ")
        child.sendline(self.token)

        if verbose:
            output = child.readline()
            while b"\r\n" in output:
                print(output)
                output = child.readline()
        else:
            child.wait()
        return True

    def log_hazard(self, title: str, body: str, labels: list[str]) -> bool:
        g: Github
        # repo

        for label in labels:
            print(label)
            if not self.verify_label(label):
                raise ValueError(
                    f"'{ label } is not a valid hazard label. Please review label.yml for available values."
                )

        # Can use assignee="github-username" too
        g = Github(self.token)
        repo = g.get_repo(f"{ self.user_org }/{ self.repo_name }")
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

    def open_hazards(self):
        g = Github(self.token)
        repo = g.get_repo(f"{ self.user_org }/{ self.repo_name }")
        open_issues = repo.get_issues(state="open")
        # print(open_issues)
        for issue in open_issues:
            print(issue)
        return


if __name__ == "__main__":
    print("Starting...")
    gc = GitController("/cshd", "clinical-safety-hazard-documentation")
    # print(gc.get_repos())
    # print(gc.current_repo_on_github("clinical-safety-hazard-documentation"))
    # gc.commit_and_push("A commit with a new function")
    # print(gc.get_repos())
    # gc.hazard_log("Test title 3", "This is a test body of issue 3", ["hazard"])
    # gc.available_hazard_labels()
    # print(gc.verify_hazard_label("hazard"))
    # gc.open_issues()
    # print(gc.create_repo("abc"))
    print(gc.delete_repo("abc"))
