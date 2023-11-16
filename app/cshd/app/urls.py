from django.urls import path
from app import views


urlpatterns = [
    path(
        "delete_mkdocs_content",
        views.delete_mkdocs_content,
        name="delete_mkdocs_content",
    ),
    path("", views.index, name="index"),
    path("new_setup", views.index, name="new_setup"),
    path(
        "placeholders_saved",
        views.placeholders_saved,
        name="placeholders_saved",
    ),
    path("edit_md", views.edit_md, name="edit_md"),
    path("saved_md", views.saved_md, name="saved_md"),
    path("log_hazard", views.log_hazard, name="log_hazard"),
]
