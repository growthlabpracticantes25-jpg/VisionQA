from django.urls import path

from .views import (
    InspeccionListCreateView,
    cerrar_sesion,
    dashboard,
    login_usuario,
    pagina_login,
    recuperar_password,
)

urlpatterns = [
    path(
        "inspecciones/",
        InspeccionListCreateView.as_view(),
        name="inspecciones-list-create",
    ),

    path(
        "login/",
        pagina_login,
        name="login",
    ),

    path(
        "logout/",
        cerrar_sesion,
        name="cerrar-sesion",
    ),

    path(
        "dashboard/",
        dashboard,
        name="dashboard",
    ),

    path(
        "recuperar-password/",
        recuperar_password,
        name="recuperar-password",
    ),

    path(
        "login-api/",
        login_usuario,
        name="api-login",
    ),
]