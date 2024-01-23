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
        "start_afresh",
        views.start_afresh,
        name="start_afresh",
    ),
    path("md_edit/<project_id>", views.md_edit, name="md_edit"),
    path("md_saved/<project_id>", views.md_saved, name="md_saved"),
    path("md_new", views.md_new, name="md_new"),
    path("hazard_new/<project_id>", views.hazard_new, name="hazard_new"),
    path(
        "hazard_comment/<hazard_number>",
        views.hazard_comment,
        name="hazard_comment",
    ),
    path("hazards_open", views.hazards_open, name="hazards_open"),
    path(
        "mkdoc_redirect",
        RedirectView.as_view(url="mkdoc_redirect/home", permanent=False),
        name="mkdoc_redirect_home",
    ),
    path("mkdoc_redirect/<path>", views.mkdoc_redirect, name="mkdoc_redirect"),
    path("upload_to_github", views.upload_to_github, name="upload_to_github"),
    path("member", views.member_landing_page, name="member_landing_page"),
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
