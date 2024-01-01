"""Manages the views for the dcsp app

This is part of a Django web server app that is used to create a static site in
mkdocs. It utilises several other functions git, github, env manipulation and 
mkdocs

Functions:
    index: placeholder
    main: placeholder
    md_edit: placeholder
    md_saved: placeholder
    md_new: placeholder
    hazard_log: placeholder
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
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings

import os
import sys
from fnmatch import fnmatch
from dotenv import find_dotenv, dotenv_values
import shutil
from typing import Any, TextIO

# from collections.abc import Buffer

import app.functions.constants as c
from app.functions.constants import EnvKeysPH

sys.path.append(c.FUNCTIONS_APP)
from app.functions.env_manipulation import ENVManipulator
from app.functions.mkdocs_control import MkdocsControl
from app.functions.docs_builder import Builder
from app.functions.git_control import GitController


from .forms import (
    InstallationForm,
    TemplateSelectForm,
    PlaceholdersForm,
    MDEditForm,
    MDFileSelectForm,
    LogHazardForm,
    UploadToGithubForm,
    HazardCommentForm,
)


def index(request: HttpRequest) -> HttpResponse:
    """Landing page for DCSP app

    Landing page for DCSP app

    Args:
        request (HttpRequest): request from user

    Returns:
        HttpResponse: for loading the correct webpage
    """
    context: dict[str, Any] = {}
    if request.method != "GET":
        return render(request, "405.html", std_context(), status=405)

    context = {}

    return render(request, "index.html", context | std_context())


@login_required
def build(request: HttpRequest) -> HttpResponse:
    """Index page, carrying out steps to initialise a static site

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
    context: dict[str, Any] = {}
    placeholders: dict[str, str] = {}
    p: str = ""
    setup_step: int = 0
    template_choice: str = ""
    form: InstallationForm | TemplateSelectForm | PlaceholdersForm
    env_m: ENVManipulator
    mkdocs: MkdocsControl
    doc_build: Builder

    if not (request.method == "POST" or request.method == "GET"):
        return render(request, "405.html", std_context(), status=405)

    env_m = ENVManipulator(settings.ENV_LOCATION)
    setup_step = setup_step_get()

    if setup_step == 0:
        if request.method == "GET":
            context = {"form": InstallationForm()}

            return render(
                request, "installation_method.html", context | std_context()
            )

        elif request.method == "POST":
            form = InstallationForm(request.POST)
            if form.is_valid():
                env_m.add(
                    EnvKeysPH.GITHUB_USERNAME.value,
                    form.cleaned_data["github_username_SA"],
                )
                env_m.add(
                    EnvKeysPH.EMAIL.value,
                    form.cleaned_data["email_SA"],
                )
                env_m.add(
                    EnvKeysPH.GITHUB_ORGANISATION.value,
                    form.cleaned_data["github_organisation_SA"],
                )
                env_m.add(
                    EnvKeysPH.GITHUB_REPO.value,
                    form.cleaned_data["github_repo_SA"],
                )
                env_m.add(
                    EnvKeysPH.GITHUB_TOKEN.value,
                    form.cleaned_data["github_token_SA"],
                )
                env_m.add("setup_step", "1")

                messages.success(request, "Initialisation selections stored")

                context = {"form": TemplateSelectForm()}

                return render(
                    request, "template_select.html", context | std_context()
                )
            else:
                context = {"form": form}

                return render(
                    request,
                    "installation_method.html",
                    context | std_context(),
                )

    elif setup_step == 1:
        if request.method == "GET":
            context = {"form": TemplateSelectForm()}

            return render(
                request, "template_select.html", context | std_context()
            )

        elif request.method == "POST":
            form = TemplateSelectForm(request.POST)  # type: ignore[assignment]
            if form.is_valid():
                env_m.add("setup_step", "2")
                template_choice = form.cleaned_data["template_choice"]

                doc_build = Builder(settings.MKDOCS_LOCATION)
                doc_build.copy_templates(template_choice)

                messages.success(
                    request,
                    f"{ template_choice } template initiated",
                )

                context = {"form": PlaceholdersForm()}

                return render(
                    request, "placeholders_show.html", context | std_context()
                )
            else:
                context = {"form": form}

                return render(
                    request, "template_select.html", context | std_context()
                )

    elif setup_step >= 2:
        if request.method == "GET":
            context = {"form": PlaceholdersForm()}

            return render(
                request, "placeholders_show.html", context | std_context()
            )

        elif request.method == "POST":
            form = PlaceholdersForm(data=request.POST)  # type: ignore[assignment]
            if form.is_valid():
                env_m.add("setup_step", "3")

                doc_build = Builder(settings.MKDOCS_LOCATION)
                placeholders = doc_build.get_placeholders()

                for p in placeholders:
                    placeholders[p] = form.cleaned_data[p]

                doc_build.save_placeholders(placeholders)

                messages.success(
                    request,
                    "Placeholders saved",
                )

                mkdocs = MkdocsControl()
                if not mkdocs.start(wait=True):
                    return render(request, "500.html")

                return render(
                    request, "placeholders_saved.html", context | std_context()
                )
            else:
                context = {"form": form}

                return render(
                    request, "placeholders_show.html", context | std_context()
                )

    # Should never really get here, but added for mypy
    return render(request, "500.html", std_context(), status=500)


@login_required
def md_edit(request: HttpRequest) -> HttpResponse:
    """Function for editing of markdown files in the static site

    A webpage to allow the user to edit the markdown files used in the
    static site on mkdocs.

    Args:
        request (HttpRequest): request from user

    Returns:
        HttpResponse: for loading the correct webpage
    """
    setup_step: int = 0
    files: list[str] = []
    name: str = ""
    md_file: str = ""
    loop_exit: bool = False
    form: MDFileSelectForm
    context: dict[str, Any] = {}
    form_fields: dict[str, str] = {}

    if not (request.method == "GET" or request.method == "POST"):
        return render(request, "405.html", status=405)

    setup_step = setup_step_get()

    if setup_step < 2:
        return redirect("/build")

    if request.method == "GET":
        if not os.path.isdir(settings.MKDOCS_DOCS_LOCATION):
            return render(request, "500.html", std_context(), status=500)

        for _, __, files in os.walk(settings.MKDOCS_DOCS_LOCATION):
            for name in files:
                if fnmatch(name, "*.md"):
                    md_file = name
                    loop_exit = True
                    break
            if loop_exit:
                break

    elif request.method == "POST":
        form = MDFileSelectForm(data=request.POST)
        if form.is_valid():
            md_file = form.cleaned_data["mark_down_file"]
        else:
            context = {"form": form}
            return render(request, "md_edit.html", context | std_context())

    with open(f"{ settings.MKDOCS_DOCS_LOCATION }{ md_file }", "r") as file:
        form_fields = {"md_text": file.read(), "document_name": md_file}

    context = {
        "MDFileSelectForm": MDFileSelectForm(
            initial={"mark_down_file": md_file}
        ),
        "form": MDEditForm(initial=form_fields),
        "document_name": md_file,
    }

    return render(request, "md_edit.html", context | std_context())


@login_required
def md_saved(request: HttpRequest) -> HttpResponse:
    """Saves the markdown file

    If no issues are found after running the markdown file through a linter
    then the file is saved.

    Args:
        request (HttpRequest): request from user

    Returns:
        HttpResponse: for loading the correct webpage
    """
    setup_step: int = 0
    form: MDEditForm
    md_file_returned: str = ""
    md_text_returned: str = ""
    file_path: str = ""
    file: TextIO
    context: dict[str, Any] = {}

    if request.method == "GET":
        return redirect("/md_edit")

    if not request.method == "POST":
        return render(request, "405.html", std_context(), status=405)

    setup_step = setup_step_get()
    if setup_step < 2:
        return redirect("/build")

    form = MDEditForm(request.POST)
    if form.is_valid():
        md_file_returned = form.cleaned_data["document_name"]
        md_text_returned = form.cleaned_data["md_text"]

        file_path = f"{ settings.MKDOCS_DOCS_LOCATION }{ md_file_returned }"

        if not os.path.isfile(file_path):
            return render(
                request, "500.html", context | std_context(), status=500
            )

        file = open(file_path, "w")
        file.write(md_text_returned)
        file.close()

        messages.success(
            request,
            f'Mark down file "{ md_file_returned }" has been successfully saved',
        )
        context = {
            "MDFileSelectForm": MDFileSelectForm(
                initial={"mark_down_file": md_file_returned}
            ),
            "form": MDEditForm(initial=request.POST),
            "document_name": md_file_returned,
        }
        return render(request, "md_edit.html", context | std_context())
    else:
        try:
            md_file_returned = form.cleaned_data["document_name"]
        except:
            return render(request, "500.html", status=500)
        context = {
            "MDFileSelectForm": MDFileSelectForm(
                initial={"mark_down_file": md_file_returned}
            ),
            "form": form,
            "document_name": md_file_returned,
        }
        return render(request, "md_edit.html", context | std_context())

    # For mypy
    return render(request, "500.html", status=500)


@login_required
def md_new(request: HttpRequest) -> HttpResponse:
    """Not complete - to create a new markdown file

    This will allow the user to create a new markdown file with subdirectories
    if required.

    Args:
        request (HttpRequest): request from user
    Returns:
        HttpResponse: for loading the correct webpage
    """
    context: dict[str, Any] = {}

    if not (request.method == "GET" or request.method == "POST"):
        return render(request, "405.html", std_context(), status=405)

    if request.method == "GET":
        context = {"form": LogHazardForm()}
        return render(request, "md_new.html", context | std_context())

    # For mypy
    return render(request, "500.html", status=500)


@login_required
def hazard_log(request: HttpRequest) -> HttpResponse:
    """Logs hazards as issues on GitHub

    Creates a hazard as an issue on GitHub

    Args:
        request (HttpRequest): request from user

    Returns:
        HttpResponse: for loading the correct webpage
    """
    context: dict[str, Any] = {}
    gc: GitController
    form: LogHazardForm
    hazard: dict[str, Any] = {}

    if not (request.method == "GET" or request.method == "POST"):
        return render(request, "405.html", std_context(), status=405)

    if request.method == "GET":
        context = {"form": LogHazardForm()}
        return render(request, "hazard_log.html", context | std_context())

    if request.method == "POST":
        form = LogHazardForm(request.POST)
        if form.is_valid():
            hazard["title"] = form.cleaned_data["title"]
            hazard["body"] = form.cleaned_data["body"]
            hazard["labels"] = form.cleaned_data["labels"]
            gc = GitController()

            try:
                gc.hazard_log(
                    hazard["title"], hazard["body"], hazard["labels"]
                )
            except Exception as error:
                messages.error(
                    request,
                    f"Error returned from logging hazard - '{ error }'",
                )

                context = {"form": LogHazardForm(initial=request.POST)}

                return render(
                    request, "hazard_log.html", context | std_context()
                )
            else:
                messages.success(
                    request,
                    f"Hazard has been uploaded to GitHub",
                )
                context = {"form": LogHazardForm()}
                return render(
                    request, "hazard_log.html", context | std_context()
                )
        else:
            context = {"form": form}
            return render(request, "hazard_log.html", context | std_context())

    # Should never really get here, but added for mypy
    return render(request, "500.html", std_context(), status=500)


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
        return render(request, "hazard_comment.html", context | std_context())

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
                request, "hazard_comment.html", context | std_context()
            )
        else:
            context = {"form": form}
            return render(
                request, "hazard_comment.html", context | std_context()
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
    Returns:
        HttpResponse: for loading the correct webpage
    """
    mkdocs: MkdocsControl

    if not request.method == "GET":
        return render(request, "405.html", std_context(), status=405)

    mkdocs = MkdocsControl()
    mkdocs.start()

    # TODO - need message page for if mkdocs is not running

    if path == "home":
        return redirect(f"http://localhost:9000")
    else:
        return redirect(f"http://localhost:9000/{ path }")

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


def std_context() -> dict[str, Any]:
    """Title

    Description

    Returns:
        dict[str,Any]: context that is comment across the different views
    """

    std_context_dict: dict[str, Any] = {}
    mkdoc_running: bool = False
    docs_available: bool = False
    mkdocs: MkdocsControl
    setup_step: int = 0

    mkdocs = MkdocsControl()
    mkdoc_running = mkdocs.is_process_running()

    setup_step = setup_step_get()

    if setup_step >= 2:
        docs_available = True

    std_context_dict = {
        "START_AFRESH": settings.START_AFRESH,
        "mkdoc_running": mkdoc_running,
        "docs_available": docs_available,
        "FORM_ELEMENTS_MAX_WIDTH": c.FORM_ELEMENTS_MAX_WIDTH,
    }

    return std_context_dict


@login_required
def start_afresh(request: HttpRequest) -> HttpResponse:
    """Title

    Description

    Args:
        request (HttpRequest): request from user

    Returns:
        HttpResponse: for loading the correct webpage
    """

    env_m: ENVManipulator
    mkdocs: MkdocsControl
    # root, dirs, files, d

    if not request.method == "GET":
        return render(request, "405.html", std_context(), status=405)

    if settings.START_AFRESH or settings.TESTING:
        for root, dirs, files in os.walk(settings.MKDOCS_DOCS_LOCATION):
            for file in files:
                if not fnmatch(file, ".gitkeep"):
                    os.unlink(os.path.join(root, file))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

        env_m = ENVManipulator(settings.ENV_LOCATION)
        env_m.delete_all()

        mkdocs = MkdocsControl()
        if not mkdocs.stop(wait=True):
            return render(request, "500.html", status=500)
    return redirect("/build")


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
