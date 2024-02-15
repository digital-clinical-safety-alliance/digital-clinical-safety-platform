"""
This module contains the code for performing a specific task.
"""

from fnmatch import fnmatch
from typing import Any, Callable
from functools import wraps
from pathlib import Path

from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# TODO - may not work in production
from django.contrib.staticfiles.views import serve

from .models import (
    Project,
)

from app.functions.projects_builder import ProjectBuilder
import app.functions.constants as c
import app.views as views


def _project_access(
    request: HttpRequest, project_id: str
) -> tuple[bool, HttpResponse, int, int]:
    """Wrapper around page views"""
    project_id_int: int = 0
    projects: list[dict[str, Any]] = []
    context: dict[str, Any] = {}
    project_builder: ProjectBuilder
    project_config: dict[str, Any] = {}
    setup_step: int = 0
    docs_dir: str = ""

    if not (request.method == "POST" or request.method == "GET"):
        return (
            False,
            render(request, "405.html", views.std_context(), status=405),
            0,
            0,
        )

    if not project_id.isdigit():
        return (
            False,
            render(request, "404.html", views.std_context(), status=404),
            0,
            0,
        )

    project_id_int = int(project_id)

    if not Project.objects.filter(id=project_id_int).exists():
        messages.error(request, f"'Project { project_id }' does not exist")
        return (
            False,
            render(request, "404.html", views.std_context(), status=404),
            0,
            0,
        )

    projects = views.user_accessible_projects(request)

    if not any(project["doc_id"] == project_id_int for project in projects):
        messages.error(request, "You do not have access to this project!")
        return (
            False,
            render(
                request, "403.html", context | views.std_context(), status=403
            ),
            0,
            0,
        )

    project_builder = ProjectBuilder(project_id_int)
    project_config = project_builder.configuration_get()
    setup_step = project_config["setup_step"]

    if setup_step >= 2:
        docs_dir = f"{ c.PROJECTS_FOLDER }project_{ project_id }/{ c.CLINICAL_SAFETY_FOLDER }docs/"
        if not Path(docs_dir).is_dir():
            messages.error(
                request,
                f"The safety documents directory for 'project { project_id }' "
                f"does not exist. It should exist at "
                f"'{ c.CLINICAL_SAFETY_FOLDER }docs/'. Please create this folder and "
                "try again. This can either be done via setup process and importing"
                "a safety template or via the external repository and then imported.",
            )
            return (
                False,
                render(
                    request,
                    "500.html",
                    views.std_context(),
                    status=500,
                ),
                0,
                0,
            )

    return (
        True,
        HttpResponse(),
        project_id_int,
        setup_step,
    )


# Rest of the code...
def project_access(
    func: (
        Callable[[HttpRequest, int, int], HttpResponse]
        | Callable[[HttpRequest, int, int, str], HttpResponse]
        | Callable[[HttpRequest, int, int, str, str], HttpResponse]
    ),
) -> Callable[[HttpRequest, str], HttpResponse]:
    """A decorator for project access (on the dynamic site)

    Restricts access to views based on if the logged in user has access to the
    project.

    functions:
        wrapper: checks if user has access
    """

    @login_required
    @wraps(func)
    def wrapper(
        request: HttpRequest, project_id: str, *args: Any, **kwargs: Any
    ) -> Any:
        """Wrapper around page views

        Args:
            request (HttpRequest): the request
            project_id (str): datanase primary key for project.

        Returns:
            HttpResponse | Callable: error responses or runs function.
        """
        passed: bool = False
        project_id_int: int = 0
        httpresponse: HttpResponse = HttpResponse()
        setup_step: int = 0

        passed, httpresponse, project_id_int, setup_step = _project_access(
            request, project_id
        )

        if not passed:
            return httpresponse

        return func(request, project_id_int, setup_step, *args, **kwargs)

    return wrapper
