from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
import sys
from fnmatch import fnmatch
from dotenv import load_dotenv, set_key, find_dotenv, dotenv_values

sys.path.append("/cshd/app/cshd/app")
from form_elements import formElements
import os
from os import environ

sys.path.append("/cshd/docs_builder")
from docs_builder import Builder

import shutil

sys.path.append("/cshd/app/cshd/app/functions")
from env_manipulation import ENVManipulator
from mkdocs_control import MkdocsControl

MKDOCS_DOCS = "/cshd/mkdocs/docs"
MKDOCS = "/cshd/mkdocs"

# TODO need to make sure this is not in the production environment
START_AFRESH = True

from .forms import (
    PlaceholdersForm,
    MDEditForm,
    MDFileSelect,
    GitHubCredentialsForm,
)


def index(request, forwarder=""):
    context: dict = {}
    chosen_template: str = ""
    placeholders: dict = {}
    github_username: str | None = None
    github_token: str | None = None

    form_ptr = formElements()

    if not (request.method == "POST" or request.method == "GET"):
        return render(request, "app/500.html", context)

    # 'environ.get' does not handle a change of envs very well, so used
    # 'env_variables = dotenv_values(find_dotenv())' instead
    if request.method == "GET":
        env_variables = dotenv_values(find_dotenv())
        github_username = env_variables.get("GITHUB_USERNAME")
        github_token = env_variables.get("GITHUB_TOKEN")

        if not (github_username and github_token):
            context = {
                "START_AFRESH": START_AFRESH,
                "form": GitHubCredentialsForm(),
            }
            return render(request, "app/installation_method.html", context)

    if forwarder == "template_select":
        if not os.listdir(MKDOCS_DOCS):
            print(2)
            form_ptr.templates_HTML()

            context = {
                "templates_html": form_ptr.templates_HTML(),
                "START_AFRESH": START_AFRESH,
            }
            return render(request, "app/template_select.html", context)

    if request.method == "POST":
        # TODO: need to say where to read placeholders from (location wise)

        # TODO: need to clean this 'get' code to use a Forms template
        chosen_template = request.POST.get("templates", "")
        print(f"{ MKDOCS }/templates/{ chosen_template }")
        shutil.copytree(
            f"{ MKDOCS }/templates/{ chosen_template }",
            MKDOCS_DOCS,
            dirs_exist_ok=True,
        )

        messages.success(
            request,
            f"{ chosen_template } selected and markdown files copied to mkdocs folder",
        )

    if request.method == "POST" or (
        request.method == "GET" and os.listdir(MKDOCS_DOCS)
    ):
        print(1)
        doc_build = Builder()
        placeholders = doc_build.get_placeholders()

        context = {
            "START_AFRESH": START_AFRESH,
            "form": PlaceholdersForm(placeholders),
        }
        return render(request, "app/showPlaceholders.html", context)

    elif request.method == "GET" and not os.listdir(MKDOCS_DOCS):
        print(2)
        form_ptr.templates_HTML()

        context = {
            "templates_html": form_ptr.templates_HTML(),
            "START_AFRESH": START_AFRESH,
        }
        return render(request, "app/new_setup.html", context)


def template_select(request):
    if not (request.method == "GET" or request.method == "POST"):
        return render(request, "app/500.html")

    if request.method == "GET":
        return redirect("/")

    if request.method == "POST":
        form = GitHubCredentialsForm(request.POST)
        if form.is_valid():
            env_m = ENVManipulator()
            file_md_returned = env_m.add(
                "GITHUB_USERNAME", form.cleaned_data["github_username"]
            )
            file_md_returned = env_m.add(
                "GITHUB_TOKEN", form.cleaned_data["github_token"]
            )

            messages.success(
                request,
                f"Github credentials Saved",
            )

            return index(request, "template_select")
            # return redirect("/")
        else:
            # TODO: need to appropriately handle form errors with error messages
            return HttpResponse("Error")

    context = {
        "START_AFRESH": START_AFRESH,
        "form": MDFileSelect(),
    }

    return render(request, "app/log_hazard.html", context)


def placeholders_saved(request):
    context: dict = {}
    placeholders: dir = {}

    doc_build = Builder()
    placeholders = doc_build.get_placeholders()

    for p, v in placeholders.items():
        placeholders[p] = request.POST.get(p, "")
        print(f"*{p} - {placeholders[p]}*")

    messages.success(
        request,
        f"Placeholders saved",
    )

    doc_build.save_placeholders(placeholders)
    context["START_AFRESH"] = START_AFRESH

    # mc = MkdocsControl()
    # mc.start()
    return render(request, "app/placeholders_saved.html", context)


def edit_md(request):
    context: dict = {}
    files_md: list[str] = []

    if not (request.method == "GET" or request.method == "POST"):
        return render(request, "app/500.html")

    if request.method == "GET":
        if not os.path.isdir(MKDOCS_DOCS):
            # TODO: need to have a better error response here
            return HttpResponse("ERROR!")

        for path, subdirs, files in os.walk(MKDOCS_DOCS):
            for name in files:
                if fnmatch(name, "*.md"):
                    files_md.append(name)
                    print(f"***{name}")
                    # TODO ? add a break to run only once?

    elif request.method == "POST":
        form = MDFileSelect(request.POST)
        if form.is_valid():
            files_md.append(form.cleaned_data["mark_down_file"])

    with open(f"{ MKDOCS_DOCS }/{ files_md[0] }", "r") as file:
        form_fields = {"text_md": file.read(), "document_name": files_md[0]}

    context = {
        "START_AFRESH": START_AFRESH,
        "MDFileSelect": MDFileSelect(initial={"mark_down_file": files_md[0]}),
        "text_md": MDEditForm(initial=form_fields),
        "document_name": files_md[0],
    }
    print(context)
    return render(request, "app/edit_md.html", context)


def saved_md(request):
    context: dict = {}
    text_md: dict = {}
    text_md_returned: str = ""
    file_md_returned: str = ""

    if request.method == "GET":
        return redirect("/edit_md")
    elif request.method == "POST":
        form = MDEditForm(request.POST)
        if form.is_valid():
            file_md_returned = form.cleaned_data["document_name"]
            text_md_returned = form.cleaned_data["text_md"]

            f = open(f"{ MKDOCS_DOCS }/{ file_md_returned }", "w")
            f.write(text_md_returned)
            f.close()

            messages.success(
                request,
                f'Mark down file "{ file_md_returned }" has been successfully saved',
            )
            context = {
                "START_AFRESH": START_AFRESH,
                "MDFileSelect": MDFileSelect(
                    initial={"mark_down_file": file_md_returned}
                ),
                "text_md": MDEditForm(initial=request.POST),
                "document_name": file_md_returned,
            }
            return render(request, "app/edit_md.html", context)
        else:
            # TODO: need to rebuild form with error messages
            return HttpResponse("Error")

        return HttpResponse("You're looking at question %s." % question_id)
    else:
        return render(request, "app/500.html", context)


def log_hazard(request):
    msg: str = ""

    if not (request.method == "GET" or request.method == "POST"):
        return render(request, "app/500.html")

    if request.method == "GET":
        msg = "GET"

    elif request.method == "POST":
        msg = "POST"

    context = {
        "START_AFRESH": START_AFRESH,
        "form": MDFileSelect(),
        "msg": msg,
    }

    return render(request, "app/log_hazard.html", context)


def mkdoc_redirect(request, path):
    mc = MkdocsControl()
    mc.start()
    print("Redirecting...")
    if path == "home":
        return redirect(f"http://localhost:9000")
    else:
        return redirect(f"http://localhost:9000/{ path }")


# -----


def start_afresh(request):
    if START_AFRESH:
        for root, dirs, files in os.walk(MKDOCS_DOCS):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

        env_m = ENVManipulator()
        env_m.delete("GITHUB_USERNAME")
        env_m.delete("GITHUB_TOKEN")
    return redirect("/")


# custom 404 view
def custom_404(request, exception):
    return render(request, "app/404.html", status=404)
