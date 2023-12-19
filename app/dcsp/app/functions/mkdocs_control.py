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

import app.functions.constants as c


class MkdocsControl:
    def __init__(self, cwd_sh: str = c.MKDOCS) -> None:
        """Initialises the MkDocsControl class

        Args:
            cwd_sh (str): the current working directory for the shell script
        """
        self.process_name: str = "mkdocs"
        self.process_arg1: str = "serve"
        self.cwd_sh: str = cwd_sh
        return

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
