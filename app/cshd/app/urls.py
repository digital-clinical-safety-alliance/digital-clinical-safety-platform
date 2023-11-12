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
]
