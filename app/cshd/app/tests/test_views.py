from django.test import TestCase
from django.urls import reverse
from django.conf import settings
import time as t
import sys


import app.functions.constants as c

settings.ENV_LOCATION = c.TESTING_ENV_PATH_DJANGO
settings.MKDOCS_LOCATION = c.TESTING_MKDOCS
settings.MKDOCS_DOCS_LOCATION = c.TESTING_MKDOCS_DOCS
settings.TESTING = True


sys.path.append(c.FUNCTIONS_APP)

from env_manipulation import ENVManipulator

import app.tests.data_views as d


# TODO - add some messages tests
class IndexViewTest(TestCase):
    def setUp(self):
        self.client.get("/start_afresh")

    def test_wrong_method(self):
        response = self.client.delete("/")
        self.assertEqual(response.status_code, 405)

    def test_installation_setup_get(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_installation_setup_get_correct_template(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "installation_method.html")

    def test_installation_post_good_data(self):
        response = self.client.post("/", d.INSTALLATION_POST_GOOD_DATA)
        self.assertEqual(response.status_code, 200)

    def test_installation_post_correct_template(self):
        response = self.client.post("/", d.INSTALLATION_POST_GOOD_DATA)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "template_select.html")

    def test_installation_post_bad_data(self):
        response = self.client.post("/", d.INSTALLATION_POST_BAD_DATA)
        self.assertContains(response, "Invalid URL")
        self.assertEqual(response.status_code, 200)

    def test_template_select_get(self):
        self.test_installation_post_good_data()
        response1 = self.client.get("/")
        self.assertEqual(response1.status_code, 200)

    def test_template_select_get_correct_template(self):
        self.test_installation_post_good_data()
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "template_select.html")

    def test_template_post_good_data(self):
        self.test_installation_post_good_data()
        response = self.client.post("/", d.TEMPLATE_GOOD_DATA)
        self.assertEqual(response.status_code, 200)

    def test_template_post_bad_data(self):
        self.test_installation_post_good_data()
        response = self.client.post("/", d.TEMPLATE_BAD_DATA)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select a valid choice.")

    def test_template_post__correct_template(self):
        self.test_installation_post_good_data()
        response = self.client.post("/", d.TEMPLATE_GOOD_DATA)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "placeholders_show.html")

    def test_placeholders_get(self):
        self.test_template_post_good_data()
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_placeholders_get_correct_template(self):
        self.test_template_post_good_data()
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "placeholders_show.html")

    def test_placeholders_post_good_data(self):
        self.test_template_post_good_data()
        response = self.client.post("/", d.PLACEHOLDERS_GOOD_DATA)
        self.assertEqual(response.status_code, 200)

    def test_placeholders_post_good_data(self):
        self.test_template_post_good_data()
        response = self.client.post("/", d.PLACEHOLDERS_GOOD_DATA)
        self.assertEqual(response.status_code, 200)

    # TODO - no cleaning check for placeholders yet, but will need a test
    # function if cleaning is implemented.


# TODO: Need to see if could use IndexViewTest to reduce code here
class EditMDViewTest(TestCase):
    def setUp(self):
        self.client.post("/start_afresh")

    def test_edit_md_wrong_method(self):
        response = self.client.post("/", d.INSTALLATION_POST_GOOD_DATA)
        self.assertEqual(response.status_code, 200)
        response1 = self.client.post("/", d.TEMPLATE_GOOD_DATA)
        self.assertEqual(response1.status_code, 200)
        response2 = self.client.delete("/edit_md")
        self.assertEqual(response2.status_code, 405)

    def test_edit_md_setup_step_none(self):
        response = self.client.get("/edit_md")
        self.assertEqual(response.status_code, 200)

    def test_edit_md_setup_step_1(self):
        """IVT = IndexViewTest()
        IVT.test_installation_post_good_data()"""
        response = self.client.post("/", d.INSTALLATION_POST_GOOD_DATA)
        self.assertEqual(response.status_code, 200)
        response1 = self.client.get("/edit_md")
        self.assertEqual(response1.status_code, 200)

    def test_edit_md_setup_step_2(self):
        response = self.client.post("/", d.INSTALLATION_POST_GOOD_DATA)
        self.assertEqual(response.status_code, 200)
        response1 = self.client.post("/", d.TEMPLATE_GOOD_DATA)
        self.assertEqual(response1.status_code, 200)
        response2 = self.client.get("/edit_md")
        self.assertEqual(response2.status_code, 200)

    def test_edit_md_correct_template(self):
        response = self.client.post("/", d.INSTALLATION_POST_GOOD_DATA)
        self.assertEqual(response.status_code, 200)
        response1 = self.client.post("/", d.TEMPLATE_GOOD_DATA)
        self.assertEqual(response1.status_code, 200)
        response2 = self.client.get("/edit_md")
        # print(response2.context["MDFileSelect"])
        self.assertEqual(response2.status_code, 200)
        self.assertTemplateUsed(response2, "edit_md.html")

    def test_edit_md_post_good_data(self):
        response = self.client.post("/", d.INSTALLATION_POST_GOOD_DATA)
        self.assertEqual(response.status_code, 200)
        response1 = self.client.post("/", d.TEMPLATE_GOOD_DATA)
        self.assertEqual(response1.status_code, 200)
        response2 = self.client.post("/edit_md", d.EDIT_MD_GOOD_DATA)
        self.assertEqual(response2.status_code, 200)
        self.assertTemplateUsed(response2, "edit_md.html")

    # TODO - no clean method for edit_md form yet, will need testing for this once implemented wth bad data


"""class SavedMdTest(TestCase):
    def test_wrong_method(self):
        pass

    def test_get(self):
        pass

    def test_post_good_data(self):
        # file updated
        pass

    def test_post_good_data_message(self):
        pass

    def test_post_bad_data(self):
        # bad file name
        pass


class LogHazardTest(TestCase):
    def test_bad_method(self):
        pass

    def test_get(self):
        pass

    def test_post(self):
        pass


class MkdocsRedirect(TestCase):
    def test_bad_method(self):
        pass

    def test_get_home(self):
        pass

    def test_get_test_template1(self):
        pass


class StdContect(TestCase):
    def test_mkdocs_running(self):
        pass

    def test_mkdocs_not_running(self):
        pass

    def test_docs_available(self):
        pass

    def test_docs_not_available(self):
        pass


class StartAfresh(TestCase):
    def test_wrong_method(self):
        pass

    def test_start_afresh_with_everything_running(self):
        pass

    def test_start_afresh_with_nothing_running(self):
        pass"""


"""class Custum404(TestCase):
    def test_(self):
        pass


class Custum405(TestCase):
    def test_(self):
        pass"""
