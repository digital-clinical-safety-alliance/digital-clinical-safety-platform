"""Starting and stopping (and test if running) of mkdocs

Starts, stops and assesses state of mkdocs serve

Classes:
    MkdocsControl: manage mkdocs server
"""

import psutil
import time as t
import os
from typing import TextIO
import subprocess  # nosec B404
from pathlib import Path
from fnmatch import fnmatch
import re
from jinja2 import Environment, FileSystemLoader

from django.template.loader import render_to_string

import app.functions.constants as c
from app.functions.projects_builder import ProjectBuilder


class MkdocsControl:
    def __init__(
        self, project_id: int | str, projects_folder: str = c.PROJECTS_FOLDER
    ) -> None:
        """Initialises the MkDocsControl class

        Args:
            cwd_sh (str): the current working directory for the shell script
        """
        self.project_id: int = 0
        self.process_name: str = "mkdocs"
        self.process_arg1: str = "serve"
        self.project_path: str = ""
        self.project_folder: str = ""

        if not isinstance(project_id, int):
            if not project_id.isdigit():
                raise ValueError(
                    f"'project_id of '{ project_id }' is not an integer"
                )

        self.project_id = int(project_id)

        if self.project_id <= 0:
            raise ValueError(
                f"'project_id of '{ project_id }' must be 1 or more"
            )

        self.project_path = f"/documentation-pages/project_{ self.project_id }"

        if not Path(self.project_path).is_dir():
            Path(self.project_path).mkdir(parents=True, exist_ok=True)

        self.documents_directory = f"{ projects_folder }project_{ project_id }/{ c.CLINICAL_SAFETY_FOLDER }"

        if not Path(projects_folder).is_dir():
            raise FileExistsError(f"'{ projects_folder }' does not exist")

        return

    def preprocessor(self) -> str:
        """Adds all hazard to the hazards-template page

        Returns:
            str: a string of outcomes from function, formatted for html
        """
        hazards_dir: str = f"{ self.documents_directory }docs/hazards/"
        hazards_hazards_dir: str = f"{ hazards_dir }hazards/"
        hazard_template_dir: str = f"{ self.documents_directory }templates/"
        files_to_check: list[str] = []
        # file
        # hazard_file
        contents_str: str = ""
        # file_name
        # hazard_name
        # hazard_number
        # hazard_name_match
        warnings: str = ""
        hazards: list[dict] = []
        project: ProjectBuilder
        new_key: str = ""
        contents_list: dict = {}
        contents_list_snake_eye: dict = {}

        if not Path(hazards_dir).is_dir():
            return (
                "<b>Failed preprocessor</b>"
                "<br><hr>"
                f"'{ hazards_dir }' directory does not exist"
                "<br><hr>"
            )

        if not Path(hazards_hazards_dir).is_dir():
            Path(hazards_hazards_dir).mkdir(parents=True, exist_ok=True)
            return (
                "<b>Preprocessor passed with INFO</b>"
                "<br><hr>"
                "INFO - '{ hazards_hazards_dir }' directory did not exist, now created"
                "<br><hr>"
            )

        for path, _, files in os.walk(hazards_hazards_dir):
            for name in files:
                if fnmatch(name, "*.md"):
                    files_to_check.append(os.path.join(path, name))

        # Sort the list of file paths based on the file numbers
        files_to_check = sorted(files_to_check, key=self.get_file_number)

        if not len(files_to_check):
            return (
                "<b>Preprocessor passed with INFO</b>"
                "<br><hr>"
                f"INFO - No hazards found in '{ hazards_hazards_dir }' folder. \
                Hazards summary page could not be created"
                "<br><hr>"
            )

        # TODO - should check there are no files with same hazard number (eg hazard-1 and hazard-01 and hazard-001)

        for file in files_to_check:
            hazard_file = open(file, "r")
            contents_str = hazard_file.read()
            file_name = Path(file).stem

            try:
                hazard_number = file_name.split("-")[1]
                if not hazard_number.isdigit():
                    hazard_number = "[Non-digit hazard number]"
                    warnings += f"WARNING - A non-digit 'number' in hazard file name '{ file_name }'"
            except:
                hazard_number = "[Number not defined]"

            project = ProjectBuilder(self.project_id)
            contents_list: dict[str, str] = project.hazard_file_read(file)

            hazards.append(
                {
                    "number": hazard_number,
                    "contents_str": contents_str,
                    "contents_list": contents_list,
                }
            )

        # Specify the path to the template file and create a Jinja environment
        env = Environment(loader=FileSystemLoader(hazard_template_dir))

        # Load the template by name
        template = env.get_template("hazard-summary.md")

        # Define the context data
        context = {"hazards": hazards}

        # Render the template with the context data
        md_content = template.render(context)

        summary_file = open(f"{ hazards_dir }{ c.HAZARDS_SUMMARY_FILE}", "w")
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

    def get_file_number(self, file_path: str) -> int | float:
        """Get the file number

        Args:
             file_path (str): the string of the file to get a value from

        Returns:
            int | float: int returned of number, otherwise a very large float is
                         returned. # TODO #49 - may change this!
        """
        try:
            return int(
                file_path.split("-")[-1].split(
                    c.MKDOCS_TEMPLATE_NUMBER_DELIMITER
                )[0]
            )
        except (ValueError, IndexError):
            return float(
                "inf"
            )  # Return a large number if no valid file number is found

    def build(self) -> str:
        """ """
        command: list[str] = []
        command_output_dir: str = (
            f"/documentation-pages/project_{ self.project_id }"
        )
        command_output: str = "error"  # default
        command_output_html: str = ""
        stdout_result: str = ""
        stderr_result: str = ""

        if not Path(command_output_dir).is_dir():
            raise FileExistsError(
                f"'{ command_output_dir }' directory does not exist"
            )

        command = ["/usr/local/bin/mkdocs", "build", "-d", command_output_dir]

        command_output = subprocess.run(
            command,
            shell=False,
            check=False,
            cwd=self.documents_directory,
            capture_output=True,
            text=True,
        )

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

        # print(command_output.stderr.encode("utf-8"))

        # print(command_output)

        return command_output_html

    def is_process_running(self) -> bool:
        """Checks if there is an instance of an mkdocs serve running

        Returns:
            bool: True is running, False if not running
        """
        process: psutil.Process  # TODO can this be initialised to something?

        for process in psutil.process_iter(["pid", "name"]):
            if process.info["name"] == self.process_name:  # type: ignore[attr-defined]
                return True
        return False

    # TODO: need to have error managment in this function
    def start(self, wait: bool = False) -> bool:
        """Tests if an instance of mkdocs serve is running

        Args:
            wait (bool): set to True to wait for the mkdocs instance to start before
                  exiting the method.

        Returns:
            bool: when wait = True, if mkdocs does not start up in alloated
                  time, False is returned.
        """
        n: int = 0
        file: TextIO

        if not self.is_process_running():
            # Needed to use shell script to stop blocking and the creation of
            # zombies
            os.chdir(self.cwd_sh)
            file = open("mkdocs_serve.sh", "w")
            file.write("#!/bin/bash\n")
            file.write("mkdocs serve > /dev/null 2>&1 &")
            file.close()
            subprocess.Popen(
                ["/usr/bin/sh", f"{ self.cwd_sh }mkdocs_serve.sh"], shell=False
            )  # nosec B603

            if wait:
                while not self.is_process_running():
                    t.sleep(c.TIME_INTERVAL)
                    n += 1
                    if n > c.MAX_WAIT:
                        return False
        return True

    def stop(self, wait: bool = False) -> bool:
        """Stops all instances of mkdocs serve that are running

        Args:
            wait (bool): set to True to wait for the mkdocs instance to stop before
                  exiting the method.

        Returns:
            bool: when wait = True, if mkdocs does not stop in alloated
                  time, False is returned
        """
        process: psutil.Process
        n: int = 0

        for process in psutil.process_iter(["pid", "name"]):
            if process.info["name"] == self.process_name:  # type: ignore[attr-defined]
                process.kill()
                # subprocess.Popen(["pkill", "-f", self.process_name])
                if wait:
                    while self.is_process_running():
                        t.sleep(c.TIME_INTERVAL)
                        n += 1
                        if n > c.MAX_WAIT:
                            return False
        return True
