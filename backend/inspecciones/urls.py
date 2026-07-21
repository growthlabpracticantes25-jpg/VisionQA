from django.urls import path

from .views import InspeccionListCreateView


urlpatterns = [
    path(
        "inspecciones/",
        InspeccionListCreateView.as_view(),
        name="inspecciones-list-create",
    ),
]