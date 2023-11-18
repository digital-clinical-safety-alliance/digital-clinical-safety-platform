from django.urls import path
from app import views


urlpatterns = [
    path("", views.index, name="index"),
    path(
        "start_afresh",
        views.start_afresh,
        name="start_afresh",
    ),
    path("new_setup", views.index, name="new_setup"),
    path(
        "placeholders_saved",
        views.placeholders_saved,
        name="placeholders_saved",
    ),
    path("edit_md", views.edit_md, name="edit_md"),
    path("saved_md", views.saved_md, name="saved_md"),
    path("log_hazard", views.log_hazard, name="log_hazard"),
    path(
        "template_select",
        views.template_select,
        name="template_select",
    ),
    path("mkdoc_redirect/<path>", views.mkdoc_redirect, name="mkdoc_redirect"),
]
