import psutil
import time as t
import os

import app.functions.constants as c


class MkdocsControl:
    def __init__(self, cwd_sh: str = c.MKDOCS) -> None:
        self.process_name: str = "mkdocs"
        self.process_arg1: str = "serve"
        self.cwd_sh: str = cwd_sh
        return

    def is_process_running(self) -> bool:
        process: psutil.Process  # TODO can this be initialised to something?

        for process in psutil.process_iter(["pid", "name"]):
            if process.info["name"] == self.process_name:  # type: ignore[attr-defined]
                return True
        return False
        """child = pexpect.spawn("ps -aux")
        readout = str(child.read())

        if "mkdocs serve" in readout:
            return True
        else:
            return False"""

    # TODO: need to have error managment in this function
    def start(self, wait: bool = False) -> bool:
        n: int = 0

        """child = pexpect.run("mkdocs serve", cwd=self.cwd_sh)
        # print(child.read())
        output = str(child.readline())
        while "\r\n" in output:
            if "Serving on http://" in output:
                break
            output = str(child.readline())"""

        if not self.is_process_running():
            # Needed to use shell script to stop blocking and
            # the creation of zombies
            os.chdir(self.cwd_sh)
            fd = open("mkdocs_serve.sh", "w")
            fd.write("#!/bin/bash\n")
            fd.write("mkdocs serve > /dev/null 2>&1 &")
            fd.close()
            os.system("sh mkdocs_serve.sh")

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
                process.kill()
                # subprocess.Popen(["pkill", "-f", self.process_name])
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
