import psutil
import subprocess
import time as t
import sys

import app.functions.constants as c


class MkdocsControl:
    def __init__(self) -> None:
        self.process_name: str = "mkdocs"
        self.process_arg1: str = "serve"
        self.cwd: str = "/cshd/app/cshd/app/functions"
        return

    def is_process_running(self) -> bool:
        process: psutil.Process  # TODO can this be initialised to something?

        for process in psutil.process_iter(["pid", "name"]):
            if process.info["name"] == self.process_name:  # type: ignore[attr-defined]
                return True
        return False

    # TODO: need to have error managment in this function
    def start(self, wait: bool = False) -> bool:
        n: int = 0

        if not self.is_process_running():
            subprocess.Popen(["sh", "mkdoc_start.sh"], cwd=self.cwd)
            if wait:
                while not self.is_process_running():
                    t.sleep(c.TIME_INTERVAL)
                    n += 1
                    if n > c.MAX_WAIT:
                        return False
        return True

    def stop(self, wait: bool = False) -> bool:
        process: psutil.Process
        n: int = 0

        for process in psutil.process_iter(["pid", "name"]):
            if process.info["name"] == self.process_name:  # type: ignore[attr-defined]
                subprocess.Popen(["pkill", "-f", self.process_name])
                if wait:
                    while self.is_process_running():
                        t.sleep(c.TIME_INTERVAL)
                        n += 1
                        if n > c.MAX_WAIT:
                            return False
        return True


if __name__ == "__main__":
    mc = MkdocsControl()
    mc.stop()
    # mc.start()
