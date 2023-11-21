""" Something

"""

import os
from pathlib import Path
from os import PathLike
from jinja2 import Environment, meta
from fnmatch import fnmatch
import re
import yaml

import app.functions.constants as c

YAML_PATH: str = f"{ c.MKDOCS_DOCS }/placeholders.yml"


class Builder:
    """ """

    def __init__(
        self,
        template_dir: str | None = "/cshd/mkdocs/templates/",
    ) -> None:
        if template_dir == None:
            raise ValueError(
                f"None received for template_dir. Check if .env is set"
            )

        if not os.path.isdir(template_dir):
            raise FileNotFoundError(
                f"Template directory '{ template_dir }' does not exist!"  # type: ignore[str-bytes-safe]
            )

        self.template_dir: str = str(template_dir)
        return None

    def read_placeholders(self) -> dict:
        # TODO may need to better initialise the dict[] here
        placeholders_extra: dict = {}
        # file

        if not os.path.isfile(YAML_PATH):
            raise FileNotFoundError(f"'{ YAML_PATH } is not a valid path")

        with open(YAML_PATH, "r") as file:
            placeholders_extra = yaml.safe_load(file)

        return placeholders_extra["extra"]

    def save_placeholders(self, placeholders: dict[str, str]) -> None:
        # TODO may need to better initialise the dict[] here
        placeholders_extra: dict = {"extra": placeholders}
        # file

        with open(YAML_PATH, "w") as file:
            yaml.dump(placeholders_extra, file)
        return

    def get_templates(self) -> list:
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
            raise RuntimeError(
                f'No templates folders found in "{ self.template_dir }" \
                template directory'
            )

        return sorted(templates, key=str.lower)

    def get_placeholders(self) -> dict[str, str]:
        """ """
        search_location: str = f"{ c.MKDOCS_DOCS }/"
        files_to_check: list[str] = []

        placeholders_sub: list[str] = []
        placeholders_raw: list[str] = []
        placeholders_clean: dict[str, str] = {}
        stored_placeholders: dict[str, str] = {}
        # path, subdirs, files, name, file

        if not os.path.isdir(search_location):
            raise FileNotFoundError(
                f"{ search_location } is not a valid directory"
            )

        for path, subdirs, files in os.walk(search_location):
            for name in files:
                if fnmatch(name, "*.md"):
                    files_to_check.append(os.path.join(path, name))

        if len(files_to_check) == 0:
            raise FileNotFoundError(
                f"No templates found in mkdocs templates folder"
            )

        for file in files_to_check:
            f = open(file, "r")
            doc_Regex = re.compile(r"\{\{.*?\}\}")

            placeholders_sub = doc_Regex.findall(f.read())

            for p in placeholders_sub:
                if p not in placeholders_raw:
                    placeholders_raw.append(p)
            f.close()

        if os.path.exists(f"{ c.MKDOCS_DOCS }/placeholders.yml"):
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


if __name__ == "__main__":
    returned_variables: dict = {}
    doc_build = Builder()
    # print(doc_build.get_templates())
    # doc_build.get_placeholders("DCB0129")
    returned_variables = doc_build.read_placeholders()
    print(returned_variables)
    returned_variables["extra"]["author_name"] = "James Doe"
    doc_build.save_placeholders(returned_variables)
