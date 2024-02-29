"""URL management

Manage the URL patterns for the app.
"""

from django.urls import path, re_path
from django.views.generic.base import RedirectView
from app import views

urlpatterns = [
    path("", views.index, name="index"),
    path(
        "setup-documents/<project_id>",
        views.setup_documents,
        name="setup_documents",
    ),
    path(
        "project-build-asap/<project_id>",
        views.project_build_asap,
        name="project_build_asap",
    ),
    path(
        "document-new/<project_id>",
        views.document_new,
        name="document_new",
    ),
    path(
        "document-update/<project_id>",
        views.document_update,
        name="document_update",
    ),
    path(
        "document-update-named/<project_id>/<document_name>",
        views.document_update_named,
        name="document_update_named",
    ),
    path(
        "entry-update/<project_id>/<entry_type>/<id_new>",
        views.entry_update,
        name="entry_update",
    ),
    path(
        "entry-select/<project_id>/<entry_type>",
        views.entry_select,
        name="entry_select",
    ),
    path(
        "member",
        views.member_landing_page,
        name="member_landing_page",
    ),
    path(
        "start-new-project",
        views.start_new_project,
        name="start_new_project",
    ),
    re_path(
        r"^view-docs/(?P<project_id>[^/]+)/(?P<doc_path>.*)/?$",
        views.view_docs,
        name="view_docs",
    ),
    path(
        "project-documents/<project_id>",
        views.project_documents,
        name="project_documents",
    ),
    path(
        "under-construction/<message>",
        views.under_construction,
        name="under_construction",
    ),
]
