"""Testing of forms

    NB: Not built for asynchronous testing

"""

from django.test import TestCase


import os
from fnmatch import fnmatch
import sys


import app.functions.constants as c

sys.path.append(c.FUNCTIONS_APP)
from docs_builder import Builder

import app.tests.data_forms as d


"""Testing of forms

    NB: Not built for asynchronous testing

"""

from unittest import TestCase

import os
from fnmatch import fnmatch
import sys

import app.functions.constants as c

sys.path.append(c.FUNCTIONS_APP)
from env_manipulation import ENVManipulator

import app.tests.data_env_manipulation as d


class ENVManipulatorTest(TestCase):
    def test_init(self):
        ENVManipulator()
        pass

    def test_delete(self):
        pass

    def test_add(self):
        pass

    def test_read(sefl):
        pass
