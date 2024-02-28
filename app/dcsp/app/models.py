"""Django Models 

Models for the DCPS app.

Functions:
    project_timestamp: Updates the last_modified timestamp of a project if it exists.

Enumerations:
    ViewAccess: Enumeration for view access levels.

Models:
    UserProfile: A user profile model.
    Project: Project model.
    UserProjectAttribute: A user project attribute model.
    ProjectGroup: A project group model.
"""

from typing import Optional

from django.db.models import (
    Model,
    TextField,
    CharField,
    OneToOneField,
    ManyToManyField,
    ForeignKey,
    DateTimeField,
    CASCADE,
    TextChoices,
    CheckConstraint,
    Q,
)
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models.expressions import Combinable


class ViewAccess(TextChoices):
    """
    Enumeration for view access levels.

    Attributes:
    PRIVATE: Represents a private access level.
    MEMBERS: Represents an access level for members only.
    PUBLIC: Represents a public access level.
    """

    PRIVATE = "PR", "private"
    MEMBERS = "ME", "members"
    PUBLIC = "PU", "public"


def project_timestamp(project_id: int) -> bool:
    """Updates the last_modified timestamp of a project if it exists.

    Args:
        project_id (int): The id of the project to update.

    Returns:
        bool: True if the project exists and was updated, False otherwise.
    """
    project: Optional[Project] = None

    if not isinstance(project_id, int):
        raise TypeError("project_id must be an integer")

    if not Project.objects.filter(id=project_id).exists():
        return False

    project = Project.objects.get(id=project_id)
    project.last_modified = timezone.now()
    project.save()
    return True


class UserProfile(Model):
    user = OneToOneField(
        User,
        verbose_name=_("User"),
        on_delete=CASCADE,
    )

    default_external_repository_username = CharField(
        verbose_name=_("Default GitHub Username"),
        max_length=256,
        blank=True,
        null=True,
    )

    default_external_repository_host = CharField(
        verbose_name=_("Default Expernal Repository Host"),
        max_length=256,
        blank=True,
        null=True,
    )

    default_external_repository_token = CharField(
        verbose_name=_("Default External Repository Token"),
        max_length=256,
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return f"{self.user.last_name}, {self.user.first_name}"

    class Meta:
        ordering = ["user__last_name"]


class Project(Model):
    name = CharField(
        verbose_name=_("Project name"), max_length=256, blank=True, null=True
    )

    description = TextField(
        verbose_name=_("Project description"),
        max_length=1000,
        blank=True,
        null=True,
    )

    owner = ForeignKey(
        User,
        verbose_name=_("owner"),
        related_name="owner_foreign_key",
        on_delete=CASCADE,
    )

    member = ManyToManyField(
        User,
        verbose_name=_("Member"),
        related_name="member_many_to_many",
        blank=True,
    )

    access = CharField(
        verbose_name=_("View access"),
        max_length=10,
        choices=ViewAccess.choices,
        default=ViewAccess.PUBLIC,
    )

    last_modified = DateTimeField(
        verbose_name=_("Last modified"), blank=True, null=True
    )

    last_built = DateTimeField(
        verbose_name=_("Last built"), blank=True, null=True
    )

    build_output = TextField(
        verbose_name=_("Build output"), max_length=5000, blank=True, null=True
    )

    external_repository_url = CharField(
        verbose_name=_("External repository URL"),
        max_length=256,
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return f"{ self.name } - { self.owner }"

    class Meta:
        ordering = ["name"]
        constraints = [
            CheckConstraint(
                name="%(app_label)s_%(class)s_access_valid",
                check=Q(access__in=ViewAccess.values),
            )
        ]


class UserProjectAttribute(Model):
    user = ForeignKey(User, verbose_name=_("User"), on_delete=CASCADE)

    project = ForeignKey(Project, verbose_name=_("Project"), on_delete=CASCADE)

    last_accessed = DateTimeField(
        verbose_name=_("Last accessed"), auto_now=True
    )

    repository_username = CharField(
        verbose_name=_("Respository username"),
        max_length=256,
        blank=True,
        null=True,
    )

    repository_password_token = CharField(
        verbose_name=_("Respository password or token"),
        max_length=256,
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return f"{ self.user } - { self.project }"

    class Meta:
        unique_together = ("user", "project")

    # TODO #38 - audit functionality


class ProjectGroup(Model):
    name = CharField(
        verbose_name=_("Name"), max_length=256, blank=True, null=True
    )

    member = ManyToManyField(User, verbose_name=_("Member"), blank=True)

    project_access = ManyToManyField(
        Project, verbose_name=_("Project(s) with access to"), blank=True
    )

    def __str__(self) -> str:
        return f"{ self.name }"
