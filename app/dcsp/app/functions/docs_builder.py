""" Something

"""

import os
from pathlib import Path
from os import PathLike
from jinja2 import Environment, meta
from fnmatch import fnmatch
import re
import yaml
import shutil

import constants as c


class Builder:
    """ """

    def __init__(self, mkdocs_dir: str | None = c.MKDOCS) -> None:
        """ """
        docs: str = f"{ mkdocs_dir }docs/"
        template_dir: str = f"{ mkdocs_dir }templates/"
        placeholders_yml_path: str = f"{ mkdocs_dir }docs/placeholders.yml"

        if not os.path.isdir(docs):
            raise FileNotFoundError(
                f"Docs folder '{ docs }' does not exist"  # type: ignore[str-bytes-safe]
            )

        if not os.path.isdir(template_dir):
            raise FileNotFoundError(
                f"Template directory '{ template_dir }' does not exist"  # type: ignore[str-bytes-safe]
            )

        if any(
            illegal in placeholders_yml_path for illegal in c.ILLEGAL_DIR_CHARS
        ):
            raise RuntimeError(
                f"'{ placeholders_yml_path }' is not a valid file name"
            )

        self.docs: str = str(docs)
        self.template_dir: str = str(template_dir)
        self.placeholders_yml_path: str = str(placeholders_yml_path)
        return None

    def get_templates(self) -> list[str]:
        """Get the different types of templates available"""
        templates: list[str] = []
        # directory

        # List of all content in a directory, filtered so only first
        # order directories are returned
        templates = [
            directory
            for directory in os.listdir(self.template_dir)
            if os.path.isdir(self.template_dir + directory)
        ]

        if not templates:
            raise FileNotFoundError(
                f'No templates folders found in "{ self.template_dir }" \
                template directory'
            )

        return sorted(templates, key=str.lower)

    def copy_templates(self, template_chosen: str) -> None:
        template_chosen_path: str = f"{ self.template_dir }{ template_chosen }"

        if not os.path.isdir(template_chosen_path):
            raise FileNotFoundError(
                f"'{ template_chosen_path }' does not exist"
            )

        shutil.copytree(
            template_chosen_path,
            self.docs,
            dirs_exist_ok=True,
        )
        return

    def empty_docs_folder(self) -> None:
        """ """
        # root, dirs, files

        for root, dirs, files in os.walk(self.docs):
            for file in files:
                os.unlink(os.path.join(root, file))
            for dir in dirs:
                shutil.rmtree(os.path.join(root, dir))
        return

    def get_placeholders(self) -> dict[str, str]:
        """ """
        files_to_check: list[str] = []

        placeholders_sub: list[str] = []
        placeholders_raw: list[str] = []
        placeholders_clean: dict[str, str] = {}
        stored_placeholders: dict[str, str] = {}
        # path, subdirs, files, name, file

        # Already checked if self.doc is valid in __init__
        for path, subdirs, files in os.walk(self.docs):
            for name in files:
                if fnmatch(name, "*.md"):
                    files_to_check.append(os.path.join(path, name))

        if len(files_to_check) == 0:
            raise FileNotFoundError(
                f"No files found in mkdocs '{ self.docs }' folder"
            )

        for file in files_to_check:
            f = open(file, "r")
            doc_Regex = re.compile(r"\{\{.*?\}\}")

            placeholders_sub = doc_Regex.findall(f.read())

            for p in placeholders_sub:
                if p not in placeholders_raw:
                    placeholders_raw.append(p)
            f.close()

        if os.path.exists(self.placeholders_yml_path):
            stored_placeholders = self.read_placeholders()

        for p in placeholders_raw:
            p = p.replace("{{", "")
            p = p.replace("}}", "")
            p = p.strip()
            if len(stored_placeholders):
                # TODO check what happens if 'p' does not exist in stored_placeholders
                try:
                    placeholders_clean[p] = stored_placeholders[p]
                except:
                    pass
            else:
                placeholders_clean[p] = ""

        return placeholders_clean

    def save_placeholders(self, placeholders: dict[str, str]) -> None:
        # TODO may need to better initialise the dict[] here
        placeholders_extra: dict = {"extra": placeholders}
        # file

        with open(self.placeholders_yml_path, "w") as file:
            yaml.dump(placeholders_extra, file)
        return

    def read_placeholders(self) -> dict:
        # TODO may need to better initialise the dict[] here
        placeholders_extra: dict = {}
        # file

        if not os.path.isfile(self.placeholders_yml_path):
            raise FileNotFoundError(
                f"'{ self.placeholders_yml_path } is not a valid path"
            )

        with open(self.placeholders_yml_path, "r") as file:
            placeholders_extra = yaml.safe_load(file)

        return placeholders_extra["extra"]


if __name__ == "__main__":
    returned_variables: dict = {}
    doc_build = Builder()
    # print(doc_build.get_templates())
    # doc_build.get_placeholders("DCB0129")
    returned_variables = doc_build.read_placeholders()
    # print(returned_variables)
    returned_variables["extra"]["author_name"] = "James Doe"
    doc_build.save_placeholders(returned_variables)
