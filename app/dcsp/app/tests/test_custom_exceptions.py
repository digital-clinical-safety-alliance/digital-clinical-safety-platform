import unittest
from app.functions.custom_exceptions import RepositoryAccessException


class TestRepositoryAccessException(unittest.TestCase):
    def test_exception_message(self):
        repo_url = "https://github.com/nonexistent/repo"
        exception = RepositoryAccessException(repo_url)
        expected_message = f"The external repository '{repo_url}' does not exist or is not accessible with your credentials"
        self.assertEqual(str(exception), expected_message)
