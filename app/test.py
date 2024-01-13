from git import Repo
from pathlib import Path

project_directory: str = "/projects/project_46"
repo = Repo.clone_from(
    "https://github.com/digital-clinical-safety-alliance/dcsp-test-bmi.git",
    project_directory,
)

p = Path(project_directory)
subdirectories = [x for x in p.iterdir() if x.is_dir()]
print(subdirectories)
