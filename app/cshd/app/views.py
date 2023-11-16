from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
import sys
from fnmatch import fnmatch

sys.path.append("/app/cshd/app")
from form_elements import formElements
import os

sys.path.append("/docs_builder")
from docs_builder import Builder

import shutil

MKDOCS_DOCS = "/mkdocs/docs"

# TODO need to make sure this is not in the production environment
ALLOW_DOCS_DELETE = True

from .forms import PlaceholdersForm, MDEditForm, MDFileSelect


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
        "ALLOW_DOCS_DELETE": ALLOW_DOCS_DELETE,
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
                "ALLOW_DOCS_DELETE": ALLOW_DOCS_DELETE,
                "MDFileSelect": MDFileSelect(
                    initial={"mark_down_file": file_md_returned}
                ),
                "text_md": MDEditForm(initial=request.POST),
                "document_name": file_md_returned,
            }
            return render(request, "app/edit_md.html", context)
        else:
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
        "ALLOW_DOCS_DELETE": ALLOW_DOCS_DELETE,
        "form": MDFileSelect(),
        "msg": msg,
    }

    return render(request, "app/log_hazard.html", context)


# -----


def delete_mkdocs_content(request):
    if ALLOW_DOCS_DELETE:
        for root, dirs, files in os.walk(MKDOCS_DOCS):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

    return redirect("/")


# custom 404 view
def custom_404(request, exception):
    return render(request, "app/404.html", status=404)
