from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth.models import User
from app.models import (
    UserProfile,
    Project,
    ProjectGroup,
    UserProjectAttribute,
    ViewAccess,
)

from app.functions import constants as c


class UserProfileTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            id=1,
            username="testuser",
            password="testpassword",
            first_name="John",
            last_name="Doe",
        )

        UserProfile.objects.create(
            id=1,
            user=user,
            default_external_repository_username="testusername",
            default_external_repository_host="testhost",
            default_external_repository_token="testtoken",
        )

    def test_user_profile_creation(self):
        user = User.objects.get(id=1)
        user_profile = UserProfile.objects.get(id=1)
        self.assertEqual(user_profile.user, user)
        self.assertEqual(
            user_profile.default_external_repository_username, "testusername"
        )
        self.assertEqual(
            user_profile.default_external_repository_host, "testhost"
        )
        self.assertEqual(
            user_profile.default_external_repository_token, "testtoken"
        )

    def test_string_output(self):
        user = User.objects.get(id=1)
        user_profile = UserProfile.objects.get(id=1)
        expected_object_name = f"{user.last_name}, {user.first_name}"
        self.assertEqual(str(user_profile), expected_object_name)


class UserProfileMetaTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_b = User.objects.create(
            username="B", first_name="User", last_name="B"
        )
        UserProfile.objects.create(user=user_b)

        user_a = User.objects.create(
            username="A", first_name="User", last_name="A"
        )
        UserProfile.objects.create(user=user_a)

    def test_ordering(self):
        users = UserProfile.objects.all()
        self.assertEqual(users[0].user.last_name, "A")
        self.assertEqual(users[1].user.last_name, "B")


class ProjectTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user
        cls.user = User.objects.create(username="testuser")

        # Create two projects
        Project.objects.create(name="B Project", owner=cls.user)
        Project.objects.create(name="A Project", owner=cls.user)

    def test_string_representation(self):
        project = Project.objects.get(name="A Project")
        self.assertEqual(str(project), "A Project - testuser")

    def test_ordering(self):
        projects = Project.objects.all()
        self.assertEqual(projects[0].name, "A Project")
        self.assertEqual(projects[1].name, "B Project")

    def test_access_choices(self):
        # Test that creating a project with a valid choice for 'access' works
        Project.objects.create(
            name="Test Project 1",
            owner=self.user,
            access=ViewAccess.PRIVATE,
        )

        # Test that creating a project with an invalid choice for 'access' raises a ValidationError
        project = Project(
            name="Test Project 2", owner=self.user, access="invalid"
        )

        with self.assertRaises(ValidationError):
            project.full_clean()
