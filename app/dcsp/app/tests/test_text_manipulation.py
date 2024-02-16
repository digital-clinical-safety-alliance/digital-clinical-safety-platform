import unittest
import sys

from app.functions.text_manipulation import snake_to_title
import unittest
from app.functions.text_manipulation import kebab_to_title


class SnakeTOTitleTest(unittest.TestCase):
    def test_1(self):
        snake_text = "hello_world"
        expected_title_text = "Hello world"
        self.assertEqual(snake_to_title(snake_text), expected_title_text)

    def test_numbers_and_specials(self):
        snake_text = "my_snake_case_text_!(£_123"
        expected_title_text = "My snake case text !(£ 123"
        self.assertEqual(snake_to_title(snake_text), expected_title_text)

    def test_underscore_at_start(self):
        snake_text = "_snake_case_text"
        expected_title_text = "Snake case text"
        self.assertEqual(snake_to_title(snake_text), expected_title_text)

    def test_underscore_at_end(self):
        snake_text = "snake_case_text_"
        expected_title_text = "Snake case text"
        self.assertEqual(snake_to_title(snake_text), expected_title_text)

    def test_underscore_double(self):
        snake_text = "snake__case__text"
        expected_title_text = "Snake case text"
        self.assertEqual(snake_to_title(snake_text), expected_title_text)

    def test_capitalised_last_word(self):
        snake_text = "snake_case_Text"
        expected_title_text = "Snake case text"
        self.assertEqual(snake_to_title(snake_text), expected_title_text)

    def test_empty(self):
        snake_text = ""
        expected_title_text = ""
        self.assertEqual(snake_to_title(snake_text), expected_title_text)


class KebabToTitleTest(unittest.TestCase):
    def test_kebab_to_title_simple(self):
        # Test with a simple kebab case text
        kebab_text = "hello-world"
        expected_title_text = "Hello world"
        self.assertEqual(kebab_to_title(kebab_text), expected_title_text)

    def test_kebab_to_title_numbers_and_specials(self):
        kebab_text = "my-kebab-case-text-!(£-123"
        expected_title_text = "My kebab case text !(£ 123"
        self.assertEqual(kebab_to_title(kebab_text), expected_title_text)

    def test_kebab_to_title_hyphen_at_start(self):
        kebab_text = "-kebab-case-text"
        expected_title_text = "Kebab case text"
        self.assertEqual(kebab_to_title(kebab_text), expected_title_text)

    def test_kebab_to_title_hyphen_at_end(self):
        kebab_text = "kebab-case-text-"
        expected_title_text = "Kebab case text"
        self.assertEqual(kebab_to_title(kebab_text), expected_title_text)

    def test_kebab_to_title_hyphen_double(self):
        kebab_text = "kebab--case--text"
        expected_title_text = "Kebab case text"
        self.assertEqual(kebab_to_title(kebab_text), expected_title_text)

    def test_kebab_to_title_capitalised_last_word(self):
        kebab_text = "kebab-case-Text"
        expected_title_text = "Kebab case text"
        self.assertEqual(kebab_to_title(kebab_text), expected_title_text)

    def test_kebab_to_title_empty(self):
        kebab_text = ""
        expected_title_text = ""
        self.assertEqual(kebab_to_title(kebab_text), expected_title_text)
