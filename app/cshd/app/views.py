from django.shortcuts import render
import sys

sys.path.append("/app/cshd/app")
from form_elements import formElements
import os

sys.path.append("/docs_builder")
from docs_builder import Builder

import shutil

trans = {
    "yes": "qui",
    "no": "noi",
    "portal": "portal",
    "Search": "Search",
}

test_placeholders = {
    "author_name": "Mark Bailey",
    "project_name": "Clinical Safety Hazard Documentation App",
    "hazard_log_url": "TBC",
    "organisation_name": "Clinicians-Who-Code",
    "clinical_safety_team_name": "Clinicians-Who-Code",
    "clinical_safety_officer_name": "Mark Bailey",
    "clinical_safety_officer_contact": "mark.bailey5@nhs.net",
    "security_responsible_disclosure_email": "mark.bailey5@nhs.net",
    "__project_slug": "TBC",
}

MKDOCS_DOCS = "/mkdocs/docs"


def index(request):
    context = {}
    context["trans"] = trans

    form_ptr = formElements()

    if request.method == "GET":
        if os.listdir(MKDOCS_DOCS):
            context["placeholders_html"] = form_ptr.create_elements(
                test_placeholders
            )
            return render(request, "app/index.html", context)
        else:
            form_ptr.templates_HTML()
            # print(form_ptr.templates_HTML())
            context["templates_html"] = form_ptr.templates_HTML()
            return render(request, "app/new_setup.html", context)
    elif request.method == "POST":
        # TODO: need to say where to read placeholders from (location wise)
        
        shutil.copytree(
            "/mkdocs/templates/DCB0129", "/mkdocs/docs", dirs_exist_ok=True
        )
        context["placeholders_html"] = form_ptr.create_elements(
            test_placeholders
        )
        return render(request, "app/index.html", context)
    else:
        return render(request, "app/500.html", context)

    return
