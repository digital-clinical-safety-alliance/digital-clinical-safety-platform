"""

"""
from dotenv import load_dotenv, set_key, find_dotenv, dotenv_values
import sys
from git import Repo
from github import Github, Issue
import pexpect
import yaml

ISSUE_LABELS_PATH: str = "/cshd/.github/labels.yml"


class GitController:
    def __init__(
        self,
        repo_path_local: str | None = None,
        repo_name: str | None = None,
        user_org: str | None = None,
        token: str | None = None,
    ) -> None:
        if user_org == None and token == None:
            # TODO - will need to change find_dotenv() to live .env location
            dot_values = dotenv_values(find_dotenv())
            self.user_org = dot_values.get("user_org")
            self.token = dot_values.get("github_token")
        else:
            raise FileNotFoundError(f"To be determined.")

        # TODO - will need to handle None case
        self.repo_path_local = repo_path_local
        self.repo_name = repo_name

        return

    def get_repos(self) -> list[str]:
        repos_found: list[str] = []
        g = Github(self.token)
        github_ctrl = g.get_user(self.user_org)

        for repo in github_ctrl.get_repos():
            repos_found.append(repo.name)

        return repos_found

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

    def hazard_log(self, title: str, body: str, labels: list[str]) -> bool:
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
        issues_names_only: list[str]

        if details != "full" and details != "name_only":
            raise ValueError(
                    f"'{ details } is not a valid option"
                )

        with open(ISSUE_LABELS_PATH, "r") as file:
            issues_yml = yaml.safe_load(file)

        # for label in issues_yml:
        #    print(label)

        if details == "full":
            return issues_yml
        else:
            for label_definition in issues_yml:
                label_definition["name"].lower():


    def verify_hazard_label(self, label: str) -> bool:
        issues_yml: list[dict[str, str]]

        issues_yml = self.available_hazard_labels()

        for label_definition in issues_yml:
            if label.lower() in label_definition["name"].lower():
                return True

        return False


if __name__ == "__main__":
    print("Starting...")
    gc = GitController("/cshd", "clinical-safety-hazard-documentation")
    # gc.commit_and_push("A commit with a new function")
    # print(gc.get_repos())
    gc.hazard_log("Test title 3", "This is a test body of issue 3", ["hazard"])
    # gc.available_hazard_labels()
    # print(gc.verify_hazard_label("hazard"))
