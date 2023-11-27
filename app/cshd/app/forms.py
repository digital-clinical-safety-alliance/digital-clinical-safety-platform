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

    def clean_github_repo_SA(self) -> str:
        github_repo_SA = self.cleaned_data["github_repo_SA"]
        if " " in github_repo_SA:
            raise forms.ValidationError("Invalid URL")
        return github_repo_SA


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
        cleaned_data: Any = self.cleaned_data
        illegal: str = ""
        key: str = ""
        value: str = ""

        for key, value in cleaned_data.items():
            if any(illegal in value for illegal in INVALID_CHARACTERS):
                raise forms.ValidationError(
                    f"Invalid character in placeholder value - '{ value }'"
                )
        else:  # TODO - remove todo??
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
        required=False,
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
            required=False,
            widget=forms.TextInput(
                attrs={
                    "class": "nhsuk-input nhsuk-input--width-30",
                }
            ),
        )

        self.fields["body"] = forms.CharField(
            required=False,
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
