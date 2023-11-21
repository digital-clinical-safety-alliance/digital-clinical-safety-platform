"""Testing of forms

"""

from django.test import TestCase


import os
from fnmatch import fnmatch
import sys


import app.functions.constants as c

sys.path.append(c.FUNCTIONS_APP)
from docs_builder import Builder

from app.forms import (
    InstallationForm,
    TemplateSelectForm,
    PlaceholdersForm,
    MDFileSelect,
    MDEditForm,
)


INSTALLATION_FORM_GOOD_DATA: dict[str, str] = {
    "installation_type": "SA",
    "github_repo_SA": "aaaf",
    "github_username_SA": "a",
    "github_token_SA": "x",
    "code_location_I": "s",
}

TemplateSelectForm
TEMPLATE_SELECT_FORM_GOOD_DATA: dict[str, str] = {"template_choice": "DCB0129"}


class InstallationFormTest(TestCase):
    def test_good_url(self):
        form = InstallationForm(data=INSTALLATION_FORM_GOOD_DATA)
        self.assertTrue(form.is_valid())


class TemplateSelectForm(TestCase):
    def template_choice_good_data(self):
        form = TemplateSelectForm(data=TEMPLATE_SELECT_FORM_GOOD_DATA)
        self.assertTrue(form.is_valid())


class PlaceholdersFormTest(TestCase):
    def test_test(self):
        form = TemplateSelectForm(data=)
        self.assertTrue(form.is_valid())


class MDEditFormTest(TestCase):
    def test_test(self):
        form = MDEditForm()
        self.assertTrue(form.is_valid())
