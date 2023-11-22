from django import forms

import os
from fnmatch import fnmatch
import sys

from typing import Any

import app.functions.constants as c

sys.path.append(c.FUNCTIONS_APP)
from docs_builder import Builder


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
        label="Github repository",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "nhsuk-input nhsuk-input--width-30",
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

    github_token_SA = forms.CharField(
        label="Github token",
        required=False,
        widget=forms.TextInput(
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

    def clean_github_repo_SA(self):
        github_repo_SA = self.cleaned_data["github_repo_SA"]
        if " " in github_repo_SA:
            raise forms.ValidationError("Invalid URL")
        return github_repo_SA


class TemplateSelectForm(forms.Form):
    doc_build: Builder
    templates: list[str] = []
    choices_list: list = []

    doc_build = Builder()
    templates = doc_build.get_templates()

    if len(templates) == 0:
        raise Exception("No templates found in templates folder!")

    for template in templates:
        choices_list.append([template, template])

    CHOICES = tuple(choices_list)

    template_choice = forms.ChoiceField(
        choices=CHOICES,
        widget=forms.Select(attrs={"class": "nhsuk-select"}),
    )


class PlaceholdersForm(forms.Form):
    def __init__(self, *args, **kwargs) -> None:
        super(PlaceholdersForm, self).__init__(*args, **kwargs)
        doc_build: Builder
        placeholder: str = ""
        value: str = ""

        doc_build = Builder()
        placeholders = doc_build.get_placeholders()

        for placeholder, value in placeholders.items():
            self.fields[placeholder] = forms.CharField(
                required=False,
                initial=value,
                widget=forms.TextInput(
                    attrs={"class": "nhsuk-input nhsuk-input--width-30"}
                ),
            )

    def clean(self):
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
        else:
            return cleaned_data


class MDFileSelect(forms.Form):
    choices_list: list = []
    # path
    # subdirs
    # files
    # name

    if not os.path.isdir(c.MKDOCS_DOCS):
        raise Exception(f"{ c.MKDOCS_DOCS } if not a valid folder location")

    for path, subdirs, files in os.walk(c.MKDOCS_DOCS):
        for name in files:
            if fnmatch(name, "*.md"):
                choices_list.append([name, name])

    CHOICES = tuple(choices_list)

    mark_down_file = forms.ChoiceField(
        choices=CHOICES,
        widget=forms.Select(
            attrs={"class": "nhsuk-select", "onChange": "form.submit()"}
        ),
    )


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
