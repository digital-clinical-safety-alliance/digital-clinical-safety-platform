from unittest import TestCase

from app.functions.text_manipulation import (
    snake_to_sentense,
    kebab_to_sentense,
    list_to_string,
)


class SnakeTOSentenceTest(TestCase):
    def test_simple(self):
        snake_text = "hello_world"
        expected_title_text = "Hello world"
        self.assertEqual(snake_to_sentense(snake_text), expected_title_text)

    def test_numbers_and_specials(self):
        snake_text = "my_snake_case_text_!(£_123"
        expected_title_text = "My snake case text !(£ 123"
        self.assertEqual(snake_to_sentense(snake_text), expected_title_text)

    def test_underscore_at_start(self):
        snake_text = "_snake_case_text"
        expected_title_text = "Snake case text"
        self.assertEqual(snake_to_sentense(snake_text), expected_title_text)

    def test_underscore_at_end(self):
        snake_text = "snake_case_text_"
        expected_title_text = "Snake case text"
        self.assertEqual(snake_to_sentense(snake_text), expected_title_text)

    def test_underscore_double(self):
        snake_text = "snake__case__text"
        expected_title_text = "Snake case text"
        self.assertEqual(snake_to_sentense(snake_text), expected_title_text)

    def test_capitalised_last_word(self):
        snake_text = "snake_case_Text"
        expected_title_text = "Snake case text"
        self.assertEqual(snake_to_sentense(snake_text), expected_title_text)

    def test_empty(self):
        snake_text = ""
        expected_title_text = ""
        self.assertEqual(snake_to_sentense(snake_text), expected_title_text)


class KebabToSentenceTest(TestCase):
    def test_simple(self):
        kebab_text = "hello-world"
        expected_title_text = "Hello world"
        self.assertEqual(kebab_to_sentense(kebab_text), expected_title_text)

    def test_numbers_and_specials(self):
        kebab_text = "my-kebab-case-text-!(£-123"
        expected_title_text = "My kebab case text !(£ 123"
        self.assertEqual(kebab_to_sentense(kebab_text), expected_title_text)

    def test_hyphen_at_start(self):
        kebab_text = "-kebab-case-text"
        expected_title_text = "Kebab case text"
        self.assertEqual(kebab_to_sentense(kebab_text), expected_title_text)

    def test_hyphen_at_end(self):
        kebab_text = "kebab-case-text-"
        expected_title_text = "Kebab case text"
        self.assertEqual(kebab_to_sentense(kebab_text), expected_title_text)

    def test_hyphen_double(self):
        kebab_text = "kebab--case--text"
        expected_title_text = "Kebab case text"
        self.assertEqual(kebab_to_sentense(kebab_text), expected_title_text)

    def test_capitalised_last_word(self):
        kebab_text = "kebab-case-Text"
        expected_title_text = "Kebab case text"
        self.assertEqual(kebab_to_sentense(kebab_text), expected_title_text)

    def test_empty(self):
        kebab_text = ""
        expected_title_text = ""
        self.assertEqual(kebab_to_sentense(kebab_text), expected_title_text)


class ListToStringTest(TestCase):
    def test_empty(self):
        input_list = []
        expected_output = ""
        self.assertEqual(list_to_string(input_list), expected_output)

    def test_single_item(self):
        input_list = ["apple"]
        expected_output = "apple"
        self.assertEqual(list_to_string(input_list), expected_output)

    def test_two_items(self):
        input_list = ["apple", "banana"]
        expected_output = "apple and banana"
        self.assertEqual(list_to_string(input_list), expected_output)

    def test_multiple_items(self):
        input_list = ["apple", "banana", "cherry"]
        expected_output = "apple, banana and cherry"
        self.assertEqual(list_to_string(input_list), expected_output)
