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
)
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

import app.functions.constants as c


class UserProfile(Model):
    user: OneToOneField = OneToOneField(
        User,
        verbose_name=_("user"),
        on_delete=CASCADE,
    )

    default_github_username: CharField = CharField(
        max_length=256, blank=True, null=True
    )

    default_github_host: CharField = CharField(
        max_length=256, blank=True, null=True
    )

    github_token: CharField = CharField(max_length=256, blank=True, null=True)


class Project(Model):
    name: CharField = CharField(max_length=256, blank=True, null=True)

    description: TextField = TextField(max_length=1000, blank=True, null=True)

    owner: ForeignKey = ForeignKey(
        User,
        related_name="owner_foreign_key",
        verbose_name=_("owner"),
        on_delete=CASCADE,
    )

    member: ManyToManyField = ManyToManyField(
        User,
        related_name="member_many_to_many",
        blank=True,
    )

    user_interaction: ManyToManyField = ManyToManyField(
        User,
        related_name="last_updated_by_user_many_to_many",
        through="UserProjectAttribute",
        blank=True,
    )

    ACCESS_CHOICES = [
        (c.StaticSiteView.PUBLIC.value, _("Public")),
        (c.StaticSiteView.MEMBERS.value, _("Members")),
        (c.StaticSiteView.PRIVATE.value, _("Private")),
    ]

    access = CharField(
        max_length=10,
        choices=ACCESS_CHOICES,
        default=c.StaticSiteView.PUBLIC.value,
    )

    last_modified: DateTimeField = DateTimeField(blank=True, null=True)

    last_built: DateTimeField = DateTimeField(blank=True, null=True)

    build_output: TextField = TextField(max_length=5000, blank=True, null=True)

    external_repo_url: CharField = CharField(
        max_length=256, blank=True, null=True
    )

    def __str__(self) -> str:
        return f"{ self.id } - { self.owner } - { self.name }"

    class Meta:
        ordering = ["id"]


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
