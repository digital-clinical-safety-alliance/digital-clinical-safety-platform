"""

"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from django.conf.urls import (
    handler400,
    handler403,
    handler404,
    handler500,
)

handler400 = "app.views.custom_400"
handler403 = "app.views.custom_403"
handler404 = "app.views.custom_404"
handler500 = "app.views.custom_500"

urlpatterns = [
    path("", include("app.urls")),
    path("admin/", admin.site.urls),
    path(
        "accounts/",
        include("django.contrib.auth.urls"),
    ),
    # TODO - should this be defined in Nginx?
    path(
        "favicon.ico",
        RedirectView.as_view(url="/static/favicon.ico"),
    ),
]
