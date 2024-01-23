"""Form management for the Django dynamic site app

Classes:
    InstallationForm: placeholder
    TemplateSelectForm: placeholder
    PlaceholdersForm: placeholder
    MDFileSelectForm: placeholder
    MDEditForm: placeholder
    LogHazardForm: placeholder
    HazardCommentForm: placeholder
    UploadToGithubForm: placeholder

Functions:
    validation_response: placeholder
    md_files: placeholder
"""

from django import forms
from django.conf import settings

from .models import (
    User,
    UserProfile,
    Project,
    ProjectGroup,
    UserProjectAttribute,
)

import os
import glob
from fnmatch import fnmatch
import sys

from typing import Any

import app.functions.constants as c
from app.functions.constants import GhCredentials

sys.path.append(c.FUNCTIONS_APP)
from app.functions.git_control import GitController
from app.functions.email_functions import EmailFunctions
from app.functions.projects_builder import ProjectBuilder
from pathlib import Path


def validation_response(
    self, field: str, valid: bool, error_message: str
) -> None:
    """A general function to create form validation results

    Provides the field class and error messages to work with Bootstrap.

    Args:
        field: name of field.
        valid: if the validation of the field passes, True = passes, False = does
               not pass.
        error_message: message to display if data does not pass validation.
    """
    if valid:
        self.fields[field].widget.attrs[
            "class"
        ] = f"form-control is-valid { c.FORM_ELEMENTS_MAX_WIDTH }"
    else:
        self.add_error(field, error_message)
        self.fields[field].widget.attrs[
            "class"
        ] = f"form-control is-invalid { c.FORM_ELEMENTS_MAX_WIDTH }"
    return


def md_files(project_id: int) -> list:
    """Finds markdown files

    Looks for markdown files in MKDOCS_PATH. Resturns a list of paths relative
    to MKDOCS_PATH

    Args:
        project_id (int): project database id number

    Returns:
        list: list of paths of markdown files relative to MKDOCS_PATH

    Raises:
        FileNotFoundError: if MKDOCS_PATH is not a valid directory
    """
    docs_location = f"{ c.PROJECTS_FOLDER }project_{ project_id }/{ c.CLINICAL_SAFETY_FOLDER }docs/"
    root: str = ""
    md_files: list = []
    file: str = ""
    file_shortened: str = ""
    md_files_shortened: list[str] = []
    choices_list: list = []

    if not os.path.isdir(docs_location):
        raise FileNotFoundError(
            f"{ docs_location } if not a valid folder location"
        )

    for root, _, __ in os.walk(docs_location):
        md_files.extend(glob.glob(os.path.join(root, "*.md")))

    for file in md_files:
        md_files_shortened.append(file.replace(docs_location, ""))

    for file_shortened in md_files_shortened:
        choices_list.append([file_shortened, file_shortened])

    return choices_list


class ProjectSetupInitialForm(forms.Form):
    """Setup a project"""

    CHOICES_1 = (
        ("", ""),
        (
            "import",
            "Import from external source",
        ),
        (
            "start_anew",
            "Start a new project from scratch",
        ),
    )

    setup_choice = forms.ChoiceField(
        choices=CHOICES_1,
        widget=forms.Select(
            attrs={
                "class": "form-select w-auto",
                "onChange": "change_visibility()",
            }
        ),
    )

    external_repo_url_import = forms.CharField(
        label="Respository URL",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": f"form-control { c.FORM_ELEMENTS_MAX_WIDTH }",
                "autocomplete": "github-username",
            }
        ),
    )

    external_repo_username_import = forms.CharField(
        label="Respository username",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": f"form-control { c.FORM_ELEMENTS_MAX_WIDTH }",
                "autocomplete": "github-username",
            }
        ),
    )

    external_repo_password_token_import = forms.CharField(
        label="Repository token",
        help_text="You can get your Github <a href='https://github.com/settings/tokens/new' target='_blank'> token</a> here",
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "class": f"form-control { c.FORM_ELEMENTS_MAX_WIDTH }",
                "autocomplete": "github-token",
            }
        ),
    )


class ProjectSetupStepTwoForm(forms.Form):
    """ProjectSetupStepTwoForm

    Fields:
        project_name_import_start_anew: name of the project
    """

    def __init__(self, *args, **kwargs) -> None:
        """Initialise the fields for the second step of project setup"""
        super(ProjectSetupStepTwoForm, self).__init__(*args, **kwargs)
        groups_list: list = []
        choices_list_1: list = []
        choices_list_2: list = []

        self.fields["project_name"] = forms.CharField(
            label="Project name",
            required=True,
            widget=forms.TextInput(
                attrs={
                    "class": f"form-control { c.FORM_ELEMENTS_MAX_WIDTH }",
                    "autocomplete": "github-username",
                }
            ),
        )

        self.fields["description"] = forms.CharField(
            required=True,
            widget=forms.Textarea(
                attrs={
                    "class": f"form-control { c.FORM_ELEMENTS_MAX_WIDTH }",
                    "rows": 3,
                    "autocomplete": "description",
                }
            ),
        )

        groups_list = ProjectGroup.objects.values("id", "name")

        for group in groups_list:
            choices_list_1.append([group["id"], group["name"]])

        CHOICES_1 = tuple(choices_list_1)

        self.fields["groups"] = forms.MultipleChoiceField(
            label="Group select",
            help_text="Press CTRL or Command (&#8984;) to select multiple groups",
            required=False,
            choices=CHOICES_1,
            widget=forms.SelectMultiple(
                attrs={
                    "class": "form-select w-auto",
                    # "style": "height: 80px",
                }
            ),
        )

        # TODO #40 - will need to figure out who you can see to add (some people may want to have membership hidden)
        members_list = User.objects.values("id", "first_name", "last_name")

        for member in members_list:
            choices_list_2.append(
                [
                    member["id"],
                    f"{ member['first_name']} { member['last_name']}",
                ]
            )

        CHOICES_2 = tuple(choices_list_2)

        self.fields["members"] = forms.MultipleChoiceField(
            label="Add members ",
            help_text="Press CTRL or Command (&#8984;) to select multiple members",
            required=False,
            choices=CHOICES_2,
            widget=forms.SelectMultiple(
                attrs={
                    "class": "form-select w-auto",
                    # "style": "height: 80px",
                }
            ),
        )


# TODO - might be able to remove this form
class InstallationForm(forms.Form):
    """For managing initial installation parameters

    Two options are available for the initial set up step for DCSP.
    - Stand alone (SA): The first is a stand alone setup which manages git and
    GitHub functionalities itself.
    - Integrated (I): an option for when DCSP is integrated into an already
    created code base, where git and GitHub functionality is handled outside of
    DCSP.

    Methods:
        clean: placeholder

    Fields:
        installation_type: Selection of installation type (stand alone or
                           integrated).
        github_username_SA: GitHub username
        email_SA: user's email address
        github_organisation_SA: Organisation that repositories can be stored
                                under. If left blank then username is used as
                                the space to store repositories.
        github_repo_SA: The name of the repository on GitHub.
        github_token_SA: GitHub token.
        code_location_I: Location of code. This is used when DCSP is integrated
                         into another code base.
    """

    CHOICES = (
        ("", ""),
        (
            "SA",
            "Stand alone",
        ),
        (
            "I",
            "Integrated",
        ),
    )

    installation_type = forms.ChoiceField(
        choices=CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select w-auto",
                "onChange": "change_visibility()",
            }
        ),
    )

    github_username_SA = forms.CharField(
        label="Github username",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": f"form-control { c.FORM_ELEMENTS_MAX_WIDTH }",
                "autocomplete": "github-username",
            }
        ),
    )

    email_SA = forms.CharField(
        label="Email",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": f"form-control { c.FORM_ELEMENTS_MAX_WIDTH }",
            }
        ),
    )

    github_organisation_SA = forms.CharField(
        label="Github organisation (leave blank if you are / will be storing the documents under your own username on Github)",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": f"form-control { c.FORM_ELEMENTS_MAX_WIDTH }",
            }
        ),
    )

    github_repo_SA = forms.CharField(
        label="Github repository (current or soon to be created)",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": f"form-control { c.FORM_ELEMENTS_MAX_WIDTH }",
            }
        ),
    )

    github_token_SA = forms.CharField(
        label="Github token (<a href='https://github.com/settings/tokens/new' target='_blank'>get Github token</a>)",
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "class": f"form-control { c.FORM_ELEMENTS_MAX_WIDTH }",
                "autocomplete": "github-token",
            }
        ),
    )

    code_location_I = forms.CharField(
        label="Local location of source code (related to the git repository root)",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": f"form-control { c.FORM_ELEMENTS_MAX_WIDTH }",
            }
        ),
    )

    def clean(self) -> dict:
        """Cleans data from InstallationForm

        Checks all data for errors and prepares validation results if there are
        errors.

        Returns:
            dict: of clean data.

        Invalids:
            email: if wrong syntax.
            github_username_SA: if username does not exist.
            github_organisation_SA: if organisation does not exist, if no
                                    organisation is supplied then username is
                                    used instead.
            github_repo_SA: if repository does not exist or user does not have
                            admin rights to the repository
            code_location_I: if space in directory path.
        """
        cleaned_data: Any = self.cleaned_data
        installation_type: str = cleaned_data["installation_type"]
        github_username: str = cleaned_data["github_username_SA"]
        email: str = cleaned_data["email_SA"]
        github_organisation: str = cleaned_data["github_organisation_SA"]
        github_repo: str = cleaned_data["github_repo_SA"]
        github_token: str = cleaned_data["github_token_SA"]
        code_location: str = cleaned_data["code_location_I"]
        credentials_check_results: dict[str, str | bool | None] = {}

        # TODO - may not need this test, as seems 'cleaned_data["installation_type"] fails with bad select data
        if installation_type != "SA" and installation_type != "I":
            self.add_error(
                "installation_type",
                f"Error with installation type received - { installation_type }",
            )

        if github_organisation == "":
            github_organisation = github_username

        if installation_type == "SA":
            email_function = EmailFunctions()

            if not email_function.valid_syntax(email):
                validation_response(
                    self,
                    "email_SA",
                    False,
                    f"Email address '{ email }' is invalid. No other processing of credentials will be checked until this error is fixed.",
                )
            else:
                validation_response(
                    self,
                    "email_SA",
                    True,
                    "",
                )

                gc = GitController(
                    github_username=github_username,
                    email=email,
                    github_organisation=github_organisation,
                    github_repo=github_repo,
                    github_token=github_token,
                )

                credentials_check_results = gc.check_github_credentials()
                validation_response(
                    self,
                    "github_username_SA",
                    bool(credentials_check_results["github_username_exists"]),
                    "Username does not exist on Github",
                )

                validation_response(
                    self,
                    "github_organisation_SA",
                    bool(
                        credentials_check_results["github_organisation_exists"]
                    ),
                    "Organisation does not exist on Github",
                )

                validation_response(
                    self,
                    "github_repo_SA",
                    bool(credentials_check_results["repo_exists"]),
                    "Repository does not exist",
                )

                validation_response(
                    self,
                    "github_repo_SA",
                    credentials_check_results["permission"] == "admin",
                    "No admin rights to this repo",
                )

        if " " in github_repo:
            self.add_error("github_repo_SA", "Invalid URL")
            self.fields["github_repo_SA"].widget.attrs["class"] = (
                f"form-control is-invalid { c.FORM_ELEMENTS_MAX_WIDTH }" ""
            )

        if installation_type == "I":
            validation_response(
                self,
                "code_location_I",
                not " " in code_location,
                "Invalid path",
            )
        return cleaned_data


class TemplateSelectForm(forms.Form):
    """Template selection form

    Provides available templates.

    Fields:
        template_choice: pick the template to use for hazard documentation.
    """

    def __init__(self, project_id: int, *args, **kwargs) -> None:
        """Initialise with available templates

        Searches in the templates folder for template sub-folders and provides
        these as options in a selection field for the user.
        """
        super(TemplateSelectForm, self).__init__(*args, **kwargs)
        project: ProjectBuilder = ProjectBuilder()
        templates: list[str] = project.get_templates()
        template: str = ""
        choices_list: list = []

        if len(templates) == 0:
            raise Exception("No templates found in templates folder!")

        for template in templates:
            choices_list.append([template, template])

        CHOICES = tuple(choices_list)

        self.fields["template_choice"] = forms.ChoiceField(
            choices=CHOICES,
            widget=forms.Select(attrs={"class": "form-select w-auto"}),
        )


class PlaceholdersForm(forms.Form):
    """Creates fields for all available placeholders

    Searches through the docs folder in mkdocs for markdown files. If a
    placeholder is found, then this is made available for the user to provide a
    value for.

    Methods:
        clean: placeholder

    Fields:
        [Automatically created]
    """

    def __init__(self, project_id: int, *args, **kwargs) -> None:
        """Find placeholders and initialises web app fields

        Searches for placeholders in markdown files in doc folder and creates
        fields for each.
        """
        super(PlaceholdersForm, self).__init__(*args, **kwargs)
        placeholders: dict[str, str] = {}
        placeholder: str = ""
        value: str = ""

        project_build = ProjectBuilder(project_id)
        placeholders = project_build.get_placeholders()

        for placeholder, value in placeholders.items():
            self.fields[placeholder] = forms.CharField(
                required=False,
                initial=value,
                widget=forms.TextInput(attrs={"class": "form-control"}),
            )

    def clean(self) -> dict:
        """Checks placeholders for invalid characters

        Current invalid characters are "{}\"'"
        """
        INVALID_CHARACTERS: str = "{}\"'"
        cleaned_data: Any = self.cleaned_data.copy()
        key: str = ""
        value: str = ""

        for key, value in cleaned_data.items():
            validation_response(
                self,
                key,
                not any(illegal in value for illegal in INVALID_CHARACTERS),
                f"Invalid character in placeholder '{ key }' - '{ value }'",
            )

        return cleaned_data


class MDFileSelectForm(forms.Form):
    """Selection of the markdown file to edit

    Provides a selection of markdown files that can be edited. These are shown
    within their respective subfolders.
    """

    def __init__(self, project_id: int, *args, **kwargs) -> None:
        """Initialisation of the selection field

        Searches the docs folder and searches for markdown files, noting the
        any subfolders. These are then provided as a selection field.
        """
        super(MDFileSelectForm, self).__init__(*args, **kwargs)
        CHOICES = tuple(md_files(project_id))

        self.fields["mark_down_file"] = forms.ChoiceField(
            choices=CHOICES,
            widget=forms.Select(
                attrs={
                    "class": "form-select w-auto",
                    "onChange": "form.submit()",
                }
            ),
        )

    # Don't need to clean ChoiceFields apparently


class MDEditForm(forms.Form):
    """Text edit area of selected markdown file

    Provides the raw markdown for the selected file.

    Fields:
        document_name: name of the document. This is hidden and used in POST so
                       that filename can be retrieved.
        md_text: raw markdown of the file with placeholders evident in double
                 curley brackets (eg {{ placeholder }})
    """

    def __init__(self, project_id: int, *args, **kwargs) -> None:
        """Initialisation of the selection field

        Searches the docs folder and searches for markdown files, noting the
        any subfolders. These are then provided as a selection field.
        """
        super(MDEditForm, self).__init__(*args, **kwargs)
        self.project_id = project_id
        self.fields["document_name"] = forms.CharField(
            label="",
            widget=forms.HiddenInput(attrs={}),
        )

        self.fields["md_text"] = forms.CharField(
            label="Markdown view",
            required=False,
            widget=forms.Textarea(
                attrs={
                    "style": "width:100%; overflow:hidden;",
                    "class": "form-control",
                    "onkeyup": "update_web_view()",
                }
            ),
        )

    def clean(self) -> dict:
        """ """
        cleaned_data: Any = self.cleaned_data
        document_name: str = cleaned_data["document_name"]
        md_text: str = cleaned_data["md_text"]
        md_files_list: list = md_files(self.project_id)
        # doc_build: Builder
        linter_results: dict[str, str] = {}

        """validation_response(
            self,
            "md_text",
            document_name in md_files_list,
            "Internal error with document_name (hidden attribute)",
        )"""

        """# Not, mkdocs directory is not provided as an argument. But this should
        # Be ok just for linting.
        doc_build = Builder()
        linter_results = doc_build.linter_text(md_text)
        results_readable: str = """

        """ if linter_results["overal"] != "pass":
            self.add_error("md_text", "Error with syntax in markdown file")"""

        """for key, value in linter_results.items():
            if value == "pass":
                results_readable += f"{ key }: {value }</br>"
            else:
                results_readable += f"<u>{ key }: {value }</u></br>"

        validation_response(
            self,
            "md_text",
            linter_results["overal"] == "pass",
            f"There is invalid syntax in the markdown file, please correct:</br> { results_readable }",
        )"""

        return cleaned_data


class HazardNewForm(forms.Form):
    """Allows user to log a new hazard

    Form for adding a new hazard for the clinical safety case.
    """

    def __init__(self, project_id: int, *args, **kwargs) -> None:
        """Initialise the hazard log form

        Gets available hazard labels and creates fields for a new hazard log.

        Fields:
            title: title of the new hazard.
            body: main text of the hazard.
            labels: hazard labels.
        """
        super(HazardNewForm, self).__init__(*args, **kwargs)
        project: ProjectBuilder = ProjectBuilder(project_id)
        hazard_template: list[dict[str, Any]] = project.hazard_file_read()
        field_type: str = ""
        help_text: str = ""
        labels_for_calculations: dict[str, str] = {}

        for index, field in enumerate(hazard_template):
            help_text = ""

            if field["field_type"] == "horizontal_line":
                self.fields[field["heading"]] = forms.CharField(
                    label="",
                    required=False,
                    widget=forms.HiddenInput(attrs={}),
                )

            elif field["field_type"] == "select":
                help_text = field["text"].replace("\n", "<br>")
                self.fields[field["heading"]] = forms.ChoiceField(
                    label=field["gui_label"],
                    choices=field["choices"],
                    help_text=f"{index}|{help_text}",
                    widget=forms.Select(
                        attrs={
                            "class": "form-select w-auto",
                        }
                    ),
                )

                if "labels" in field:
                    self.labels_for_calculations[
                        f"id_{ field['heading'] }"
                    ] = field["labels"]

            elif field["field_type"] == "multiselect":
                help_text = field["text"].replace("\n", "<br>")
                self.fields[field["heading"]] = forms.MultipleChoiceField(
                    label=field["gui_label"],
                    required=False,
                    choices=field["choices"],
                    help_text=f"{index}|{help_text}",
                    widget=forms.SelectMultiple(
                        attrs={
                            "class": "selectpicker",
                            "style": "height: 150px",
                            "multiple": "true",
                        }
                    ),
                )

            elif field["field_type"] == "calculate":
                labels_for_calculations = {}

                help_text = field["text"].replace("\n", "<br>")
                self.fields[field["heading"]] = forms.CharField(
                    label=f"{ field['gui_label'] } (read only)",
                    required=False,
                    help_text=f"{index}|{help_text}",
                    widget=forms.TextInput(
                        attrs={
                            "class": "form-control",
                            "disabled": "disabled",
                        }
                    ),
                )

                # Match only labels that are required for this calculation field
                for label in field["labels"]:
                    for key, value in self.labels_for_calculations.items():
                        for label2 in value:
                            if label2 == label:
                                labels_for_calculations[key] = value

                self.calculation_field.append(
                    {
                        "id": f"id_{ field['heading'] }",
                        "monitor_labels": labels_for_calculations,
                        "choices": field["choices"],
                    },
                )

            elif field["field_type"] == "text_area":
                self.fields[field["heading"]] = forms.CharField(
                    label=field["gui_label"],
                    required=False,
                    widget=forms.Textarea(
                        attrs={
                            "class": "form-control",
                            "rows": 3,
                            "placeholder": field["text"],
                        }
                    ),
                )

            else:
                # TODO #48 - need a soft fail here
                raise ValueError(
                    f"'field_type' has wrong value of '{ field_type }'"
                )

    labels_for_calculations: dict[str, str] = {}
    calculation_field: list[dict[str, str]] = []


class HazardCommentForm(forms.Form):
    """Form for adding comments to a preexisting hazard

    A simple form to add a comment to a pre-existing hazard.

    Fields:
        comment: a new comment for the hazard.
    """

    comment = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "style": "height: 500px",
                "onkeyup": "update_web_view()",
            }
        ),
    )


class UploadToGithubForm(forms.Form):
    """Add comment for commit

    Form to add comment to then add to commit and then push to GitHub

    Fields:
        comment
    """

    comment = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "style": "height: 150px",
            }
        ),
    )
