"""Functionality to create and manipulate files for mkdocs

This module carries out all of the functionality needed to create and manipulate
markdown and yaml files for use in mkdocs, a static web site generator.

Classes:
    Builder
"""

import os
from fnmatch import fnmatch
import re
import yaml
import shutil
from typing import TextIO, Pattern


import app.functions.constants as c


class Builder:
    """Functionality to manipulate files related to Mkdocs"""

    def __init__(self, mkdocs_dir: str = c.MKDOCS) -> None:
        """Initiliases the mkdocs manipulator class

        Args:
            mkdocs_dir (str): the location of the mkdocs main folder.
        Raises:
            FileNotFoundError: if 'docs' folder not found in mkdocs main folder.
            FileNotFoundError: if 'templates' fodler not found in mkdocs main
                               folder.
            RuntimeError: if invalid characters are found in the placeholders
                        yaml path.
        """
        docs: str = ""
        template_dir: str = ""
        placeholders_yml_path: str = ""
        self.mkdocs_dir: str = ""
        self.docs: str = ""
        self.template_dir: str = ""
        self.placeholders_yml_path: str = ""

        if not os.path.isdir(str(mkdocs_dir)):
            raise FileNotFoundError(
                f"Invalid path '{ mkdocs_dir }' for mkdocs directory"  # type: ignore[str-bytes-safe]
            )

        docs = f"{ mkdocs_dir }docs/"
        template_dir = f"{ mkdocs_dir }templates/"
        placeholders_yml_path = f"{ mkdocs_dir }docs/placeholders.yml"

        if not os.path.isdir(docs):
            raise FileNotFoundError(
                f"Docs folder '{ docs }' does not exist"  # type: ignore[str-bytes-safe]
            )

        if not os.path.isdir(template_dir):
            raise FileNotFoundError(
                f"Template directory '{ template_dir }' does not exist"  # type: ignore[str-bytes-safe]
            )

        if any(
            illegal in placeholders_yml_path for illegal in c.ILLEGAL_DIR_CHARS
        ):
            raise RuntimeError(
                f"'{ placeholders_yml_path }' is not a valid file name"
            )

        self.mkdocs_dir = str(mkdocs_dir)
        self.docs = str(docs)
        self.template_dir = str(template_dir)
        self.placeholders_yml_path = str(placeholders_yml_path)
        return None

    def get_templates(self) -> list[str]:
        """Get the different types of templates available

        Looks in the template folder for subfolders, which it lists as
        "templates". Technically a template is a collection of markdown files.

        Returns:
            list[str]: a list of templates in alphabetical order.
        Raises:
            FileNotFoundError: if no template subfolder found in templates main
                               folder.
        """
        templates: list[str] = []

        # Example of 'list comprehesion'
        templates = [
            directory
            for directory in os.listdir(self.template_dir)
            if os.path.isdir(self.template_dir + directory)
        ]

        if not templates:
            raise FileNotFoundError(
                f"No templates folders found in '{ self.template_dir }' template directory"
            )

        return sorted(templates, key=str.lower)

    def copy_templates(self, template_chosen: str) -> None:
        """Copies a template to the docs folder

        Copies the chosen template in the "templates" main folder over to the
        docs folder within the mkdocs main folder.

        Args:
            template_chosen (str): the template to copy across.
        Returns:
            None
        Raises:
            FileNotFoundError: if template folder does not exist.
        """
        template_chosen_path: str = f"{ self.template_dir }{ template_chosen }"

        if not os.path.isdir(template_chosen_path):
            raise FileNotFoundError(
                f"'{ template_chosen_path }' does not exist"
            )

        shutil.copytree(
            template_chosen_path,
            self.docs,
            dirs_exist_ok=True,
        )
        return

    def empty_docs_folder(self) -> None:
        """Deletes the content of the docs folder

        Deletes all files and folders in the 'docs' folder within the main
        mkdocs folder.

        Returns:
            None
        """
        root: str = ""
        dirs: list[str] = []
        files: list[str] = []

        for root, dirs, files in os.walk(self.docs):
            for file in files:
                os.unlink(os.path.join(root, file))
            for dir in dirs:
                shutil.rmtree(os.path.join(root, dir))
        return

    def get_placeholders(self) -> dict[str, str]:
        """Returns the placeholders found in markdown files

        Searches the docs folder for markdown files and extracts all placeholders.

        Returns:
            dic[str,str]: a dictionary with the placeholder name as the key and the
                          value set to an empty string if no previously stored
                          placeholders, or updated to stored values if they are
                          available. Uses ninja2 formating, eg {{ placeholder }}.
        Raises:
            FileNotFoundError: if no files found in the docs folder.
        """
        files_to_check: list[str] = []
        placeholders_sub: list[str] = []
        placeholders_raw: list[str] = []
        placeholders_clean: dict[str, str] = {}
        stored_placeholders: dict[str, str] = {}
        path: str = ""
        files: list[str] = []
        name: str = ""
        file: str = ""
        f: TextIO
        doc_Regex: Pattern[str]
        p: str = ""

        # Already checked if self.docs is valid in __init__
        for path, _, files in os.walk(self.docs):
            for name in files:
                if fnmatch(name, "*.md"):
                    files_to_check.append(os.path.join(path, name))

        if not len(files_to_check):
            raise FileNotFoundError(
                f"No files found in mkdocs '{ self.docs }' folder"
            )

        for file in files_to_check:
            f = open(file, "r")
            doc_Regex = re.compile(r"\{\{.*?\}\}", flags=re.S)

            placeholders_sub = doc_Regex.findall(f.read())

            for p in placeholders_sub:
                if p not in placeholders_raw:
                    placeholders_raw.append(p)
            f.close()

        if os.path.exists(self.placeholders_yml_path):
            stored_placeholders = self.read_placeholders()

        for p in placeholders_raw:
            p = p.replace("{{", "")
            p = p.replace("}}", "")
            p = p.strip()
            if len(stored_placeholders):
                try:
                    placeholders_clean[p] = stored_placeholders[p]
                except:
                    pass
            else:
                placeholders_clean[p] = ""

        return placeholders_clean

    def save_placeholders(self, placeholders: dict[str, str]) -> None:
        """Saves placeholders to yaml

        Saves the placeholders, supplied as a dictionary, into a file in docs
        call docs/placeholders.yml.

        Args:
            placeholders (dict[str,str]): dictionary of placeholders. Key is name
                                          of placeholder and value is the value.
        Returns:
            None
        """
        placeholders_extra: dict = {"extra": placeholders}
        file: TextIO

        with open(self.placeholders_yml_path, "w") as file:
            yaml.dump(placeholders_extra, file)
        return

    def read_placeholders(self) -> dict[str, str]:
        """Read placeholders from yaml file

        Reads already stored placeholder values as stored in placeholders.yml.

        Returns:
            dict[str,str]: placeholder names and value pairs.
        Raises:
            FileNotFoundError: if placeholder yaml is not a valid file.
            ValueError: if error reading content of yaml file.
        """
        placeholders_extra: dict = {}
        return_dict: dict[str, str] = {}
        file: TextIO

        if not os.path.isfile(self.placeholders_yml_path):
            raise FileNotFoundError(
                f"'{ self.placeholders_yml_path }' is not a valid path"
            )

        with open(self.placeholders_yml_path, "r") as file:
            placeholders_extra = yaml.safe_load(file)

        try:
            return_dict = placeholders_extra["extra"]
        except:
            raise ValueError(
                "Error with placeholders yaml file, likely 'extra' missing from file"
            )

        return return_dict

    def linter_files(
        self, folder_file_to_examine: str
    ) -> dict[str, dict[str, str]]:
        """Check through markdown  file(s) to valid placeholder syntax

        Using regex, checks supplied markdown file, or folder of files for errors
        in the syntax of placeholders.

        Args:
            folder_file_to_examine (str): a file or a folder contain files to be
                                          linted.
        Returns:
            dict[str, dict[str, str]]: contains outcomes for the individual tests
                                       along with an overal outcome.
        Raises:
            ValueError: if an invalid file and folder string given.
        """
        full_path: str = f"{self.mkdocs_dir}{folder_file_to_examine}"
        files_to_examine: list[str] = []
        file_path: str = ""
        file_ptr: TextIO
        content: str = ""
        linter_results: dict[str, dict[str, str]] = {}
        path: str = ""
        files: list[str] = []
        file: str = ""
        name: str = ""
        doc_Regex: Pattern[str]
        left_stake_single: list = []
        right_stake_single: list = []
        left_stake_double: list = []
        right_stake_double: list = []
        properly_formatted_placeholders: list = []

        if os.path.isfile(full_path):
            files_to_examine.append(full_path)
            linter_results[full_path] = {"overal": "pass"}
        elif os.path.isdir(full_path):
            for path, _, files in os.walk(full_path):
                for name in files:
                    if fnmatch(name, "*.md"):
                        file_path = os.path.join(path, name)
                        files_to_examine.append(file_path)
                        linter_results[file_path] = {"overal": "pass"}
        else:
            raise ValueError(
                f"'{ folder_file_to_examine }' is not a valid file or folder"
            )

        for file in files_to_examine:
            file_ptr = open(file, "r")
            content = file_ptr.read()

            linter_results[file] = self.linter_sub(content)

            """# Finding number of SINGLE curley brackets
            doc_Regex = re.compile(r"\{")
            left_stake_single = doc_Regex.findall(content)
            doc_Regex = re.compile(r"\}")
            right_stake_single = doc_Regex.findall(content)

            if len(left_stake_single) == len(right_stake_single):
                linter_results[file]["equal_brackets"] = "pass"
            else:
                linter_results[file]["equal_brackets"] = "fail"
                linter_results[file]["overal"] = "fail"

            # Finding number of DOUBLE curley brackets
            doc_Regex = re.compile(r"\{\{")
            left_stake_double = doc_Regex.findall(content)
            doc_Regex = re.compile(r"\}\}")
            right_stake_double = doc_Regex.findall(content)

            if len(left_stake_double) == len(right_stake_double):
                linter_results[file]["equal_double_brackets"] = "pass"
            else:
                linter_results[file]["equal_double_brackets"] = "fail"
                linter_results[file]["overal"] = "fail"

            # Check for no placholders in front matter (metadata)
            doc_Regex = re.compile(r"---.*?---", flags=re.S)
            front_matter = doc_Regex.findall(content)
            doc_Regex = re.compile(r"\{\{.*?\}\}", flags=re.S)
            front_matter_placeholders = doc_Regex.findall(front_matter[0])

            if not len(front_matter_placeholders):
                linter_results[file]["placeholder_in_front_matter"] = "pass"
            else:
                linter_results[file]["placeholder_in_front_matter"] = "fail"
                linter_results[file]["overal"] = "fail"

            # Make sure number of {{ placeholders }} is exactly half of left or
            # right curley brackets
            doc_Regex = re.compile(r"\{\{.*?\}\}", flags=re.S)
            properly_formatted_placeholders = doc_Regex.findall(content)

            if (len(left_stake_single) == len(right_stake_single)) and len(
                left_stake_single
            ) == (len(properly_formatted_placeholders) * 2):
                linter_results[file][
                    "placeholders_half_curley_numbers"
                ] = "pass"
            else:
                linter_results[file][
                    "placeholders_half_curley_numbers"
                ] = "fail"
                linter_results[file]["overal"] = "fail" """
        return linter_results

    def linter_text(self, text: str) -> dict[str, str]:
        return self.linter_sub(text)

    def linter_sub(self, content) -> dict[str, str]:
        """ """
        front_matter_placeholders: list[str] = []
        linter_results: dict[str, str] = {"overal": "pass"}
        # Finding number of SINGLE curley brackets
        doc_Regex = re.compile(r"\{")
        left_stake_single = doc_Regex.findall(content)
        doc_Regex = re.compile(r"\}")
        right_stake_single = doc_Regex.findall(content)

        # Checking for equal numbers of left and right curley brackets
        if len(left_stake_single) == len(right_stake_single):
            linter_results["equal_brackets"] = "pass"
        else:
            linter_results["equal_brackets"] = "fail"
            linter_results["overal"] = "fail"

        # Finding number of DOUBLE curley brackets
        doc_Regex = re.compile(r"\{\{")
        left_stake_double = doc_Regex.findall(content)
        doc_Regex = re.compile(r"\}\}")
        right_stake_double = doc_Regex.findall(content)

        if len(left_stake_double) == len(right_stake_double):
            linter_results["equal_double_brackets"] = "pass"
        else:
            linter_results["equal_double_brackets"] = "fail"
            linter_results["overal"] = "fail"

        # Check for no placholders in front matter (metadata)
        doc_Regex = re.compile(r"---.*?---", flags=re.S)
        front_matter = doc_Regex.findall(content)
        doc_Regex = re.compile(r"\{\{.*?\}\}", flags=re.S)
        if len(front_matter) > 0:
            front_matter_placeholders = doc_Regex.findall(front_matter[0])

        if not len(front_matter_placeholders):
            linter_results["placeholder_in_front_matter"] = "pass"
        else:
            linter_results["placeholder_in_front_matter"] = "fail"
            linter_results["overal"] = "fail"

        # Make sure number of {{ placeholders }} is exactly half of left or
        # right curley brackets
        doc_Regex = re.compile(r"\{\{.*?\}\}", flags=re.S)
        properly_formatted_placeholders = doc_Regex.findall(content)

        if (len(left_stake_single) == len(right_stake_single)) and len(
            left_stake_single
        ) == (len(properly_formatted_placeholders) * 2):
            linter_results["placeholders_half_curley_numbers"] = "pass"
        else:
            linter_results["placeholders_half_curley_numbers"] = "fail"
            linter_results["overal"] = "fail"

        return linter_results
