""" Something

"""

import os
from pathlib import Path
from jinja2 import Environment, meta
from fnmatch import fnmatch
import re


class Builder:
    """ """

    def __init__(
        self,
        template_dir: str | None = "/templates/",
        output_dir: str | None = "/hazard_logs",
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

        return templates

    def get_template_placeholders(self, template):
        """ """
        placeholders: list = []
        search_location: str = f"/templates/{ template }/"
        files_to_check: list = []

        placeholders_sub: list = []
        placeholders_raw: list = []
        placeholders_clean: list = []

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

        for p in placeholders_raw:
            p = p.replace("{{", "")
            p = p.replace("}}", "")
            p = p.strip()
            placeholders_clean.append(p)
            print(p)

        return


if __name__ == "__main__":
    doc_build = Builder()
    print(doc_build.get_templates())
    doc_build.get_template_placeholders("DCB0129")
