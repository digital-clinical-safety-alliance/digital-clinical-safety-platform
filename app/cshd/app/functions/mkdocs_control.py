import psutil
import subprocess
import time


class MkdocsControl:
    def __init__(self):
        self.process_name = "mkdocs"
        self.process_arg1 = "serve"
        self.cwd = "/cshd/mkdocs/"
        return

    def is_process_running(self):
        """Check if a process with the given name is running."""
        for process in psutil.process_iter(["pid", "name"]):
            if process.info["name"] == self.process_name:
                return True
        return False

    # TODO: need to have error managment in this function
    def start(self):
        if self.is_process_running():
            print(f"Already running")
        else:
            print(f"Starting...")
            subprocess.Popen(
                [self.process_name, self.process_arg1], cwd=self.cwd
            )

    def stop(self):
        for process in psutil.process_iter(["pid", "name"]):
            if process.info["name"] == self.process_name:
                print("Stopping...")
                subprocess.Popen(["pkill", "-f", self.process_name])
                return True
        print("Not running")
        return False


if __name__ == "__main__":
    mc = MkdocsControl()
    mc.stop()
    # mc.start()
