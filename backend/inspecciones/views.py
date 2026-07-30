from django.contrib.auth import (
    authenticate,
    login as auth_login,
    logout as auth_logout,
)
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required 
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Inspeccion
from .serializers import InspeccionSerializer


class InspeccionListCreateView(generics.ListCreateAPIView):
    queryset = Inspeccion.objects.all().order_by("-fecha")
    serializer_class = InspeccionSerializer


def pagina_login(request):
    error = None

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not username or not password:
            error = "Debes ingresar usuario y contraseña."

        else:
            usuario = authenticate(
                request=request,
                username=username,
                password=password,
            )

            if usuario is None:
                error = "Usuario o contraseña incorrectos."

            elif not usuario.is_active:
                error = "El usuario está desactivado."

            else:
                auth_login(request, usuario)

                return redirect(
                    "http://127.0.0.1:8501"
            )

    return render(
        request,
        "inspecciones/login.html",
        {
            "error": error,
        },
    )
@login_required
def cerrar_sesion(request):
    auth_logout(request)

    return redirect("login")
def dashboard(request):
    return render(
        request,
        "inspecciones/dashboard.html",
    )
def recuperar_password(request):

    if request.method == "POST":

        username = request.POST.get("username", "").strip()

        if username:

            return render(
                request,
                "inspecciones/recuperacion_exitosa.html"
            )

    return render(
        request,
        "inspecciones/recuperar_password.html"
    )

def login_usuario(request):
    username = request.data.get("username", "").strip()
    password = request.data.get("password", "")

    if not username or not password:
        return Response(
            {
                "success": False,
                "message": "Debes ingresar usuario y contraseña.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    usuario = authenticate(
        request=request,
        username=username,
        password=password,
    )

    if usuario is None:
        return Response(
            {
                "success": False,
                "message": "Usuario o contraseña incorrectos.",
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not usuario.is_active:
        return Response(
            {
                "success": False,
                "message": "El usuario está desactivado.",
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    return Response(
        {
            "success": True,
            "message": "Inicio de sesión correcto.",
            "username": usuario.username,
            "first_name": usuario.first_name,
            "is_staff": usuario.is_staff,
            "is_superuser": usuario.is_superuser,
        },
        status=status.HTTP_200_OK,
    )