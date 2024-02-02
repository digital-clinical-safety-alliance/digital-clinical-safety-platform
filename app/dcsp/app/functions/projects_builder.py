"""Functionality to create and manipulate files for mkdocs

This module carries out all of the functionality needed to create and manipulate
markdown and yaml files for use in mkdocs, a static web site generator.

Classes:
    Builder: builds up the documents
"""

import os
from fnmatch import fnmatch
import re
import yaml
import shutil
from typing import TextIO, Pattern, Tuple, Any
from django.http import HttpRequest
from pathlib import Path
from git import Repo
from django.utils import timezone
from functools import wraps
import glob

from django.shortcuts import get_object_or_404

import app.functions.constants as c

from app.functions.env_manipulation import ENVManipulator
from app.functions.git_control import GitHubController
from app.functions.text_manipulation import kebab_to_title
from app.functions.general_fuctions import list_to_string

from ..models import (
    User,
    UserProfile,
    Project,
    ProjectGroup,
    UserProjectAttribute,
)


class ProjectBuilder:
    # TODO - will need to change the template directory to not inclue the name mkdocs
    def __init__(
        self,
        project_id: int = 0,
        template_dir: str = c.DOCUMENT_TEMPLATES,
    ) -> None:
        """ """
        self.project_id: int = 0
        self.template_dir: str = ""
        self.safety_dir: str = ""
        self.placeholders_yaml: str = ""
        self.new_build: bool = False

        if project_id == 0:
            self.new_build = True
        elif project_id < 0:
            raise ValueError(
                f"'project_id' '{ project_id }' is not a positive integer"
            )

        self.project_id = project_id
        self.template_dir: str = template_dir
        self.safety_dir = f"{ c.PROJECTS_FOLDER }project_{ self.project_id }/{ c.CLINICAL_SAFETY_FOLDER }"
        self.documents_yaml = f"{ self.safety_dir }documents.yml"
        self.docs_dir: str = f"{ self.safety_dir }docs/"
        self.placeholders_yaml = f"{ self.docs_dir }placeholders.yml"
        self.templates_dir: str = f"{ self.safety_dir }templates/"

        return

    def new_build_prohibit(func):
        """A decorator checking if a method can be used

        If used, this decorator only allows a method to be used if a project_id is specified

        functions:
            wrapper: checks if
        """

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            """Wraps around the page function.

            Args:
                request (HttpRequest):
                project_id (str): datanase primary key for project

            Returns:
                HttpResponse | func: error responses or runs func.
            """
            if self.new_build:
                raise SyntaxError(
                    "This function is not allowed for a new-build project (with no primary key)"
                )

            return func(self, *args, **kwargs)

        return wrapper

    def new_build(self, request: HttpRequest) -> Tuple[bool, str]:
        """ """
        inputs = request.session["inputs"]
        new_project: Project
        # group_id
        # project_directory
        # project_parent_folder
        # project_CS_documents
        ghc: GitHubController
        new_user_project_attribute: UserProjectAttribute

        if (
            inputs["setup_choice"] != "start_anew"
            and inputs["setup_choice"] != "import"
        ):
            return False, "'setup_choice' is incorrectly set"

        if inputs["repository_type"] == "github":
            ghc = GitHubController(
                inputs["external_repo_username_import"],
                inputs["external_repo_password_token_import"],
            )
            if "external_repo_url_import" in inputs:
                if not ghc.exists(inputs["external_repo_url_import"]):
                    return (
                        False,
                        f"The external repository '{ inputs['external_repo_url_import'] }' does not exist or is not accessible with your credentials",
                    )
        else:
            # TODO #44
            return (
                False,
                "Code for other external repositories is not yet written.",
            )

        # TODO - need to check user has 'admin' (I think) rights for git push later

        # Database record creation
        new_project = Project()
        new_project.name = inputs["project_name"]
        new_project.description = inputs["description"]
        new_project.owner = User.objects.get(id=request.user.id)

        if inputs["setup_choice"] == "import":
            new_project.external_repo_url = inputs["external_repo_url_import"]
            """new_project.external_repo_username = inputs[
                "external_repo_username_import"
            ]
            new_project.external_repo_password_token = inputs[
                "external_repo_password_token_import"
            ]"""

        new_project.save()
        new_project.member.set(User.objects.filter(id__in=inputs["members"]))
        new_project.save()

        new_user_project_attribute = UserProjectAttribute()
        new_user_project_attribute.user = User.objects.get(id=request.user.id)
        new_user_project_attribute.project = new_project

        if inputs["setup_choice"] == "import":
            new_user_project_attribute.repo_username = inputs[
                "external_repo_username_import"
            ]
            new_user_project_attribute.repo_password_token = inputs[
                "external_repo_password_token_import"
            ]

        new_user_project_attribute.save()

        for group_id in inputs["groups"]:
            group = ProjectGroup.objects.get(id=int(group_id))
            group.project_access.add(new_project)
            group.save()

        # Folder creation
        project_directory = (
            f"{ c.PROJECTS_FOLDER }/project_{ new_project.id }/"
        )

        if os.path.isdir(project_directory):
            return False, f"'{ project_directory }' already exists"

        Path(project_directory).mkdir(parents=True, exist_ok=True)

        if inputs["setup_choice"] == "import":
            repo = Repo.clone_from(
                f"{ inputs['external_repo_url_import'] }.git",
                project_directory,
            )

        project_CS_documents = (
            f"{ project_directory }{ c.CLINICAL_SAFETY_FOLDER }/"
        )

        if not os.path.isdir(project_CS_documents):
            Path(project_CS_documents).mkdir(parents=True, exist_ok=True)

        request.session["project_id"] = new_project.id

        return True, "All passed"

    def document_templates_get(self) -> list[str]:
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
            for directory in os.listdir(self.template_directory)
            if os.path.isdir(self.template_directory + directory)
        ]

        if not templates:
            raise FileNotFoundError(
                f"No templates folders found in '{ self.template_directory }' template directory"
            )

        return sorted(templates, key=str.lower)

    @new_build_prohibit
    def configuration_get(self) -> dict[str, str]:
        """ """
        configration_file: str = f"{ c.PROJECTS_FOLDER }project_{ self.project_id }/{ c.CLINICAL_SAFETY_FOLDER }setup.ini"
        config: ENVManipulator = ENVManipulator(configration_file)
        setup_step: None | str = None

        setup_step = config.read("setup_step")

        if not setup_step.isdigit():
            setup_step = "0"
            config.add("setup_step", setup_step)

        return {"setup_step": int(setup_step)}

    @new_build_prohibit
    def configuration_set(self, key: str, value: str) -> None:
        """ """
        configration_file: str = f"{ c.PROJECTS_FOLDER }project_{ self.project_id }/{ c.CLINICAL_SAFETY_FOLDER }setup.ini"
        config: ENVManipulator = ENVManipulator(configration_file)

        config.add(key, str(value))
        return

    @new_build_prohibit
    def copy_templates(self, template_chosen: str) -> None:
        """Copies a template to the clinical safety folder

        ---TODO

        Args:
            template_chosen (str): the template to copy across.

        Returns:
            None

        Raises:
            FileNotFoundError: if template folder does not exist.
        """
        template_chosen_path: str = (
            f"{ self.template_directory }{ template_chosen }"
        )

        if not os.path.isdir(template_chosen_path):
            raise FileNotFoundError(
                f"'{ template_chosen_path }' does not exist"
            )

        shutil.copytree(
            template_chosen_path,
            self.safety_dir,
            dirs_exist_ok=True,
        )
        return

    @new_build_prohibit
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
        file_ptr: TextIO
        doc_Regex: Pattern[str]
        placeholder: str = ""

        for path, _, files in os.walk(self.docs_dir):
            for name in files:
                if fnmatch(name, "*.md"):
                    files_to_check.append(os.path.join(path, name))

        if not len(files_to_check):
            raise FileNotFoundError(
                f"No files found in mkdocs '{ self.docs_dir }' folder"
            )

        for file in files_to_check:
            file_ptr = open(file, "r")
            doc_Regex = re.compile(r"\{\{.*?\}\}", flags=re.S)

            placeholders_sub = doc_Regex.findall(file_ptr.read())

            for placeholder in placeholders_sub:
                if placeholder not in placeholders_raw:
                    placeholders_raw.append(placeholder)
            file_ptr.close()

        if os.path.exists(self.placeholders_yaml):
            stored_placeholders = self.read_placeholders()

        for placeholder in placeholders_raw:
            placeholder = placeholder.replace("{{", "")
            placeholder = placeholder.replace("}}", "")
            placeholder = placeholder.strip()
            # print(f"**{ stored_placeholders }**")
            placeholders_clean[placeholder] = stored_placeholders.get(
                placeholder, ""
            )

        return placeholders_clean

    @new_build_prohibit
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

        with open(self.placeholders_yaml, "w") as file:
            yaml.dump(placeholders_extra, file)
        return

    @new_build_prohibit
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

        if not os.path.isfile(self.placeholders_yaml):
            raise FileNotFoundError(
                f"'{ self.placeholders_yaml }' is not a valid path"
            )

        with open(self.placeholders_yaml, "r") as file:
            placeholders_extra = yaml.safe_load(file)

        try:
            return_dict = placeholders_extra["extra"]
        except:
            raise ValueError(
                "Error with placeholders yaml file, likely 'extra' missing from file"
            )
        return return_dict

    @new_build_prohibit
    def available_hazard_labels(self, details: str = "full") -> list:
        """Provides a list of available hazard labels

        Reads from the labels yaml file and returns a list of valid hazard labels

        Args:
            details (str): full = all details of all hazard labels. name_only =
                           names only of all hazard labels.

        Returns:
            list: either a list[dict[str,str]] if "full" details are requested or
                  else a list[str] if names_only requested.

        Raises:
            ValueError: if details argument is not "full" or "name_only"
            FileNotFoundError: if a bad file path is given for the labels yaml.
        """
        label_yml: list[dict[str, str]]
        label_names_only: list[str] = []
        templates_location: str = f"{ c.PROJECTS_FOLDER }project_{ self.project_id }/{ c.CLINICAL_SAFETY_FOLDER }templates/"
        labels_path = f"{templates_location}{ c.HAZARD_LABELS_FILE }"

        if details != "full" and details != "name_only":
            raise ValueError(
                f"'{ details }' is not a valid option for return values of hazard labels"
            )

        if not Path(labels_path).is_file():
            print(f"'{ labels_path }' does not exists")

        """file_labels = open(labels_path, "r")
        labels = file_labels.read()
        return labels"""

        try:
            with open(labels_path, "r") as file:
                label_yml = yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Labels.yml does not exist at '{ labels_path }'"
            )

        if details == "full":
            return label_yml
        else:
            """print(label_yml)
            for label_definition in label_yml:
                label_names_only.append(label_definition["name"].lower())"""

            return [
                "fine",
                "okay",
                "hmm",
                "not so good",
                "terrible",
            ]  # label_names_only

    @new_build_prohibit
    def verify_hazard_label(self, label: str) -> bool:
        """Checks if a label name is valid

        Checking against all known valid hazard labels, checks if label name
        supplied is valid.

        Args:
            label (str): label to be examined.

        Returns:
            bool: True if a valid label, False if not.
        """
        issues_yml: list = self.available_hazard_labels("name_only")
        label_name: str = ""

        for label_name in issues_yml:
            if label.lower() in label_name.lower():
                return True

        return False

    @new_build_prohibit
    def entry_exists(self, entry_type: str, id: str) -> bool:
        """Checks if an entry of certain type exists

        Args:
            type (str): named type of entry
            id (int): the id to be assessed if an associated entry exists

        Returns:
            bool: true if the entry of certain type exists.
        """
        directory_to_check: str = f"{ c.PROJECTS_FOLDER }project_{ self.project_id }/{ c.CLINICAL_SAFETY_FOLDER }docs/{ entry_type }s/{ entry_type }s/"
        file_to_find: str = f"{ entry_type }-{ id }.md"

        if not id.isdigit():
            return False

        for path, _, files in os.walk(directory_to_check):
            for name in files:
                if fnmatch(name, file_to_find):
                    if file_to_find == name:
                        return True
        return False

    @new_build_prohibit
    def entry_file_read(
        self, non_template_path: str = ""
    ) -> list[dict[str, Any]]:
        """ """
        lines: list = []
        content_list: list[dict[str, Any]] = []
        heading: str = ""
        headed: bool = False
        horizontal_line: str = ""
        horizontal_line_numbered: str = ""
        icon_line_numbered: str = ""
        MAX_LOOP: int = 100
        templates_location: str = ""
        hazard_file_path: str = ""
        text_list: str = ""
        choices_list: list = []
        choices_dict_split: dict = {}
        potential_number: str = ""
        heading_numbered: str = ""
        code_line_numbered: str = ""

        if non_template_path == "":
            templates_location: str = f"{ c.PROJECTS_FOLDER }project_{ self.project_id }/{ c.CLINICAL_SAFETY_FOLDER }templates/"
            hazard_file_path = (
                f"{templates_location}{ c.HAZARD_TEMPLATE_FILE }"
            )
        else:
            hazard_file_path = non_template_path

        if not Path(hazard_file_path).is_file():
            raise FileExistsError(f"'{ hazard_file_path }' does not exists")

        file_template = open(hazard_file_path, "r")
        contents = file_template.read()
        lines = contents.split("\n")

        for line in lines:
            line = line.strip()

            if re.match(r"^#", line):
                headed = True

                """heading = self._heading_numbering(line, content_list)

                content_list.append(
                    {
                        "field_type": "text_area",  # This is changed later if needed
                        "heading": heading,
                        "gui_label": self._create_gui_label(heading),
                        "text": "",
                    }
                )"""

                heading = line

                if not any(d["heading"] == heading for d in content_list):
                    content_list.append(
                        {
                            "field_type": "text_area",  # This is changed later if needed
                            "heading": heading,
                            "gui_label": self._create_gui_label(heading),
                            "text": "",
                        }
                    )

                else:
                    for x in range(2, MAX_LOOP):
                        heading_numbered = f"{ line } [{ x }]"
                        if not any(
                            d["heading"] == heading_numbered
                            for d in content_list
                        ):
                            content_list.append(
                                {
                                    "field_type": "text_area",
                                    "heading": heading_numbered.strip(),
                                    "gui_label": self._create_gui_label(
                                        heading
                                    ),
                                    "text": "",
                                }
                            )
                            break
                        if x == MAX_LOOP:
                            # TODO #46 - need a soft fail state and user update
                            raise ValueError("For loop over { MAX_LOOP }!")

            elif re.match(r"^-", line):
                horizontal_line = line
                headed = False

                if not any(
                    d["heading"] == horizontal_line for d in content_list
                ):
                    content_list.append(
                        {
                            "field_type": "horizontal_line",
                            "heading": horizontal_line,
                        }
                    )
                else:
                    for x in range(2, MAX_LOOP):
                        horizontal_line_numbered = (
                            f"{ horizontal_line } [{ x }]"
                        )

                        if not any(
                            d["heading"] == horizontal_line_numbered
                            for d in content_list
                        ):
                            content_list.append(
                                {
                                    "field_type": "horizontal_line",
                                    "heading": horizontal_line_numbered,
                                }
                            )
                            break
                        if x == MAX_LOOP:
                            # TODO #46 - need a soft fail state and user update
                            raise ValueError(f"For loop over { MAX_LOOP }!")

            elif re.match(r"^<!--\s*\[\s*icon\s*\]\s*-->$", line):
                headed = False

                if not any(d["heading"] == line for d in content_list):
                    content_list.append(
                        {
                            "field_type": "icon",
                            "heading": "icon",
                        }
                    )
                else:
                    for x in range(2, MAX_LOOP):
                        icon_line_numbered = f"{ horizontal_line } [{ x }]"

                        if not any(
                            d["heading"] == icon_line_numbered
                            for d in content_list
                        ):
                            content_list.append(
                                {
                                    "field_type": "icon",
                                    "heading": icon_line_numbered,
                                }
                            )
                            break
                        if x == MAX_LOOP:
                            # TODO #46 - need a soft fail state and user update
                            raise ValueError(f"For loop over { MAX_LOOP }!")

            elif headed and line:
                if line[0] == "[":
                    pattern = r"\[([^\]]+)\]"
                    matches = re.findall(pattern, line)
                    content_list[-1]["labels"] = []
                    for argument in matches:
                        argument = argument.strip()
                        if argument == "select":
                            content_list[-1]["field_type"] = "select"
                        elif argument == "multiselect":
                            content_list[-1]["field_type"] = "multiselect"
                        elif argument == "calculate":
                            content_list[-1]["field_type"] = "calculate"
                        elif argument == "code":
                            content_list[-1]["field_type"] = "code"
                            # content_list[-1]["text"] = "<!-- [code] -->"
                        else:
                            content_list[-1]["labels"].append(argument)
                else:
                    content_list[-1]["text"] += f"{ line.strip() }\n"

        for index, element in enumerate(content_list):
            choice_name = ""
            choices_dict_split = {}

            if element["field_type"] == "select":
                choices_list = [("", "")]
            else:
                choices_list = []

            for key, value in element.items():
                if key != "labels":
                    content_list[index][key] = value.strip()

            if (
                element["field_type"] == "select"
                or element["field_type"] == "multiselect"
            ):
                text_list = element["text"].split("\n")

                for choice in text_list:
                    choice_name = choice.split(":")[0]
                    choices_list.append([choice, choice_name])
                    content_list[index]["choices"] = tuple(choices_list)

            elif element["field_type"] == "calculate":
                choices_list = element["text"].split("\n")

                for choice in choices_list:
                    choice_split = choice.split("[")
                    choices_dict_split[
                        choice_split[0]
                    ] = f"[{ choice_split[1] }"

                content_list[index]["choices"] = choices_dict_split

            if "text" in element:
                content_list[index]["number"] = []
                lines = element["text"].split("\n")

                for line in lines:
                    potential_number = line.split(
                        c.MKDOCS_TEMPLATE_NUMBER_DELIMITER
                    )[0]
                    potential_number = potential_number.strip()
                    if potential_number.isdigit():
                        content_list[index]["number"].append(potential_number)

        # print(content_list)
        return content_list

    def entry_read_with_field_types(
        self, entry_file_path: str
    ) -> list[dict[str, Any]]:
        """ """
        entry: list[dict[str, Any]] = self.entry_file_read(entry_file_path)
        template: list[dict[str, Any]] = self.entry_file_read()

        # print(template)
        # print(entry)

        for index_entry, field_entry in enumerate(entry):
            for field_template in template:
                if field_entry["heading"] == field_template["heading"]:
                    entry[index_entry]["field_type"] = field_template[
                        "field_type"
                    ]
        # print(entry)
        return entry

    def _heading_numbering(self, heading: str, content_list: list[str]) -> str:
        """ """
        heading = heading.strip()

        if not any(d["heading"] == heading for d in content_list):
            return heading

        else:
            for x in range(2, c.HEADING_MAX_LOOP):
                heading_numbered = f"{ heading } [{ x }]"
                if not any(
                    d["heading"] == heading_numbered for d in content_list
                ):
                    return heading_numbered

                if x == (c.HEADING_MAX_LOOP - 1):
                    # TODO #46 - need a soft fail state and user update
                    raise ValueError("For loop over { MAX_LOOP }!")

    def _create_gui_label(self, string: str) -> str:
        """Create user readable label

        User reable string

        Args:
            string (str): the string to change

        Returns:
            string: the user readable string in Title form
        """

        string = string.replace("#", "")
        string = string.strip()
        string = kebab_to_title(string)
        return string

    @new_build_prohibit
    def entry_update(
        self,
        form_data: dict[str, str],
        entry_type: str = "hazard",
        id: str = "new",
    ) -> dict[str, Any]:
        """ """
        TESTING_CREATION: bool = False
        hazards_directory: str = f"{ c.PROJECTS_FOLDER }project_{ self.project_id }/{ c.CLINICAL_SAFETY_FOLDER }docs/{ entry_type }s/{ entry_type }s/"
        files_to_check: list[str] = []
        entry_file: TextIO
        pattern: Pattern
        results: dict[str, Any] = []
        id_int: int = 0
        to_write: str = ""

        # print(form_data)

        if not Path(hazards_directory).is_dir():
            Path(hazards_directory).mkdir(parents=True, exist_ok=True)

        for path, _, files in os.walk(hazards_directory):
            for name in files:
                if fnmatch(name, "*.md"):
                    files_to_check.append(name)

        if id == "new":
            if TESTING_CREATION:
                id = 1
            elif files_to_check:
                numbers = (
                    [  # TODO may have to change to pattern = r"-([0-9]+)\.md"
                        int(re.search(r"\d+", file_name).group())
                        for file_name in files_to_check
                        if re.search(r"\d+", file_name)
                    ]
                )
                id_int = max(numbers) + 1

        elif id.isdigit() and self.entry_exists(entry_type, id):
            id_int = int(id)
        else:
            results = {
                "pass": False,
            }

            return results

        # Used to remove number in square brackets (eg "[2]") at end of keys
        pattern = re.compile(r"\s*\[\d+\]$")

        entry_file = open(f"{ hazards_directory }hazard-{ id_int }.md", "w")

        for key, value in form_data.items():
            to_write = re.sub(pattern, "", key)
            if to_write == "icon":
                entry_file.write("<!-- [icon] -->\n")
            else:
                entry_file.write(f"{ to_write }\n")

            if isinstance(value, list):
                for item in value:
                    entry_file.write(f"{ item }\n\n")
            else:
                entry_file.write(f"{ value }\n\n")
        """elif to_write == "code":
                entry_file.write("to_write<!-- [code] -->\n")"""
        entry_file.close()

        # TODO #54 need to get ride of the 404 in this none view.py code
        project = get_object_or_404(Project, id=self.project_id)
        project.last_modified = timezone.now()
        project.save()

        results = {
            "pass": True,
            "id": id_int,
            "name": next(iter(form_data.values())),
            "hazard_url": f"hazards/hazards/hazard-{ id_int }.html",
        }

        return results

    def entry_file_read_to_form(
        self,
        file_read: list[dict[str, Any]],
        icon_html: str = "",
        code_html: str = "",
    ) -> dict[str, Any]:
        """ """
        element: dict[str, Any] = {}
        entry_form: dict[str, Any] = {}
        key: str = ""

        for element in file_read:
            if element["field_type"] == "icon":
                # print("icon")
                # To copy across ' [number]' if present
                key = element["heading"].replace("icon", "")
                key = f"<!-- [icon] -->{ key }"
                entry_form[key] = f"{ icon_html }"

            elif element["field_type"] == "code":
                # print("code")
                entry_form[
                    element["heading"]
                ] = f"<!-- [code] -->\n{ code_html }\n<!-- [codeend] -->"

            elif element["field_type"] == "horizontal_line":
                entry_form[element["heading"]] = ""

            # TODO #55 might need to consider updating the file_read to include field_types
            # only the template gives this information at the moment
            elif "number" in element:
                entry_form[element["heading"]] = element["text"].replace(
                    "\n", "\n\n"
                )

            else:
                # print(element["heading"])
                entry_form[element["heading"]] = element["text"]

        return entry_form

    @new_build_prohibit
    def entry_template_names(self) -> list:
        """ """
        templates: list[Path] = Path(self.templates_dir).glob("*-template.md")
        templates = [file.stem for file in templates]
        templates_prefix: list[str] = []
        documents_config: dict[str] = {}

        for template in templates:
            templates_prefix.append(str(template).replace("-template", ""))

        if Path(self.documents_yaml).is_file():
            with open(self.documents_yaml, "r") as file:
                documents_config = yaml.safe_load(file)
            try:
                entried_ordered = documents_config["entries"]

            except KeyError:
                pass
            else:
                order_dict = {
                    element: index
                    for index, element in enumerate(entried_ordered)
                }
                templates_prefix = sorted(
                    templates_prefix,
                    key=lambda x: order_dict.get(x, float("inf")),
                )

        return templates_prefix

    @new_build_prohibit
    def hazards_all_get(self) -> list[str]:
        """Get all of the hazards for the project

        Returns:
            list[str]: A list of all hazards found for a project.
        """
        documents_directory = f"{ c.PROJECTS_FOLDER }project_{ self.project_id }/{ c.CLINICAL_SAFETY_FOLDER }"
        hazards_dir: str = f"{ documents_directory }docs/hazards/"
        hazards_hazards_dir: str = f"{ hazards_dir }hazards/"
        hazard_template_dir: str = f"{ documents_directory }templates/"
        hazard_file_contents: list[str] = []
        hazards_list: list = []
        hazard_with_attributes: list = []

        for path, _, files in os.walk(hazards_hazards_dir):
            for name in files:
                if fnmatch(name, "*.md"):
                    hazard_file_contents.append(os.path.join(path, name))

        hazard_file_contents = sorted(hazard_file_contents, reverse=True)

        for file in hazard_file_contents:
            pattern = r"-([0-9]+)\.md"

            matches = re.search(pattern, file)

            # print(matches.group(1))
            # TODO #50 need to handel a bad file name eg hazard-abc.md
            hazard_with_attributes = [
                {"file": file, "number": matches.group(1)}
            ]
            hazard_with_attributes.extend(self.entry_file_read(file))
            hazards_list.append(hazard_with_attributes)

            # print(hazards_list)
        return hazards_list

    @new_build_prohibit
    def form_initial(self, entry_type: str, id: int) -> dict:
        """Return data for initialising a django form

        Args:
            entry_type (str): the data/template type (eg hazard, incident, compliance
                        sign off).
            id (int): the id of the type.

        Returns:
            dict: dictionary of the fields initial values
        """
        file_path: str = ""
        data: list[dict[str, str]] = []
        data_initial: dict = {}

        file_path = f"{ c.PROJECTS_FOLDER }project_{ self.project_id }/{ c.CLINICAL_SAFETY_FOLDER }docs/{ entry_type }s/{ entry_type }s/{ entry_type }-{ id }.md"
        template = self.entry_file_read()
        data = self.entry_file_read(file_path)

        for field_data in data:
            for field_template in template:
                if field_data["heading"] == field_template["heading"]:
                    if field_template["field_type"] == "multiselect":
                        selected_options = field_data["text"].split("\n")
                        data_initial[field_data["heading"]] = selected_options

                    elif field_template["field_type"] == "code":
                        data_initial[field_data["heading"]] = "<!-- [code] -->"

                    elif (
                        field_template["field_type"] != "horizontal_line"
                        and field_template["field_type"] != "icon"
                    ):
                        data_initial[field_data["heading"]] = field_data[
                            "text"
                        ]

        return data_initial

    @new_build_prohibit
    def document_create_check(self, path: str) -> Tuple[bool, str]:
        """Checks and creates a new document

        Args:
            path (str): the path (after the /docs/ folder) of the file to be
                        created.

        Returns;
            Tuple: bool for if successful or not. String for error messsages.
        """
        docs_directory = f"{ c.PROJECTS_FOLDER }project_{ self.project_id }/{ c.CLINICAL_SAFETY_FOLDER }docs/"
        successful_creation: bool = True
        error_messages: list[str] = []

        full_path = Path(docs_directory).joinpath(Path(path))

        if full_path.is_file():
            successful_creation = False
            error_messages.append("file already exists")

        return successful_creation, error_messages

    @new_build_prohibit
    def document_create(self, path: str) -> bool:
        """Creates the document

        Args:
            path (str): the path (after the /docs/ folder) of the file to be
                        created.

        Returns;
            Tuple: bool for if successful or not. String for error messsages.
        """
        docs_directory = f"{ c.PROJECTS_FOLDER }project_{ self.project_id }/{ c.CLINICAL_SAFETY_FOLDER }docs/"

        full_path = Path(docs_directory).joinpath(Path(path))
        try:
            open(full_path, "w").close()
        except:
            return False
        else:
            return True

    @new_build_prohibit
    def documents_list(self) -> list[str]:
        """Returns documents for the project

        Returns a list of documents for the clinical safety project. An entries
        (eg, hazards, incidences) are removed from this list.

        Returns:
            list[str]: a list of documents for the project, minus any "entries".
        """
        docs_location = f"{ c.PROJECTS_FOLDER }project_{ self.project_id }/{ c.CLINICAL_SAFETY_FOLDER }docs/"
        excluded_directory: list[str] = self._entry_templates_exclude()
        exclude: bool = False
        md_files: list = []

        if not os.path.isdir(docs_location):
            raise FileNotFoundError(
                f"{ docs_location } is not a valid folder location"
            )

        for path, dir, files in os.walk(docs_location):
            for name in files:
                exclude = False
                if fnmatch(name, "*.md"):
                    file_full_name = os.path.join(path, name)
                    file_full_name = file_full_name.replace(docs_location, "")

                    for directory in excluded_directory:
                        if file_full_name.startswith(directory):
                            exclude = True

                    if not exclude:
                        md_files.append(file_full_name)

        return md_files

    @new_build_prohibit
    def _entry_templates_list(self) -> list[str]:
        """ """
        entry_templates_location = f"{ c.PROJECTS_FOLDER }project_{ self.project_id }/{ c.CLINICAL_SAFETY_FOLDER }templates/"
        templates: list[str] | Path = []

        templates = Path(entry_templates_location).rglob(
            f"*{ c.TEMPLATE_SUFFIX }"
        )

        templates = [file_path.name for file_path in templates]
        # print(templates)
        return templates

    def _entry_templates_exclude(self) -> list[str]:
        """ """
        directories_to_exclude: list[str] = []
        templates: list[str] = self._entry_templates_list()

        for template in templates:
            directories_to_exclude.append(
                template.replace(c.TEMPLATE_SUFFIX, "s/")
            )

        return directories_to_exclude


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
        self.placeholders_yaml: str = ""

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
        self.placeholders_yaml = str(placeholders_yml_path)
        return None

    def document_templates_get(self) -> list[str]:
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
        mkdocs folder. Leaves .gitkeep untouched.

        Returns:
            None
        """
        root: str = ""
        dirs: list[str] = []
        files: list[str] = []

        for root, dirs, files in os.walk(self.docs):
            for file in files:
                if not fnmatch(file, ".gitkeep"):
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

        if os.path.exists(self.placeholders_yaml):
            stored_placeholders = self.read_placeholders()

        for p in placeholders_raw:
            p = p.replace("{{", "")
            p = p.replace("}}", "")
            p = p.strip()
            # print(f"**{ stored_placeholders }**")
            placeholders_clean[p] = stored_placeholders.get(p, "")

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

        with open(self.placeholders_yaml, "w") as file:
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

        if not os.path.isfile(self.placeholders_yaml):
            raise FileNotFoundError(
                f"'{ self.placeholders_yaml }' is not a valid path"
            )

        with open(self.placeholders_yaml, "r") as file:
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
