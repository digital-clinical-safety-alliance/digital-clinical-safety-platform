"""Testing of mkdocs_control

    NB: Not built for asynchronous testing

"""
from unittest import TestCase
import sys

import app.functions.constants as c

sys.path.append(c.FUNCTIONS_APP)
from app.functions.mkdocs_control import MkdocsControl


class MkdocsControlTest(TestCase):
    def test_init(self):
        MkdocsControl()

    def test_is_process_running_up(self):
        mkdoc_control = MkdocsControl(c.TESTING_MKDOCS_CONTROL)
        if not mkdoc_control.is_process_running():
            self.assertTrue(mkdoc_control.start(wait=True))

        self.assertTrue(mkdoc_control.is_process_running())

    def test_is_process_running_down(self):
        mkdoc_control = MkdocsControl(c.TESTING_MKDOCS_CONTROL)
        mkdoc_control.stop(wait=True)
        self.assertFalse(mkdoc_control.is_process_running())

    def test_start(self):
        mkdoc_control = MkdocsControl(c.TESTING_MKDOCS_CONTROL)
        mkdoc_control.stop(wait=True)
        mkdoc_control.start(wait=True)
        self.assertTrue(mkdoc_control.is_process_running())

    def test_stop(self):
        mkdoc_control = MkdocsControl(c.TESTING_MKDOCS_CONTROL)
        mkdoc_control.start(wait=True)
        mkdoc_control.stop(wait=True)
        self.assertFalse(mkdoc_control.is_process_running())

    @classmethod
    def tearDownClass(cls):
        pass
        mkdoc_control = MkdocsControl(c.TESTING_MKDOCS_CONTROL)
        mkdoc_control.stop(wait=True)
