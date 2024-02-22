"""Form management for the Django dynamic site app

Classes:
    InstallationForm: placeholder
    TemplateSelectForm: placeholder
    PlaceholdersForm: placeholder
    DocumentUpdateForm: placeholder
    LogHazardForm: placeholder
    HazardCommentForm: placeholder
    UploadToGithubForm: placeholder

Functions:
    validated_response: placeholder
    md_files: placeholder
"""

from django import forms
from django.conf import settings
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

from .models import ProjectGroup, ViewAccess

import os
from fnmatch import fnmatch
import sys
from typing import Any, Mapping

import app.functions.constants as c

sys.path.append(c.FUNCTIONS_APP)
import app.functions.project_builder as project_builder
from app.functions.general_functions import valid_partial_linux_path
from app.functions.text_manipulation import list_to_string


def validated_response(  # type: ignore[no-untyped-def]
    self,
    field: str,
    valid: bool,
    error_message: str,
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


def md_files(project_id: int) -> list[tuple[Any, Any]]:
    """Finds markdown files

    Looks for markdown files in MKDOCS_PATH. Returns a list of paths.

    Args:
        project_id (int): project database id number

    Returns:
        list: list of paths of markdown files relative to MKDOCS_PATH

    Raises:
        FileNotFoundError: if the docs location is not a valid directory
    """
    md_files: list[Any] = []
    file: Any = ""
    choices_list: list[tuple[Any, Any]] = []

    project: project_builder.ProjectBuilder = project_builder.ProjectBuilder(
        project_id
    )
    md_files = project.documents_list()

    for file in md_files:
        choices_list.append((file, file))

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
                "class": c.SELECT_STYLE,
                "onChange": "change_visibility()",
            }
        ),
    )

    external_repository_url_import = forms.CharField(
        label="Respository URL",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": f"form-control field-color-dcsp font-dcsp border-info { c.FORM_ELEMENTS_MAX_WIDTH }",
                "autocomplete": "url",
            }
        ),
    )

    external_repository_username_import = forms.CharField(
        label="Respository username",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": f"form-control field-color-dcsp font-dcsp border-info { c.FORM_ELEMENTS_MAX_WIDTH }",
                "autocomplete": "username",
            }
        ),
    )

    external_repository_password_token_import = forms.CharField(
        label="Repository token",
        help_text="You can get your Github <a class='link-dcsp' href='https://github.com/settings/tokens/new' target='_blank'> token here</a>",
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "class": f"form-control field-color-dcsp font-dcsp border-info { c.FORM_ELEMENTS_MAX_WIDTH }",
                "autocomplete": "current-password",
            }
        ),
    )

    def clean(self) -> dict[str, str]:
        """ """
        cleaned_data: dict[str, str] = self.cleaned_data
        setup_choice: str = cleaned_data["setup_choice"]
        external_repository_url_import: str = cleaned_data[
            "external_repository_url_import"
        ]

        if setup_choice == "start_anew":
            cleaned_data.pop("external_repository_url_import", None)
            cleaned_data.pop("external_repository_username_import", None)
            cleaned_data.pop("external_repository_password_token_import", None)
        else:
            validated_response(
                self,
                "external_repository_url_import",
                not " " in external_repository_url_import,
                "Spaces are not allowed in a url",
            )

        return cleaned_data


class ProjectSetupStepTwoForm(forms.Form):
    """ProjectSetupStepTwoForm

    Fields:
        project_name_import_start_anew: name of the project
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialise the fields for the second step of project setup"""
        super(ProjectSetupStepTwoForm, self).__init__(*args, **kwargs)
        groups_list: QuerySet[Any] = ProjectGroup.objects.none()
        choices_list_1: list[Any] = []
        choices_list_2: list[Any] = []

        self.fields["project_name"] = forms.CharField(
            label="Project name",
            required=True,
            widget=forms.TextInput(
                attrs={
                    "class": f"form-control field-color-dcsp font-dcsp border-info { c.FORM_ELEMENTS_MAX_WIDTH }",
                    "autocomplete": "off",
                }
            ),
        )

        self.fields["description"] = forms.CharField(
            required=True,
            widget=forms.Textarea(
                attrs={
                    "class": f"form-control field-color-dcsp font-dcsp border-info { c.FORM_ELEMENTS_MAX_WIDTH }",
                    "rows": 3,
                    "autocomplete": "off",
                }
            ),
        )

        self.fields["access"] = forms.ChoiceField(
            choices=ViewAccess.choices,
            initial=ViewAccess.PUBLIC,
            widget=forms.Select(
                attrs={
                    "class": c.SELECT_STYLE,
                    "onChange": "change_visibility()",
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


"""# TODO - might be able to remove this form
class InstallationForm(forms.Form):
    For managing initial installation parameters

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
        default_external_repository_token_SA: GitHub token.
        code_location_I: Location of code. This is used when DCSP is integrated
                         into another code base.
    

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
                "class": c.SELECT_STYLE,
                "onChange": "change_visibility()",
            }
        ),
    )

    github_username_SA = forms.CharField(
        label="Github username",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": f"form-control field-color-dcsp font-dcsp border-info { c.FORM_ELEMENTS_MAX_WIDTH }",
                "autocomplete": "github-username",
            }
        ),
    )

    email_SA = forms.CharField(
        label="Email",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": f"form-control field-color-dcsp font-dcsp border-info { c.FORM_ELEMENTS_MAX_WIDTH }",
            }
        ),
    )

    github_organisation_SA = forms.CharField(
        label="Github organisation (leave blank if you are / will be storing the documents under your own username on Github)",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": f"form-control field-color-dcsp font-dcsp border-info { c.FORM_ELEMENTS_MAX_WIDTH }",
            }
        ),
    )

    github_repo_SA = forms.CharField(
        label="Github repository (current or soon to be created)",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": f"form-control field-color-dcsp font-dcsp border-info { c.FORM_ELEMENTS_MAX_WIDTH }",
            }
        ),
    )

    default_external_repository_token_SA = forms.CharField(
        label="Github token (<a href='https://github.com/settings/tokens/new' target='_blank'>get Github token</a>)",
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "class": f"form-control field-color-dcsp font-dcsp border-info { c.FORM_ELEMENTS_MAX_WIDTH }",
                "autocomplete": "github-token",
            }
        ),
    )

    code_location_I = forms.CharField(
        label="Local location of source code (related to the git repository root)",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": f"form-control field-color-dcsp font-dcsp border-info { c.FORM_ELEMENTS_MAX_WIDTH }",
            }
        ),
    )

    def clean(self) -> dict:
        Cleans data from InstallationForm

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
        
        cleaned_data: Any = self.cleaned_data
        installation_type: str = cleaned_data["installation_type"]
        github_username: str = cleaned_data["github_username_SA"]
        email: str = cleaned_data["email_SA"]
        github_organisation: str = cleaned_data["github_organisation_SA"]
        github_repo: str = cleaned_data["github_repo_SA"]
        default_external_repository_token: str = cleaned_data["default_external_repository_token_SA"]
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
                validated_response(
                    self,
                    "email_SA",
                    False,
                    f"Email address '{ email }' is invalid. No other processing of credentials will be checked until this error is fixed.",
                )
            else:
                validated_response(
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
                    default_external_repository_token=default_external_repository_token,
                )

                credentials_check_results = gc.check_github_credentials()
                validated_response(
                    self,
                    "github_username_SA",
                    bool(credentials_check_results["github_username_exists"]),
                    "Username does not exist on Github",
                )

                validated_response(
                    self,
                    "github_organisation_SA",
                    bool(
                        credentials_check_results["github_organisation_exists"]
                    ),
                    "Organisation does not exist on Github",
                )

                validated_response(
                    self,
                    "github_repo_SA",
                    bool(credentials_check_results["repo_exists"]),
                    "Repository does not exist",
                )

                validated_response(
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
            validated_response(
                self,
                "code_location_I",
                not " " in code_location,
                "Invalid path",
            )
        return cleaned_data"""


class TemplateSelectForm(forms.Form):
    """Template selection form

    Provides available templates.

    Fields:
        template_choice: pick the template to use for hazard documentation.
    """

    def __init__(self, project_id: int, *args: Any, **kwargs: Any) -> None:
        """Initialise with available templates

        Searches in the templates folder for template sub-folders and provides
        these as options in a selection field for the user.
        """
        super(TemplateSelectForm, self).__init__(*args, **kwargs)
        project: project_builder.ProjectBuilder = (
            project_builder.ProjectBuilder(project_id)
        )
        templates: list[str] = project.document_templates_get()
        template: str = ""
        choices_list: list[Any] = []

        if len(templates) == 0:
            raise Exception("No templates found in templates folder!")

        for template in templates:
            choices_list.append([template, template])

        CHOICES = tuple(choices_list)

        self.fields["template_choice"] = forms.ChoiceField(
            choices=CHOICES,
            widget=forms.Select(attrs={"class": c.SELECT_STYLE}),
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

    def __init__(self, project_id: int, *args: Any, **kwargs: Any) -> None:
        """Find placeholders and initialises web app fields

        Searches for placeholders in markdown files in doc folder and creates
        fields for each.
        """
        super(PlaceholdersForm, self).__init__(*args, **kwargs)
        placeholders: dict[str, str] = {}
        placeholder: str = ""
        value: str = ""

        project_build = project_builder.ProjectBuilder(project_id)
        placeholders = project_build.get_placeholders()

        for (
            placeholder,
            value,
        ) in placeholders.items():
            self.fields[placeholder] = forms.CharField(
                required=False,
                initial=value,
                widget=forms.TextInput(
                    attrs={
                        "class": "form-control field-color-dcsp font-dcsp border-info"
                    }
                ),
            )

    def clean(self) -> dict[str, Any]:
        """Checks placeholders for invalid characters

        Current invalid characters are "{}\"'"
        """
        INVALID_CHARACTERS: str = "{}\"'"
        cleaned_data: dict[str, Any] = self.cleaned_data.copy()
        key: str = ""
        value: str = ""

        for key, value in cleaned_data.items():
            validated_response(
                self,
                key,
                not any(illegal in value for illegal in INVALID_CHARACTERS),
                f"Invalid character in placeholder '{ key }' - '{ value }'",
            )

        return cleaned_data


class DocumentNewForm(forms.Form):
    """ """

    def __init__(self, project_id: int, *args: Any, **kwargs: Any) -> None:
        """Initialisation of the selection field

        Searches the docs folder and searches for markdown files, noting the
        any subfolders. These are then provided as a selection field.
        """
        super(DocumentNewForm, self).__init__(*args, **kwargs)
        self.project_id: int = project_id

        self.fields["document_name"] = forms.CharField(
            help_text="This must be a valid path and end in '.md'",
            required=True,
            widget=forms.TextInput(
                attrs={
                    "class": "form-control field-color-dcsp font-dcsp border-info"
                }
            ),
        )

    def clean(self) -> dict[str, Any]:
        """Checks if a valid path"""
        cleaned_data: dict[str, Any] = self.cleaned_data
        document_name: str = cleaned_data["document_name"]
        valid_1: bool = False
        valid_2: bool = False
        error_messages_1: list[str] = []
        error_messages_2: list[str] = []

        (
            valid_1,
            error_messages_1,
        ) = valid_partial_linux_path(document_name)

        project = project_builder.ProjectBuilder(self.project_id)
        (
            valid_2,
            error_messages_2,
        ) = project.document_create_check(document_name)

        errors_all = list_to_string(error_messages_1 + error_messages_2)

        validated_response(
            self,
            "document_name",
            valid_1 and valid_2,
            f"The supplied path is invalid due to: { errors_all }",
        )

        return cleaned_data


class DocumentUpdateForm(forms.Form):
    """Text edit area of selected markdown file

    Provides the raw markdown for the selected file.

    Fields:
        document_name: TODO
        document_markdown: raw markdown of the file with placeholders evident in double
                 curley brackets (eg {{ placeholder }})
    """

    def __init__(self, project_id: int, *args: Any, **kwargs: Any) -> None:
        """Initialisation of the selection field

        Searches the docs folder and searches for markdown files, noting the
        any subfolders. These are then provided as a selection field.
        """
        super(DocumentUpdateForm, self).__init__(*args, **kwargs)
        self.project_id: int = project_id
        document_name: str = ""
        docs_dir: str = f"{ c.PROJECTS_FOLDER }project_{ project_id }/{ c.CLINICAL_SAFETY_FOLDER }docs/"
        initial_data: Mapping[str, str] = self.initial or {}
        document_markdown: str = ""

        # TODO - perhaps a message that docs folder is missing should be presented.

        if initial_data == {}:
            for _, __, files in os.walk(docs_dir):
                for name in files:
                    if fnmatch(name, "*.md"):
                        document_name = name
                        loop_exit = True
                        break
                if loop_exit:
                    break

            with open(
                f"{ docs_dir }{ document_name }",
                "r",
            ) as file:
                document_markdown = file.read()
                document_markdown = document_markdown.replace("\n", "\r\n")

        else:
            document_name = initial_data.get("document_name", "")
            document_markdown = initial_data.get("document_markdown", "")

        CHOICES = tuple(md_files(self.project_id))

        self.fields["document_name"] = forms.ChoiceField(
            choices=CHOICES,
            initial=document_name,
            widget=forms.Select(
                attrs={
                    "class": c.SELECT_STYLE,
                    "onChange": "form.submit()",
                }
            ),
        )

        self.fields["document_markdown"] = forms.CharField(
            label="Markdown view",
            initial=document_markdown,
            widget=forms.Textarea(
                attrs={
                    "style": "width:100%; overflow:hidden;",
                    "class": "form-control field-color-dcsp font-dcsp border-info",
                    "onkeyup": "update_web_view()",
                }
            ),
        )

        self.fields["document_name_initial"] = forms.CharField(
            initial=document_name,
            widget=forms.HiddenInput(attrs={}),
        )

        self.fields["document_markdown_initial"] = forms.CharField(
            initial=document_markdown,
            widget=forms.HiddenInput(attrs={}),
        )

    def clean(self) -> dict[str, Any]:
        """ """
        cleaned_data: dict[str, Any] = self.cleaned_data
        """document_name: str = cleaned_data["document_name"]"""
        # document_markdown: str = cleaned_data["document_markdown"]
        # md_files_list: list = md_files(self.project_id)
        # doc_build: Builder
        linter_results: dict[str, str] = {}

        """validated_response(
            self,
            "document_markdown",
            document_name in md_files_list,
            "Internal error with document_name (hidden attribute)",
        )"""

        """# Not, mkdocs directory is not provided as an argument. But this should
        # Be ok just for linting.
        doc_build = Builder()
        linter_results = doc_build.linter_text(document_markdown)
        results_readable: str = """

        """ if linter_results["overal"] != "pass":
            self.add_error("document_markdown", "Error with syntax in markdown file")"""

        """for key, value in linter_results.items():
            if value == "pass":
                results_readable += f"{ key }: {value }</br>"
            else:
                results_readable += f"<u>{ key }: {value }</u></br>"

        validated_response(
            self,
            "document_markdown",
            linter_results["overal"] == "pass",
            f"There is invalid syntax in the markdown file, please correct:</br> { results_readable }",
        )"""

        return cleaned_data


class EntryUpdateForm(forms.Form):
    def __init__(
        self,
        project_id: int,
        entry_type: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initialise the entry form

        Gets available entry labels for entry form

        Fields:
            horizontal_line: a horizontal line across the web page.
            TODO:TODO
        """
        super(EntryUpdateForm, self).__init__(*args, **kwargs)
        project: project_builder.ProjectBuilder = (
            project_builder.ProjectBuilder(project_id)
        )
        entry_template: list[dict[str, Any]] = project.entry_file_read(
            entry_type
        )

        field_type: str = ""
        help_text: str = ""
        self.labels_for_calculations: dict[str, str] = {}
        labels_for_calculations: dict[str, str] = {}
        self.calculation_field: list[dict[str, Any]] = []

        for index, field in enumerate(entry_template):
            help_text = ""

            if field["field_type"] == "horizontal_line":
                self.fields[field["heading"]] = forms.CharField(
                    label="",
                    required=False,
                    widget=forms.HiddenInput(attrs={}),
                )

            elif field["field_type"] == "icon":
                self.fields[field["heading"]] = forms.CharField(
                    label="",
                    required=False,
                    widget=forms.HiddenInput(attrs={}),
                )

            elif field["field_type"] == "code":
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
                            "class": c.SELECT_STYLE,
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
                            "class": "selectpicker font-dcsp border-info",
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
                            "class": "form-control field-color-dcsp font-dcsp border-info no-pointer-cursor",
                            "readonly": "readonly",
                        }
                    ),
                )

                # Match only labels that are required for this calculation field
                for label in field["labels"]:
                    for (
                        key,
                        value,
                    ) in self.labels_for_calculations.items():
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
                    # initial="test data",
                    required=False,
                    widget=forms.Textarea(
                        attrs={
                            "class": "form-control field-color-dcsp font-dcsp border-info",
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


class HazardCommentForm(forms.Form):
    """Form for adding comments to a preexisting hazard

    A simple form to add a comment to a pre-existing hazard.

    Fields:
        comment: a new comment for the hazard.
    """

    comment = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control field-color-dcsp font-dcsp border-info",
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
                "class": "form-control field-color-dcsp font-dcsp border-info",
                "style": "height: 150px",
            }
        ),
    )
