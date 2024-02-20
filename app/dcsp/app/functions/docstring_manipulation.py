"""Extracts docstrings from Python files

class:
    DocstringManipulation: Extracts docstrings from Python files.
"""

import ast
import re
from pathlib import Path
from typing import Any, Tuple, Optional, TextIO, Generator

import app.functions.constants as c


class DocstringManipulation:
    """Extracts docstrings from Python files

    Extracts docstrings from Python files.

    functions:
        docstring_all: Matches hazards in markdown files with code files.
        extract_docstrings: Extracts docstrings from Python files.
        extract_hazards: Extracts hazards from Python files.
    """

    def __init__(self, project_id: int) -> None:
        self.project_id: int = project_id
        return

    def docstring_all(self) -> list[dict[str, Any]]:
        """Matches hazards in markdown files with code files

        Searches for hazards in markdown files and matches them with the python
        files.

        Args:
            project_id (int): The project id.

        Returns:
            list[dict[str, Any]]: A list of dictionaries containing the file
                                  path, function name, code path and hazards.
        """
        docs_folder: str = (
            f"{ c.PROJECTS_FOLDER }project_{ self.project_id }"
            f"/{ c.CLINICAL_SAFETY_FOLDER }docs/"
        )
        markdown_files: Optional[Generator[Path, None, None]] = None
        project_folder: str = (
            f"{ c.PROJECTS_FOLDER }project_{ self.project_id }/"
        )
        function_paths: list[Any] = []
        file_path: Optional[Path] = None
        lines: list[str] = []
        matching_lines: list[str] = []
        hazard_docs_attributes: list[dict[str, Any]] = []
        index: int = 0
        function_info: dict[str, Any] = {}
        code_file: str = ""
        code_file_path: Path
        hazards: list[dict[str, Any]] = []

        if not Path(docs_folder).exists():
            return []

        if not Path(project_folder).exists():
            return []

        markdown_files = Path(docs_folder).rglob("*.md")

        # list used here as Path is a Generator, and cannot be called twice
        # in later code.
        function_paths = list(Path(project_folder).rglob("*.py"))

        for file_path in markdown_files:
            with open(file_path, "r") as file:
                lines = file.readlines()
                matching_lines = [
                    f"{ line.lstrip().replace(':::', '').strip() }.py"
                    for line in lines
                    if line.startswith(":::")
                ]

                if matching_lines:
                    for matching_line in matching_lines:
                        hazard_docs_attributes.append(
                            {
                                "mk_file_path": str(file_path).replace(
                                    docs_folder, ""
                                ),
                                "code_file": matching_line,
                            }
                        )

        for index, function_info in enumerate(hazard_docs_attributes):
            code_file = function_info["code_file"]
            for code_file_path in function_paths:
                if code_file_path.name == code_file:
                    hazard_docs_attributes[index]["code_file_path"] = str(
                        code_file_path
                    )
                    hazards = self.extract_hazards(str(code_file_path))
                    if hazards:
                        hazard_docs_attributes[index]["hazards"] = hazards

        hazard_docs_attributes = [
            item for item in hazard_docs_attributes if "hazards" in item
        ]

        return hazard_docs_attributes

    def extract_docstrings(self, file_path: str) -> list[Tuple[str, Any]]:
        """Extracts docstrings from Python files

        Extracts docstrings from Python files.

        Args:
            file_path (str): The file path.

        Returns:
            list[Tuple[str, Any]]: A list of tuples containing the subroutine
                                        name and docstring.
        """
        docstrings: list[Tuple[str, Any]] = []
        file: Optional[TextIO] = None
        tree: Optional[ast.AST] = None
        node: Optional[ast.AST] = None

        if not Path(file_path).exists():
            return []

        with open(file_path, "r") as file:
            file_contents = file.read()
            tree = ast.parse(file_contents, filename=file_path)

        for node in ast.walk(tree):
            if isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            ):
                if (
                    node.body
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(
                        node.body[0].value,
                        ast.Constant,
                    )
                ):
                    docstrings.append(
                        (
                            node.name,  # This is named sub_routine elsewhere
                            node.body[0].value.s,
                        )
                    )

        return docstrings

    def extract_hazards(self, file_path: str) -> list[dict[str, Any]]:
        """Extracts hazards from Python files

        Extracts hazards from Python files.

        Args:
            file_path (str): The file path.

        Returns:
            list[dict[str, Any]]: A list of dictionaries containing the module
                                  name, hazard name and hazard number.
        """
        sub_routine: str = ""
        docstring: str = ""
        docstrings: Optional[list[Tuple[str, Any]]] = None
        HAZARD_TITLE: str = "Hazards:"
        section_found: bool = False
        hazard_number: Optional[str] = None
        line: str = ""
        match: Optional[re.Match[Any]] = None
        section_content: list[dict[str, Any]] = []

        if not Path(file_path).exists():
            return []

        docstrings = self.extract_docstrings(file_path)

        for (
            sub_routine,
            docstring,
        ) in docstrings:
            if HAZARD_TITLE in docstring:
                section_found = False
                hazard_number = None

                for line in docstring.splitlines():
                    if section_found:
                        if line.strip() == "" or '"""' in line:
                            section_found = False

                        else:
                            # Look for value between parentheses
                            match = re.search(r"\(([^)]+)\)", line)
                            hazard_number = (
                                match.group(1).strip() if match else None
                            )

                            if not str(hazard_number).isdigit():
                                hazard_number = None

                            section_content.append(
                                {
                                    "sub_routine": sub_routine,
                                    "hazard_full": line.lstrip(),
                                    "hazard_number": hazard_number,
                                }
                            )
                    elif line.strip() == f"{ HAZARD_TITLE }":
                        section_found = True

        return section_content
