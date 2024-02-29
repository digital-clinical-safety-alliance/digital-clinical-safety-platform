"""Functionality to create and manipulate files for mkdocs

This module carries out all of the functionality needed to create and manipulate
markdown and yaml files for use in mkdocs, a static web site generator.

Classes:
    ProjectBuilder: a class to create and manipulate files for mkdocs
"""

import os
from fnmatch import fnmatch
import re
import yaml
import shutil
from typing import (
    TextIO,
    Pattern,
    Tuple,
    Any,
    Callable,
    Any,
    Dict,
    Generator,
    Optional,
)
from django.http import HttpRequest
from pathlib import Path
from git import Repo
from django.utils import timezone
from functools import wraps
import glob

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

import app.functions.constants as c

from app.functions.env_manipulation import ENVManipulator
from app.functions.git_control import GitHubController, GitController
from app.functions.text_manipulation import kebab_to_sentense, list_to_string
from app.functions.custom_exceptions import RepositoryAccessException
from ..models import (
    Project,
    ProjectGroup,
    UserProjectAttribute,
    project_timestamp,
)
from ..forms import PlaceholdersForm


class ProjectBuilder:
    """A class to create and manipulate files for mkdocs

    This class carries out all of the functionality needed to create and manipulate
    markdown and yaml files for use in mkdocs, a static web site generator.

    functions:
        new_build_prohibit: a decorator to stop certain methods being used for a new
                            build project.
        new_build: creates a new project and associated files.
        master_template_get: gets the different types of document templates available.
        configuration_get: gets the configuration settings for the project.
        configuration_set: sets the configuration settings for the project.
        copy_templates: copies a project template to the clinical safety folder.
        get_placeholders: gets the placeholders found in markdown files.
        save_placeholders: saves placeholders to yaml.
        save_placeholders_from_form: saves placeholders to yaml from a form.
        read_placeholders: reads placeholders from yaml file.
        entry_exists: checks if an entry of certain type exists.
        entry_file_read: reads the contents of either an entry template or entry instance.
        entry_read_with_field_types: read an instance of a entry with field typing.
        _heading_numbering: creates a numbered heading.
        _create_gui_label: creates a user readable label.
        entry_update: creates or updates entries (eg Hazards and incidents).
        entry_file_read_to_form: reads the contents of either an entry template or entry instance.
        entry_template_names: gets the names of the entry templates.
        entry_type_exists: checks if an entry type exists.
        entries_all_get: gets all of the hazards for the project.
        form_initial: returns data for initialising a django form.
        document_create_check: checks and creates a new document.
        document_create: creates a new document.
        document_list: Returns documents for the project.
        _entry_templates_list: returns a list of entry templates.
        _entry_templates_exclude: directories to exclude.
    """

    def __init__(
        self,
        project_id: int = 0,
    ) -> None:
        """Initialises the ProjectBuilder class

        Project builder initialiser

        Args:
            project_id (int): the id of the project to be worked on. A value of
                              0 means a new project is being created.

        Raises:
            TypeError: if project_id is not an integer.
            ValueError: if project_id is not a positive integer
        """
        self.new_build_flag: bool = False
        self.project_id: int = 0
        self.master_template_directory: str = ""
        self.project_directory: str = ""
        self.safety_directory: str = ""
        self.documents_yaml: str = ""
        self.docs_dir: str = ""
        self.placeholders_yaml: str = ""
        self.entries_templates_dir: str = ""

        if not isinstance(project_id, int):
            raise TypeError(f"'project_id' '{ project_id }' is not an integer")

        if project_id == 0:
            self.new_build_flag = True
        elif project_id < 0:
            raise ValueError(
                f"'project_id' '{ project_id }' is not a positive integer"
            )

        self.project_id = project_id
        self.master_template_directory = c.MASTER_TEMPLATES
        self.project_directory = (
            f"{ c.PROJECTS_FOLDER }project_{ self.project_id }/"
        )
        self.safety_directory = (
            f"{ self.project_directory }{ c.CLINICAL_SAFETY_FOLDER }"
        )
        self.documents_yaml = f"{ self.safety_directory }documents.yml"
        self.docs_dir = f"{ self.safety_directory }docs/"
        self.placeholders_yaml = f"{ self.safety_directory }placeholders.yml"
        self.entries_templates_dir = f"{ self.safety_directory }templates/"

        return

    @staticmethod
    def new_build_prohibit(func: Callable[..., Any]) -> Callable[..., Any]:
        """A decorator checking if a method can be used

        If used, this decorator only allows a method to be used if a project_id
        is 1 or more.

        functions:
            wrapper: to check if a method can be used
        """

        @wraps(func)
        def wrapper(self: "ProjectBuilder", *args: Any, **kwargs: Any) -> Any:
            """Wraps around the page function.

            Args:
                request (HttpRequest):
                project_id (str): datanase primary key for project

            Returns:
                HttpResponse | func: error responses or runs func.

            Raises:
                SyntaxError: if the function is not allowed for a new-build project
            """
            if self.new_build_flag:
                raise SyntaxError(
                    "This function is not allowed for a new-build project (with no primary key)"
                )

            return func(self, *args, **kwargs)

        return wrapper

    def test_no_wrapper(self) -> None:
        """Do not alter this function.

        Used for testing the new_build_prohibit decorator.
        """
        return

    @new_build_prohibit
    def test_with_wrapper(self) -> None:
        """Do not alter this function (or decorator).

        Used for testing the new_build_prohibit decorator.
        """
        return

    def new_build(self, request: HttpRequest) -> None:
        """Creates a new project and associated files

        This function creates a new project and associated files. It also creates a
        new project in the database.

        Args:
            request (HttpRequest): the request object

        Returns:
            Tuple[bool, str]: True when successful build. String is a list of
                              errors, if present.

        Raises:
            ValueError: User id could not be converted to an integer
            KeyError: 'setup_choice' not set
            ValueError: 'setup_choice' is incorrectly set
            KeyError: 'external_repository_username_import' not set
            KeyError: 'external_repository_password_token_import' not set
            KeyError: 'external_repository_url_import' not set
            RepositoryAccessException: if the repository does not exist or is not
                                       accessible
            NotImplementedError: Code for other external repositories is not yet
                                 written.
            FileExistsError: if the project directory already exists
        """
        user_id: int = 0
        inputs = request.session["inputs"]
        new_project: Project
        group_id: int = 0
        github_controller: GitHubController
        new_user_project_attribute: UserProjectAttribute
        new_project_directory: str = ""
        new_safety_directory: str = ""

        if not isinstance(request.user.id, int):
            raise ValueError("User id could not be converted to an integer")

        user_id = int(request.user.id)

        if not "setup_choice" in inputs:
            raise KeyError("'setup_choice' not set")

        if (
            inputs["setup_choice"] != "start_anew"
            and inputs["setup_choice"] != "import"
        ):
            raise ValueError("'setup_choice' is incorrectly set")

        if inputs["setup_choice"] == "import":
            if not "external_repository_username_import" in inputs:
                raise KeyError("'external_repository_username_import' not set")
            if not "external_repository_password_token_import" in inputs:
                raise KeyError(
                    "'external_repository_password_token_import' not set"
                )
            if not "external_repository_url_import" in inputs:
                raise KeyError("'external_repository_url_import' not set")

        if inputs["setup_choice"] == "import":
            if inputs["repository_type"] == "github":
                github_controller = GitHubController(
                    inputs["external_repository_username_import"],
                    inputs["external_repository_password_token_import"],
                )
                if not github_controller.repository_exists(
                    inputs["external_repository_url_import"]
                ):
                    raise RepositoryAccessException(
                        inputs["external_repository_url_import"]
                    )

            else:
                # TODO #44
                raise NotImplementedError(
                    "Code for other external repositories is not yet written.",
                )

        # Database record creation
        new_project = Project()
        new_project.name = inputs["project_name"]
        new_project.description = inputs["description"]
        new_project.access = inputs["access"]
        new_project.owner = User.objects.get(id=user_id)

        if inputs["setup_choice"] == "import":
            new_project.external_repository_url = inputs[
                "external_repository_url_import"
            ]

        new_project.save()
        new_project.member.set(User.objects.filter(id__in=inputs["members"]))
        new_project.save()

        request.session["project_id"] = new_project.id

        new_user_project_attribute = UserProjectAttribute()
        new_user_project_attribute.user = User.objects.get(id=user_id)
        new_user_project_attribute.project = new_project

        if inputs["setup_choice"] == "import":
            new_user_project_attribute.repository_username = inputs[
                "external_repository_username_import"
            ]
            new_user_project_attribute.repository_password_token = inputs[
                "external_repository_password_token_import"
            ]

        new_user_project_attribute.save()

        for group_id in map(int, inputs["groups"]):
            group = ProjectGroup.objects.get(id=group_id)
            group.project_access.add(new_project)
            group.save()

        new_project_directory = (
            f"{ c.PROJECTS_FOLDER }project_{ new_project.id }/"
        )
        new_safety_directory = (
            f"{ new_project_directory }{ c.CLINICAL_SAFETY_FOLDER }"
        )

        if Path(new_project_directory).is_dir():
            raise FileExistsError(
                f"'{ new_project_directory }' already exists",
            )

        Path(new_project_directory).mkdir(parents=True, exist_ok=True)

        if inputs["setup_choice"] == "import":
            git_controller = GitController()
            git_controller.clone(
                inputs["external_repository_url_import"],
                new_project_directory,
            )

        if not Path(new_safety_directory).is_dir():
            Path(new_safety_directory).mkdir(parents=True, exist_ok=True)

        return

    def master_template_get(self) -> list[str]:
        """Get the different types of master templates available

        Looks in the master template folder for template subfolders. Technically
        a template is a collection of markdown and yaml files.

        Returns:
            list[str]: a list of templates in alphabetical order.

        Raises:
            FileNotFoundError: if no template subfolder found in templates main
                               folder.
        """
        templates: list[str] = []

        templates = [
            directory.name
            for directory in Path(self.master_template_directory).iterdir()
            if directory.is_dir()
        ]

        if not templates:
            raise FileNotFoundError(
                f"No templates folders found in '{ self.master_template_directory }' template directory"
            )

        return sorted(templates, key=str.lower)

    @new_build_prohibit
    def configuration_get(self) -> dict[str, Any]:
        """Returns the configuration settings for the project

        Reads the setup.ini file in the clinical safety folder and returns the
        settings.

        Returns:
            dict[str, Any]: a dictionary of the settings.

        Raises:
            FileNotFoundError: if the clinical safety folder does not exist.
        """
        configration_file: str = f"{ self.safety_directory }setup.ini"
        config: Optional[ENVManipulator] = None

        if not Path(self.safety_directory).is_dir():
            raise FileNotFoundError(
                f"'{ self.safety_directory }' does not exist"
            )

        config = ENVManipulator(configration_file)
        setup_step: Optional[str] = None

        setup_step = config.read("setup_step")

        # catches negative numbers and non-numeric characters
        if not setup_step.isdigit():
            setup_step = "1"
            config.add("setup_step", setup_step)

        return {"setup_step": int(setup_step)}

    @new_build_prohibit
    def configuration_set(self, key: str, value: str) -> bool:
        """Sets the configuration settings for the project

        Writes to the setup.ini file in the clinical safety folder.

        Args:
            key (str): the key to be set.
            value (str): the value to be set.

        Returns:
            bool: True if successful, False if not.

        Raises:
            FileNotFoundError: if the clinical safety folder does not exist.
        """
        configration_file: str = f"{ self.safety_directory }setup.ini"
        config: Optional[ENVManipulator] = None

        if not Path(self.safety_directory).is_dir():
            raise FileNotFoundError(
                f"'{ self.safety_directory }' does not exist"
            )

        config = ENVManipulator(configration_file)

        config.add(key, str(value))
        return True

    @new_build_prohibit
    def copy_master_template(self, template_chosen: str) -> None:
        """Copies a master template to the clinical safety folder

        Copies a master template to the clinical safety folder.

        Args:
            template_chosen (str): the template to copy across.

        Raises:
            FileNotFoundError: if the template chosen does not exist.
        """
        template_chosen_path: str = (
            f"{ self.master_template_directory }{ template_chosen }"
        )

        if not Path(template_chosen_path).is_dir():
            raise FileNotFoundError(
                f"'{ template_chosen_path }' does not exist"
            )

        shutil.copytree(
            template_chosen_path,
            self.safety_directory,
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
        file_path: str = ""
        file: Optional[TextIO] = None
        doc_Regex: Optional[Pattern[str]] = None
        placeholders_sub: list[str] = []
        placeholder: str = ""
        placeholders_raw: list[str] = []
        stored_placeholders: dict[str, str] = {}
        placeholders_clean: dict[str, str] = {}

        files_to_check = [str(p) for p in Path(self.docs_dir).rglob("*.md")]

        if not len(files_to_check):
            raise FileNotFoundError(
                f"No files found in mkdocs '{ self.docs_dir }' folder"
            )

        for file_path in files_to_check:
            file = open(file_path, "r")
            doc_Regex = re.compile(r"\{\{.*?\}\}", flags=re.S)
            placeholders_sub = doc_Regex.findall(file.read())
            for placeholder in placeholders_sub:
                if placeholder not in placeholders_raw:
                    placeholders_raw.append(placeholder)
            file.close()

        if Path(self.placeholders_yaml).exists():
            stored_placeholders = self.read_placeholders()

        for placeholder in placeholders_raw:
            placeholder = placeholder.replace("{{", "")
            placeholder = placeholder.replace("}}", "")
            placeholder = placeholder.strip()
            placeholders_clean[placeholder] = stored_placeholders.get(
                placeholder, ""
            )
        return placeholders_clean

    @new_build_prohibit
    def save_placeholders(self, placeholders: dict[str, str]) -> None:
        """Saves placeholders to yaml file

        Saves the placeholders, supplied as a dictionary, into the
        placeholders.yml file in the clinical safety folder.

        Args:
            placeholders (dict[str,str]): dictionary of placeholders. Key is name
                                          of placeholder and value is the value.

        Raises:
            FileNotFoundError: if the safety directory does not exist.
        """
        placeholders_extra: dict[str, dict[str, str]] = {"extra": placeholders}
        file: Optional[TextIO] = None

        if not Path(self.safety_directory).is_dir():
            raise FileNotFoundError(
                f"'{ self.safety_directory }' does not exist"
            )

        with open(self.placeholders_yaml, "w") as file:
            yaml.dump(placeholders_extra, file)
        return

    def save_placeholders_from_form(self, form: PlaceholdersForm) -> None:
        """Saves placeholders to yaml

        Saves the placeholders, as supplied via a web form. Note that
        get_placeholders can raise a FileNotFoundError if no files found in the
        docs folder and save_placeholders can raise a FileNotFoundError if the
        safety directory does not exist.

        Args:
            form (dict[str,str]): dictionary of placeholders.
        """
        placeholders: dict[str, str] = self.get_placeholders()

        for placeholder in placeholders:
            placeholders[placeholder] = form.cleaned_data.get(placeholder, "")

        self.save_placeholders(placeholders)
        return

    @new_build_prohibit
    def read_placeholders(self) -> dict[str, str]:
        """Read placeholders from yaml file

        Reads already stored placeholder values as stored in placeholders.yml.

        Returns:
            dict[str,str]: placeholder names and value pairs.

        Raises:
            FileNotFoundError: if placeholder yaml is not a valid file.
            ValueError: if error reading content of yaml file (eg no 'extra'
                        key).
        """
        placeholders_extra: dict[str, dict[str, str]] = {}
        file: Optional[TextIO] = None
        return_dict: dict[str, str] = {}

        if not Path(self.placeholders_yaml).is_file():
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
    def entry_exists(self, entry_type: str, id: int) -> bool:
        """Checks if an entry of certain type exists

        Args:
            entry_type (str): named type of entry
            id (int): the id to be assessed if an associated entry exists

        Returns:
            bool: true if entry is a positive integer and exists.
        """
        directory_to_check: str = f"{ c.PROJECTS_FOLDER }project_{ self.project_id }/{ c.CLINICAL_SAFETY_FOLDER }docs/{ entry_type }s/{ entry_type }s/"
        file_to_find: str = f"{ entry_type }-{ id }.md"

        if not isinstance(id, int):
            raise ValueError(f"'id' '{ id }' is not an integer")

        if id < 1:
            raise ValueError(f"'id' '{ id }' is not a positive integer")

        if any(Path(directory_to_check).rglob(file_to_find)):
            return True

        return False

    @new_build_prohibit
    def entry_file_read(
        self,
        entry_type: str,
        non_template_path: str = "",
    ) -> list[dict[str, Any]]:
        """Read the contents of either an entry template or entry instance

        Args:
            entry_type (str): the type of entry (eg hazard or incident)
            non_template_path (str): if empty string, then read template,
                                     otherwise read contents from file path.

        Returns:
            list[dict[str, Any]]: a dictionary of fields.

        Raises:
            FileExistsError: if entry instance or template does not exist.
        """
        entry_file_path: str = ""
        lines: list[str] = []
        line: str = ""
        headed: bool = False
        heading: str = ""
        content_list: list[dict[str, Any]] = []
        horizontal_line: str = ""
        br_line: str = ""
        matches: list[str] = []
        argument: str = ""
        index: int = 0
        element: dict[str, Any] = {}
        choice_name: str = ""
        choices_list: list[Any] = []
        key: str = ""
        value: str = ""
        text_list: list[str] = []
        choice: str = ""
        choice_split: list[str] = []
        choices_dict_split: dict[str, str] = {}
        potential_number: str = ""

        if non_template_path == "":
            entry_file_path = f"{ self.entries_templates_dir }{ entry_type }{ c.ENTRY_TEMPLATE_SUFFIX }"
        else:
            entry_file_path = non_template_path

        if not Path(entry_file_path).is_file():
            raise FileNotFoundError(f"'{ entry_file_path }' does not exists")

        lines = open(entry_file_path, "r").read().split("\n")

        for line in lines:
            line = line.strip()

            # To match the heading line
            if re.match(r"^#", line):
                headed = True
                heading = line

                content_list.append(
                    {
                        "field_type": "text_area",  # This is changed later if needed
                        "heading": self._heading_numbering(
                            heading,
                            content_list,
                        ),
                        "gui_label": self._create_gui_label(heading),
                        "text": "",
                    }
                )

            # To match the horizontal line
            elif re.match(r"^-", line):
                horizontal_line = line
                headed = False

                content_list.append(
                    {
                        "field_type": "horizontal_line",
                        "heading": self._heading_numbering(
                            horizontal_line,
                            content_list,
                        ),
                    }
                )

            # To match new line tag <br>
            elif re.match(r"^<br>", line):
                br_line = line
                headed = False

                content_list.append(
                    {
                        "field_type": "new_line",
                        "heading": self._heading_numbering(
                            br_line,
                            content_list,
                        ),
                    }
                )

            # To match the icon line
            elif re.match(
                r"^<!--\s*\[\s*icon\s*\]\s*-->$",
                line,
            ):
                headed = False

                content_list.append(
                    {
                        "field_type": "icon",
                        "heading": self._heading_numbering(
                            "icon",
                            content_list,
                        ),
                    }
                )

            elif headed and line:
                # To match for labels
                if line[0] == "[":
                    matches = re.findall(r"\[([^\]]+)\]", line)
                    content_list[-1]["labels"] = []
                    for argument in matches:
                        argument = argument.strip()
                        if argument == "select":
                            content_list[-1]["field_type"] = "select"
                        elif argument == "multiselect":
                            content_list[-1]["field_type"] = "multiselect"
                        elif argument == "calculate":
                            content_list[-1]["field_type"] = "calculate"
                        elif argument == "readonly":
                            content_list[-1]["field_type"] = "readonly"
                        elif argument == "date":
                            content_list[-1]["field_type"] = "date"
                        elif argument == "code":
                            content_list[-1]["field_type"] = "code"
                            # content_list[-1]["text"] = "<!-- [code] -->"
                        else:
                            content_list[-1]["labels"].append(argument)

                # If no labels then use as text
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

                # TODO what what I trying to do here?
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

        return content_list

    def entry_read_with_field_types(
        self,
        entry_type: str,
        entry_file_path: str,
    ) -> list[dict[str, Any]]:
        """Returns an entry instance with field typing

        Looks up the entry template and the entry instance and matches the
        fields.

        Args:
            entry_type (str): the type of entry (eg hazard or incident)
            entry_file_path (str): the path to the entry file
        """
        entry_instance: list[dict[str, Any]] = self.entry_file_read(
            entry_type, entry_file_path
        )
        index_entry: int = 0
        field_entry: dict[str, Any] = {}
        entry_template: list[dict[str, Any]] = self.entry_file_read(entry_type)

        for index_entry, field_entry in enumerate(entry_instance):
            for field_template in entry_template:
                if field_entry["heading"] == field_template["heading"]:
                    entry_instance[index_entry]["field_type"] = field_template[
                        "field_type"
                    ]

        return entry_instance

    def _heading_numbering(
        self,
        heading: str,
        content_list: list[dict[str, str]],
    ) -> str:
        """Adds a number to the heading if needed

        Returns a numbered heading if the heading does already exists in the
        content list.

        Args:
            heading (str): the heading to be numbered
            content_list (list[dict[str, str]]): a list of headings. A copy of the
                                                 list is made to avoid changing the
                                                 original list.

        Returns:
            str: the heading with a number if needed.

        Raises:
            ValueError: if loop exceeds HEADING_MAX_LOOP.
        """
        heading = heading.strip()
        heading_numbered: str = ""

        content_list = content_list.copy()

        if not any(d["heading"] == heading for d in content_list):
            return heading

        for x in range(2, c.HEADING_MAX_LOOP):
            heading_numbered = f"{ heading } [{ x }]"
            if not any(d["heading"] == heading_numbered for d in content_list):
                return heading_numbered
            if x == (c.HEADING_MAX_LOOP - 1):
                # Used break here to get 'raise' outside of for loop and satisfy
                # mypy
                break

        raise ValueError(f"For loop over { c.HEADING_MAX_LOOP }!")

    def _create_gui_label(self, string: str) -> str:
        """Create user readable label

        User reable string

        Args:
            string (str): the string to change

        Returns:
            string: the user readable string in Sentence case.
        """

        string = string.replace("#", "")
        string = string.strip()
        return string

    @new_build_prohibit
    def entry_update(
        self,
        form_data: dict[str, str],
        entry_type: str = "hazard",
        id_new: str = "new",
    ) -> dict[str, Any]:
        """Create or update entries (eg hazards and incidents)

        Depending on the value of id_new (a valid int or the str "new"), either
        a new entry will be created or a pre-existing one updated.

        Args:
            form_data (dict[str, str]): key value pairs of data to be written
                                        to file
            entry_type (str): type of entry, eg hazard, incident, officer.
            id_new (str): a valid digit (1 of more) to update an existing entry
                          or the word "new" to create a new one.

        Returns:
            dict[str, Any]: returns a dictionary of method outcomes.
        """
        entries_directory: str = f"{ c.PROJECTS_FOLDER }project_{ self.project_id }/{ c.CLINICAL_SAFETY_FOLDER }docs/{ entry_type }s/{ entry_type }s/"
        files_to_check: list[str] = []
        filename: str = ""
        match: Optional[re.Match[str]] = None
        extracted_number: int = 0
        numbers: list[int] = []
        entry_file: Optional[TextIO] = None
        id_int: int = 0
        to_write: str = ""
        entry_name: str = ""

        if not Path(entries_directory).is_dir():
            Path(entries_directory).mkdir(parents=True, exist_ok=True)

        # files_to_check = [f.name for f in Path(entries_directory).rglob('*.md')]
        for path, _, files in os.walk(entries_directory):
            for name in files:
                if fnmatch(name, "*.md"):
                    files_to_check.append(name)

        if id_new == "new":
            if files_to_check:
                for filename in files_to_check:
                    match = re.search(r"-(\d+)\.md", filename)
                    if match:
                        extracted_number = int(match.group(1))
                        numbers.append(extracted_number)
                # what happens if numbers is an empty list?
                id_int = max(numbers) + 1
            else:
                id_int = 1

        elif id_new.isdigit() and self.entry_exists(entry_type, int(id_new)):
            id_int = int(id_new)
        else:
            return {
                "pass": False,
            }

        entry_file = open(
            f"{ entries_directory }{ entry_type }-{ id_int }.md",
            "w",
        )

        for key, value in form_data.items():
            to_write = re.sub(r"\s*\[\d+\]$", "", key)
            if to_write == "icon":
                entry_file.write("<!-- [icon] -->\n")
            else:
                entry_file.write(f"{ to_write }\n")

            if isinstance(value, list):
                for item in value:
                    entry_file.write(f"{ item }\n\n")
            else:
                entry_file.write(f"{ value }\n\n")
        entry_file.close()

        # TODO #54 need to get ride of the 404 in this none view.py code
        project_timestamp(self.project_id)
        """project = get_object_or_404(Project, id=self.project_id)
        project.last_modified = timezone.now()
        project.save()"""

        for key, value in form_data.items():
            if "name" in key.lower():
                entry_name = value
                break

        return {
            "pass": True,
            "id": id_int,
            "name": entry_name,
            "entries_url": f"{ entry_type }s/{ entry_type }s/{ entry_type }-{ id_int }.html",
        }

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
    def entry_template_names(self) -> list[str]:
        """ """
        templates: Generator[Path, None, None] = Path(
            self.entries_templates_dir
        ).glob("*-template.md")
        templates_ls: list[str] = [file.stem for file in templates]
        templates_prefix: list[str] = []
        documents_config: dict[str, str] = {}

        for template in templates_ls:
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
    def entry_type_exists(self, entry_type: str) -> bool:
        """ """
        entry_types_found: list[str] = self.entry_template_names()

        if entry_type in entry_types_found:
            return True

        return False

    @new_build_prohibit
    def entries_all_get(
        self, entry_type: str
    ) -> list[str | list[dict[str, Any]]]:
        """Get all of the hazards for the project

        Returns:
            list[str]: A list of all hazards found for a project.
        """
        entry_dir: str = f"{ self.safety_directory }docs/{ entry_type }s/"
        entry_entry_dir: str = f"{ entry_dir }{ entry_type }s/"
        entry_file_contents: list[str] = []
        entries_list: list[str | list[dict[str, Any]]] = []
        fields: list[dict[str, Any]] = []
        name: str = ""
        entry_with_attributes: list[dict[str, Any]] = []
        entry_number: str | None = ""
        # element

        for path, _, files in os.walk(entry_entry_dir):
            for name in files:
                if fnmatch(name, "*.md"):
                    entry_file_contents.append(os.path.join(path, name))

        entry_file_contents = sorted(entry_file_contents, reverse=True)

        for file in entry_file_contents:
            pattern = r"-([0-9]+)\.md"
            name = ""

            matches = re.search(pattern, file)

            # print(matches.group(1))
            # TODO #50 need to handel a bad file name eg hazard-abc.md

            if matches:
                entry_number = matches.group(1)
            else:
                entry_number = None

            fields = self.entry_file_read(entry_type, file)

            for element in fields:
                if "name" in element["heading"]:
                    name = element["text"]
                    break

            entry_with_attributes = [
                {
                    "file": file,
                    "number": entry_number,
                    "name": name,
                }
            ]
            entry_with_attributes.extend(fields)
            entries_list.append(entry_with_attributes)

            # print(entries_list)
        return entries_list

    @new_build_prohibit
    def form_initial(
        self, entry_type: str, id: int
    ) -> dict[str, str | list[str]]:
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
        data_initial: dict[str, str | list[str]] = {}
        selected_options: list[str] = []

        file_path = f"{ c.PROJECTS_FOLDER }project_{ self.project_id }/{ c.CLINICAL_SAFETY_FOLDER }docs/{ entry_type }s/{ entry_type }s/{ entry_type }-{ id }.md"
        template = self.entry_file_read(entry_type)
        data = self.entry_file_read(entry_type, file_path)

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
                        and field_template["field_type"] != "new_line"
                    ):
                        data_initial[field_data["heading"]] = field_data[
                            "text"
                        ]

        return data_initial

    @new_build_prohibit
    def document_create_check(self, path: str) -> Tuple[bool, list[str]]:
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
        md_files: list[str] = []

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
        templates: Generator[Path, None, None] = Path(
            entry_templates_location
        ).rglob(f"*{ c.TEMPLATE_SUFFIX }")

        return [file_path.name for file_path in templates]

    def _entry_templates_exclude(
        self,
    ) -> list[str]:
        """ """
        directories_to_exclude: list[str] = []
        templates: list[str] = self._entry_templates_list()

        for template in templates:
            directories_to_exclude.append(
                template.replace(c.TEMPLATE_SUFFIX, "s/")
            )

        return directories_to_exclude
