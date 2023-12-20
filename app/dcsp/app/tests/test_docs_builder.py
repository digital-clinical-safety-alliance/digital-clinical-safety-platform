"""Testing for the mkdocs building functionality
    NB: Not built for asynchronous testing
"""

from unittest import TestCase

# from django.test import TestCase
import sys
import os
from fnmatch import fnmatch
import shutil
import yaml

import app.functions.constants as c

sys.path.append(c.FUNCTIONS_APP)
from app.functions.docs_builder import Builder

import app.tests.data_docs_builder as d


class BuilderTestDocsEmpty(TestCase):
    def test_init(self):
        # TODO: may need to improve this test
        # Basically want to check a valid object is returned
        Builder()

    def test_init_bad_mkdocs_directory(self):
        with self.assertRaises(FileNotFoundError) as error:
            Builder(d.PATH_BAD)
        self.assertEqual(
            str(error.exception),
            f"Invalid path '{ d.PATH_BAD }' for mkdocs directory",
        )

    def test_init_no_docs_folder(self):
        with self.assertRaises(FileNotFoundError) as error:
            Builder(c.TESTING_MKDOCS_NO_DOCS_FOLDER)
        self.assertEqual(
            str(error.exception),
            f"Invalid path '{ c.TESTING_MKDOCS_NO_DOCS_FOLDER }' for mkdocs directory",
        )

    def test_init_no_templates_folder(self):
        with self.assertRaises(FileNotFoundError) as error:
            Builder(c.TESTING_MKDOCS_NO_TEMPLATES_FOLDER)
        self.assertEqual(
            str(error.exception),
            f"Invalid path '{ c.TESTING_MKDOCS_NO_TEMPLATES_FOLDER }' for mkdocs directory",
        )

    def test_get_templates(self):
        doc_build = Builder(c.TESTING_MKDOCS)
        self.assertEqual(["test_templates"], doc_build.get_templates())

    def test_get_templates_empty(self):
        doc_build = Builder(c.TESTING_MKDOCS_EMPTY_FOLDERS)
        with self.assertRaises(FileNotFoundError) as error:
            doc_build.get_templates()
        self.assertEqual(
            str(error.exception),
            f"No templates folders found in '{ c.TESTING_MKDOCS_EMPTY_FOLDERS }templates/' template directory",
        )

    def test_copy_templates(self):
        files_to_check = []
        doc_build = Builder(c.TESTING_MKDOCS)
        doc_build.copy_templates("test_templates")

        for path, subdirs, files in os.walk(c.TESTING_MKDOCS_DOCS):
            for name in files:
                if fnmatch(name, "*.md"):
                    files_to_check.append(os.path.join(path, name))

        self.assertEqual(
            d.FILES_EXPECTED_ON_TEMPLATES_COPY.sort(), files_to_check.sort()
        )

        for root, dirs, files in os.walk(c.TESTING_MKDOCS_DOCS):
            for file in files:
                os.unlink(os.path.join(root, file))
            for dir in dirs:
                shutil.rmtree(os.path.join(root, dir))

    def test_empty_docs_folder(self):
        open(c.TESTING_MKDOCS_PLACEHOLDERS_YAML, "a").close()
        doc_build = Builder(c.TESTING_MKDOCS)
        doc_build.empty_docs_folder()
        self.assertFalse(os.listdir(c.TESTING_MKDOCS_DOCS))

    def test_read_placeholders_yaml_missing(self):
        doc_build = Builder(c.TESTING_MKDOCS)
        with self.assertRaises(FileNotFoundError) as error:
            doc_build.read_placeholders()
        self.assertEqual(
            str(error.exception),
            f"'{ c.TESTING_MKDOCS }docs/placeholders.yml' is not a valid path",
        )


class BuilderTestDocsPresent(TestCase):
    def setUp(self):
        doc_build = Builder(c.TESTING_MKDOCS)
        doc_build.copy_templates("test_templates")

    def test_get_placeholders(self):
        doc_build = Builder(c.TESTING_MKDOCS)
        self.assertEqual(d.PLACEHOLDERS_EXPECTED, doc_build.get_placeholders())
        doc_build.get_placeholders()

    def test_get_placeholders_file_empty(self):
        doc_build = Builder(c.TESTING_MKDOCS)
        self.assertEqual(d.PLACEHOLDERS_EXPECTED, doc_build.get_placeholders())
        open(f"{ c.TESTING_MKDOCS }docs/placeholders.yml", "w").close()
        with self.assertRaises(ValueError) as error:
            doc_build.get_placeholders()
        self.assertEqual(
            str(error.exception),
            "Error with placeholders yaml file, likely 'extra' missing from file",
        )

    def test_get_placeholders_only_one_placeholder_in_yaml(self):
        doc_build = Builder(c.TESTING_MKDOCS)
        self.assertEqual(d.PLACEHOLDERS_EXPECTED, doc_build.get_placeholders())
        f = open(f"{ c.TESTING_MKDOCS }docs/placeholders.yml", "w").close()
        doc_build.save_placeholders({"name_of_app": "The App"})
        doc_build.get_placeholders()

    def test_get_placeholders_empty_docs_folder(self):
        doc_build = Builder(c.TESTING_MKDOCS_EMPTY_FOLDERS)
        with self.assertRaises(FileNotFoundError) as error:
            doc_build.get_placeholders()
        self.assertEqual(
            str(error.exception),
            f"No files found in mkdocs '{ c.TESTING_MKDOCS_EMPTY_FOLDERS }docs/' folder",
        )

    def test_save_placeholders(self):
        doc_build = Builder(c.TESTING_MKDOCS)
        doc_build.save_placeholders(d.PLACEHOLDERS_GOOD)
        with open(c.TESTING_MKDOCS_PLACEHOLDERS_YAML, "r") as file:
            placeholders_extra = yaml.safe_load(file)

        self.assertEqual(placeholders_extra["extra"], d.PLACEHOLDERS_GOOD)

    def test_read_placeholders(self):
        doc_build = Builder(c.TESTING_MKDOCS)
        doc_build.save_placeholders(d.PLACEHOLDERS_GOOD)
        placeholders = doc_build.read_placeholders()
        self.assertEqual(placeholders, d.PLACEHOLDERS_GOOD)

    def test_linter_single_file(self):
        doc_build = Builder(c.TESTING_MKDOCS_LINTER)
        results = doc_build.linter_files("good_files/good_file1.md")
        self.assertEqual(results, d.TEST_LINTER_SINGLE_FILE)

    def test_linter_folder(self):
        doc_build = Builder(c.TESTING_MKDOCS_LINTER)
        results = doc_build.linter_files("good_files")
        self.assertEqual(results, d.TEST_LINTER_FOLDER)

    def test_linter_single_file_bad(self):
        doc_build = Builder(c.TESTING_MKDOCS_LINTER)
        results = doc_build.linter_files("bad_files/bad_file1.md")
        self.assertEqual(results, d.TEST_LINTER_SINGLE_FILE_BAD)

    def test_linter_folder_bad(self):
        doc_build = Builder(c.TESTING_MKDOCS_LINTER)
        results = doc_build.linter_files("bad_files")
        self.assertEqual(results, d.TEST_LINTER_FOLDER_BAD)

    def tearDown(self):
        doc_build = Builder(c.TESTING_MKDOCS)
        doc_build.empty_docs_folder()
        pass
