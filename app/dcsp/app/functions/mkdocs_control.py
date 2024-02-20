"""Starting and stopping (and test if running) of mkdocs

Starts, stops and assesses state of mkdocs serve

Classes:
    MkdocsControl: manage mkdocs server
"""

import time as t
import os
from typing import Any
from subprocess import CompletedProcess  # nosec B404
import subprocess  # nosec B404
from pathlib import Path
from fnmatch import fnmatch
import re
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

from django.template.loader import (
    render_to_string,
)
from django.utils import timezone

from app.models import Project

import app.functions.constants as c
from app.functions.projects_builder import (
    ProjectBuilder,
)
from app.functions.docstring_manipulation import (
    DocstringManipulation,
)


class MkdocsControl:
    def __init__(
        self,
        project_id: int | str,
        projects_folder: str = c.PROJECTS_FOLDER,
    ) -> None:
        """Initialises the MkDocsControl class

        Args:
            cwd_sh (str): the current working directory for the shell script
        """
        self.project_id: int = 0
        self.process_name: str = "mkdocs"
        self.process_arg1: str = "serve"
        self.documentation_pages: str = ""
        self.project_folder: str = ""

        if not isinstance(project_id, int):
            if not project_id.isdigit():
                raise ValueError(
                    f"'project_id of '{ project_id }' is not an integer"
                )

        self.project_id = int(project_id)

        # TODO should check in model if project ID exists
        if self.project_id <= 0:
            raise ValueError(
                f"'project_id of '{ project_id }' must be 1 or more"
            )

        self.documentation_pages = (
            f"{ c.DOCUMENTATION_PAGES }/project_{ self.project_id }"
        )

        if not Path(self.documentation_pages).is_dir():
            Path(self.documentation_pages).mkdir(parents=True, exist_ok=True)

        self.project_folder = f"{ projects_folder }project_{ project_id }/"

        self.documents_directory = (
            f"{ self.project_folder }{ c.CLINICAL_SAFETY_FOLDER }"
        )

        # TODO #56 - was this meant to check projects_folder or project_folder (not the s)
        if not Path(projects_folder).is_dir():
            raise FileExistsError(f"'{ projects_folder }' does not exist")

        return

    def preprocessor(self, entry_type: str = "hazard") -> str:
        """Adds all entry to the entries-summary page

        Returns:
            str: a string of outcomes from function, formatted for html
        """
        entries_dir: str = f"{ self.documents_directory }docs/{ entry_type }s/"
        entries_entries_dir: str = f"{ entries_dir }{ entry_type }s/"
        entry_template_dir: str = f"{ self.documents_directory }templates/"
        files_to_check: list[str] = []
        docstring: DocstringManipulation
        # file
        # entry_file
        contents_str: str = ""
        # file_name
        # entry_name
        # entry_number
        # entry_name_match
        warnings: str = ""
        entries: list[dict[str, Any]] = []
        project: ProjectBuilder
        contents_list: list[dict[str, Any]] = []
        entry_form: dict[str, Any]
        icon_html: str = ""
        code_html: str = ""
        referenced_hazards: list[dict[str, Any]] = []
        function_hazards: list[str] = []

        if not Path(entries_dir).is_dir():
            return (
                "<b>Failed preprocessor</b>"
                "<br><hr>"
                f"'{ entries_dir }' directory does not exist"
                "<br><hr>"
            )

        if not Path(entries_entries_dir).is_dir():
            Path(entries_entries_dir).mkdir(parents=True, exist_ok=True)
            return (
                "<b>Preprocessor passed with INFO</b>"
                "<br><hr>"
                f"INFO - '{ entries_entries_dir }' directory did not exist, now created"
                "<br><hr>"
            )

        for path, _, files in os.walk(entries_entries_dir):
            for name in files:
                if fnmatch(name, "*.md"):
                    files_to_check.append(os.path.join(path, name))

        # Sort the list of file paths based on the file numbers
        files_to_check = sorted(files_to_check, reverse=True)

        if not len(files_to_check):
            return (
                "<b>Preprocessor passed with INFO</b>"
                "<br><hr>"
                f"INFO - No entries found in '{ entries_entries_dir }' folder."
                "Entries summary page could not be created"
                "<br><hr>"
            )

        # TODO - should check there are no files with same entry number (eg hazard-1 and hazard-01 and hazard-001)

        docstring = DocstringManipulation(self.project_id)
        referenced_hazards = docstring.docstring_all()

        for file in files_to_check:
            icon_html = ""
            function_hazards = []

            entry_file = open(file, "r")
            contents_str = entry_file.read()
            file_name = Path(file).stem

            try:
                entry_number = file_name.split("-")[1]
                if not entry_number.isdigit():
                    entry_number = "[Non-digit entry number]"
                    warnings += f"WARNING - A non-digit 'number' in entry file name '{ file_name }'"
            except:
                entry_number = "[Number not defined]"

            for function_info in referenced_hazards:
                for hazard in function_info["hazards"]:
                    if hazard["hazard_number"] == entry_number:
                        function_hazards.append(function_info["mk_file_path"])

                        # print(entry_number)
                        # print(function_hazards)

            project = ProjectBuilder(self.project_id)
            # TODO - need to figure out which entry_types are preprocessed
            contents_list = project.entry_read_with_field_types("hazard", file)

            for field in contents_list:
                if field["field_type"] == "icon":
                    env = Environment(
                        loader=FileSystemLoader(entry_template_dir),
                        autoescape=True,
                    )
                    template = env.get_template(f"{ entry_type }-icons.md")
                    context = {"contents_list": contents_list}
                    icon_html = template.render(context)
                    icon_html = f"{ icon_html }\n<!-- [iconend] -->"

                elif field["field_type"] == "code":
                    code_html = ""

                    for function in referenced_hazards:
                        for hazard in function["hazards"]:
                            if hazard["hazard_number"] == entry_number:
                                code_html += (
                                    f"[{ function['code_file'].replace('.py', '') }"
                                    f".{ hazard['sub_routine']}](../../{ function['mk_file_path'] }"
                                    f"#{ hazard['sub_routine']}_hazard)\n\n"
                                )

                    code_html = code_html.rstrip("\n\n")

                    if not code_html:
                        code_html = "Hazard not mentioned in source code"

            entry_form = project.entry_file_read_to_form(
                contents_list,
                icon_html,
                code_html,
            )

            project.entry_update(
                entry_form,
                entry_type,
                entry_number,
            )
            pattern = re.compile(
                r"<!--\s*\[icon\]\s*-->.*?<!--\s*\[iconend\]\s*-->",
                re.DOTALL,
            )
            contents_str = re.sub(pattern, "", contents_str)
            contents_str = contents_str.replace("../../", "../")
            icon_html = icon_html.replace("../../", "../")
            icon_html = icon_html.replace(
                'class="icon-large"',
                'class="icon-small"',
            )

            entries.append(
                {
                    "number": entry_number,
                    "contents_str": contents_str,
                    "contents_list": contents_list,
                    "icon_html": icon_html,
                }
            )

        # Creating the summary
        env = Environment(
            loader=FileSystemLoader(entry_template_dir), autoescape=True
        )
        template = env.get_template(
            f"{ entry_type }{ c.ENTRY_SUMMARY_SUFFIX }"
        )
        context = {"entries": entries}
        md_content = template.render(context)
        summary_file = open(
            f"{ entries_dir }{ entry_type }{ c.ENTRY_SUMMARY_SUFFIX }",
            "w",
        )
        summary_file.write(md_content)
        summary_file.close()

        if warnings:
            return (
                "<b>Successful preprocessor step with WARNINGS</b>"
                "<br><hr>"
                f"{ warnings }"
                "<br><hr>"
            )
        else:
            return "<b>Successful preprocessor step</b>" "<br><hr>"

    def build(self) -> str:
        """ """
        command: list[str] = []
        command_output_dir: str = (
            f"{ c.DOCUMENTATION_PAGES }/project_{ self.project_id }"
        )
        command_output: CompletedProcess[str]
        command_output_html: str = ""
        stdout_result: str = ""
        stderr_result: str = ""

        if not Path(command_output_dir).is_dir():
            raise FileExistsError(
                f"'{ command_output_dir }' directory does not exist"
            )

        command = [
            "/usr/local/bin/mkdocs",
            "build",
            "-d",
            command_output_dir,
        ]

        command_output = subprocess.run(
            command,
            shell=False,
            check=False,
            cwd=self.documents_directory,
            capture_output=True,
            text=True,
        )  # nosec B603

        if command_output.returncode == 0:
            command_output_html += "<b>Successful mkdocs build</b>"
        else:
            command_output_html += "<b>Mkdocs build errors!</b>"

        command_output_html += "<br><hr>"

        stdout_result = command_output.stdout.replace("\n", "<br>")
        command_output_html += f"<b>Stdout:</b> { stdout_result }"

        command_output_html += "<br><hr>"

        stderr_result = command_output.stderr.replace("\n", "<br>")
        command_output_html += f"<b>Stderr:</b> { stderr_result }"

        return command_output_html

    def build_documents(self, force: bool = False) -> str:
        """Build the documents static pages

        Builds the documents static pages if any documents have been modified since
        last build.

        Args:
            project_id (str): the primary key for the project
        """
        project: Project
        time_now = timezone.now()
        build_output: str = ""
        last_build: datetime
        last_modified: datetime
        preprocessor_output: str = ""

        project = project = Project.objects.get(id=self.project_id)
        last_build = project.last_built
        last_modified = project.last_modified

        if (
            isinstance(last_modified, datetime)
            and isinstance(last_build, datetime)
            and not force
        ):
            if last_modified < last_build:
                return ""

        preprocessor_output = self.preprocessor()
        if preprocessor_output == "":
            return "Preprocessor error!"

        build_output = self.build()
        if build_output == "":
            return "mkdocs build error!"

        build_output = f"{ preprocessor_output } {build_output}"

        project.last_built = time_now
        project.build_output = build_output
        project.save()

        return build_output
