"""Manages the views for the DCSP app

This is part of a Django web server app that is used to create a static site in
mkdocs.

Functions:
    index: landing page for DCSP app, redirects logged members.
    member_landing_page: landing page for logged in members
    start_new_project: start a new project, import from git or from clean slate.
    setup_documents: build up the documents for the static site.
    project_build_asap: build the static site ad hoc
    project_documents: main page for document editing.
    view_docs: provides static site via NGINX X-Accel-Redirect
    document_new: create a new document.
    document_update: edit of main documents.
    entry_update: create a new entry or update a preexisting one.
    entry_select: select an entry file to edit.
    upload_to_external_repository: git commit and push project to external 
                                   repository.
    std_context: provides a standard collection of values for views.
    user_accessible_projects: provides a list of projects a user has access to.
    placeholders: gets placeholders (used in document_update to convert
                  placeholders to their values).
    build_documents: builds the static webpages via mkdocs.
    custom_400: custom 400 (bad request) page.
    custom_403: custom 403 (forbidden) page.
    custom_404: custom 404 (not found) page.
    custom_500: custom 500 (internal server error) page.
"""

from fnmatch import fnmatch
from typing import Any, TextIO, Optional, Dict
from datetime import datetime
import json
from functools import wraps

from pathlib import Path

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpRequest
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db.models.query import QuerySet
from django.db.models import F
from django.db.models import QuerySet
from django.contrib.auth.models import User
from django.forms.models import model_to_dict

from app.decorators import project_access

# TODO - may not work in production
from django.contrib.staticfiles.views import serve

from .models import Project, ProjectGroup, ViewAccess, project_timestamp

import app.functions.constants as c
from app.functions.project_builder import ProjectBuilder


from app.functions.mkdocs_control import MkdocsControl
from app.functions.custom_exceptions import RepositoryAccessException
from app.functions.text_manipulation import (
    snake_to_sentense,
    kebab_to_sentense,
)


from .forms import (
    ProjectSetupInitialForm,
    ProjectSetupStepTwoForm,
    TemplateSelectForm,
    PlaceholdersForm,
    DocumentNewForm,
    DocumentUpdateForm,
    EntryUpdateForm,
    UploadToGithubForm,
)


def index(request: HttpRequest) -> HttpResponse:
    """Landing page for DCSP app

    Landing page for DCSP app

    Args:
        request (HttpRequest): request from user

    Returns:
        HttpResponse: for loading the correct webpage
    """
    context: dict[str, Any] = {
        "page_title": "Welcome to the Digital Clinical Safety Platform",
        "NON_EXISTENT_VARIABLE": "NON_EXISTENT_VARIABLE",
    }

    if request.method != "GET":
        return custom_405(request)

    if request.user.is_authenticated:
        return redirect("/member")

    return render(request, "index.html", context | std_context())


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
    projects: list[dict[str, Any]] = []
    viewed_documents: bool = False
    context: dict[str, Any] = {}

    if request.method != "GET":
        return custom_405(request)

    projects = user_accessible_projects(request)

    viewed_documents = any(
        record.get("doc_last_accessed") is not None for record in projects
    )

    context = {
        "page_title": "Safety documents",
        "available_projects": projects,
        "viewed_documents": viewed_documents,
    }

    return render(request, "member_landing_page.html", context | std_context())


@login_required
def start_new_project(  # type: ignore[return]
    request: HttpRequest,
) -> HttpResponse:
    """Setup a new project

    Create a project by importing an external git repository or starting from a
    blank slate. A clinical safety document folder will be added if not already
    present.

    Args:
        request (HttpRequest): request from user

    Returns:
        HttpResponse: for loading the correct webpage
    """
    context: dict[str, Any] = {}
    form: ProjectSetupInitialForm | ProjectSetupStepTwoForm
    setup_choice: str = ""
    external_repo_url: str = ""
    setup_step: int = 0
    inputs: dict[str, str] = {}
    project_builder: ProjectBuilder
    project_id: str = ""

    if not (request.method == "POST" or request.method == "GET"):
        return custom_405(request)

    if request.method == "GET":
        setup_step = 1
        request.session.pop("repository_type", None)
        request.session["project_setup_step"] = setup_step
        request.session["inputs"] = {}

        context = {
            "page_title": "Setup a new project",
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
                        "external_repository_url_import"
                    ]

                    if "github.com/" in external_repo_url:
                        request.session["inputs"]["repository_type"] = "github"
                    elif "gitlab.com/" in external_repo_url:
                        request.session["inputs"]["repository_type"] = "gitlab"
                    elif "gitbucket" in external_repo_url:
                        request.session["inputs"][
                            "repository_type"
                        ] = "gitbucket"
                    else:
                        request.session["inputs"]["repository_type"] = "other"

                # start_anew just jumps straight to the next step
                context = {
                    "page_title": "Setup a new project",
                    "setup_choice": snake_to_sentense(setup_choice),
                    "form": ProjectSetupStepTwoForm(),
                    "setup_step": setup_step,
                }

                return render(
                    request,
                    "start_new_project.html",
                    context | std_context(),
                )

            else:
                context = {
                    "page_title": "Setup a new project",
                    "form": form,
                    "setup_step": setup_step,
                }

                return render(
                    request,
                    "start_new_project.html",
                    context | std_context(),
                    status=400,
                )

        elif setup_step == 2:
            form = ProjectSetupStepTwoForm(request.POST)
            if form.is_valid():
                setup_choice = request.session["project_setup_1_form_data"][
                    "setup_choice"
                ]
                if setup_choice != "start_anew" and setup_choice != "import":
                    return custom_500(request)

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

                request.session["inputs"].update(inputs)

                context = {
                    "page_title": "Setup a new project",
                    "setup_choice": snake_to_sentense(setup_choice),
                    "inputs_GUI": start_new_project_step_2_input_GUI(inputs),
                    "setup_step": setup_step,
                    "CLINICAL_SAFETY_FOLDER": c.CLINICAL_SAFETY_FOLDER,
                }

                return render(
                    request, "start_new_project.html", context | std_context()
                )
            else:
                context = {"form": form, "setup_step": setup_step}

                return render(
                    request,
                    "start_new_project.html",
                    context | std_context(),
                    status=400,
                )

        elif setup_step == 3:
            setup_step = 4
            request.session["project_setup_step"] = setup_step

            project_builder = ProjectBuilder()
            try:
                project_builder.new_build(request)
            except (
                ValueError,
                KeyError,
                RepositoryAccessException,
                NotImplementedError,
                FileExistsError,
            ) as e:
                messages.error(
                    request,
                    f"There was an error with the data you supplied: '{ e }'. Please correct these errors.",
                )

                context = {
                    "page_title": "Error with data supplied",
                    "setup_step": setup_step,
                    "restart_button": "yes",
                }

                return render(
                    request,
                    "start_new_project.html",
                    context | std_context(),
                    status=400,
                )

            inputs = request.session["inputs"]

            messages.success(
                request,
                f"You have successfully created the project titled '{inputs['project_name']}'.",
            )

            project_id = request.session["project_id"]

            request.session.pop("project_id")

            context = {
                "page_title": "Complete",
                "setup_step": setup_step,
                "project_id": project_id,
            }

            return render(
                request, "start_new_project.html", context | std_context()
            )

        elif setup_step == 4:
            return redirect("/start_new_project")


@project_access
def setup_documents(  # type: ignore[return]
    request: HttpRequest,
    project_id: int,
    setup_step: int,
) -> HttpResponse:
    """Setup the safety documents prior to building them

    After the project has been initialised via 'start_new_project' above, this
    method setups the safety documents, enabling safety documents to then be
    built. The state of the installation is stored in an setup.ini file as
    'setup_step'.

    Args:
        request (HttpRequest): request from user

    Returns:
        HttpResponse: for loading the correct webpage
    """
    project_builder: ProjectBuilder = ProjectBuilder(project_id)
    context: dict[str, Any] = {}
    template_choice: str = ""
    form: TemplateSelectForm | PlaceholdersForm

    if setup_step == 1:
        if request.method == "GET":
            context = {
                "page_title": "Select Template",
                "form": TemplateSelectForm(project_id),
                "project_id": project_id,
            }

            return render(
                request,
                "setup_documents_template_select.html",
                context | std_context(project_id),
            )

        elif request.method == "POST":
            form = TemplateSelectForm(project_id, request.POST)
            if form.is_valid():
                project_builder.configuration_set("setup_step", 2)
                template_choice = form.cleaned_data["template_choice"]
                project_builder.copy_master_template(template_choice)

                messages.success(
                    request,
                    f"{ template_choice } template initiated",
                )

                context = {
                    "page_title": "Edit placeholders",
                    "form": PlaceholdersForm(project_id),
                    "project_id": project_id,
                    "project_side_bars": True,
                }

                return render(
                    request,
                    "setup_documents_placeholders_show.html",
                    context | std_context(project_id),
                )
            else:
                context = {
                    "page_title": "Select Template",
                    "form": form,
                    "project_id": project_id,
                }

                return render(
                    request,
                    "setup_documents_template_select.html",
                    context | std_context(project_id),
                    status=400,
                )

    elif setup_step >= 2:
        if request.method == "GET":
            context = {
                "page_title": "Edit placeholders",
                "form": PlaceholdersForm(project_id),
                "project_id": project_id,
                "project_name": Project.objects.get(id=project_id).name,
                "project_side_bars": True,
            }

            return render(
                request,
                "setup_documents_placeholders_show.html",
                context | std_context(project_id),
            )

        elif request.method == "POST":
            form = PlaceholdersForm(project_id, request.POST)
            if form.is_valid():
                project_builder.configuration_set("setup_step", 3)

                project_builder.save_placeholders_from_form(form)

                project_timestamp(project_id)

                context = {
                    "page_title": "Documents published",
                    "project_id": project_id,
                    "project_name": Project.objects.get(id=project_id).name,
                    "project_side_bars": True,
                }

                return render(
                    request,
                    "setup_documents_placeholders_saved.html",
                    context | std_context(project_id),
                )
            else:
                context = {
                    "page_title": "Edit placeholders",
                    "form": form,
                    "project_id": project_id,
                    "project_name": Project.objects.get(id=project_id).name,
                    "project_side_bars": True,
                }

                return render(
                    request,
                    "setup_documents_placeholders_show.html",
                    context | std_context(project_id),
                    status=400,
                )


@project_access
def project_build_asap(  # type: ignore[return]
    request: HttpRequest,
    project_id: int,
    _: int,
) -> HttpResponse:
    """Ad hoc build of the static site

    This function allows the user to build the static site ad hoc. This is
    useful if the user has made changes to the documents and wants to see the
    changes immediately.

    Args:
        request (HttpRequest): request from user
        project_id (int): primary key of project

    Returns:
        HttpResponse: for loading the webpage
    """
    context: dict[str, Any] = {}
    build_output: str = ""
    mkdocs_control: MkdocsControl = MkdocsControl(project_id)

    if request.method == "GET":
        context = {
            "page_title": "Build documents",
            "project_id": project_id,
            "project_name": Project.objects.get(id=project_id).name,
            "project_side_bars": True,
        }

        return render(
            request,
            "project_build_asap.html",
            context | std_context(project_id),
        )
    elif request.method == "POST":
        build_output = mkdocs_control.build_documents(force=True)

        context = {
            "page_title": "Build documents",
            "project_id": project_id,
            "build_output": build_output,
            "project_name": Project.objects.get(id=project_id).name,
            "project_side_bars": True,
        }

        return render(
            request,
            "project_build_asap.html",
            context | std_context(project_id),
        )


@project_access
def project_documents(
    request: HttpRequest,
    project_id: int,
    _: int,
) -> HttpResponse:
    """Shows the project main page

    This provides an overview of the project and the documents that are part of
    it.

    Args:
        request (HttpRequest): request from user.
        project_id (int): primary key of project.

    Returns:
        HttpResponse: for loading the correct webpage.
    """
    project: Optional[Project] = None
    members: QuerySet[User] = User.objects.none()
    groups: QuerySet[ProjectGroup] = ProjectGroup.objects.none()
    context: dict[str, Any] = {}

    if request.method != "GET":
        return custom_405(request)

    project = Project.objects.get(id=project_id)
    members = project.member.all()
    groups = ProjectGroup.objects.filter(project_access=project)

    context = {
        "page_title": "--- Placeholder ---",
        "page_title": project.name,
        "project": project,
        "members": members,
        "groups": groups,
        "project_id": project_id,
        "project_name": project.name,
        "project_side_bars": True,
    }
    return render(
        request,
        "project_documents.html",
        context | std_context(project_id),
    )


def view_docs(
    request: HttpRequest,
    project_id: str,
    doc_path: str = "",
) -> HttpResponse:
    """Delivers controlled access to static site material

    Delivers controlled access to static site pages. It uses the NGINX
    X-Accel-Redirect. Depending on if the project's documents have private,
    membership or public access, the user will be able to view the documents.
    Hence, access to the static pages are also dependent on if the user is
    authenticated.

    Args:
        request (HttpRequest): request from user
        project_id (str): primary key of project
        doc_path (str): path to the document

    Returns:
        HttpResponse: for loading the correct webpage
    """
    project_id_int: int
    accessible_projects: list[dict[str, str]] = []
    internal_path: str = ""
    mkdocs_control: Optional[MkdocsControl] = None
    file: Optional[TextIO] = None
    document_content = ""
    context: dict[str, Any] = {}
    content_type: str = "invalid"
    file_extension: str = ""
    key: str = ""
    value: str = ""
    response: Optional[HttpResponse] = None

    if project_id.isdigit():
        project_id_int = int(project_id)
    else:
        return custom_404(request)

    if not Project.objects.filter(id=project_id_int).exists():
        messages.error(request, f"'Project { project_id }' does not exist")
        return custom_404(request)

    project = Project.objects.get(id=project_id)

    if project.access == ViewAccess.MEMBERS:
        if not request.user.is_authenticated:
            messages.error(
                request,
                f"You do not have access to 'project { project_id }'. "
                "This is a members only project.",
            )
            return custom_403(request)

    elif project.access == ViewAccess.PRIVATE:
        accessible_projects = user_accessible_projects(request)
        if not any(
            doc for doc in accessible_projects if doc["doc_id"] == project_id
        ):
            messages.error(
                request, f"You do not have access to 'project { project_id }'."
            )
            return custom_403(request)

    internal_path = str(
        Path(c.DOCUMENTATION_PAGES) / f"project_{project_id}" / doc_path
    )

    file_extension = Path(internal_path).suffix[1:]

    if file_extension == "html":
        mkdocs_control = MkdocsControl(project_id)
        mkdocs_control.build_documents()

    if not Path(internal_path).is_file():
        messages.error(request, f"File '{ doc_path }' does not exist.")
        return custom_404(request)

    if file_extension == "html":
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
        for key, value in c.MIME_TYPES.items():
            if file_extension == key:
                content_type = value
                break

        response = HttpResponse(content_type=content_type)
        response["X-Accel-Redirect"] = internal_path
        return response


@project_access
def document_new(  # type: ignore[return]
    request: HttpRequest,
    project_id: int,
    setup_step: int,
) -> HttpResponse:
    """To create a new safety document

    This will allow the user to create a new safety document, which are stored as
    markdown files. A new directory will be created if it does not already exist.

    Args:
        request (HttpRequest): request from user
        project_id (int): primary key of project
        setup_step (int): the step in the setup process

    Returns:
        HttpResponse: for loading the correct webpage
    """
    context: dict[str, Any] = {}
    form: Optional[DocumentNewForm] = None
    project: Optional[ProjectBuilder] = None
    document_name_new: str = ""

    if setup_step < 2:
        return redirect(f"/setup_documents/{ project_id }")

    if request.method == "GET":
        context = {
            "page_title": "Create a new safety document",
            "project_name": Project.objects.get(id=project_id).name,
            "form": DocumentNewForm(project_id),
            "project_id": project_id,
        }
        return render(
            request,
            "document_new.html",
            context | std_context(project_id),
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

            context = {
                "page_title": "New document created",
                "project_name": Project.objects.get(id=project_id).name,
                "submitted": True,
                "project_id": project_id,
                "document_name_new": document_name_new,
            }

            return render(
                request, "document_new.html", context | std_context(project_id)
            )

        else:
            context = {
                "page_title": "Create a new safety document",
                "project_name": Project.objects.get(id=project_id).name,
                "form": form,
                "project_id": project_id,
            }

            return render(
                request,
                "document_new.html",
                context | std_context(project_id),
                status=400,
            )


@project_access
def document_update(  # type: ignore[return]
    request: HttpRequest, project_id: int, setup_step: int
) -> HttpResponse:
    """Save the safety document

    If no issues are found after running the markdown file through a linter
    the file is saved.

    Args:
        request (HttpRequest): request from user
        project_id (int): primary key of project
        setup_step (int): the step in the setup process

    Returns:
        HttpResponse: for loading the correct webpage
    """
    form: Optional[DocumentUpdateForm] = None
    document_name_initial: str = ""
    document_name: str = ""
    document_markdown_initial: str = ""
    document_markdown: str = ""
    document_markdown_file_read: str = ""
    form_data: dict[str, str] = {}
    docs_dir: str = f"{ c.PROJECTS_FOLDER }project_{ project_id }/{ c.CLINICAL_SAFETY_FOLDER }docs/"
    file: TextIO
    context: dict[str, Any] = {}

    if setup_step < 2:
        return redirect(f"/setup_documents/{ project_id }")

    if request.method == "GET":
        form = DocumentUpdateForm(project_id)

        context = {
            "page_title_left": "Edit safety document",
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

    elif request.method == "POST":
        form = DocumentUpdateForm(project_id, data=request.POST)

        if form.is_valid():
            document_name_initial = form.cleaned_data["document_name_initial"]
            document_name = form.cleaned_data["document_name"]
            document_markdown_initial = form.cleaned_data[
                "document_markdown_initial"
            ]
            document_markdown = form.cleaned_data["document_markdown"]

            if document_name_initial != document_name:
                with open(Path(docs_dir) / document_name, "r") as file:
                    document_markdown_file_read = file.read()
                    document_markdown_file_read = (
                        document_markdown_file_read.replace("\n", "\r\n")
                    )

                form_data = {
                    "document_name": document_name,
                    "document_markdown": document_markdown_file_read,
                }

                context = {
                    "page_title_left": "Edit safety document",
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
                with open(Path(docs_dir) / document_name, "w") as file:
                    file.write(document_markdown)

                project_timestamp(project_id)

                form_data = {
                    "document_name": document_name,
                    "document_markdown": document_markdown,
                }

                messages.success(
                    request,
                    f"Mark down file '{ document_name }' has been successfully saved",
                )

                context = {
                    "page_title_left": "Edit safety document",
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
            else:
                messages.success(
                    request,
                    "As no changes have been made, no save has been made",
                )
                context = {
                    "page_title_left": "Edit safety document",
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
                "page_title_left": "Edit safety document",
                "form": form,
                "project_id": project_id,
                "placeholders": placeholders(project_id),
                "nav_top": "True",
            }
            return render(
                request,
                "document_update.html",
                context | std_context(project_id),
                status=400,
            )


@project_access
def document_update_named(  # type: ignore[return]
    request: HttpRequest, project_id: int, setup_step: int, document_name: str
) -> HttpResponse:
    """Select a specific document to edit

    Uses the url to select a specific document to edit.

    Args:
        request (HttpRequest): request from user
        project_id (int): primary key of project
        setup_step (int): the step in the setup process
        document_name (str): name of the document to edit

    Returns:
        HttpResponse: for loading the correct webpage
    """
    form: Optional[DocumentUpdateForm] = None
    context: dict[str, Any] = {}

    if not request.method == "GET":
        return custom_405(request)

    if setup_step < 2:
        return redirect(f"/setup_documents/{ project_id }")

    if request.method == "GET":
        try:
            form = DocumentUpdateForm(project_id, document_name)
        except FileNotFoundError:
            return custom_404(request)

        context = {
            "page_title_left": "Edit safety document",
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


@project_access
def entry_update(  # type: ignore[return]
    request: HttpRequest,
    project_id: int,
    setup_step: int,
    entry_type: str,
    id_new: str,
) -> HttpResponse:
    """Create or update an entry

    Creates a new entry (for example a hazard or incident) or updates a pre-
    existing one.

    Args:
        request (HttpRequest): request user.
        project_id (int): the primary key of the project.
        setup_step (int): the step in the setup process.
        entry_type (str): type of entry (eg hazard, incident).
        id_new (str): an entry file number or "new" to create a new entry.

    Returns:
        HttpResponse: for loading the webpage.
    """
    project: ProjectBuilder = ProjectBuilder(project_id)
    context: dict[str, Any] = {"project_id": project_id}
    form_initial: dict[str, str] = {}
    form: EntryUpdateForm
    entry_update_outcome: bool = False
    page_title: str = ""

    if setup_step < 2:
        return redirect(f"/setup_documents/{ project_id }")

    if id_new != "new":
        if not id_new.isdigit() or not project.entry_exists(
            entry_type, int(id_new)
        ):
            return custom_404(request)

    if not project.entry_type_exists(entry_type):
        return custom_404(request)

    if request.method == "GET":
        if id_new == "new":
            context = {
                "page_title": f"Create new { kebab_to_sentense(entry_type) }",
                "project_name": Project.objects.get(id=project_id).name,
                "project_id": project_id,
                "form": EntryUpdateForm(project_id, entry_type),
                "entry_type": entry_type,
                "id_new": id_new,
                "project_side_bars": True,
            }
            return render(
                request,
                "entry_update.html",
                context | std_context(project_id),
            )

        else:
            form_initial = project.form_initial(entry_type, int(id_new))
            context = {
                "page_title": f"Update { kebab_to_sentense(entry_type) }",
                "project_name": Project.objects.get(id=project_id).name,
                "project_id": project_id,
                "form": EntryUpdateForm(
                    project_id,
                    entry_type,
                    initial=form_initial,
                ),
                "entry_type": entry_type,
                "id_new": id_new,
                "project_side_bars": True,
            }
            return render(
                request,
                "entry_update.html",
                context | std_context(project_id),
            )

    elif request.method == "POST":
        form = EntryUpdateForm(project_id, entry_type, request.POST)
        if form.is_valid():
            project_timestamp(project_id)

            entry_update_outcome = project.entry_update(
                form.cleaned_data,
                entry_type,
                id_new,
            )

            context = {
                "page_title": f"{ kebab_to_sentense(entry_type) } saved",
                "project_name": Project.objects.get(id=project_id).name,
                "project_id": project_id,
                "entry_update_outcome": entry_update_outcome,
                "entry_type": entry_type,
                "id_new": id_new,
                "project_side_bars": True,
            }
            return render(
                request,
                "entry_saved.html",
                context | std_context(project_id),
            )

        else:
            if id_new == "new":
                page_title = f"Create new { kebab_to_sentense(entry_type) }"
            else:
                page_title = f"Update { kebab_to_sentense(entry_type) }"

            context = {
                "page_title": page_title,
                "project_name": Project.objects.get(id=project_id).name,
                "form": form,
                "project_id": project_id,
                "entry_type": entry_type,
                "id_new": id_new,
                "project_side_bars": True,
            }
            return render(
                request,
                "entry_update.html",
                context | std_context(project_id),
            )


@project_access
def entry_select(
    request: HttpRequest,
    project_id: int,
    setup_step: int,
    entry_type: str,
) -> HttpResponse:
    """Displays entries that can be edited

    For the given entry type, displays the entries that can be edited.

    Args:
        request (HttpRequest): request from user
        project_id (int): primary key of the project
        setup_step (int): the step in the setup process
        entry_type (str): type of entry (eg hazard, incident)

    Returns:
        HttpResponse: for loading the correct webpage
    """
    context: dict[str, Any] = {}
    project: ProjectBuilder = ProjectBuilder(int(project_id))
    entries: list[str] = []

    if setup_step < 2:
        return redirect(f"/setup_documents/{ project_id }")

    if request.method != "GET":
        return custom_405(request)

    if not project.entry_type_exists(entry_type):
        return custom_404(request)

    entries = project.entries_all_get(entry_type)

    context = {
        "page_title": f"Select { kebab_to_sentense(entry_type) } to edit",
        "project_name": Project.objects.get(id=project_id).name,
        "project_id": project_id,
        "entries": entries,
        "entry_type": entry_type,
        "project_side_bars": True,
    }
    return render(
        request, "entry_select.html", context | std_context(project_id)
    )


def under_construction(
    request: HttpRequest,
    message: str,
) -> HttpResponse:
    """Under construction page

    This page is displayed when a page is under construction.

    Args:
        request (HttpRequest): request from user.
        message (str): message to display.

    Returns:
        HttpResponse: for loading the correct webpage.
    """
    context: dict[str, Any] = {
        "page_title": " Under contruction",
        "message": message,
    }

    return render(request, "under_construction.html", context | std_context())


# ----- Helper functions -----


def std_context(project_id: int = 0) -> dict[str, Any]:
    """Provides standard context for the rendered view

    Provides a standard collection of values that can be used in page renderings.

    Args:
        project_id (int): primary key of project.

    Returns:
        dict[str,Any]: context that is comment across the different views
    """
    project: Optional[ProjectBuilder] = None
    entry_templates: list[str] = []
    std_context_dict: dict[str, Any] = {}
    project_setup_step: int = 0

    if not isinstance(project_id, int):
        raise ValueError("project_id must be an integer")

    if project_id > 0:
        project = ProjectBuilder(project_id)
        entry_templates = project.entry_template_names()
        project_setup_step = project.configuration_get()["setup_step"]

    std_context_dict = {
        "entry_templates": entry_templates,
        "project_setup_step": project_setup_step,
    }

    return std_context_dict


def user_accessible_projects(
    request: HttpRequest,
) -> list[dict[str, Any]]:
    """Finds all documents that the user has access to

    Provides a list of all documents that the user has access to. This includes
    documents that the user owns, documents that the user is a member of, and
    documents that the user has access to through a project group.

    Args:
        request (HttpRequest): request from user

    Returns:
        list[None | dict[str, Any]]: a list of documents
    """
    user_id: int = (
        int(str(request.user.id)) if request.user.id is not None else 0
    )
    documents_owner: QuerySet[Any] = Project.objects.none()
    documents_member: QuerySet[Any] = Project.objects.none()
    project_group: QuerySet[Any] = ProjectGroup.objects.none()
    record: Any = {}
    documents_combined: list[dict[str, Any]] = []
    documents_sorted: list[dict[str, Any]] = []
    i: int = 0

    documents_owner = Project.objects.values(
        doc_id=F("id"),
        project_name=F("name"),
        doc_last_accessed=F("userprojectattribute__last_accessed"),
    ).filter(owner=user_id)

    documents_member = Project.objects.values(
        doc_id=F("id"),
        project_name=F("name"),
        doc_last_accessed=F("userprojectattribute__last_accessed"),
    ).filter(member=user_id)

    project_group = (
        ProjectGroup.objects.values(
            doc_id=F("project_access__id"),
            project_name=F("project_access__name"),
            doc_last_accessed=F(
                "project_access__userprojectattribute__last_accessed"
            ),
        )
        .filter(member=user_id)
        .order_by(
            "project_access__name",
            "project_access__id",
        )
        .distinct("project_access__name")
    )

    if documents_owner:
        for record in list(documents_owner):
            documents_combined.append(record)

    if documents_member:
        for record in documents_member:
            documents_combined.append(record)

    if project_group:
        for record in project_group:
            documents_combined.append(record)

    documents_combined = list(
        {tuple(sorted(d.items())): d for d in documents_combined}.values()
    )

    for i in range(len(documents_combined)):
        if documents_combined[i]["doc_last_accessed"] != None:
            documents_combined[i]["doc_last_accessed"] = documents_combined[i][
                "doc_last_accessed"
            ].replace(tzinfo=None)

    documents_sorted = sorted(
        documents_combined,
        key=lambda x: (
            x["doc_last_accessed"] or datetime.min,
            x["doc_id"],
        ),
        reverse=True,
    )

    documents_sorted = [
        item
        for item in documents_sorted
        if item
        != {
            "doc_id": None,
            "project_name": None,
            "doc_last_accessed": None,
        }
    ]

    """if documents_sorted == [{}]:
        documents_sorted = []"""

    return documents_sorted


def start_new_project_step_2_input_GUI(
    inputs: dict[str, str]
) -> dict[str, str]:
    """Converts the inputs into a more user friendly format

    Takes the user inputs from the previous submissions and prepares them for
    displaying in the GUI.

    Args:
        inputs (dict[str, str]): inputs from the previous submissions.

    Returns:
        dict[str, str]: inputs in a GUI friendly format.
    """
    key: str = ""
    value: str = ""
    inputs_GUI: dict[str, str] = {}
    groups_list: list[str] = []
    members_list: QuerySet[Any] = User.objects.none()
    members_list_fullnames: list[str] = []

    for key, value in inputs.items():
        key = key.replace("import", "")
        key = key.replace("start_anew", "")
        key = snake_to_sentense(key)

        if key == "Setup choice":
            inputs_GUI[key] = snake_to_sentense(value)

        elif key == "Groups":
            groups_list = [
                name
                for name in ProjectGroup.objects.filter(
                    id__in=value
                ).values_list("name", flat=True)
                if name is not None
            ]
            inputs_GUI[key] = ", ".join(groups_list)
            if inputs_GUI[key] == "":
                inputs_GUI[key] = "<i>none selected</i>"

        elif key == "Members":
            members_list = User.objects.filter(id__in=value).values(
                "id", "first_name", "last_name"
            )
            members_list_fullnames = [
                f"{member['first_name']} {member['last_name']}"
                for member in members_list
            ]
            inputs_GUI[key] = ", ".join(members_list_fullnames)
            if inputs_GUI[key] == "":
                inputs_GUI[key] = "<i>none selected</i>"
        elif key == "Access":
            inputs_GUI[key] = ViewAccess.get_label(value)

        elif any(keyword in key for keyword in ["password", "token"]):
            key = key.replace("password token", "password / token")
            inputs_GUI[key] = "***"

        else:
            inputs_GUI[key] = value

    return inputs_GUI


def placeholders(project_id: int) -> str:
    """Provides placeholders in serialised form

    This is used in the documents edit page, where markdown is converted to
    html and placeholders are converted into their corresponding values.

    Args:
        project_id (str): placeholders in a serialised form.

    Returns:
        str: placeholders in serialised form, with empty values replaced with
             "[key undefined]"
    """
    project_builder: Optional[ProjectBuilder] = None
    placeholders: dict[str, str] = {}
    key: str = ""
    value: str = ""

    if not isinstance(project_id, int):
        return ""

    if not Project.objects.filter(id=project_id).exists():
        return ""

    project_builder = ProjectBuilder(int(project_id))
    placeholders = project_builder.get_placeholders()
    for key, value in placeholders.items():
        if value == "":
            placeholders[key] = f"[{ key } undefined]"

    return json.dumps(placeholders)


def custom_400(
    request: HttpRequest, exception: Optional[Exception] = None
) -> HttpResponse:
    """Custom 400 - bad request page

    Custom 400 page for bad request.

    Args:
        request (HttpRequest): request from user

    Returns:
        HttpResponse: for loading the correct webpage
    """

    context: dict[str, Any] = {"page_title": "400 - Bad request"}

    return render(
        request, "error_handler.html", context | std_context(), status=400
    )


def custom_403(
    request: HttpRequest, exception: Optional[Exception] = None
) -> HttpResponse:
    """Custom 403 - access forbidden page

    Custom 403 page for access forbidden

    Args:
        request (HttpRequest): request from user

    Returns:
        HttpResponse: for loading the correct webpage
    """

    context: dict[str, Any] = {"page_title": "403 - Forbidden access"}

    return render(
        request, "error_handler.html", context | std_context(), status=403
    )


def custom_403_csrf(request: HttpRequest, reason: Any = None) -> HttpResponse:
    """Custom 403 - CSRF page

    Custom 403 access forbidden when CRSF triggered.

    Args:
        request (HttpRequest): request from user

    Returns:
        HttpResponse: for loading the correct webpage
    """
    return custom_403(request)


def custom_404(
    request: HttpRequest, exception: Optional[Exception] = None
) -> HttpResponse:
    """Custom 404 page - page not found

    Custom page not found.

    Args:
        request (HttpRequest): request from user

    Returns:
        HttpResponse: for loading the correct webpage
    """
    context: dict[str, Any] = {"page_title": "404 - Page not found"}

    return render(
        request, "error_handler.html", context | std_context(), status=404
    )


def custom_405(
    request: HttpRequest, exception: Optional[Exception] = None
) -> HttpResponse:
    """Custom 405 page - method not allowed

    Custom page method not allowed

    Args:
        request (HttpRequest): request from user

    Returns:
        HttpResponse: for loading the correct webpage
    """
    context: dict[str, Any] = {"page_title": "405 - method not allowed"}

    return render(
        request, "error_handler.html", context | std_context(), status=405
    )


def custom_500(
    request: HttpRequest, exception: Optional[Exception] = None
) -> HttpResponse:
    """Custom 500 page - internal server error

    Description

    Args:
        request (HttpRequest): request from user

    Returns:
        HttpResponse: for loading the correct webpage
    """
    context: dict[str, Any] = {"page_title": "500 - Internal Server Error"}

    return render(
        request,
        "error_handler.html",
        context | std_context(),
        status=500,
    )
