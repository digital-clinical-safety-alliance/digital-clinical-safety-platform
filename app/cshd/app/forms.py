from django import forms
from django.conf import settings

import os
from fnmatch import fnmatch
import sys

from typing import Any

import app.functions.constants as c

sys.path.append(c.FUNCTIONS_APP)
from docs_builder import Builder
from git_control import GitController


# TODO: need to set to 'required'
class InstallationForm(forms.Form):
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

    github_repo_SA = forms.CharField(
        label="Github repository (current or soon to be created)",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "nhsuk-input nhsuk-input--width-30",
            }
        ),
    )

    github_username_org_SA = forms.CharField(
        label="Github username / organisation (of where the documents will be / are stored)",
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
        label="Location of source code",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "nhsuk-input nhsuk-input--width-30",
            }
        ),
    )

    def clean(self):
        print("clean")
        cleaned_data: Any = self.cleaned_data
        installation_type: str = cleaned_data["installation_type"]
        github_repo: str = cleaned_data["github_repo_SA"]
        github_username_org: str = cleaned_data["github_username_org_SA"]
        github_token: str = cleaned_data["github_token_SA"]
        code_location: str = cleaned_data["code_location_I"]
        print(installation_type)

        if installation_type != "SA" and installation_type != "I":
            raise ValueError(
                f"Error with installation type received - { installation_type }"
            )

        if installation_type == "SA":
            gc = GitController(
                repo_name=github_repo,
                user_org=github_username_org,
                token=github_token,
            )

            if not gc.check_credentials():
                self.add_error(
                    "github_username_org_SA",
                    f"Credentials supplied for Github are not valid. Please try again",
                )

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
        # path
        # subdirs
        # files
        # name

        mkdocs_path = settings.MKDOCS_DOCS_LOCATION
        if not os.path.isdir(mkdocs_path):
            raise FileNotFoundError(
                f"{ mkdocs_path } if not a valid folder location"
            )

        for path, subdirs, files in os.walk(mkdocs_path):
            for name in files:
                if fnmatch(name, "*.md"):
                    choices_list.append([name, name])

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
            widget=forms.TextInput(
                attrs={
                    "class": "nhsuk-input nhsuk-input--width-30",
                }
            ),
        )

        self.fields["labels"] = forms.MultipleChoiceField(
            label="Label (press CTRL / CMD and select several as needed)",
            choices=CHOICES,
            widget=forms.SelectMultiple(
                attrs={"class": "nhsuk-select", "style": "height: 150px"}
            ),
        )
