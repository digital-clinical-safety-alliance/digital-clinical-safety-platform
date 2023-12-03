"""Testing of git_control.py

    Maybe used in async mode

"""

from unittest import TestCase
import sys

import app.functions.constants as c

sys.path.append(c.FUNCTIONS_APP)
from git_control import GitController

import app.tests.data_git_control as d
