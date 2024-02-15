"""URL management
"""

from django.urls import path, re_path
from django.views.generic.base import RedirectView
from app import views

"""URL patterns
"""
urlpatterns = [
    path("", views.index, name="index"),
    path(
        "setup_documents/<project_id>",
        views.setup_documents,
        name="setup_documents",
    ),
    path(
        "project_build_asap/<project_id>",
        views.project_build_asap,
        name="project_build_asap",
    ),
    path(
        "document_update/<project_id>",
        views.document_update,
        name="document_update",
    ),
    path(
        "document_new/<project_id>",
        views.document_new,
        name="document_new",
    ),
    path(
        "entry_update/<project_id>/<entry_type>/<id_new>",
        views.entry_update,
        name="entry_update",
    ),
    path(
        "entry_select/<project_id>/<entry_type>",
        views.entry_select,
        name="entry_select",
    ),
    path(
        "member",
        views.member_landing_page,
        name="member_landing_page",
    ),
    path(
        "start_new_project",
        views.start_new_project,
        name="start_new_project",
    ),
    re_path(
        r"^view_docs/(?P<project_id>[^/]+)/(?P<doc_path>.*)/?$",
        views.view_docs,
        name="view_docs",
    ),
    path(
        "project_documents/<project_id>",
        views.project_documents,
        name="project_documents",
    ),
]
