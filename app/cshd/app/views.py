from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest
from django.contrib import messages
from django.conf import settings

import os
import sys
from fnmatch import fnmatch
from dotenv import find_dotenv, dotenv_values
import shutil
from typing import Any

import app.functions.constants as c
from app.functions.constants import EnvKeys

sys.path.append(c.FUNCTIONS_APP)
from env_manipulation import ENVManipulator
from mkdocs_control import MkdocsControl
from docs_builder import Builder
from git_control import GitController


from .forms import (
    InstallationForm,
    TemplateSelectForm,
    PlaceholdersForm,
    MDEditForm,
    MDFileSelect,
    LogHazardForm,
    UploadToGithub,
    HazardCommentForm,
)


def index(request: HttpRequest) -> HttpResponse:
    context: dict[str, Any] = {}
    placeholders: dict[str, str] = {}
    setup_step: str | None = None
    template_choice: str = ""
    # form

    if not (request.method == "POST" or request.method == "GET"):
        return render(request, "405.html", std_context(), status=405)

    # 'environ.get' does not handle a change of envs very well, so used
    # 'env_variables = dotenv_values(find_dotenv())' instead
    # TODO: use new env_manipulator functions
    # env_variables = dotenv_values(settings.ENV_LOCATION)
    # setup_step = env_variables.get("setup_step")
    em = ENVManipulator(settings.ENV_LOCATION)
    setup_step = em.read("setup_step")

    if not setup_step:
        if request.method == "GET":
            context = {"form": InstallationForm()}

            return render(
                request, "installation_method.html", context | std_context()
            )

        elif request.method == "POST":
            form = InstallationForm(request.POST)
            if form.is_valid():
                env_m = ENVManipulator(settings.ENV_LOCATION)

                env_m.add(
                    EnvKeys.GITHUB_USERNAME.value,
                    form.cleaned_data["github_username_SA"],
                )
                env_m.add(
                    EnvKeys.EMAIL.value,
                    form.cleaned_data["email_SA"],
                )
                env_m.add(
                    EnvKeys.GITHUB_ORGANISATION.value,
                    form.cleaned_data["github_organisation_SA"],
                )
                env_m.add(
                    EnvKeys.GITHUB_REPO.value,
                    form.cleaned_data["github_repo_SA"],
                )
                env_m.add(
                    EnvKeys.GITHUB_TOKEN.value,
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

    elif setup_step == "1":
        if request.method == "GET":
            context = {"form": TemplateSelectForm()}

            return render(
                request, "template_select.html", context | std_context()
            )

        elif request.method == "POST":
            form = TemplateSelectForm(request.POST)  # type: ignore[assignment]
            if form.is_valid():
                env_m = ENVManipulator(settings.ENV_LOCATION)
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

    elif setup_step == "2" or setup_step == "3":
        if request.method == "GET":
            context = {"form": PlaceholdersForm()}

            return render(
                request, "placeholders_show.html", context | std_context()
            )

        elif request.method == "POST":
            form = PlaceholdersForm(data=request.POST)  # type: ignore[assignment]
            if form.is_valid():
                env_m = ENVManipulator(settings.ENV_LOCATION)
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


def edit_md(request: HttpRequest) -> HttpResponse:
    context: dict[str, Any] = {}
    files_md: str = ""
    loop_exit: bool = False
    files: list[str] = []
    name: str = ""
    em: ENVManipulator

    if not (request.method == "GET" or request.method == "POST"):
        return render(request, "405.html", status=405)

    em = ENVManipulator(settings.ENV_LOCATION)
    setup_step = em.read("setup_step")

    if setup_step != "2" and setup_step != "3":
        return redirect("/")

    if request.method == "GET":
        if not os.path.isdir(settings.MKDOCS_DOCS_LOCATION):
            return render(request, "500.html", std_context(), status=500)

        # TODO: can we somehow remove p and v here?
        for p, v, files in os.walk(settings.MKDOCS_DOCS_LOCATION):
            for name in files:
                if fnmatch(name, "*.md"):
                    files_md = name
                    loop_exit = True
                    break
            if loop_exit:
                break

    elif request.method == "POST":
        form = MDFileSelect(data=request.POST)
        if form.is_valid():
            files_md = form.cleaned_data["mark_down_file"]
        else:
            context = {"form": form}
            return render(request, "edit_md.html", context | std_context())

    with open(f"{ settings.MKDOCS_DOCS_LOCATION }{ files_md }", "r") as file:
        form_fields = {"text_md": file.read(), "document_name": files_md}

    context = {
        "MDFileSelect": MDFileSelect(initial={"mark_down_file": files_md}),
        "text_md": MDEditForm(initial=form_fields),
        "document_name": files_md,
    }

    return render(request, "edit_md.html", context | std_context())


def saved_md(request: HttpRequest) -> HttpResponse:
    context: dict = {}
    text_md_returned: str = ""
    file_md_returned: str = ""
    file_path: str = ""
    em: ENVManipulator

    if request.method == "GET":
        return redirect("/edit_md")

    if not request.method == "POST":
        return render(request, "405.html", std_context(), status=405)

    em = ENVManipulator(settings.ENV_LOCATION)
    setup_step = em.read("setup_step")

    # TODO need to safety return a number from .env or appropriately handle the error
    if int(setup_step) < 2:
        return redirect("/")

    form = MDEditForm(request.POST)
    if form.is_valid():
        file_md_returned = form.cleaned_data["document_name"]
        text_md_returned = form.cleaned_data["text_md"]

        file_path = f"{ settings.MKDOCS_DOCS_LOCATION }{ file_md_returned }"

        if not os.path.isfile(file_path):
            return render(
                request, "500.html", context | std_context(), status=500
            )

        f = open(file_path, "w")
        f.write(text_md_returned)
        f.close()

        messages.success(
            request,
            f'Mark down file "{ file_md_returned }" has been successfully saved',
        )
        context = {
            "MDFileSelect": MDFileSelect(
                initial={"mark_down_file": file_md_returned}
            ),
            "text_md": MDEditForm(initial=request.POST),
            "document_name": file_md_returned,
        }
        return render(request, "edit_md.html", context | std_context())
    else:
        context = {"form": form}
        return render(request, "edit_md.html", context | std_context())

    # For mypy
    return render(request, "500.html", status=500)


def new_md(request: HttpRequest) -> HttpResponse:
    """ """

    if not (request.method == "GET" or request.method == "POST"):
        return render(request, "405.html", std_context(), status=405)

    if request.method == "GET":
        context = {"form": LogHazardForm()}
        return render(request, "new_md.html", context | std_context())

    # For mypy
    return render(request, "500.html", status=500)


def log_hazard(request: HttpRequest) -> HttpResponse:
    context: dict[str, Any] = {}
    gc: GitController

    if not (request.method == "GET" or request.method == "POST"):
        return render(request, "405.html", std_context(), status=405)

    if request.method == "GET":
        context = {"form": LogHazardForm()}
        return render(request, "log_hazard.html", context | std_context())

    if request.method == "POST":
        form = LogHazardForm(request.POST)
        if form.is_valid():
            hazard_title = form.cleaned_data["title"]
            hazard_body = form.cleaned_data["body"]
            hazard_labels = form.cleaned_data["labels"]
            gc = GitController()

            if gc.log_hazard(hazard_title, hazard_body, hazard_labels):
                messages.success(
                    request,
                    f"Hazard has been uploaded to GitHub",
                )
                context = {"form": LogHazardForm()}
                return render(
                    request, "log_hazard.html", context | std_context()
                )
            else:
                messages.error(
                    request,
                    f"Error with hazard upload to GitHub",
                )

                context = {"form": LogHazardForm(initial=request.POST)}

                return render(
                    request, "log_hazard.html", context | std_context()
                )
        else:
            context = {"form": form}
            return render(request, "log_hazard.html", context | std_context())

    # Should never really get here, but added for mypy
    return render(request, "500.html", std_context(), status=500)


def hazard_comment(request: HttpRequest, hazard_number: "str") -> HttpResponse:
    context: dict[str, Any] = {}
    gc: GitController
    open_hazard: dict = {}

    if not (request.method == "GET" or request.method == "POST"):
        return render(request, "405.html", std_context(), status=405)

    if request.method == "GET":
        gc = GitController()
        open_hazards_full = gc.open_hazards()

        for hazard in open_hazards_full:
            if hazard["number"] == int(hazard_number):
                open_hazard = hazard.copy()
                break

        context = {
            "open_hazard": open_hazard,
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


# TODO - testing needed
def open_hazards(request: HttpRequest) -> HttpResponse:
    context: dict[str, Any] = {}
    gc: GitController
    open_hazards: list[dict] = []

    if not (request.method == "GET" or request.method == "POST"):
        return render(request, "405.html", std_context(), status=405)

    if request.method == "GET":
        # TODO need to check github credentials are valid
        gc = GitController()
        open_hazards = gc.open_hazards()
        context = {"open_hazards": open_hazards}

        return render(request, "open_hazards.html", context | std_context())

    if request.method == "POST":
        return HttpResponse("POST handling not yet built")


def mkdoc_redirect(request: HttpRequest, path: str) -> HttpResponse:
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


# TODO - testing needed
def upload_to_github(request: HttpRequest) -> HttpResponse:
    context: dict[str, Any] = {}
    gc: GitController

    if not (request.method == "GET" or request.method == "POST"):
        return render(request, "405.html", std_context(), status=405)

    if request.method == "GET":
        context = {"form": UploadToGithub()}

        return render(
            request, "upload_to_github.html", context | std_context()
        )

    if request.method == "POST":
        form = UploadToGithub(request.POST)
        if form.is_valid():
            comment = form.cleaned_data["comment"]
            gc = GitController()
            # TODO - need to handle if branch is already up to date
            gc.commit_and_push(comment)
            messages.success(
                request,
                f"Uploaded to Github with a comment of '{ comment }'",
            )
            context = {"form": UploadToGithub()}
            return render(
                request, "upload_to_github.html", context | std_context()
            )

        else:
            context = {"form": form}
            return render(
                request, "upload_to_github.html", context | std_context()
            )


# -----


def std_context() -> dict[str, Any]:
    std_context_dict: dict[str, Any] = {}
    mkdoc_running: bool = False
    docs_available: bool = False
    # mkdocs

    mkdocs = MkdocsControl()
    mkdoc_running = mkdocs.is_process_running()

    em = ENVManipulator(settings.ENV_LOCATION)
    setup_step = em.read("setup_step")

    if setup_step == "2" or setup_step == "3":
        docs_available = True

    std_context_dict = {
        "START_AFRESH": settings.START_AFRESH,
        "mkdoc_running": mkdoc_running,
        "docs_available": docs_available,
    }

    return std_context_dict


def start_afresh(request: HttpRequest) -> HttpResponse:
    env_m: ENVManipulator
    mkdocs: MkdocsControl
    # root, dirs, files, d

    if not request.method == "GET":
        return render(request, "405.html", std_context(), status=405)

    if settings.START_AFRESH or settings.TESTING:
        for root, dirs, files in os.walk(settings.MKDOCS_DOCS_LOCATION):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

        env_m = ENVManipulator(settings.ENV_LOCATION)
        env_m.delete("setup_step")
        env_m.delete("GITHUB_REPO")
        env_m.delete("GITHUB_USERNAME_ORG")
        env_m.delete("GITHUB_TOKEN")

        mkdocs = MkdocsControl()
        if not mkdocs.stop(wait=True):
            return render(request, "500.html", status=500)
    return redirect("/")


def custom_404(request: HttpRequest, exception) -> HttpResponse:
    return render(request, "404.html", context=std_context(), status=404)


def custom_405(request: HttpRequest, exception) -> HttpResponse:
    return render(request, "405.html", context=std_context(), status=405)
