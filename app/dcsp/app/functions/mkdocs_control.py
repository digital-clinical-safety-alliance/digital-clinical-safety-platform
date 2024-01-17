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

import app.functions.constants as c


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
        files_to_check: list[str] = []
        hazard_summary: str = (
            "---" "title: Hazards summary" "---" "# Hazards Summary"
        )
        # file
        # hazard_file
        # hazard_contents
        # file_name
        # hazard_name
        # hazard_number
        # hazard_name_match
        warnings: str = ""

        if not Path(hazards_dir).is_dir():
            return (
                "<b>Failed preprocessor</b>"
                "<br><hr>"
                f"'{ hazards_dir }' directory does not exist"
                "<br><hr>"
            )

        if not Path(hazards_hazards_dir).is_dir():
            return (
                "<b>Failed preprocessor</b>"
                "<br><hr>"
                "'{ hazards_hazards_dir }' directory does not exist"
                "<br><hr>"
            )

        for path, _, files in os.walk(hazards_hazards_dir):
            for name in files:
                if fnmatch(name, "*.md"):
                    files_to_check.append(os.path.join(path, name))

        if not len(files_to_check):
            return (
                "<b>Failed preprocessor</b>"
                "<br><hr>"
                f"No hazards found in '{ hazards_hazards_dir }' folder"
                "<br><hr>"
            )

        # TODO - should check there are no files with same hazard number (eg hazard-1 and hazard-01 and hazard-001)

        for file in files_to_check:
            hazard_file = open(file, "r")
            hazard_contents = hazard_file.read()
            file_name = Path(file).stem

            try:
                hazard_number = file_name.split("-")[1]
                if not hazard_number.isdigit():
                    hazard_number = "[Non-digit hazard number]"
                    warnings += f"WARNING - A non-digit 'number' in hazard file name '{ file_name }'"
            except:
                hazard_number = "[Number not defined]"

            hazard_name_match = re.search(
                r"### Name\n(.*?)\n", hazard_contents, re.DOTALL
            )
            if hazard_name_match:
                hazard_name = hazard_name_match.group(1)
            else:
                hazard_name = "[Name undefined]"

            hazard_summary += (
                "<details markdown='1'>"
                "<summary>Hazard { hazard_number } - { hazard_name }</summary>"
                "{ hazard_contents }"
                "</details>"
            )

        summary_file = open(f"{ hazards_dir }{ c.HAZARDS_SUMMARY_FILE}", "w")
        summary_file.write(hazard_summary)
        summary_file.close()

        if warnings:
            return (
                "<b>Successful preprocessor step</b>"
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
            command_output_html += "<b>Build errors!</b>"

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
