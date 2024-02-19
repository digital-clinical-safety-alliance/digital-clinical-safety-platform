import unittest
from app.functions.general_functions import valid_partial_linux_path


class GeneralFunctionsTest(unittest.TestCase):
    def test_empty(self):
        path = ""
        valid, failure_reasons = valid_partial_linux_path(path)
        self.assertFalse(valid)
        self.assertEqual(failure_reasons, ["empty string"])

    def test_valid(self):
        path = "home/user/file.md"
        valid, failure_reasons = valid_partial_linux_path(path)
        self.assertTrue(valid)
        self.assertEqual(failure_reasons, [])

    def test_backslash(self):
        path = "home/user\\file.md"
        valid, failure_reasons = valid_partial_linux_path(path)
        self.assertFalse(valid)
        self.assertEqual(failure_reasons, ["included backslash (eg '\\')"])

    def test_two_forwardslashes(self):
        path = "home/user//file.md"
        valid, failure_reasons = valid_partial_linux_path(path)
        self.assertFalse(valid)
        self.assertEqual(
            failure_reasons, ["2 or more forwards slashes in a row (eg'//')"]
        )

    def test_wrong_extension(self):
        path = "home/user/file.py"
        valid, failure_reasons = valid_partial_linux_path(path, "txt")
        self.assertFalse(valid)
        self.assertEqual(failure_reasons, ["did not end in '.txt'"])

    def test_starts_with_fullstop(self):
        path = "./home/user/file.md"
        valid, failure_reasons = valid_partial_linux_path(path)
        self.assertFalse(valid)
        self.assertEqual(failure_reasons, ["started with a fullstop (eg '.')"])

    def test_start_with_forwardslash(self):
        path = "/home/user/file.md"
        valid, failure_reasons = valid_partial_linux_path(path)
        self.assertFalse(valid)
        self.assertEqual(
            failure_reasons, ["started with forward slash (eg '/')"]
        )
