"""Overwrites files to enable "Hazard" headings

"""
from pathlib import Path
import shutil
from typing import Any

source_directory: str = "/dcsp/overwrites"
files: Any = Path(source_directory).rglob("*")
source_file: str = ""
destination_file: str = ""


# Filter out directories, keep only files
files = [file for file in files if file.is_file()]

for source_file in files:
    destination_file = str(source_file)
    destination_file = destination_file.replace(source_directory, "")
    print(source_file)
    print(destination_file)
    shutil.copy2(str(source_file), destination_file)
