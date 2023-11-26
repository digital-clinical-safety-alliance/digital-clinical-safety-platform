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
        self, user_org: str | None = None, token: str | None = None
    ) -> None:
        if user_org == None and token == None:
            # TODO - will need to change find_dotenv() to live .env location
            dot_values = dotenv_values(find_dotenv())
            self.user_org = dot_values.get("user_org")
            print(self.user_org)
            self.token = dot_values.get("github_token")
            print(self.token)
        else:
            raise FileNotFoundError(f"To be determined.")

    def get_repos(self) -> list[str]:
        repos_found: list[str] = []
        g = Github(self.token)
        github_ctrl = g.get_user(self.user_org)

        for repo in github_ctrl.get_repos():
            repos_found.append(repo.name)

        return repos_found

    def commit_and_push(self) -> bool:
        # Path to the local repository
        repo_path = "/cshd"
        # Open the repository
        repo = Repo(repo_path)
        print(1)
        # Stage all changes
        repo.git.add("--all")
        print(2)
        # Commit the changes
        commit_message = "Testing commits and pushes via python"
        repo.git.commit("-m", commit_message)
        print(3)
        # Push the changes to the remote repository
        # repo.remote().push()
        origin = repo.remote(name="origin")
        # origin.push()
        child = pexpect.spawn("git push", timeout=10)
        # print(child.readline())
        child.expect("Username for 'https://github.com': ")
        child.sendline(self.user_org)
        child.expect(f"Password for 'https://{ self.user_org }@github.com': ")
        child.sendline(self.token)
        # child.wait()
        output = child.readline()
        while not (pexpect.EOF in str(output)):
            print(output)
            output = child.readline()
        # print(child.read())
        # print(child.before)
        child.wait()
        print(4)
        # asdjflksajhssssggg11s
        print("Changes committed and pushed successfully.")
        return True


if __name__ == "__main__":
    print("Starting...")
    gc = GitController()
    gc.commit_and_push()
    # print(gc.get_repos())
