"""Manages the views for the dcsp app

This is part of a Django web server app that is used to create a static site in
mkdocs. It utilises several other functions git, github, env manipulation and 
mkdocs

Functions:
    index: placeholder
    member_landing_page: placeholder
    build: placeholder
    document_update: placeholder
    document_update: placeholder
    document_new: placeholder
    entry_update: placeholder
    hazard_comment: placeholder
    hazards_open: placeholder
    mkdoc_redirect: placeholder
    upload_to_github: placeholder
    setup_step: placeholder
    std_context: placeholder
    start_afresh: placeholder
    custom_404: placeholder
    custom_405: placeholder
"""
import os
import sys
from fnmatch import fnmatch
import shutil
from typing import Any, TextIO
from datetime import datetime
import json
from functools import wraps
import difflib

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpRequest
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils.functional import SimpleLazyObject
from django.db.models.query import QuerySet
from django.db.models import Q, F
from django.utils import timezone


# TODO - may not work in production
from django.contrib.staticfiles.views import serve

from .models import (
    User,
    UserProfile,
    Project,
    ProjectGroup,
    UserProjectAttribute,
)

import app.functions.constants as c
from app.functions.constants import EnvKeysPH
from app.functions.projects_builder import ProjectBuilder

# TODO can this be removed?
sys.path.append(c.FUNCTIONS_APP)
from app.functions.env_manipulation import ENVManipulator
from app.functions.mkdocs_control import MkdocsControl
from app.functions.docs_builder import Builder
from app.functions.git_control import GitController
from app.functions.general_fuctions import snake_to_title


from .forms import (
    ProjectSetupInitialForm,
    ProjectSetupStepTwoForm,
    InstallationForm,
    TemplateSelectForm,
    PlaceholdersForm,
    DocumentNewForm,
    DocumentUpdateForm,
    MDFileSelectForm,
    EntryUpdateForm,
    UploadToGithubForm,
    HazardCommentForm,
)


def project_access(func):
    """A decorator for project access

    functions:
        wrapper: tests correct state before getting setup_step and then passing
                 function.
    """

    @wraps(func)
    def wrapper(request: HttpRequest, project_id: str, *args, **kwargs):
        """Wraps around the page function.

        Args:
            request (HttpRequest):
            project_id (str): datanase primary key for project

        Returns:
            HttpResponse | func: error responses or runs func.
        """
        project_id_int: int = 0
        projects: dict = {}
        project_builder: ProjectBuilder
        project_config: dict
        setup_step: int = 0

        if not (request.method == "POST" or request.method == "GET"):
            return render(request, "405.html", std_context(), status=405)

        if not project_id.isdigit():
            return render(request, "404.html", std_context(), status=404)

        project_id_int = int(project_id)

        if not Project.objects.filter(id=project_id_int).exists():
            messages.error(
                request,
                f"'Project { project_id }' does not exist",
            )
            return render(request, "404.html", std_context(), status=404)

        projects = user_accessible_projects(request)

        if not any(
            project["doc_id"] == project_id_int for project in projects
        ):
            context = {"message": "You do not have access to this project!"}
            return render(
                request, "403.html", context | std_context(), status=403
            )

        project_builder = ProjectBuilder(project_id_int)
        project_config = project_builder.configuration_get()
        setup_step = project_config["setup_step"]

        return func(request, project_id_int, setup_step, *args, **kwargs)

    return wrapper


# TODO #39 needs unit testing
def index(request: HttpRequest) -> HttpResponse:
    """Landing page for DCSP app

    Landing page for DCSP app

    Args:
        request (HttpRequest): request from user

    Returns:
        HttpResponse: for loading the correct webpage
    """
    context: dict[str, Any] = {
        "NON_EXISTENT_VARIABLE": "NON_EXISTENT_VARIABLE"
    }

    if request.method != "GET":
        return render(request, "405.html", std_context(), status=405)

    if request.user.is_authenticated:
        return redirect("/member")

    return render(request, "index.html", context | std_context())


# TODO needs unit testing
@login_required
def member_landing_page(request: HttpRequest) -> HttpResponse:
    """Landing page for members

    If no documents related to user, will help user set this up. If user has
    access to documents, these will be displayed here.

    Args:
        request (HttpRequest): request from user

    Returns:
        HttpResponse: for loading the correct webpage
    """
    context: dict[str, Any] = {}
    # projects
    viewed_documents: bool = False

    if request.method != "GET":
        return render(request, "405.html", std_context(), status=405)

    projects = user_accessible_projects(request)

    viewed_documents = any(
        record.get("doc_last_accessed") is not None for record in projects
    )

    context = {
        "available_projects": projects,
        "viewed_documents": viewed_documents,
    }

    return render(request, "member_landing_page.html", context | std_context())


@login_required
def start_new_project(request: HttpRequest) -> HttpResponse:
    """Setup a new project

    Import a current git repository or start fresh. A clinical safety document
    folder will be added if not already present.

    Args:
        request (HttpRequest): request from user

    Returns:
        HttpResponse: for loading the correct webpage
    """
    context: dict[str, Any] = {}
    setup_step: int = 0
    inputs: dict = {}
    inputs_GUI: dict = {}
    groups_list: list = []
    members_list: list = []
    members_string: str = ""
    members_list_fullnames: list = []
    # new_project
    project_builder: ProjectBuilder
    final_message: str = ""
    build_status: bool = False
    build_errors: str = ""

    if not (request.method == "POST" or request.method == "GET"):
        return render(request, "405.html", std_context(), status=405)

    if request.method == "GET":
        setup_step = 1
        request.session.pop("repository_type", None)
        request.session["project_setup_step"] = setup_step
        request.session["inputs"] = {}

        context = {
            "setup_step": setup_step,
            "form": ProjectSetupInitialForm(),
        }

        return render(
            request, "start_new_project.html", context | std_context()
        )

    elif request.method == "POST":
        setup_step = request.session.get("project_setup_step", None)
        if setup_step == None:
            return redirect("/start_new_project")
        if setup_step == 1:
            form = ProjectSetupInitialForm(request.POST)
            if form.is_valid():
                setup_step = 2
                request.session["project_setup_step"] = setup_step
                request.session[
                    "project_setup_1_form_data"
                ] = form.cleaned_data
                setup_choice = form.cleaned_data["setup_choice"]

                if setup_choice == "import":
                    external_repo_url = form.cleaned_data[
                        "external_repo_url_import"
                    ]

                    if "github.com/" in external_repo_url:
                        # print("A Github repository")
                        request.session["inputs"]["repository_type"] = "github"
                    elif "gitlab.com/" in external_repo_url:
                        # print("A Gitlab repository")
                        request.session["inputs"]["repository_type"] = "gitlab"
                    elif "gitbucket" in external_repo_url:
                        # print("A GitBucket repository")
                        request.session["inputs"][
                            "repository_type"
                        ] = "gitbucket"
                    else:
                        # print("another type of repository")
                        request.session["inputs"]["repository_type"] = "other"

                    context = {
                        "setup_choice": snake_to_title(setup_choice),
                        "form": ProjectSetupStepTwoForm(),
                        "setup_step": setup_step,
                    }

                    return render(
                        request,
                        "start_new_project.html",
                        context | std_context(),
                    )

                elif setup_choice == "start_anew":
                    context = {
                        "setup_choice": snake_to_title(setup_choice),
                        "form": ProjectSetupStepTwoForm(),
                        "setup_step": setup_step,
                    }

                    return render(
                        request,
                        "start_new_project.html",
                        context | std_context(),
                    )
                else:
                    return render(
                        request, "500.html", std_context(), status=500
                    )

            else:
                context = {
                    "form": form,
                    "setup_step": setup_step,
                }

                return render(
                    request,
                    "start_new_project.html",
                    context | std_context(),
                )

        elif setup_step == 2:
            form = ProjectSetupStepTwoForm(request.POST)
            if form.is_valid():
                setup_step = 3
                request.session["project_setup_step"] = setup_step

                request.session[
                    "project_setup_2_form_data"
                ] = form.cleaned_data

                inputs = request.session["project_setup_1_form_data"].copy()
                inputs.update(request.session["project_setup_2_form_data"])
                setup_choice = request.session["project_setup_1_form_data"][
                    "setup_choice"
                ]

                if setup_choice == "start_anew":
                    inputs.pop("external_repo_url_import")
                    inputs.pop("external_repo_username_import")
                    inputs.pop("external_repo_password_token_import")
                elif (
                    request.session["project_setup_1_form_data"][
                        "setup_choice"
                    ]
                    != "import"
                ):
                    return render(
                        request, "500.html", std_context(), status=500
                    )

                request.session["inputs"].update(inputs)

                for key, value in inputs.items():
                    key = key.replace("import", "")
                    key = key.replace("start_anew", "")
                    key = snake_to_title(key)

                    if key == "Setup choice":
                        inputs_GUI[key] = snake_to_title(value)

                    elif key == "Groups":
                        groups_list = list(
                            ProjectGroup.objects.filter(
                                id__in=value
                            ).values_list("name", flat=True)
                        )
                        inputs_GUI[key] = ", ".join(groups_list)
                        if inputs_GUI[key] == "":
                            inputs_GUI[key] = "<i>none selected</i>"

                    elif key == "Members":
                        members_list = User.objects.filter(
                            id__in=value
                        ).values("id", "first_name", "last_name")
                        members_list_fullnames = [
                            f"{member['first_name']} {member['last_name']}"
                            for member in members_list
                        ]
                        inputs_GUI[key] = ", ".join(members_list_fullnames)
                        if inputs_GUI[key] == "":
                            inputs_GUI[key] = "<i>none selected</i>"

                    elif any(
                        keyword in key for keyword in ["password", "token"]
                    ):
                        key = key.replace("password token", "password / token")
                        inputs_GUI[key] = "***"
                    else:
                        inputs_GUI[key] = value

                context = {
                    "setup_choice": snake_to_title(setup_choice),
                    "inputs_GUI": inputs_GUI,
                    "setup_step": setup_step,
                    "CLINICAL_SAFETY_FOLDER": c.CLINICAL_SAFETY_FOLDER,
                }

                return render(
                    request,
                    "start_new_project.html",
                    context | std_context(),
                )

        elif setup_step == 3:
            setup_step = 4
            request.session["project_setup_step"] = setup_step

            project_builder = ProjectBuilder()
            build_status, build_errors = project_builder.new_build(request)

            if not build_status:
                messages.error(
                    request,
                    f"There was an error with the data you supplied: '{ build_errors }'. Please correct these errors.",
                )

                context = {
                    "setup_step": setup_step,
                    "title": "Error with data supplied",
                    "restart_button": "yes",
                }

                return render(
                    request,
                    "start_new_project.html",
                    context | std_context(),
                )

            inputs = request.session["inputs"]
            messages.success(
                request,
                f"You have successfully created the project titled '{inputs['project_name']}'.",
            )

            # TODO - need to update this with a real destination for the documents
            document_url = f"setup_documents/{ request.session['project_id'] }"

            request.session.pop("project_id")

            context = {
                "setup_step": setup_step,
                "document_url": document_url,
                "title": "Complete",
                # "CLINICAL_SAFETY_FOLDER": c.CLINICAL_SAFETY_FOLDER,
            }

            return render(
                request,
                "start_new_project.html",
                context | std_context(),
            )

        elif setup_step == 4:
            return redirect("/start_new_project")

    # Should never really get here, but added for mypy
    return render(request, "500.html", std_context(), status=500)


@login_required
@project_access
def setup_documents(
    request: HttpRequest, project_id: int, setup_step: int
) -> HttpResponse:
    """Build page, carrying out steps to initialise a static site

    Acting as a single page application, this function undertakes several
    steps to set up the mkdocs static site. The state of the installation is
    stored in an .env file as 'setup_step'. There are 4 steps in the
    installation process (labelled steps None, 1, 2 and 3).

    - None: Initial step for the installation process. No value stored for the
    step_step in the .env file. During this step the user is asked if they want
    a 'stand alone' or an 'integrated' installation.
        - Stand alone: this setup is very the DCSP app is only used for hazard
          documentation, with no source code integration. Basically the version
          control is managed by the DCSP app.
        - Integrated: the DCSP is integrated into an already version controlled
          source base, for example along side already written source code.
    - 1: In this step the user is asked to chose a template for the static
         website.
    - 2: In this step the user is asked to enter values for placeholders for the
         static site.
    - 3: The static site is now built and mkdocs has been started and the site
         should be visible.

    Args:
        request (HttpRequest): request from user

    Returns:
        HttpResponse: for loading the correct webpage
    """
    project_id_int: int = 0
    project_builder: ProjectBuilder
    context: dict[str, Any] = {}
    placeholders: dict[str, str] = {}
    template_choice: str = ""
    form: InstallationForm | TemplateSelectForm | PlaceholdersForm
    mkdocs: MkdocsControl

    project_id_int = int(project_id)
    project_builder = ProjectBuilder(project_id_int)
    time_now = timezone.now()

    # TODO this should really be started at '1' eg step 1.
    if setup_step == 0:
        if request.method == "GET":
            context = {
                "form": TemplateSelectForm(project_id_int),
                "project_id": project_id_int,
            }

            return render(
                request,
                "template_select.html",
                context | std_context(project_id),
            )

        elif request.method == "POST":
            form = TemplateSelectForm(project_id_int, request.POST)  # type: ignore[assignment]
            if form.is_valid():
                project_builder.configuration_set("setup_step", 1)
                template_choice = form.cleaned_data["template_choice"]

                project_build = ProjectBuilder(project_id_int)

                project_build.copy_templates(template_choice)

                messages.success(
                    request,
                    f"{ template_choice } template initiated",
                )

                context = {
                    "form": PlaceholdersForm(project_id_int),
                    "project_id": project_id_int,
                }

                return render(
                    request,
                    "placeholders_show.html",
                    context | std_context(project_id),
                )
            else:
                context = {
                    "form": form,
                    "project_id": project_id_int,
                }

                return render(
                    request,
                    "template_select.html",
                    context | std_context(project_id),
                )

    elif setup_step >= 1:
        if request.method == "GET":
            context = {
                "form": PlaceholdersForm(project_id_int),
                "project_id": project_id_int,
                "project_name": Project.objects.get(id=project_id).name,
            }
            # return render(request, "test.html")

            return render(
                request,
                "placeholders_show.html",
                context | std_context(project_id),
            )

        elif request.method == "POST":
            form = PlaceholdersForm(project_id_int, data=request.POST)  # type: ignore[assignment]
            if form.is_valid():
                project_builder.configuration_set("setup_step", 2)

                placeholders = project_builder.get_placeholders()

                for p in placeholders:
                    placeholders[p] = form.cleaned_data[p]

                project_builder.save_placeholders(placeholders)

                project = get_object_or_404(Project, id=project_id)
                project.last_modified = time_now
                project.save()

                context = {
                    "project_id": project_id,
                    "project_name": Project.objects.get(id=project_id).name,
                }

                return render(
                    request,
                    "placeholders_saved.html",
                    context | std_context(project_id),
                )
            else:
                context = {
                    "form": form,
                    "project_id": project_id_int,
                    "project_name": Project.objects.get(id=project_id).name,
                }

                return render(
                    request,
                    "placeholders_show.html",
                    context | std_context(project_id),
                )

    # Should never really get here, but added for mypy
    return render(request, "500.html", std_context(), status=500)


@login_required
@project_access
def project_build_asap(
    request: HttpRequest, project_id: int, setup_step: int
) -> HttpResponse:
    """ """
    context: dict[str, Any] = {}
    build_output: str = ""

    if request.method == "GET":
        context = {
            "project_id": project_id,
            "project_name": Project.objects.get(id=project_id).name,
        }

        return render(
            request,
            "project_build_asap.html",
            context | std_context(project_id),
        )
    elif request.method == "POST":
        build_output = build_documents(int(project_id), force=True)

        context = {
            "project_id": project_id,
            "build_output": build_output,
            "project_name": Project.objects.get(id=project_id).name,
        }

        return render(
            request,
            "project_build_asap.html",
            context | std_context(project_id),
        )

    # Should never really get here, but added for mypy
    return render(request, "500.html", std_context(), status=500)


@login_required
@project_access
def project_documents(
    request: HttpRequest, project_id: int, setup_step: int
) -> HttpResponse:
    """Shows the project main page

    --- TODO

    Args:
        request (HttpRequest): request from user

    Returns:
        HttpResponse: for loading the correct webpage
    """
    project: Project = Project.objects.get(id=project_id)
    members = project.member.all()
    groups: ProjectGroup = ProjectGroup.objects.filter(project_access=project)
    context: dict[str, Any] = {
        "project": project,
        "members": members,
        "groups": groups,
        "project_id": project_id,
        "project_name": project.name,
    }
    return render(
        request, "project_documents.html", context | std_context(project_id)
    )


# TODO - Need to limit who can view (perhaps private, members-only, and open access views)
@login_required
def view_docs(
    request: HttpRequest, project_id: str, doc_path: str = ""
) -> HttpResponse:
    """Functionality for  X-Accel-Redirect from django to nginx

    ---TODO

    Args:
        request (HttpRequest): request from user

    Returns:
        HttpResponse: for loading the correct webpage
    """
    context: dict[str, Any] = {}
    document_content = ""
    internal_path: str = ""
    # redirect_path
    project_id_int: int

    if project_id.isdigit():
        project_id_int = int(project_id)
    else:
        return render(request, "500.html", std_context(), status=500)

    # TODO - error if no project_id supplied, it is not an int and/or not an active project

    internal_path = os.path.join(
        "/documentation-pages", f"project_{ project_id}", doc_path
    )

    build_documents(project_id_int)

    # TODO #41 - may have to convert os.path to Path... all over the shop!
    if not os.path.isfile(
        internal_path
    ):  # and not os.path.isdir(internal_path):
        return render(request, "404.html", context=std_context(), status=404)

    if internal_path.endswith(".html"):
        file = open(internal_path, "r")
        document_content = file.read()
        context = {
            "document_content": document_content,
            "project_id": project_id,
        }
        return render(
            request,
            "document_serve.html",
            context | std_context(project_id_int),
        )
    else:
        content_type = "invalid"
        _, file_extension = os.path.splitext(internal_path)
        file_extension = file_extension.replace(".", "")

        for key, value in c.MIME_TYPES.items():
            if file_extension == key:
                content_type = value
                break

        response = HttpResponse(content_type=content_type)
        response["X-Accel-Redirect"] = internal_path
        return response

    # Should never really get here, but added for mypy
    return render(request, "500.html", std_context(), status=500)


@login_required
@project_access
def document_update(
    request: HttpRequest,
    project_id: int,
    setup_step: int,
) -> HttpResponse:
    """Function for editing of markdown files in the static site

    A webpage to allow the user to edit the markdown files used in the
    static site on mkdocs.

    Args:
        request (HttpRequest): request from user

    Returns:
        HttpResponse: for loading the correct webpage
    """
    files: list[str] = []
    name: str = ""
    md_file: str = ""
    loop_exit: bool = False
    form: MDFileSelectForm
    context: dict[str, Any] = {}
    form_fields: dict[str, str] = {}
    docs_dir: str = f"{ c.PROJECTS_FOLDER }project_{ project_id }/{ c.CLINICAL_SAFETY_FOLDER }docs/"

    if setup_step < 2:
        return redirect(f"/setup_documents/{ project_id }")

    if request.method == "GET":
        # TODO - perhaps a message that docs folder is missing should be presented.

        if not os.path.isdir(docs_dir):
            return render(request, "500.html", std_context(), status=500)

        for _, __, files in os.walk(docs_dir):
            for name in files:
                if fnmatch(name, "*.md"):
                    md_file = name
                    loop_exit = True
                    break
            if loop_exit:
                break

    elif request.method == "POST":
        form = MDFileSelectForm(project_id, data=request.POST)
        if form.is_valid():
            md_file = form.cleaned_data["document_name"]
        else:
            context = {
                "form": form,
                "project_id": project_id,
                "placeholders": placeholders(project_id),
                "nav_top": "True",
            }
            return render(
                request,
                "document_update.html",
                context | std_context(project_id),
            )

    with open(f"{ docs_dir }{ md_file }", "r") as file:
        form_fields = {
            "document_markdown": file.read(),
            "document_name": md_file,
        }

    context = {
        "MDFileSelectForm": MDFileSelectForm(
            project_id,
            initial={"document_name": md_file},
        ),
        "form": DocumentUpdateForm(project_id, initial=form_fields),
        "document_name": md_file,
        "project_id": project_id,
        "placeholders": placeholders(project_id),
        "nav_top": "True",
    }

    return render(
        request, "document_update.html", context | std_context(project_id)
    )


@login_required
@project_access
def document_new(
    request: HttpRequest, project_id: int, setup_step: int
) -> HttpResponse:
    """To create a new markdown file

    This will allow the user to create a new markdown file with subdirectories
    if required.

    Args:
        request (HttpRequest): request from user
        project_id (int): primary key of project
        setup_step (int): not used in this function
    Returns:
        HttpResponse: for loading the correct webpage
    """
    context: dict[str, Any] = {}
    form: DocumentNewForm
    project: ProjectBuilder
    valid: bool = True
    error_messages: str = ""

    if not (request.method == "GET" or request.method == "POST"):
        return render(request, "405.html", std_context(), status=405)

    if request.method == "GET":
        context = {
            "form": DocumentNewForm(project_id),
            "project_id": project_id,
        }
        return render(
            request, "document_new.html", context | std_context(project_id)
        )

    elif request.method == "POST":
        form = DocumentNewForm(project_id, request.POST)
        if form.is_valid():
            document_name_new = form.cleaned_data["document_name"]

            project = ProjectBuilder(project_id)

            project.document_create(document_name_new)

            messages.success(
                request,
                f"Document '{ document_name_new }' has been created",
            )

            context = {"form": form, "project_id": project_id}
            return render(
                request, "document_new.html", context | std_context(project_id)
            )

        else:
            context = {"form": form, "project_id": project_id}
            return render(
                request, "document_new.html", context | std_context(project_id)
            )

    # For mypy
    return render(request, "500.html", status=500)


@login_required
@project_access
def document_update(
    request: HttpRequest, project_id: int, setup_step: int
) -> HttpResponse:
    """Saves the markdown file

    If no issues are found after running the markdown file through a linter
    then the file is saved.

    Args:
        request (HttpRequest): request from user

    Returns:
        HttpResponse: for loading the correct webpage
    """
    form: DocumentUpdateForm
    document_markdown_file_read: str = ""
    document_name: str = ""
    document_markdown: str = ""
    file_path: str = ""
    file: TextIO
    context: dict[str, Any] = {}
    project: Project
    docs_dir: str = f"{ c.PROJECTS_FOLDER }project_{ project_id }/{ c.CLINICAL_SAFETY_FOLDER }docs/"

    if not os.path.isdir(docs_dir):
        return render(request, "500.html", std_context(), status=500)

    if setup_step < 2:
        return redirect(f"/setup_documents/{ project_id }")

    if request.method == "GET":
        # form = document_update_form_initialise(project_id)
        form = DocumentUpdateForm(project_id)

        context = {
            "form": form,
            "project_id": project_id,
            "placeholders": placeholders(project_id),
            "nav_top": "True",
        }

        return render(
            request, "document_update.html", context | std_context(project_id)
        )

    elif request.method == "POST":
        form = DocumentUpdateForm(project_id, request.POST)

        if form.is_valid():
            document_name_initial = form.cleaned_data["document_name_initial"]
            document_name = form.cleaned_data["document_name"]
            document_markdown_initial = form.cleaned_data[
                "document_markdown_initial"
            ]
            document_markdown = form.cleaned_data["document_markdown"]

            if document_name_initial != document_name:
                with open(f"{ docs_dir }{ document_name }", "r") as file:
                    document_markdown_file_read = file.read()
                    document_markdown_file_read = (
                        document_markdown_file_read.replace("\n", "\r\n")
                    )

                form_data = {
                    "document_name": document_name,
                    "document_markdown": document_markdown_file_read,
                }

                context = {
                    "form": DocumentUpdateForm(
                        project_id,
                        initial=form_data,
                    ),
                    "project_id": project_id,
                    "placeholders": placeholders(project_id),
                    "nav_top": "True",
                }

                return render(
                    request,
                    "document_update.html",
                    context | std_context(project_id),
                )

            elif document_markdown_initial != document_markdown:
                file_path = f"{ docs_dir }{ document_name }"

                file = open(file_path, "w")
                file.write(document_markdown)
                file.close()

                project = get_object_or_404(Project, id=project_id)
                project.last_modified = timezone.now()
                project.save()

                form_data = {
                    "document_name": document_name,
                    "document_markdown": document_markdown,
                }

                messages.success(
                    request,
                    f'Mark down file "{ document_name }" has been successfully saved',
                )

                context = {
                    "form": DocumentUpdateForm(project_id, initial=form_data),
                    "project_id": project_id,
                    "placeholders": placeholders(project_id),
                    "nav_top": "True",
                }
                return render(
                    request,
                    "document_update.html",
                    context | std_context(project_id),
                )
            else:
                messages.success(
                    request,
                    f"As no changes have been made, no save has been made",
                )
                context = {
                    "form": form,
                    "project_id": project_id,
                    "placeholders": placeholders(project_id),
                    "nav_top": "True",
                }
                return render(
                    request,
                    "document_update.html",
                    context | std_context(project_id),
                )

        else:
            context = {
                "form": form,
                "project_id": project_id,
                "placeholders": placeholders(project_id),
                "nav_top": "True",
            }
            return render(
                request,
                "document_update.html",
                context | std_context(project_id),
            )

    # For mypy
    return render(request, "500.html", status=500)


@login_required
@project_access
def entry_update(
    request: HttpRequest,
    project_id: int,
    setup_step: int,
    entry_type: str,
    id_new: str,
) -> HttpResponse:
    """Log hazards

    --- TODO

    Args:
        request (HttpRequest): request from user

    Returns:
        HttpResponse: for loading the correct webpage
    """
    context: dict[str, Any] = {"project_id": project_id}
    form: EntryUpdateForm
    project_builder: ProjectBuilder
    entry_update_outcome: bool = False

    if not (request.method == "GET" or request.method == "POST"):
        return render(request, "405.html", std_context(), status=405)

    project = ProjectBuilder(project_id)

    if id_new != "new":
        if not project.entry_exists(entry_type, id_new):
            return render(request, "404.html", std_context(), status=404)

    if request.method == "GET":
        if id_new == "new":
            context = {
                "project_id": project_id,
                "form": EntryUpdateForm(project_id),
                "MKDOCS_TEMPLATE_NUMBER_DELIMITER": c.MKDOCS_TEMPLATE_NUMBER_DELIMITER,
                "entry_type": entry_type,
                "id_new": id_new,
            }
            return render(
                request, "entry_update.html", context | std_context(project_id)
            )

        else:
            print(id_new)
            form_initial = project.form_initial("hazard", int(id_new))
            print(form_initial)
            context = {
                "project_id": project_id,
                "form": EntryUpdateForm(project_id, initial=form_initial),
                "MKDOCS_TEMPLATE_NUMBER_DELIMITER": c.MKDOCS_TEMPLATE_NUMBER_DELIMITER,
                "entry_type": entry_type,
                "id_new": id_new,
            }
            return render(
                request, "entry_update.html", context | std_context(project_id)
            )

    if request.method == "POST":
        form = EntryUpdateForm(project_id, request.POST)
        # print(request.POST)
        if form.is_valid():
            project_builder = ProjectBuilder(int(project_id))
            # print(form.cleaned_data)

            entry_update_outcome = project_builder.entry_update(
                form.cleaned_data, entry_type, id_new
            )

            context = {
                "project_id": project_id,
                "form": EntryUpdateForm(project_id),
                "entry_update_outcome": entry_update_outcome,
                "MKDOCS_TEMPLATE_NUMBER_DELIMITER": c.MKDOCS_TEMPLATE_NUMBER_DELIMITER,
                "entry_type": entry_type,
                "id_new": id_new,
            }
            return render(
                request, "entry_saved.html", context | std_context(project_id)
            )

        else:
            # TODO - need better error messaging per field
            context = {
                "form": form,
                "project_id": project_id,
                "entry_type": entry_type,
                "id_new": id_new,
            }
            return render(
                request, "entry_update.html", context | std_context(project_id)
            )

    # For mypy
    return render(request, "500.html", status=500)


@login_required
@project_access
def entry_select(
    request: HttpRequest, project_id: int, setup_step: int
) -> HttpResponse:
    """Hazard selection to edit

    Show selection of hazards that can be edited

    Args:
        request (HttpRequest): request from user
        project_id (int): primary key of the project

    Returns:
        HttpResponse: for loading the correct webpage
    """
    context: dict[str, Any] = {"project_id": project_id}
    form: EntryUpdateForm
    project_builder: ProjectBuilder
    hazards: bool = False

    if not request.method == "GET":
        return render(request, "405.html", std_context(), status=405)

    project_builder = ProjectBuilder(int(project_id))
    hazards = project_builder.hazards_all_get()

    context = {
        "project_id": project_id,
        "hazards": hazards,
    }
    return render(
        request, "entry_select.html", context | std_context(project_id)
    )


@login_required
@project_access
def entry_edit(
    request: HttpRequest, project_id: int, setup_step: int, hazard_id: str
) -> HttpResponse:
    """Hazard selection to edit

    Show selection of hazards that can be edited

    Args:
        request (HttpRequest): request from user
        project_id (int): primary key of the project

    Returns:
        HttpResponse: for loading the correct webpage
    """
    context: dict[str, Any] = {"project_id": project_id}
    form: EntryUpdateForm
    project_builder: ProjectBuilder
    hazards: bool = False
    project: ProjectBuilder
    form_initial: dict

    if not (request.method == "GET" or request.method == "POST"):
        return render(request, "405.html", std_context(), status=405)

    # TODO need to check if hazard_id exists

    if request.method == "GET":
        print(hazard_id)
        project = ProjectBuilder(project_id)
        form_initial = project.form_initial("hazard", hazard_id)

        print(form_initial)
        context = {
            "project_id": project_id,
            "form": EntryUpdateForm(project_id, initial=form_initial),
            "MKDOCS_TEMPLATE_NUMBER_DELIMITER": c.MKDOCS_TEMPLATE_NUMBER_DELIMITER,
        }
        return render(
            request, "entry_edit.html", context | std_context(project_id)
        )

    # For mypy
    return render(request, "500.html", status=500)


@login_required
def hazard_comment(request: HttpRequest, hazard_number: "str") -> HttpResponse:
    """Adds a comment to an issue

    If an issue is available, will add a comment on GitHub

    Args:
        request (HttpRequest): request from user

    Returns:
        HttpResponse: for loading the correct webpage
    """
    gc: GitController
    hazards_open_full: list[dict[str, Any]] = []
    hazard: dict[str, Any] = {}
    hazard_open: dict = {}
    form: HazardCommentForm
    context: dict[str, Any] = {}

    if not (request.method == "GET" or request.method == "POST"):
        return render(request, "405.html", std_context(), status=405)

    try:
        int(hazard_number)
    except ValueError:
        messages.error(
            request,
            f"hazard_number '{hazard_number }' is not valid",
        )
        return render(request, "400.html", std_context(), status=400)

    if request.method == "GET":
        gc = GitController(
            github_repo=settings.GITHUB_REPO,
            env_location=settings.ENV_LOCATION,
        )
        hazards_open_full = gc.hazards_open()

        for hazard in hazards_open_full:
            if hazard["number"] == int(hazard_number):
                hazard_open = hazard.copy()
                break

        if not hazard_open:
            messages.error(
                request,
                f"hazard_number '{hazard_number }' is not valid",
            )
            return render(request, "400.html", std_context(), status=400)

        context = {
            "hazard_open": hazard_open,
            "form": HazardCommentForm(
                initial={"comment": c.TEMPLATE_HAZARD_COMMENT}
            ),
            "hazard_number": hazard_number,
        }
        return render(
            request, "hazard_comment.html", context | std_context(project_id)
        )

    if request.method == "POST":
        form = HazardCommentForm(request.POST)
        if form.is_valid():
            comment = form.cleaned_data["comment"]
            gc = GitController()
            # TODO - need error handling here
            gc.add_comment_to_hazard(
                hazard_number=int(hazard_number), comment=comment
            )
            messages.success(
                request,
                f"Hazard '{ hazard_number }' updated.",
            )
            context = {"form": LogHazardForm()}
            return render(
                request,
                "hazard_comment.html",
                context | std_context(project_id),
            )
        else:
            context = {"form": form}
            return render(
                request,
                "hazard_comment.html",
                context | std_context(project_id),
            )

    # Should never really get here, but added for mypy
    return render(request, "500.html", std_context(), status=500)


@login_required
# TODO - testing needed
def hazards_open(request: HttpRequest) -> HttpResponse:
    """Title

    Description

    Args:
        request (HttpRequest): request from user

    Returns:
        HttpResponse: for loading the correct webpage
    """
    context: dict[str, Any] = {}
    gc: GitController
    hazards_open: list[dict] = []

    if not (request.method == "GET" or request.method == "POST"):
        return render(request, "405.html", std_context(), status=405)

    if request.method == "GET":
        # TODO need to check github credentials are valid
        gc = GitController()
        hazards_open = gc.hazards_open()
        context = {"hazards_open": hazards_open}

        return render(request, "hazards_open.html", context | std_context())

    if request.method == "POST":
        return HttpResponse("POST handling not yet built")

    # Should never really get here, but added for mypy
    return render(request, "500.html", std_context(), status=500)


@login_required
def mkdoc_redirect(request: HttpRequest, path: str) -> HttpResponse:
    """Title

    Description

    Args:
        request (HttpRequest): request from user
        path (str): path after domain url
    Returns:
        HttpResponse: for loading the correct webpage
    """
    mkdocs: MkdocsControl
    host_url: str = request.get_host().split(":")[0]

    if not request.method == "GET":
        return render(request, "405.html", std_context(), status=405)

    mkdocs = MkdocsControl()
    mkdocs.start()

    # TODO - need message page for if mkdocs is not running

    if path == "home":
        return redirect(f"http://{ host_url }:9000")
    else:
        return redirect(f"http://{ host_url }:9000/{ path }")

    # Should never really get here, but added for mypy
    return render(request, "500.html", std_context(), status=500)


@login_required
# TODO - testing needed
def upload_to_github(request: HttpRequest) -> HttpResponse:
    """Title

    Description

    Args:
        request (HttpRequest): request from user

    Returns:
        HttpResponse: for loading the correct webpage
    """
    context: dict[str, Any] = {}
    gc: GitController
    form: UploadToGithubForm

    if not (request.method == "GET" or request.method == "POST"):
        return render(request, "405.html", std_context(), status=405)

    if request.method == "GET":
        context = {"form": UploadToGithubForm()}

        return render(
            request, "upload_to_github.html", context | std_context()
        )

    if request.method == "POST":
        form = UploadToGithubForm(request.POST)
        if form.is_valid():
            comment = form.cleaned_data["comment"]
            gc = GitController()
            # TODO - need to handle if branch is already up to date
            gc.commit_and_push(comment)
            messages.success(
                request,
                f"Uploaded to Github with a comment of '{ comment }'",
            )
            context = {"form": UploadToGithubForm()}
            return render(
                request, "upload_to_github.html", context | std_context()
            )

        else:
            context = {"form": form}
            return render(
                request, "upload_to_github.html", context | std_context()
            )

    # Should never really get here, but added for mypy
    return render(request, "500.html", std_context(), status=500)


# -----


# TODO needs testing
def setup_step_get(env_location: str = settings.ENV_LOCATION) -> int:
    """Pulls 'setup_step" from .env and converts to int

    Extracts the setup step from the local environment file and returns this as
    an integer

    Args:
        env_location (str): location of the environmental variables file.

    Returns:
        int: value of setup_step, sets to zero (0) if variable is set to empty
             string or does not exist in the env file.
    """
    env_m: ENVManipulator = ENVManipulator(env_location)
    setup_step: str | None = env_m.read("setup_step")
    return_value: int = 0

    if setup_step == None or setup_step == "":
        return_value = 0
    else:
        return_value = int(setup_step)  # type: ignore[arg-type]

    return return_value


def std_context(project_id: int = 0) -> dict[str, Any]:
    """Title

    Description

    Returns:
        dict[str,Any]: context that is comment across the different views
    """

    std_context_dict: dict[str, Any] = {}
    docs_available: bool = False
    setup_step: int = 0
    entry_templates: list[str] = []

    setup_step = setup_step_get()

    if setup_step >= 2:
        docs_available = True

    if project_id > 0:
        project = ProjectBuilder(project_id)
        entry_templates = project.entry_template_names()
        # print(entry_templates)

    std_context_dict = {
        "START_AFRESH": settings.START_AFRESH,
        "docs_available": docs_available,
        "FORM_ELEMENTS_MAX_WIDTH": c.FORM_ELEMENTS_MAX_WIDTH,
        "entry_templates": entry_templates,
    }

    return std_context_dict


# TODO - will need to also grant access to public open access documents.
def user_accessible_projects(request: HttpRequest) -> list[dict[str, str]]:
    """Finds all documents that the user has access to

    Checking against user.id, finds all documents that the user is owner of
    or a member of

    Args:
        request (HttpRequest): request from user

    Returns:
        list: a list of documents
    """
    current_user: SimpleLazyObject = request.user
    user_id: int = current_user.id
    documents_owner_member: QuerySet
    project_group: QuerySet
    documents_sorted: list = []
    documents_combined: list = []

    documents_owner_member = (
        Project.objects.values(
            doc_id=F("id"),
            doc_name=F("name"),
            doc_last_accessed=F("userprojectattribute__last_accessed"),
        )
        .filter(Q(owner=user_id) | Q(member=user_id))
        .order_by("name", "id")
        .distinct("name")
    )

    project_group = (
        ProjectGroup.objects.values(
            doc_id=F("project_access__id"),
            doc_name=F("project_access__name"),
            doc_last_accessed=F(
                "project_access__userprojectattribute__last_accessed"
            ),
        )
        .filter(member=user_id)
        .order_by("project_access__name", "project_access__id")
        .distinct("project_access__name")
    )

    for record in documents_owner_member:
        documents_combined.append(record)

    for item in project_group:
        if all(item["doc_id"] != d["doc_id"] for d in documents_combined):
            documents_combined.append(item)

    for i in range(len(documents_combined)):
        if documents_combined[i]["doc_last_accessed"] != None:
            documents_combined[i]["doc_last_accessed"] = documents_combined[i][
                "doc_last_accessed"
            ].replace(tzinfo=None)

    documents_sorted = sorted(
        documents_combined,
        key=lambda x: (x["doc_last_accessed"] or datetime.min, x["doc_id"]),
        reverse=True,
    )
    # TODO #45 - figure out why {'doc_id': None, 'doc_name': None, 'doc_last_accessed': None} and stop it.
    documents_sorted = [
        item
        for item in documents_sorted
        if item
        != {"doc_id": None, "doc_name": None, "doc_last_accessed": None}
    ]
    return documents_sorted


def placeholders(project_id: int) -> str:
    """Provides placeholders in serialised form

    This is used in the documents edit page, where markdown is converted to
    html and placeholders are converted into their corresponding values.

    Args:
        project_id (str): placeholders in a serialised form.

    Returns:
        str: placeholders in serialised form, with empty ones replaced with
    """
    if not isinstance(project_id, int):
        return ""

    if not Project.objects.filter(id=project_id).exists():
        return ""

    project_builder: ProjectBuilder = ProjectBuilder(int(project_id))
    placeholders: dict[str, str] = project_builder.get_placeholders()
    for key, value in placeholders.items():
        if value == "":
            placeholders[key] = f"[{ key } undefined]"

    return json.dumps(placeholders)


def build_documents(project_id: int, force: bool = False) -> str:
    """Build the documents static pages

    Builds the documents static pages if any documents have been modified since
    last build.

    Args:
        project_id (str): the primary key for the project
    """
    mkdocs: MkdocsControl = MkdocsControl(project_id)
    project: Project
    time_now = timezone.now()
    build_output: str = ""
    last_build: datetime
    last_modified: datetime
    preprocessor_output: str = ""

    project = get_object_or_404(Project, id=project_id)
    last_build = project.last_built
    last_modified = project.last_modified

    if (
        isinstance(last_modified, datetime)
        and isinstance(last_build, datetime)
        and not force
    ):
        if last_modified < last_build:
            return ""

    preprocessor_output = mkdocs.preprocessor()
    if preprocessor_output == "":
        return "Preprocessor error!"

    build_output = mkdocs.build()
    if build_output == "":
        return "mkdocs build error!"

    build_output = f"{ preprocessor_output } {build_output}"

    project.last_built = time_now
    project.build_output = build_output
    project.save()

    return build_output


def custom_404(request: HttpRequest, exception) -> HttpResponse:
    """Title

    Description

    Args:
        request (HttpRequest): request from user

    Returns:
        HttpResponse: for loading the correct webpage
    """

    return render(request, "404.html", context=std_context(), status=404)


def custom_405(request: HttpRequest, exception) -> HttpResponse:
    """Title

    Description

    Args:
        request (HttpRequest): request from user

    Returns:
        HttpResponse: for loading the correct webpage
    """

    return render(request, "405.html", context=std_context(), status=405)
