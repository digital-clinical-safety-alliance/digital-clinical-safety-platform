from unittest import TestCase
from unittest.mock import Mock, MagicMock, patch, call, PropertyMock
from django.test import tag

from app.functions.docstring_manipulation import DocstringManipulation
import app.functions.constants as c
import app.tests.data_docstring_manipulation as d


class DocstringAllTest(TestCase):
    @patch("app.functions.docstring_manipulation.Path")
    def test_invalid_docs_folder_path(self, mock_path):
        project_id = 1
        docs_folder = (
            f"{ c.PROJECTS_FOLDER }project_{ project_id }"
            f"/{ c.CLINICAL_SAFETY_FOLDER }docs/"
        )

        mock_path.return_value.exists.return_value = False

        doc = DocstringManipulation(project_id)
        docstring_return = doc.docstring_all()

        self.assertEqual(docstring_return, [])

        mock_path.assert_called_once_with(docs_folder)
        mock_path.return_value.exists.assert_called_once_with()

    @patch("app.functions.docstring_manipulation.Path")
    def test_invalid_project_folder_path(self, mock_path):
        project_id = 1

        mock_path.return_value.exists.side_effect = [True, False]

        doc = DocstringManipulation(project_id)
        docstring_return = doc.docstring_all()

        self.assertEqual(docstring_return, [])

        self.assertEqual(mock_path.call_count, 2)
        self.assertEqual(mock_path.return_value.exists.call_count, 2)

    @patch("app.functions.docstring_manipulation.Path")
    @patch("app.functions.docstring_manipulation.open")
    @patch(
        "app.functions.docstring_manipulation.DocstringManipulation.extract_hazards"
    )
    def test_function_and_hazard_present(
        self, mock_extract_hazards, mock_open, mock_path
    ):
        project_id = 1
        docs_folder: str = f"{ c.PROJECTS_FOLDER }project_{ project_id }/{ c.CLINICAL_SAFETY_FOLDER }docs/"

        mock_path.return_value.exists.side_effect = [True, True]

        mock_file_1 = MagicMock()
        mock_file_1.name = "function_1.py"
        mock_file_1.__str__.return_value = "/path/to/function_1.py"

        mock_file_2 = MagicMock()
        mock_file_2.name = "function_2.py"
        mock_file_2.__str__.return_value = "/path/to/function_2.py"

        mock_path.return_value.rglob.side_effect = [
            [
                f"{ docs_folder }file1.md",
                f"{ docs_folder }file2.md",
            ],
            [
                mock_file_1,
                mock_file_2,
            ],
        ]

        mock_open.return_value.__enter__().readlines.side_effect = [
            ["# Title 1", "## Subtitle 1", "Some text 1", ":::function_1"],
            ["# Title 2", "## Subtitle 2", "Some text 2", ":::function_2"],
        ]

        mock_extract_hazards.side_effect = [
            [
                {
                    "sub_routine": "sub_routine_1",
                    "hazard_full": "WrongPatient (1): The wrong patient",
                    "hazard_number": "1",
                },
            ],
            [
                {
                    "sub_routine": "sub_routine_2",
                    "hazard_full": "WrongDemograhics (2): The wrong patient gender",
                    "hazard_number": "2",
                },
            ],
        ]

        doc = DocstringManipulation(project_id)
        docstring_return = doc.docstring_all()

        self.assertEqual(docstring_return, d.DOCSTRING_ALL_RETURN_SINGLE)

        self.assertEqual(mock_path.call_count, 4)
        self.assertEqual(mock_path.return_value.exists.call_count, 2)
        self.assertEqual(mock_path.return_value.rglob.call_count, 2)
        self.assertEqual(mock_file_1.__str__.call_count, 2)
        self.assertEqual(mock_file_2.__str__.call_count, 2)
        mock_path.return_value.rglob.calls = [call("*.md"), call("*.py")]
        self.assertEqual(
            mock_open.return_value.__enter__().readlines.call_count, 2
        )
        self.assertEqual(mock_extract_hazards.call_count, 2)

    @patch("app.functions.docstring_manipulation.Path")
    @patch("app.functions.docstring_manipulation.open")
    @patch(
        "app.functions.docstring_manipulation.DocstringManipulation.extract_hazards"
    )
    def test_two_lines_of_triple_colons(
        self, mock_extract_hazards, mock_open, mock_path
    ):
        project_id = 1
        docs_folder: str = f"{ c.PROJECTS_FOLDER }project_{ project_id }/{ c.CLINICAL_SAFETY_FOLDER }docs/"

        mock_path.return_value.exists.side_effect = [True, True]

        mock_file_1 = MagicMock()
        mock_file_1.name = "function_1.py"
        mock_file_1.__str__.return_value = "/path/to/function_1.py"

        mock_file_2 = MagicMock()
        mock_file_2.name = "function_2.py"
        mock_file_2.__str__.return_value = "/path/to/function_2.py"

        mock_file_3 = MagicMock()
        mock_file_3.name = "function_3.py"
        mock_file_3.__str__.return_value = "/path/to/function_3.py"

        mock_path.return_value.rglob.side_effect = [
            [
                f"{ docs_folder }file1.md",
                f"{ docs_folder }file2.md",
            ],
            [
                mock_file_1,
                mock_file_2,
                mock_file_3,
            ],
        ]

        mock_open.return_value.__enter__().readlines.side_effect = [
            ["# Title 1", "## Subtitle 1", "Some text 1", ":::function_1"],
            [
                "# Title 2",
                "## Subtitle 2",
                "Some text 2",
                ":::function_2",
                ":::function_3",
            ],
        ]

        mock_extract_hazards.side_effect = [
            [
                {
                    "sub_routine": "sub_routine_1",
                    "hazard_full": "WrongPatient (1): The wrong patient",
                    "hazard_number": "1",
                },
            ],
            [
                {
                    "sub_routine": "sub_routine_2",
                    "hazard_full": "WrongDemograhics (2): The wrong patient gender",
                    "hazard_number": "2",
                },
            ],
            [
                {
                    "sub_routine": "sub_routine_3",
                    "hazard_full": "WrongDemograhics (3): The wrong patient address",
                    "hazard_number": "3",
                },
            ],
        ]

        doc = DocstringManipulation(project_id)
        docstring_return = doc.docstring_all()

        self.assertEqual(docstring_return, d.DOCSTRING_ALL_RETURN_DOUBLE)

        self.assertEqual(mock_path.call_count, 4)
        self.assertEqual(mock_path.return_value.exists.call_count, 2)
        self.assertEqual(mock_path.return_value.rglob.call_count, 2)
        self.assertEqual(mock_file_1.__str__.call_count, 2)
        self.assertEqual(mock_file_2.__str__.call_count, 2)
        self.assertEqual(mock_file_3.__str__.call_count, 2)
        self.assertEqual(
            mock_open.return_value.__enter__().readlines.call_count, 2
        )
        self.assertEqual(mock_extract_hazards.call_count, 3)

    @patch("app.functions.docstring_manipulation.Path")
    @patch("app.functions.docstring_manipulation.open")
    @patch(
        "app.functions.docstring_manipulation.DocstringManipulation.extract_hazards"
    )
    def test_no_functions_in_markdown_files(
        self, mock_extract_hazards, mock_open, mock_path
    ):
        project_id = 1
        docs_folder: str = f"{ c.PROJECTS_FOLDER }project_{ project_id }/{ c.CLINICAL_SAFETY_FOLDER }docs/"

        mock_path.return_value.exists.side_effect = [True, True]

        mock_file_1 = MagicMock()
        mock_file_1.name = "function_1.py"
        mock_file_1.__str__.return_value = "/path/to/function_1.py"

        mock_file_2 = MagicMock()
        mock_file_2.name = "function_2.py"
        mock_file_2.__str__.return_value = "/path/to/function_2.py"

        mock_path.return_value.rglob.side_effect = [
            [
                f"{ docs_folder }file1.md",
                f"{ docs_folder }file2.md",
            ],
            [
                mock_file_1,
                mock_file_2,
            ],
        ]

        mock_open.return_value.__enter__().readlines.side_effect = [
            [
                "# Title 1",
                "## Subtitle 1",
                "Some text 1",
                "no functions",
            ],
            [
                "# Title 2",
                "## Subtitle 2",
                "Some text 2",
                "no functions either",
            ],
        ]

        mock_extract_hazards.side_effect = [
            [
                {
                    "sub_routine": "sub_routine_1",
                    "hazard_full": "WrongPatient (1): The wrong patient",
                    "hazard_number": "1",
                },
            ],
            [
                {
                    "sub_routine": "sub_routine_2",
                    "hazard_full": "WrongDemograhics (2): The wrong patient gender",
                    "hazard_number": "2",
                },
            ],
        ]

        doc = DocstringManipulation(project_id)
        docstring_return = doc.docstring_all()

        self.assertEqual(docstring_return, [])

        self.assertEqual(mock_path.call_count, 4)
        self.assertEqual(mock_path.return_value.exists.call_count, 2)
        self.assertEqual(mock_path.return_value.rglob.call_count, 2)
        mock_file_1.__str__.assert_not_called()
        mock_file_2.__str__.assert_not_called()
        self.assertEqual(
            mock_open.return_value.__enter__().readlines.call_count, 2
        )
        mock_extract_hazards.assert_not_called()

    @patch("app.functions.docstring_manipulation.Path")
    @patch("app.functions.docstring_manipulation.open")
    @patch(
        "app.functions.docstring_manipulation.DocstringManipulation.extract_hazards"
    )
    def test_no_hazards_in_function_files(
        self, mock_extract_hazards, mock_open, mock_path
    ):
        project_id = 1
        docs_folder: str = f"{ c.PROJECTS_FOLDER }project_{ project_id }/{ c.CLINICAL_SAFETY_FOLDER }docs/"

        mock_path.return_value.exists.side_effect = [True, True]

        mock_file_1 = MagicMock()
        mock_file_1.name = "function_1.py"
        mock_file_1.__str__.return_value = "/path/to/function_1.py"

        mock_file_2 = MagicMock()
        mock_file_2.name = "function_2.py"
        mock_file_2.__str__.return_value = "/path/to/function_2.py"

        mock_path.return_value.rglob.side_effect = [
            [
                f"{ docs_folder }file1.md",
                f"{ docs_folder }file2.md",
            ],
            [
                mock_file_1,
                mock_file_2,
            ],
        ]

        mock_open.return_value.__enter__().readlines.side_effect = [
            ["# Title 1", "## Subtitle 1", "Some text 1", ":::function_1"],
            ["# Title 2", "## Subtitle 2", "Some text 2", ":::function_2"],
        ]

        mock_extract_hazards.side_effect = [[], []]

        doc = DocstringManipulation(project_id)
        docstring_return = doc.docstring_all()

        self.assertEqual(docstring_return, [])

        self.assertEqual(mock_path.call_count, 4)
        self.assertEqual(mock_path.return_value.exists.call_count, 2)
        self.assertEqual(mock_path.return_value.rglob.call_count, 2)
        self.assertEqual(mock_file_1.__str__.call_count, 2)
        self.assertEqual(mock_file_2.__str__.call_count, 2)
        self.assertEqual(
            mock_open.return_value.__enter__().readlines.call_count, 2
        )
        self.assertEqual(mock_extract_hazards.call_count, 2)


class ExtractDocstringTest(TestCase):
    @patch("app.functions.docstring_manipulation.Path")
    def test_bad_filename(self, mock_path):
        project_id = 1
        file_name = "file.py"

        mock_path.return_value.exists.return_value = False

        doc = DocstringManipulation(project_id)
        docstring_returned = doc.extract_docstrings(file_name)

        self.assertEqual(docstring_returned, [])

        mock_path.assert_called_once_with(file_name)
        mock_path.return_value.exists.assert_called_once_with()

    @patch("app.functions.docstring_manipulation.Path")
    @patch("app.functions.docstring_manipulation.open")
    def test_valid(self, mock_open, mock_path):
        project_id = 1
        file_name = "file.py"

        mock_path.return_value.exists.return_value = True

        mock_open.return_value.__enter__().read.return_value = (
            d.PROVIDED_DOCSTRING
        )

        doc = DocstringManipulation(project_id)
        docstring_returned = doc.extract_docstrings(file_name)

        self.assertEqual(docstring_returned, d.RETURN_DOCSTRING)

        mock_path.assert_called_once_with(file_name)
        mock_path.return_value.exists.assert_called_once_with()
        mock_open.assert_called_once_with(
            file_name,
            "r",
        )

    @patch("app.functions.docstring_manipulation.Path")
    @patch("app.functions.docstring_manipulation.open")
    def test_empty_file(self, mock_open, mock_path):
        project_id = 1
        file_name = "file.py"

        mock_path.return_value.exists.return_value = True

        mock_open.return_value.__enter__().read.return_value = ""

        doc = DocstringManipulation(project_id)
        docstring_returned = doc.extract_docstrings(file_name)

        self.assertEqual(docstring_returned, [])

        mock_path.assert_called_once_with(file_name)
        mock_path.return_value.exists.assert_called_once_with()
        mock_open.assert_called_once_with(
            file_name,
            "r",
        )


class ExtractHazardsTest(TestCase):
    @patch("app.functions.docstring_manipulation.Path")
    def test_bad_file_path(self, mock_path):
        project_id = 1
        file_name = "file.py"

        mock_path.return_value.exists.return_value = False

        doc = DocstringManipulation(project_id)
        hazards = doc.extract_hazards(file_name)

        self.assertEqual(hazards, [])

        mock_path.assert_called_once_with(file_name)

    @patch("app.functions.docstring_manipulation.Path")
    @patch(
        "app.functions.docstring_manipulation.DocstringManipulation.extract_docstrings"
    )
    def test_valid(self, mock_extract_docstrings, mock_path):
        project_id = 1
        file_name = "file.py"

        mock_path.return_value.exists.return_value = True

        mock_extract_docstrings.return_value = d.RETURN_DOCSTRING

        doc = DocstringManipulation(project_id)
        hazards = doc.extract_hazards(file_name)

        self.assertEqual(hazards, d.RETURN_HAZARDS)

        mock_path.assert_called_once_with(file_name)
        mock_extract_docstrings.assert_called_once_with(file_name)

    @patch("app.functions.docstring_manipulation.Path")
    @patch(
        "app.functions.docstring_manipulation.DocstringManipulation.extract_docstrings"
    )
    def test_no_hazards(self, mock_extract_docstrings, mock_path):
        project_id = 1
        file_name = "file.py"

        mock_path.return_value.exists.return_value = True

        mock_extract_docstrings.return_value = d.RETURN_DOCSTRING_NO_HAZARDS

        doc = DocstringManipulation(project_id)
        hazards = doc.extract_hazards(file_name)

        self.assertEqual(hazards, [])

        mock_path.assert_called_once_with(file_name)
        mock_extract_docstrings.assert_called_once_with(file_name)

    @patch("app.functions.docstring_manipulation.Path")
    @patch(
        "app.functions.docstring_manipulation.DocstringManipulation.extract_docstrings"
    )
    def test_hazard_non_digit(self, mock_extract_docstrings, mock_path):
        project_id = 1
        file_name = "file.py"

        mock_path.return_value.exists.return_value = True

        mock_extract_docstrings.return_value = (
            d.DOCSTRING_NON_DIGIT_HAZARD_NUMBER
        )

        doc = DocstringManipulation(project_id)
        hazards = doc.extract_hazards(file_name)

        self.assertEqual(hazards, d.RETURN_HAZARDS_NON_DIGIT_HAZARD_NUMBER)

        mock_path.assert_called_once_with(file_name)
        mock_extract_docstrings.assert_called_once_with(file_name)
