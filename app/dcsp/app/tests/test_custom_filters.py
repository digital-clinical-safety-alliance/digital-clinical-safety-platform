from unittest.mock import Mock, MagicMock

from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TestCase, tag

import app.templatetags.custom_filters as custom_filters


class HasTagTest(TestCase):
    def create_mock(self):
        mock_message = Mock()
        mock_message.tags = "tag1"
        self.mock_storage = Mock(spec=FallbackStorage)
        self.mock_storage._queued_messages = [mock_message]

    def test_no_tags(self):
        mock_message = MagicMock(spec=[])
        mock_storage = Mock(spec=FallbackStorage)
        mock_storage._queued_messages = [mock_message]
        self.assertFalse(custom_filters.has_tag(mock_storage, "tag1"))

    def test_no_tag(self):
        self.create_mock()
        self.assertFalse(custom_filters.has_tag(self.mock_storage, ""))

    def test_true(self):
        self.create_mock()
        self.assertTrue(custom_filters.has_tag(self.mock_storage, "tag1"))

    def test_false(self):
        self.create_mock()
        self.assertFalse(custom_filters.has_tag(self.mock_storage, "tag4"))

    def test_empty(self):
        mock_storage = Mock(spec=FallbackStorage)
        mock_storage._queued_messages = []
        self.assertFalse(custom_filters.has_tag(mock_storage, ""))


class StartsWithTest(TestCase):
    def test_true(self):
        self.assertTrue(custom_filters.starts_with("Hello, world!", "Hello"))

    def test_false(self):
        self.assertFalse(
            custom_filters.starts_with("Hello, world!", "Goodbye")
        )


class GetTest(TestCase):
    def test_valid(self):
        mapping = {"key1": "value1", "key2": "value2"}
        self.assertEqual(custom_filters.get(mapping, "key1"), "value1")

    def test_invalid(self):
        mapping = {"key1": "value1", "key2": "value2"}
        self.assertEqual(custom_filters.get(mapping, "key3"), "")

    def test_empty_dict(self):
        mapping = {}
        self.assertEqual(custom_filters.get(mapping, "key3"), "")


class SplitTest(TestCase):
    def test_empty(self):
        self.assertEqual(custom_filters.split("", 1), "")

    def test_wrong_separator_1(self):
        self.assertEqual(custom_filters.split("apple:banana:cherry", 1), "")

    def test_wrong_separator_0(self):
        self.assertEqual(custom_filters.split("apple:banana:cherry", 0), "")

    def test_index_is_str(self):
        self.assertEqual(
            custom_filters.split("apple|banana|cherry", "a string"), ""
        )

    def test_negative_index(self):
        self.assertEqual(custom_filters.split("apple|banana|cherry", -1), "")

    def test_high_index(self):
        self.assertEqual(custom_filters.split("apple|banana|cherry", 3), "")

    def test_only_separator(self):
        self.assertEqual(custom_filters.split("|", 0), "")

    def test_starts_with_separator(self):
        self.assertEqual(custom_filters.split("|apple|banana|cherry", 0), "")

    def test_ends_with_separator(self):
        self.assertEqual(custom_filters.split("apple|banana|cherry|", 3), "")

    def test_valid(self):
        self.assertEqual(
            custom_filters.split("apple|banana|cherry", 1), "banana"
        )


class RemoveFirstElementTest(TestCase):
    def test_empty(self):
        self.assertEqual(custom_filters.remove_first_element(""), "")

    def test_valid(self):
        self.assertEqual(
            custom_filters.remove_first_element("abcdefg"), "bcdefg"
        )


class KebabToSentenceFilterTest(TestCase):
    def test_valid(self):
        self.assertEqual(
            custom_filters.kebab_to_sentense_filter("hello-world"),
            "Hello world",
        )


class ChooseAAnTest(TestCase):
    def test_an(self):
        self.assertEqual(custom_filters.choose_a_an("apple"), "an")

    def test_a(self):
        self.assertEqual(custom_filters.choose_a_an("banana"), "a")

    def test_empty(self):
        self.assertEqual(custom_filters.choose_a_an(""), "")
