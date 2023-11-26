"""

"""
import git
from dotenv import load_dotenv, set_key, find_dotenv, dotenv_values
import sys
from git import Repo
from github import Github
import os
import pexpect


class GitController:
    def __init__(
        self,
        repo_path: str | None = None,
        user_org: str | None = None,
        token: str | None = None,
    ) -> None:
        if user_org == None and token == None:
            # TODO - will need to change find_dotenv() to live .env location
            dot_values = dotenv_values(find_dotenv())
            self.repo_path = repo_path
            # TODO - will need to handle None case
            self.user_org = dot_values.get("user_org")
            self.token = dot_values.get("github_token")
        else:
            raise FileNotFoundError(f"To be determined.")

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
        repo = Repo(self.repo_path)
        repo.git.add("--all")

        repo.git.commit("-m", commit_message)

        origin = repo.remote(name="origin")
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


if __name__ == "__main__":
    print("Starting...")
    gc = GitController("/cshd")
    gc.commit_and_push("A commit with a new function")
    # print(gc.get_repos())
