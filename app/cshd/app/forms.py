from django import forms

import os
from fnmatch import fnmatch

# TODO: need to make this a passable variable between modules.
MKDOCS_DOCS = "/cshd/mkdocs/docs"


class PlaceholdersForm(forms.Form):
    def __init__(self, placeholders, *args, **kwargs):
        super(PlaceholdersForm, self).__init__(*args, **kwargs)
        placeholder: str = ""
        value: str = ""

        for placeholder, value in placeholders.items():
            self.fields[placeholder] = forms.CharField(
                required=False,
                initial=value,
                widget=forms.TextInput(
                    attrs={"class": "nhsuk-input nhsuk-input--width-30"}
                ),
            )

    # TODO need to check no invalid values entered eg '{}'


class MDFileSelect(forms.Form):
    choices_list: list = []

    if os.path.isdir(MKDOCS_DOCS):
        for path, subdirs, files in os.walk(MKDOCS_DOCS):
            for name in files:
                if fnmatch(name, "*.md"):
                    choices_list.append([name, name])
    else:
        raise Exception(f"{ MKDOCS_DOCS } if not a valid folder location")

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


# TODO: need to set both to 'required'
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
