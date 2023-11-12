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
    path("variables_saved", views.variables_saved, name="variables_saved"),
]
