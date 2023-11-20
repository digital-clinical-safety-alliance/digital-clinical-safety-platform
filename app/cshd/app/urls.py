from django.urls import path
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
    path("mkdoc_redirect/<path>", views.mkdoc_redirect, name="mkdoc_redirect"),
]
