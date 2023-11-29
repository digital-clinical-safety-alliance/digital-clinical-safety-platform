from django.urls import path
from django.views.generic.base import RedirectView
from app import views


urlpatterns = [
    path("", views.index, name="index"),
    path(
        "start_afresh",
        views.start_afresh,
        name="start_afresh",
    ),
    path("edit_md", views.edit_md, name="edit_md"),
    path("saved_md", views.saved_md, name="saved_md"),
    path("log_hazard", views.log_hazard, name="log_hazard"),
    path(
        "hazard_comment/<number>",
        views.hazard_comment,
        name="hazard_comment",
    ),
    path("open_hazards", views.open_hazards, name="open_hazards"),
    path(
        "mkdoc_redirect",
        RedirectView.as_view(url="mkdoc_redirect/home", permanent=False),
        name="mkdoc_redirect_home",
    ),
    path("mkdoc_redirect/<path>", views.mkdoc_redirect, name="mkdoc_redirect"),
    path("upload_to_github", views.upload_to_github, name="upload_to_github"),
]
