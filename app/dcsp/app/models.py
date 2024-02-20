"""Django Models 

"""

# mypy: disable-error-code="type-arg"
# TODO - need to figure out how to give the right type hints below

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

import app.functions.constants as c


class UserProfile(Model):
    user: OneToOneField = OneToOneField(
        User,
        verbose_name=_("User"),
        on_delete=CASCADE,
    )

    default_external_repository_username: CharField = CharField(
        verbose_name=_("Default GitHub Username"),
        max_length=256,
        blank=True,
        null=True,
    )

    default_external_repository_host: CharField = CharField(
        verbose_name=_("Default Expernal Repository Host"),
        max_length=256,
        blank=True,
        null=True,
    )

    default_external_repository_token: CharField = CharField(
        verbose_name=_("Default External Repository Token"),
        max_length=256,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.user.last_name}, {self.user.first_name}"

    class Meta:
        ordering = ["user__last_name"]


class ViewAccess(TextChoices):
    PRIVATE = "PR", "private"
    MEMBERS = "ME", "members"
    PUBLIC = "PU", "public"


class Project(Model):
    name: CharField = CharField(
        verbose_name=_("Project name"), max_length=256, blank=True, null=True
    )

    description: TextField = TextField(
        verbose_name=_("Project description"),
        max_length=1000,
        blank=True,
        null=True,
    )

    owner: ForeignKey = ForeignKey(
        User,
        verbose_name=_("owner"),
        related_name="owner_foreign_key",
        on_delete=CASCADE,
    )

    member: ManyToManyField = ManyToManyField(
        User,
        verbose_name=_("Member"),
        related_name="member_many_to_many",
        blank=True,
    )

    user_interaction: ManyToManyField = ManyToManyField(
        User,
        verbose_name=_("User interaction"),
        related_name="last_updated_by_user_many_to_many",
        through="UserProjectAttribute",
        blank=True,
    )

    access = CharField(
        verbose_name=_("View access"),
        max_length=10,
        choices=ViewAccess.choices,
        default=ViewAccess.PUBLIC,
    )

    last_modified: DateTimeField = DateTimeField(
        verbose_name=_("Last modified"), blank=True, null=True
    )

    last_built: DateTimeField = DateTimeField(
        verbose_name=_("Last built"), blank=True, null=True
    )

    build_output: TextField = TextField(
        verbose_name=_("Build output"), max_length=5000, blank=True, null=True
    )

    external_repository_url: CharField = CharField(
        verbose_name=_("External repository URL"),
        max_length=256,
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return f"{ self.name } - { self.owner }"

    class Meta:
        ordering = ["name"]
        """constraints = [
            CheckConstraint(
                name="%(app_label)s_%(class)s_access_valid",
                check=Q(access__in=ViewAccess.values),
            )
        ]"""


class UserProjectAttribute(Model):
    user: ForeignKey = ForeignKey(User, on_delete=CASCADE)

    project: ForeignKey = ForeignKey(Project, on_delete=CASCADE)

    last_accessed: DateTimeField = DateTimeField(auto_now=True)

    repo_username: CharField = CharField(max_length=256, blank=True, null=True)

    repo_password_token = CharField(max_length=256, blank=True, null=True)

    class Meta:
        unique_together = ("user", "project")

    # TODO #38 - audit functionality


class ProjectGroup(Model):
    name: CharField = CharField(max_length=256, blank=True, null=True)

    member: ManyToManyField = ManyToManyField(User, blank=True)

    project_access: ManyToManyField = ManyToManyField(Project, blank=True)

    def __str__(self) -> str:
        return f"{ self.name }"
