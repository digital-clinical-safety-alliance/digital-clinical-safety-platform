"""URL management
"""
from django.urls import path
from django.views.generic.base import RedirectView
from app import views

"""URL patterns
"""
urlpatterns = [
    path("", views.index, name="index"),
    path(
        "start_afresh",
        views.start_afresh,
        name="start_afresh",
    ),
    path("md_edit", views.md_edit, name="md_edit"),
    path("md_saved", views.md_saved, name="md_saved"),
    path("md_new", views.md_new, name="md_new"),
    path("hazard_log", views.hazard_log, name="hazard_log"),
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
]
