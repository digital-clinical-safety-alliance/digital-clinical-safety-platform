from django.shortcuts import render, redirect
import sys

sys.path.append("/app/cshd/app")
from form_elements import formElements
import os

sys.path.append("/docs_builder")
from docs_builder import Builder

import shutil

MKDOCS_DOCS = "/mkdocs/docs"

# TODO need to make sure this is not in the production environment
ALLOW_DOCS_DELETE = True

from .forms import PlaceholdersForm, MDEditForm


def index(request):
    context: dict = {}
    chosen_template: str = ""
    placeholders: dict = {}

    form_ptr = formElements()

    if request.method == "POST":
        # TODO: need to say where to read placeholders from (location wise)

        # TODO: need to clean this 'get' code
        # print(request.POST.get("templates", ""))
        chosen_template = request.POST.get("templates", "")

        shutil.copytree(
            f"/mkdocs/templates/{ chosen_template }",
            MKDOCS_DOCS,
            dirs_exist_ok=True,
        )

    if request.method == "POST" or (
        request.method == "GET" and os.listdir(MKDOCS_DOCS)
    ):
        doc_build = Builder()
        placeholders = doc_build.get_placeholders()

        context = {
            "ALLOW_DOCS_DELETE": ALLOW_DOCS_DELETE,
            "form": PlaceholdersForm(placeholders),
        }
        return render(request, "app/showPlaceholders.html", context)

    elif request.method == "GET" and not os.listdir(MKDOCS_DOCS):
        form_ptr.templates_HTML()

        context = {
            "templates_html": form_ptr.templates_HTML(),
            "ALLOW_DOCS_DELETE": ALLOW_DOCS_DELETE,
        }
        return render(request, "app/new_setup.html", context)
    else:
        return render(request, "app/500.html", context)


def placeholders_saved(request):
    context: dict = {}
    placeholders: dir = {}

    doc_build = Builder()
    placeholders = doc_build.get_placeholders()

    for p, v in placeholders.items():
        placeholders[p] = request.POST.get(p, "")
        print(f"*{p} - {placeholders[p]}*")

    doc_build.save_placeholders(placeholders)
    context["ALLOW_DOCS_DELETE"] = ALLOW_DOCS_DELETE

    return render(request, "app/placeholders_saved.html", context)


def edit_md(request):
    context: dict = {}
    text_md: dict = {}
    file_md: str = "index.md"

    with open(f"{ MKDOCS_DOCS }/{ file_md }", "r") as file:
        text_md["text_md"] = file.read()

    context = {
        "ALLOW_DOCS_DELETE": ALLOW_DOCS_DELETE,
        "text_md": MDEditForm(initial=text_md),
        "document_name": file_md,
    }
    return render(request, "app/edit_md.html", context)


def delete_mkdocs_content(request):
    if ALLOW_DOCS_DELETE:
        for root, dirs, files in os.walk(MKDOCS_DOCS):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

    response = redirect("/")
    return response
