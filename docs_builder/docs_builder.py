""" Something

"""

import os
from pathlib import Path
from jinja2 import Environment, meta
from fnmatch import fnmatch
import re
import yaml


MKDOCS_DOCS = "/mkdocs/docs"


class Builder:
    """ """

    def __init__(
        self,
        template_dir: str | None = "/mkdocs/templates/",
        output_dir: str | None = "/mkdocs/hazard_logs",
    ) -> None:
        if template_dir == None:
            raise ValueError(
                f"None received for template_dir. Check if .env is set"
            )

        if not os.path.isdir(template_dir):
            raise ValueError(
                f'Template directory "{ template_dir }" does not exist!'
            )

        if output_dir == None:
            raise ValueError(
                f"None received for output_dir. Check if .env is set"
            )

        # No need to check if output_dir exists, as it will be created
        # in self.create()
        # TODO: check if true

        self.template_dir: str = str(template_dir)
        self.output_dir: str = str(output_dir)
        return None

    def read_placeholders(self) -> dict:
        placeholders_extra: dict = {}

        # TODO need to check if file exists
        with open(f"{ MKDOCS_DOCS }/placeholders.yml", "r") as file:
            placeholders_extra = yaml.safe_load(file)

        return placeholders_extra["extra"]

    def save_placeholders(self, placeholders: dict) -> None:
        placeholders_extra: dict = {"extra": placeholders}

        with open(f"{ MKDOCS_DOCS }/placeholders.yml", "w") as file:
            yaml.dump(placeholders_extra, file)
        return

    def get_template_types(self):
        """ """
        return

    def get_templates(self) -> list:
        """Get the different types of templates available"""
        templates: list[str] = []

        # List of all content in a directory, filtered so only directories
        # are returned
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

    def get_placeholders(self) -> dir:
        """ """
        placeholders: list = []
        search_location: str = f"{ MKDOCS_DOCS }/"
        files_to_check: list = []

        placeholders_sub: list = []
        placeholders_raw: list = []
        placeholders_clean: dict = {}
        stored_placeholders: dict = {}

        if os.path.isdir(search_location):
            for path, subdirs, files in os.walk(search_location):
                for name in files:
                    if fnmatch(name, "*.md"):
                        files_to_check.append(os.path.join(path, name))

        # print(files_to_check)

        for file in files_to_check:
            f = open(file, "r")
            doc_Regex = re.compile(r"\{\{.*?\}\}")

            placeholders_sub = doc_Regex.findall(f.read())

            for p in placeholders_sub:
                if p not in placeholders_raw:
                    placeholders_raw.append(p)

            """ templ_str = f.read()
            env = Environment()
            ast = env.parse(templ_str)
            print(meta.find_undeclared_variables(ast))"""
            f.close()

        if os.path.exists(f"{ MKDOCS_DOCS }/placeholders.yml"):
            stored_placeholders = self.read_placeholders()

        for p in placeholders_raw:
            p = p.replace("{{", "")
            p = p.replace("}}", "")
            p = p.strip()
            if len(stored_placeholders):
                # TODO check what happens if 'p' does not exist in stored_placeholders
                placeholders_clean[p] = stored_placeholders[p]
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
    doc_build.save_variables(returned_variables)
