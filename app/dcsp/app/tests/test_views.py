from django.test import TestCase
from django.urls import reverse
from django.conf import settings
import time as t
import sys
import os


import app.functions.constants as c

settings.ENV_LOCATION = c.TESTING_ENV_PATH_DJANGO
settings.MKDOCS_LOCATION = c.TESTING_MKDOCS
settings.MKDOCS_DOCS_LOCATION = c.TESTING_MKDOCS_DOCS
settings.TESTING = True
settings.START_AFRESH = True


sys.path.append(c.FUNCTIONS_APP)

from env_manipulation import ENVManipulator
from app.views import std_context
import app.tests.data_views as d


def setup_level(self, level):
    if not isinstance(level, int):
        raise ValueError("Supplied level is not convertable into an integer")

    if level > 3 or level < 1:
        raise ValueError("Supplied level must be between 1 and 3")

    if level >= 1:
        response = self.client.post("/", d.INSTALLATION_POST_GOOD_DATA)
        self.assertEqual(response.status_code, 200)
    if level >= 2:
        response1 = self.client.post("/", d.TEMPLATE_GOOD_DATA)
        self.assertEqual(response1.status_code, 200)
    if level >= 3:
        response3 = self.client.post("/", d.PLACEHOLDERS_GOOD_DATA)
        self.assertEqual(response3.status_code, 200)
    return


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

    # TODO
    def test_installation_post_good_data_message(self):
        pass

    def test_installation_post_bad_data(self):
        response = self.client.post("/", d.INSTALLATION_POST_BAD_DATA)
        self.assertContains(response, "Invalid URL")
        self.assertEqual(response.status_code, 200)

    def test_template_select_get(self):
        setup_level(self, 1)
        response1 = self.client.get("/")
        self.assertEqual(response1.status_code, 200)

    def test_template_select_get_correct_template(self):
        setup_level(self, 1)
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "template_select.html")

    def test_template_post_good_data(self):
        self.test_installation_post_good_data()
        response = self.client.post("/", d.TEMPLATE_GOOD_DATA)
        self.assertEqual(response.status_code, 200)

    # TODO
    def test_template_post_good_data_message(self):
        pass

    def test_template_post_bad_data(self):
        self.test_installation_post_good_data()
        response = self.client.post("/", d.TEMPLATE_BAD_DATA)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select a valid choice.")

    def test_template_post_correct_template(self):
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

    # TODO
    def test_post_good_data_message(self):
        pass

    # TODO - no cleaning check for placeholders yet, but will need a test
    # function if cleaning is implemented.


# TODO: Need to see if could use IndexViewTest to reduce code here
class EditMDViewTest(TestCase):
    def setUp(self):
        self.client.get("/start_afresh")

    def test_edit_md_wrong_method(self):
        response = self.client.post("/", d.INSTALLATION_POST_GOOD_DATA)
        self.assertEqual(response.status_code, 200)
        response1 = self.client.post("/", d.TEMPLATE_GOOD_DATA)
        self.assertEqual(response1.status_code, 200)
        response2 = self.client.delete("/edit_md")
        self.assertEqual(response2.status_code, 405)

    def test_edit_md_setup_step_none(self):
        self.client.post("/start_afresh")
        response = self.client.get("/edit_md")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("index"))

    def test_edit_md_setup_step_1(self):
        # TODO: #1 why is this not working!
        """IVT = IndexViewTest()
        IVT.test_installation_post_good_data()"""
        response = self.client.post("/", d.INSTALLATION_POST_GOOD_DATA)
        self.assertEqual(response.status_code, 200)
        response1 = self.client.get("/edit_md")
        self.assertEqual(response1.status_code, 302)
        self.assertRedirects(response1, reverse("index"))

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


class SavedMdTest(TestCase):
    def setUp(self):
        self.client.get("/start_afresh")

    def test_edit_md_wrong_method(self):
        response = self.client.delete("/saved_md")
        self.assertEqual(response.status_code, 405)

    def test_get_setup_None(self):
        response = self.client.get("/saved_md")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("edit_md"), target_status_code=302
        )

    def setup_2_initialise(self):
        response = self.client.post("/", d.INSTALLATION_POST_GOOD_DATA)
        self.assertEqual(response.status_code, 200)
        response1 = self.client.post("/", d.TEMPLATE_GOOD_DATA)
        self.assertEqual(response1.status_code, 200)

    def test_get_setup_2_good_data(self):
        self.setup_2_initialise()
        response2 = self.client.post("/saved_md", d.SAVED_MD_GOOD_DATA)
        self.assertEqual(response2.status_code, 200)
        f = open(d.SAVED_MD_TEMPLATE_FILE_PATH, "r")
        self.assertEqual(f.read(), d.SAVED_MD_GOOD_DATA["text_md"])

    def test_get_setup_2_good_data_correct_template(self):
        self.setup_2_initialise()
        response2 = self.client.post("/saved_md", d.SAVED_MD_GOOD_DATA)
        self.assertEqual(response2.status_code, 200)
        self.assertTemplateUsed(response2, "edit_md.html")

    # TODO
    def test_post_good_data_message(self):
        pass

    def test_post_bad_filename(self):
        self.setup_2_initialise()
        response2 = self.client.post("/saved_md", d.SAVED_MD_BAD_FILENAME)
        self.assertEqual(response2.status_code, 500)

    # TODO - there is no markdown validity checker yet. But will need a test when in place


class LogHazardTest(TestCase):
    def setUp(self):
        self.client.get("/start_afresh")

    def test_bad_method(self):
        response = self.client.delete("/log_hazard")
        self.assertEqual(response.status_code, 405)

    def test_get(self):
        pass

    def test_get_correct_template(self):
        response = self.client.get("/log_hazard")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "log_hazard.html")

    def test_post(self):
        pass


class MkdocsRedirect(TestCase):
    def setUp(self):
        self.client.get("/start_afresh")

    def test_bad_method(self):
        response = self.client.delete("/mkdoc_redirect/home")
        self.assertEqual(response.status_code, 405)

    def test_get_home(self):
        response = self.client.get("/mkdoc_redirect/home")
        self.assertEqual(response.status_code, 302)


class StdContect(TestCase):
    def setUp(self):
        self.client.get("/start_afresh")

    def test_setup_None(self):
        self.assertEqual(std_context(), d.STD_CONTEXT_SETUP_NONE)

    def test_setup_1(self):
        setup_level(self, 1)
        self.assertEqual(std_context(), d.STD_CONTEXT_SETUP_1)

    def test_setup_2(self):
        setup_level(self, 2)
        self.assertEqual(std_context(), d.STD_CONTEXT_SETUP_2)

    def test_setup_3(self):
        setup_level(self, 3)
        self.assertEqual(std_context(), d.STD_CONTEXT_SETUP_3)


class StartAfreshEnabled(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.start_fresh_previous_state = settings.START_AFRESH
        settings.START_AFRESH = True
        cls.testing_previous_state = settings.TESTING
        settings.TESTING = True
        cls.env_location_previous = settings.ENV_LOCATION
        settings.ENV_LOCATION = c.TESTING_ENV_PATH_DJANGO

    def setUp(self):
        self.client.get("/start_afresh")

    def test_bad_method(self):
        response = self.client.delete("/start_afresh")
        self.assertEqual(response.status_code, 405)

    def test_start_afresh_with_nothing_running(self):
        if not os.path.isfile(c.TESTING_ENV_PATH_DJANGO):
            self.assertTrue(False)

        f = open(c.TESTING_ENV_PATH_DJANGO, "r")
        self.assertEqual(f.read(), "")

    def test_start_afresh_with_everything_running(self):
        setup_level(self, 3)
        if not os.path.isfile(c.TESTING_ENV_PATH_DJANGO):
            self.assertTrue(False)

        f = open(c.TESTING_ENV_PATH_DJANGO, "r")
        self.assertEqual(f.read(), d.START_AFRESH_SETUP_3)
        self.client.get("/start_afresh")
        f = open(c.TESTING_ENV_PATH_DJANGO, "r")
        self.assertEqual(f.read(), "")

    @classmethod
    def tearDownClass(cls):
        settings.START_AFRESH = cls.start_fresh_previous_state
        settings.TESTING = cls.testing_previous_state
        settings.ENV_LOCATION = cls.env_location_previous


class StartAfreshDisabled(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.start_fresh_previous_state = settings.START_AFRESH
        settings.START_AFRESH = False
        cls.testing_previous_state = settings.TESTING
        settings.TESTING = False

    def setUp(self):
        settings.TESTING = True
        self.client.get("/start_afresh")
        settings.TESTING = False

    def test_bad_method(self):
        response = self.client.delete("/start_afresh")
        self.assertEqual(response.status_code, 405)

    def test_start_afresh_with_nothing_running(self):
        if not os.path.isfile(c.TESTING_ENV_PATH_DJANGO):
            self.assertTrue(False)

        f = open(c.TESTING_ENV_PATH_DJANGO, "r")
        self.assertEqual(f.read(), "")

    def test_start_afresh_with_everything_running(self):
        setup_level(self, 3)
        if not os.path.isfile(c.TESTING_ENV_PATH_DJANGO):
            self.assertTrue(False)

        f = open(c.TESTING_ENV_PATH_DJANGO, "r")
        self.assertEqual(f.read(), d.START_AFRESH_SETUP_3)
        self.client.get("/start_afresh")
        f = open(c.TESTING_ENV_PATH_DJANGO, "r")
        self.assertEqual(f.read(), d.START_AFRESH_SETUP_3)

    @classmethod
    def tearDownClass(cls):
        settings.START_AFRESH = cls.start_fresh_previous_state
        settings.TESTING = cls.testing_previous_state


class Custum404(TestCase):
    def test_(self):
        pass


class Custum405(TestCase):
    def test_(self):
        pass
