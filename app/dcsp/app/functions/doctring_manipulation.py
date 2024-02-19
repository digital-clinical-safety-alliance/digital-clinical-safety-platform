"""Extracts docstrings from Python files

class:
    DocstringManipulation: Extracts docstrings from Python files.
"""

import ast
import re
from pathlib import Path
from typing import Any, Tuple

import app.functions.constants as c


class DocstringManipulation:
    def __init__(self, project_id: int) -> None:
        self.project_id: int = project_id
        return

    def docstring_all(self) -> list[dict[str, Any]]:
        """ """
        docs_folder: str = (
            f"{ c.PROJECTS_FOLDER }project_{ self.project_id }/{ c.CLINICAL_SAFETY_FOLDER }docs/"
        )
        markdown_files: list[Path] = list(Path(docs_folder).rglob("*.md"))
        project_folder: str = (
            f"{ c.PROJECTS_FOLDER }project_{ self.project_id }/"
        )
        hazard_docs_attributes: list[dict[str, Any]] = []
        code_path: Path

        for file_path in markdown_files:
            # print(markdown_files)
            with open(file_path, "r") as file:
                lines = file.readlines()
                matching_lines = [
                    f"{ line.lstrip().replace(':::', '').strip() }.py"
                    for line in lines
                    if line.startswith(":::")
                ]
                if matching_lines:
                    hazard_docs_attributes.append(
                        {
                            "doc_file_path": str(file_path).replace(
                                docs_folder, ""
                            ),
                            "function_name": matching_lines[0],
                        }
                    )
                    # print(hazard_docs_attributes)

        for index, function_info in enumerate(hazard_docs_attributes):
            function_name = function_info["function_name"]

            for code_path in Path(project_folder).rglob("*.py"):
                if code_path.name == function_name and code_path.is_file():
                    hazard_docs_attributes[index]["code_path"] = str(code_path)
                    hazards = self.extract_hazard(str(code_path))

                    if hazards:
                        hazard_docs_attributes[index]["hazards"] = hazards

        hazard_docs_attributes = [
            item for item in hazard_docs_attributes if "hazards" in item
        ]

        return hazard_docs_attributes

    def extract_docstrings(self, filename: str) -> list[Tuple[str, str, Any]]:
        with open(filename, "r") as file:
            tree = ast.parse(file.read(), filename=filename)

        docstrings = []
        for node in ast.walk(tree):
            if isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            ):
                module_name = node.name

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
                            module_name,
                            node.name if hasattr(node, "name") else "",
                            node.body[0].value.s,
                        )
                    )
        return docstrings

    def extract_hazard(self, filename: str) -> list[dict[str, Any]]:
        """ """
        docstrings = self.extract_docstrings(filename)
        section_content: list[dict[str, Any]] = []

        for (
            module_name,
            name,
            docstring,
        ) in docstrings:
            if "Hazards:" in docstring:
                # print(module_name)
                """print(name)
                print(docstring)"""
                # print(docstring)

                section_found = False
                section_name = "Hazards:"
                hazard_number: str | None = None

                for line in docstring.splitlines():
                    if section_found:
                        # print(line)
                        if line.strip() == "" or '"""' in line:
                            section_found = False

                        else:
                            match = re.search(r"\(([^)]+)\)", line)
                            hazard_number = (
                                match.group(1).strip() if match else None
                            )

                            if not str(hazard_number).isdigit():
                                hazard_number = None
                            section_content.append(
                                {
                                    "module_name": module_name,
                                    "hazard_full": line.lstrip(),
                                    "hazard_number": hazard_number,
                                }
                            )
                    elif line.strip() == f"{section_name}":
                        section_found = True

        return section_content
