from django.urls import path

from .views import (
    InspeccionListCreateView,
    login_usuario
)

urlpatterns = [
    path(
        "inspecciones/",
        InspeccionListCreateView.as_view(),
        name="inspecciones-list-create",
    ),

    path(
        "login/",
        login_usuario,
        name="login",
    ),
]