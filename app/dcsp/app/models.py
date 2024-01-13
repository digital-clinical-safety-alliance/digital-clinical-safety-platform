"""Django Models 

"""

import os
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from datetime import date


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        verbose_name=_("user"),
        on_delete=models.CASCADE,
    )

    default_github_username = models.CharField(
        max_length=256, blank=True, null=True
    )

    default_github_host = models.CharField(
        max_length=256, blank=True, null=True
    )

    github_token = models.CharField(max_length=256, blank=True, null=True)


class Project(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True)

    description = models.TextField(max_length=1000, blank=True, null=True)

    owner = models.ForeignKey(
        User,
        related_name="owner_foreign_key",
        verbose_name=_("owner"),
        on_delete=models.CASCADE,
    )

    member = models.ManyToManyField(
        User, related_name="member_many_to_many", blank=True
    )

    user_interaction = models.ManyToManyField(
        User,
        related_name="last_updated_by_user_many_to_many",
        through="UserProjectAttribute",
        blank=True,
    )

    external_repo_url = models.CharField(max_length=256, blank=True, null=True)

    external_repo_username = models.CharField(
        max_length=256, blank=True, null=True
    )

    external_repo_password_token = models.CharField(
        max_length=256, blank=True, null=True
    )

    def __str__(self):
        return f"{ self.id } - { self.owner } - { self.name }"

    class Meta:
        ordering = ["id"]


class UserProjectAttribute(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    last_accessed = models.DateTimeField(auto_now=True)

    repo_username = models.CharField(max_length=256, blank=True, null=True)

    repo_password_token = models.CharField(
        max_length=256, blank=True, null=True
    )

    class Meta:
        unique_together = ("user", "project")

    # TODO #38 - audit functionality


class ProjectGroup(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True)

    member = models.ManyToManyField(User, blank=True)

    project_access = models.ManyToManyField(Project, blank=True)

    def __str__(self):
        return f"{ self.name }"
