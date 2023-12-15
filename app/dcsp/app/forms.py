"""Form management for the Django dynamic site app

Classes:
    InstallationForm
    TemplateSelectForm
    PlaceholdersForm
    MDFileSelectForm
    MDEditForm
    LogHazardForm
    HazardCommentForm
    UploadToGithubForm

Functions:
    validation_response
    md_files
"""

from django import forms
from django.conf import settings

import os
import glob
from fnmatch import fnmatch
import sys

from typing import Any

import app.functions.constants as c
from app.functions.constants import GhCredentials

sys.path.append(c.FUNCTIONS_APP)
from app.functions.docs_builder import Builder
from app.functions.git_control import GitController
from app.functions.email_functions import EmailFunctions


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


def md_files() -> list:
    MKDOCS_PATH: str = settings.MKDOCS_DOCS_LOCATION
    root: str = ""
    md_files: list = []
    file: str = ""
    file_shortened: str = ""
    md_files_shortened: list[str] = []
    choices_list: list = []

    if not os.path.isdir(MKDOCS_PATH):
        raise FileNotFoundError(
            f"{ MKDOCS_PATH } if not a valid folder location"
        )

    for root, _, __ in os.walk(MKDOCS_PATH):
        md_files.extend(glob.glob(os.path.join(root, "*.md")))

    for file in md_files:
        md_files_shortened.append(file.replace(MKDOCS_PATH, ""))

    for file_shortened in md_files_shortened:
        choices_list.append([file_shortened, file_shortened])

    return choices_list


class InstallationForm(forms.Form):
    """For managing initial installation parameters

    Two options are available for the initial set up step for DCSP.
    - Stand alone (SA): The first is a stand alone setup which manages git and
    GitHub functionalities itself.
    - Integrated (I): an option for when DCSP is integrated into an already
    created code base, where git and GitHub functionality is handled outside of
    DCSP.

    Methods:
        clean
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

    def __init__(self, *args, **kwargs) -> None:
        """Initialise with available templates

        Searches in the templates folder for template sub-folders and provides
        these as options in a selection field for the user.
        """
        super(TemplateSelectForm, self).__init__(*args, **kwargs)
        doc_build: Builder = Builder(settings.MKDOCS_LOCATION)
        templates: list[str] = doc_build.get_templates()
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
        clean
    Fields:
        [Automatically created]
    """

    def __init__(self, *args, **kwargs) -> None:
        """Find placeholders and initialises web app fields

        Searches for placeholders in markdown files in doc folder and creates
        fields for each.
        """
        super(PlaceholdersForm, self).__init__(*args, **kwargs)
        doc_build: Builder
        placeholders: dict[str, str] = {}
        placeholder: str = ""
        value: str = ""

        doc_build = Builder(settings.MKDOCS_LOCATION)
        placeholders = doc_build.get_placeholders()

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

    def __init__(self, *args, **kwargs) -> None:
        """Initialisation of the selection field

        Searches the docs folder and searches for markdown files, noting the
        any subfolders. These are then provided as a selection field.
        """
        super(MDFileSelectForm, self).__init__(*args, **kwargs)
        CHOICES = tuple(md_files())

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

    document_name = forms.CharField(
        label="",
        widget=forms.HiddenInput(attrs={}),
    )

    md_text = forms.CharField(
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
        md_files_list: list = md_files()
        doc_build: Builder
        linter_results: dict[str, str] = {}

        """validation_response(
            self,
            "md_text",
            document_name in md_files_list,
            "Internal error with document_name (hidden attribute)",
        )"""

        # Not, mkdocs directory is not provided as an argument. But this should
        # Be ok just for linting.
        doc_build = Builder()
        linter_results = doc_build.linter_text(md_text)
        results_readable: str = ""

        """ if linter_results["overal"] != "pass":
            self.add_error("md_text", "Error with syntax in markdown file")"""

        for key, value in linter_results.items():
            if value == "pass":
                results_readable += f"{ key }: {value }</br>"
            else:
                results_readable += f"<u>{ key }: {value }</u></br>"

        validation_response(
            self,
            "md_text",
            linter_results["overal"] == "pass",
            f"There is invalid syntax in the markdown file, please correct:</br> { results_readable }",
        )

        return cleaned_data


class LogHazardForm(forms.Form):
    """Allows user to log a new hazard

    Form for adding a new hazard for the clinical safety case.
    """

    def __init__(self, *args, **kwargs) -> None:
        """Initialise the log hazard form

        Gets available hazard labels and creates fields for a new hazard log.

        Fields:
            title: title of the new hazard.
            body: main text of the hazard.
            labels: hazard labels.
        """
        super(LogHazardForm, self).__init__(*args, **kwargs)
        gc: GitController = GitController(env_location=settings.ENV_LOCATION)
        available_labels: list[dict[str, str]] | list[
            str
        ] = gc.available_hazard_labels("name_only")
        labels_choices: list = []

        for label in available_labels:
            labels_choices.append([label, label])

        CHOICES = tuple(labels_choices)

        self.fields["title"] = forms.CharField(
            widget=forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
        )

        self.fields["body"] = forms.CharField(
            widget=forms.Textarea(
                attrs={
                    "class": "form-control",
                    "style": "height: 150px",
                }
            ),
        )

        self.fields["labels"] = forms.MultipleChoiceField(
            label="Label (press CTRL / CMD and select several as needed)",
            choices=CHOICES,
            widget=forms.SelectMultiple(
                attrs={
                    "class": "form-select w-auto",
                    "style": "height: 150px",
                }
            ),
        )


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
