"""Admin view for site

"""

from django.contrib import admin
from .models import (
    UserProfile,
    Project,
    ProjectGroup,
    UserProjectAttribute,
)
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django import forms
from django.forms.widgets import TextInput

admin.site.unregister(User)  # Necessary


class UserProfileInline(admin.TabularInline):
    model = UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


class UserProjectAttributeInline(admin.TabularInline):
    model = UserProjectAttribute
    extra = 1  # Number of empty forms to display
    readonly_fields = ["last_accessed"]  # Make 'last_accessed' field read-only


class ProjectAdmin(admin.ModelAdmin):
    inlines = [UserProjectAttributeInline]


admin.site.register(Project, ProjectAdmin)

admin.site.register(ProjectGroup)

admin.site.register(UserProjectAttribute)
