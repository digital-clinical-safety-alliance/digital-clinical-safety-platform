from github import Github

g = Github("xyAAAXcXACZYBx2YybC1zAzCxAYxc1Cxyz2AByb2")

repo = g.get_repo("sandbox/gh_api")

with open("dataset.csv", "r") as file:
    data = file.read()

repo.create_file("data/dataset.csv", "upload csv", data, branch="main")
