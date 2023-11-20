""" Just doing some testing of testing

"""

import subprocess

# Typing checking
print("Checking functions folder...")
subprocess.call(["mypy", "/cshd/app/cshd/app/functions/"])

print("Checking view.py...")
subprocess.call(["mypy", "/cshd/app/cshd/app/views.py"])
