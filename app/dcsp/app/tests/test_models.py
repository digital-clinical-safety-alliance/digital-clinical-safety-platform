from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from django.utils import timezone
from django.db import IntegrityError
from django.test import TestCase
from django.contrib.auth.models import User
from django.test import tag

from app.models import (
    ViewAccess,
    project_timestamp,
    UserProfile,
    Project,
    ProjectGroup,
    UserProjectAttribute,
    ViewAccess,
)

from app.functions import constants as c

t = timezone.make_aware(datetime(2024, 1, 24))


class TestViewAccess(TestCase):
    def test_get_label(self):
        self.assertEqual(ViewAccess.get_label("PR"), "private")
        self.assertEqual(ViewAccess.get_label("ME"), "members")
        self.assertEqual(ViewAccess.get_label("PU"), "public")

    def test_get_label_invalid_choice(self):
        with self.assertRaises(ValueError):
            ViewAccess.get_label("invalid")


class TestProjectTimestamp(TestCase):
    def test_project_id_invalid(self):
        with self.assertRaises(TypeError) as error:
            project_timestamp("invalid")
        self.assertEqual(str(error.exception), "project_id must be an integer")

    @patch("app.models.Project")
    def test_nonexistent_project(self, mock_project):
        mock_project.objects.filter.return_value.exists.return_value = False

        result = project_timestamp(1)

        self.assertFalse(result)

        mock_project.objects.filter.assert_called_once_with(id=1)
        mock_project.objects.get.assert_not_called()

    @patch("app.models.Project")
    @patch("django.utils.timezone.now")
    def test_project_timestamp(self, mock_now, mock_project):
        mock_now.return_value = "2022-01-01T00:00:00Z"
        mock_project.objects.filter.return_value.exists.return_value = True
        mock_project.objects.get.return_value = Mock()

        result = project_timestamp(1)

        self.assertTrue(result)

        mock_project.objects.filter.assert_called_once_with(id=1)
        mock_project.objects.get.assert_called_once_with(id=1)
        mock_project.objects.get.return_value.save.assert_called_once()


class UserProfileTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            id=1,
            username="testuser",
            password="testpassword",
            first_name="John",
            last_name="Doe",
        )  # nosec B106

        UserProfile.objects.create(
            id=1,
            user=user,
            default_external_repository_username="testusername",
            default_external_repository_host="testhost",
            default_external_repository_token="testtoken",
        )  # nosec B106

    def test_fields(self):
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

    def test__str__(self):
        user = User.objects.get(id=1)
        user_profile = UserProfile.objects.get(id=1)
        expected_object_name = f"{user.last_name}, {user.first_name}"
        self.assertEqual(str(user_profile), expected_object_name)


class UserProfileOrderingTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_b = User.objects.create(
            id=1, username="bob.bates", first_name="Bob", last_name="Bates"
        )
        UserProfile.objects.create(user=user_b)

        user_a = User.objects.create(
            id=2, username="anne.anchor", first_name="Anne", last_name="Anchor"
        )
        UserProfile.objects.create(user=user_a)

    def test_ordering(self):
        users = UserProfile.objects.all()
        self.assertEqual(users[0].user.last_name, "Anchor")
        self.assertEqual(users[1].user.last_name, "Bates")


class ProjectTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(id=1, username="testuser")
        cls.member = User.objects.create(id=2, username="testmember")

        project = Project.objects.create(
            id=1,
            name="A Project",
            description="a project description",
            owner=cls.user,
            # member added below
            access=ViewAccess.PUBLIC,
            last_modified=t,
            last_built=t,
            build_output="success",
            external_repository_url="a-url",
        )

        project.member.add(cls.member)

    def test_fields(self):
        project = Project.objects.get(name="A Project")
        self.assertEqual(project.name, "A Project")
        self.assertEqual(project.description, "a project description")
        self.assertEqual(project.owner, self.user)
        self.assertEqual(project.member.first(), self.member)
        self.assertEqual(project.access, ViewAccess.PUBLIC)
        self.assertEqual(project.last_modified, t)
        self.assertEqual(project.last_built, t)
        self.assertEqual(project.build_output, "success")
        self.assertEqual(project.external_repository_url, "a-url")

    def test__str__(self):
        project = Project.objects.get(name="A Project")
        self.assertEqual(str(project), "A Project - testuser")

    def test_access_constraint_invalid(self):
        Project.objects.create(
            id=2,
            name="Test Project 2",
            owner=self.user,
            access=ViewAccess.PRIVATE,
        )

        project = Project(
            name="Test Project 2", owner=self.user, access="invalid"
        )

        with self.assertRaises(IntegrityError):
            project.save()


class ProjectOrderingTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(id=1, username="testuser")
        cls.member = User.objects.create(id=2, username="testmember")

        Project.objects.create(
            id=1,
            name="B Project",
            owner=cls.user,
        )
        project_a = Project.objects.create(
            id=2,
            name="A Project",
            owner=cls.user,
        )

        project_a.member.add(cls.member)

    def test_ordering(self):
        projects = Project.objects.all()
        self.assertEqual(projects[0].name, "A Project")
        self.assertEqual(projects[1].name, "B Project")


class UserProjectAttributeTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(id=1, username="testuser")
        cls.project = Project.objects.create(
            id=1, name="Test Project", owner=cls.user
        )
        cls.attribute = UserProjectAttribute.objects.create(
            id=1,
            user=cls.user,
            project=cls.project,
            # last_accessed is auto set
            repository_username="testusername",
            repository_password_token="testtoken",
        )  # nosec B106

    def test_fields(self):
        attribute = UserProjectAttribute.objects.get(id=1)
        self.assertEqual(attribute.user, self.user)
        self.assertEqual(attribute.project, self.project)
        current_datetime = datetime.now()
        difference = (
            timezone.make_aware(current_datetime) - attribute.last_accessed
        )
        self.assertLess(difference, timedelta(minutes=5))
        self.assertEqual(attribute.repository_username, "testusername")
        self.assertEqual(attribute.repository_password_token, "testtoken")

    def test__str__(self):
        attribute = UserProjectAttribute.objects.get(id=1)
        self.assertEqual(str(attribute), f"{self.user} - {self.project}")


class UserProjectAttributeUniqueTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.project = Project.objects.create(
            name="testproject", owner=self.user
        )

    def test_unique_together(self):
        UserProjectAttribute.objects.create(
            user=self.user, project=self.project
        )

        with self.assertRaises(IntegrityError):
            UserProjectAttribute.objects.create(
                user=self.user, project=self.project
            )


class ProjectGroupTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="testuser")

        cls.project = Project.objects.create(
            name="testproject", owner=cls.user
        )

        cls.project_group = ProjectGroup.objects.create(name="testgroup")
        cls.project_group.member.add(cls.user)
        cls.project_group.project_access.add(cls.project)

    def test_fields(self):
        project_group = ProjectGroup.objects.get(name="testgroup")
        self.assertEqual(project_group.name, "testgroup")
        self.assertEqual(list(project_group.member.all()), [self.user])
        self.assertEqual(
            list(project_group.project_access.all()), [self.project]
        )

    def test__str__(self):
        project_group = ProjectGroup.objects.get(name="testgroup")
        self.assertEqual(str(project_group), "testgroup")
