"""Overwrites files to enable "Hazard" headings

"""
from pathlib import Path
import shutil

path = "/dcsp/overwrites"
directory_path = Path("/dcsp/overwrites")

# Use the rglob() method to recursively find all files
files = directory_path.rglob("*")

# Filter out directories, keep only files
files = [file for file in files if file.is_file()]

for file in files:
    file_str = str(file)
    file_str = file_str.replace(path, "")
    print(file)
    print(file_str)
    shutil.copy2(file, file_str)
