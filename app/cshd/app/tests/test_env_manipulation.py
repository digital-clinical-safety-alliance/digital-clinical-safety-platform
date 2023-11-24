"""Testing of env_manipulation.py

    NB: Not built for asynchronous testing

"""

from unittest import TestCase
import sys
from dotenv import set_key, dotenv_values

import app.functions.constants as c

sys.path.append(c.FUNCTIONS_APP)
from env_manipulation import ENVManipulator

import app.tests.data_env_manipulation as d


class ENVManipulatorTest(TestCase):
    def test_init(self):
        ENVManipulator(c.TESTING_ENV_PATH)

    def test_delete(self):
        # Clears out the contents
        open(c.TESTING_ENV_PATH, "w").close()
        set_key(c.TESTING_ENV_PATH, "key1", d.VALUE1)
        set_key(c.TESTING_ENV_PATH, "key2", d.VALUE2)
        em = ENVManipulator(c.TESTING_ENV_PATH)
        self.assertTrue(em.delete("key1"))
        self.assertTrue(em.delete("key2"))

    def test_delete_key_not_present(self):
        # Clears out the contents
        open(c.TESTING_ENV_PATH, "w").close()
        set_key(c.TESTING_ENV_PATH, "key1", d.VALUE1)
        em = ENVManipulator(c.TESTING_ENV_PATH)
        self.assertFalse(em.delete("wrong_key"))

    def test_add(self):
        # Clears out the contents
        open(c.TESTING_ENV_PATH, "w").close()
        em = ENVManipulator(c.TESTING_ENV_PATH)
        em.add("key1", d.VALUE1)
        dot_values = dotenv_values(c.TESTING_ENV_PATH)
        self.assertEqual(d.VALUE1, dot_values.get("key1"))

    def test_read(self):
        # Clears out the contents
        open(c.TESTING_ENV_PATH, "w").close()
        set_key(c.TESTING_ENV_PATH, "key1", d.VALUE1)
        em = ENVManipulator(c.TESTING_ENV_PATH)
        self.assertEqual(d.VALUE1, em.read("key1"))
