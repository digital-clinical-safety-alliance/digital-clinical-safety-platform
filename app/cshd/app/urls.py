from django.urls import path
from app import views

urlpatterns = [
    path("", views.index, name="index"),
    path("new_setup", views.index, name="new_setup"),
]
