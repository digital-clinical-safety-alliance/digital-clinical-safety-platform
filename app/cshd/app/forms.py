"""Form management for the Django dynamic site app

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
from docs_builder import Builder
from git_control import GitController


# TODO: need to set to 'required'
class InstallationForm(forms.Form):
    """For managing initial installation parameters"""

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
                "class": "nhsuk-select",
                "onChange": "change_visibility()",
            }
        ),
    )

    github_username_SA = forms.CharField(
        label="Github username",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "nhsuk-input nhsuk-input--width-30",
            }
        ),
    )

    email_SA = forms.CharField(
        label="Email",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "nhsuk-input nhsuk-input--width-30",
            }
        ),
    )

    github_organisation_SA = forms.CharField(
        label="Github organisation (leave blank if you are / will be storing the documents under your own username on Github)",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "nhsuk-input nhsuk-input--width-30",
            }
        ),
    )

    github_repo_SA = forms.CharField(
        label="Github repository (current or soon to be created)",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "nhsuk-input nhsuk-input--width-30",
            }
        ),
    )

    github_token_SA = forms.CharField(
        label="Github token (<a href='https://github.com/settings/tokens/new' target='_blank'>get Github token</a>)",
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "nhsuk-input nhsuk-input--width-30",
            }
        ),
    )

    code_location_I = forms.CharField(
        label="Local location of source code (related to the git repository root)",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "nhsuk-input nhsuk-input--width-30",
            }
        ),
    )

    def clean(self):
        cleaned_data: Any = self.cleaned_data
        installation_type: str = cleaned_data["installation_type"]
        github_username: str = cleaned_data["github_username_SA"]
        email: str = cleaned_data["email_SA"]
        github_organisation: str = cleaned_data["github_organisation_SA"]
        github_repo: str = cleaned_data["github_repo_SA"]
        github_token: str = cleaned_data["github_token_SA"]
        code_location: str = cleaned_data["code_location_I"]
        credentials_check_results: dict[str, str | bool] = {}

        if installation_type != "SA" and installation_type != "I":
            self.add_error(
                "installation_type",
                f"Error with installation type received - { installation_type }",
            )

        if github_organisation == "":
            github_organisation = github_username

        if installation_type == "SA":
            gc = GitController(
                github_username=github_username,
                email=email,
                github_organisation=github_organisation,
                github_repo=github_repo,
                github_token=github_token,
            )

            credentials_check_results = gc.check_github_credentials()

            if not credentials_check_results["github_username_exists"]:
                self.add_error(
                    "github_username_SA", "Username does not exist on Github"
                )

            if not credentials_check_results["github_organisation_exists"]:
                self.add_error(
                    "github_organisation_SA",
                    "Organisation does not exist on Github",
                )

            if not credentials_check_results["repo_exists"]:
                self.add_error("github_repo_SA", "Repository does not exist")

            if credentials_check_results["permission"] != "admin":
                self.add_error(
                    "github_repo_SA", "No admin rights to this repo"
                )

            # TODO - need to check emails are valid

            if " " in github_repo:
                self.add_error("github_repo_SA", "Invalid URL")

        if installation_type == "I":
            if " " in code_location:
                self.add_error("code_location_I", "Invalid path")

        return cleaned_data


class TemplateSelectForm(forms.Form):
    def __init__(self, *args, **kwargs) -> None:
        super(TemplateSelectForm, self).__init__(*args, **kwargs)
        doc_build: Builder
        templates: list[str] = []
        choices_list: list = []

        doc_build = Builder(settings.MKDOCS_LOCATION)
        templates = doc_build.get_templates()

        if len(templates) == 0:
            raise Exception("No templates found in templates folder!")

        for template in templates:
            choices_list.append([template, template])

        CHOICES = tuple(choices_list)

        self.fields["template_choice"] = forms.ChoiceField(
            choices=CHOICES,
            widget=forms.Select(attrs={"class": "nhsuk-select"}),
        )


class PlaceholdersForm(forms.Form):
    def __init__(self, *args, **kwargs) -> None:
        super(PlaceholdersForm, self).__init__(*args, **kwargs)
        doc_build: Builder
        placeholder: str = ""
        value: str = ""

        doc_build = Builder(settings.MKDOCS_LOCATION)
        placeholders = doc_build.get_placeholders()

        for placeholder, value in placeholders.items():
            self.fields[placeholder] = forms.CharField(
                required=False,
                initial=value,
                widget=forms.TextInput(
                    attrs={"class": "nhsuk-input nhsuk-input--width-30"}
                ),
            )

    def clean(self) -> dict:
        INVALID_CHARACTERS: str = "{}\"'"
        cleaned_data: Any = self.cleaned_data.copy()
        illegal: str = ""
        key: str = ""
        value: str = ""

        for key, value in cleaned_data.items():
            if any(illegal in value for illegal in INVALID_CHARACTERS):
                self.add_error(
                    key,
                    f"Invalid character in placeholder '{ key }' - '{ value }'",
                )

        return cleaned_data


class MDFileSelect(forms.Form):
    def __init__(self, *args, **kwargs) -> None:
        super(MDFileSelect, self).__init__(*args, **kwargs)
        choices_list: list = []
        name_with_path: str = ""
        md_files_shortened: list = []
        # path
        # subdirs
        # files
        # name

        mkdocs_path = settings.MKDOCS_DOCS_LOCATION

        if not os.path.isdir(mkdocs_path):
            raise FileNotFoundError(
                f"{ mkdocs_path } if not a valid folder location"
            )

        md_files = []
        for root, dirs, files in os.walk(mkdocs_path):
            md_files.extend(glob.glob(os.path.join(root, "*.md")))

        for file in md_files:
            md_files_shortened.append(file.replace(mkdocs_path, ""))

        for file in md_files_shortened:
            choices_list.append([file, file])
            print(file)

        # self.choices_list = choices_list
        CHOICES = tuple(choices_list)

        self.fields["mark_down_file"] = forms.ChoiceField(
            choices=CHOICES,
            widget=forms.Select(
                attrs={"class": "nhsuk-select", "onChange": "form.submit()"}
            ),
        )

    # Don't need to clean ChoiceFields apparently


class MDEditForm(forms.Form):
    document_name = forms.CharField(
        label="",
        widget=forms.HiddenInput(attrs={}),
    )

    text_md = forms.CharField(
        label="",
        required=False,
        widget=forms.Textarea(
            attrs={
                "style": "width:100%; overflow:hidden;",
                "class": "nhsuk-textarea",
                "onkeyup": "update_web_view()",
            }
        ),
    )


class LogHazardForm(forms.Form):
    def __init__(self, *args, **kwargs) -> None:
        super(LogHazardForm, self).__init__(*args, **kwargs)
        gc: GitController = GitController()
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
                    "class": "nhsuk-input nhsuk-input--width-30",
                }
            ),
        )

        self.fields["body"] = forms.CharField(
            widget=forms.Textarea(
                attrs={
                    "class": "nhsuk-input nhsuk-input--width-30",
                    "style": "height: 150px",
                }
            ),
        )

        self.fields["labels"] = forms.MultipleChoiceField(
            label="Label (press CTRL / CMD and select several as needed)",
            choices=CHOICES,
            widget=forms.SelectMultiple(
                attrs={
                    "class": "nhsuk-select",
                    "style": "height: 150px",
                }
            ),
        )


class HazardCommentForm(forms.Form):
    comment = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "nhsuk-input nhsuk-u-width-full",
                "style": "height: 500px",
                "onkeyup": "update_web_view()",
            }
        ),
    )


class UploadToGithub(forms.Form):
    comment = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "nhsuk-input nhsuk-input--width-30",
                "style": "height: 150px",
            }
        ),
    )
