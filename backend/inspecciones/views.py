from urllib.parse import quote
from django.contrib.auth.models import User 
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
from django.core import signing
from django.contrib.sessions.models import Session
from .models import Inspeccion
from django.utils import timezone 
from .serializers import InspeccionSerializer


class InspeccionListCreateView(generics.ListCreateAPIView):
    queryset = Inspeccion.objects.all().order_by("-fecha")
    serializer_class = InspeccionSerializer


def pagina_login(request):
    error = None

    if request.method == "POST":
        correo = request.POST.get("username", "").strip().lower()
        password = request.POST.get("password", "")

        if not correo or not password:
            error = "Debes ingresar correo electrónico y contraseña."

        else:
            try:
                usuario_encontrado = User.objects.get(email__iexact=correo)

            except User.DoesNotExist:
                error = "Correo electrónico o contraseña incorrectos."

            else:
                usuario = authenticate(
                    request=request,
                    username=usuario_encontrado.username,
                    password=password,
                )

                if usuario is None:
                    error = "Correo electrónico o contraseña incorrectos."

                elif not usuario.is_active:
                    error = "El usuario está desactivado."

                else:
                    auth_login(request, usuario)

                    # Asegurar que Django cree la sesión
                    if not request.session.session_key:
                        request.session.save()

                    token_acceso = signing.dumps(
                        {
                            "usuario_id": usuario.id,
                            "username": usuario.username,
                            "session_key": request.session.session_key,
                        },
                        salt="visionqa-streamlit",
                    )

                    token_codificado = quote(token_acceso)

                    return redirect(
                        f"http://127.0.0.1:8501/?token={token_codificado}"
                    )

    return render(
        request,
        "inspecciones/login.html",
        {
            "error": error,
        },
    )

def registrar_usuario(request):
    error = None

    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        username = request.POST.get("nuevo_usuario", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirmar_password = request.POST.get(
            "confirmar_password",
            ""
        )

        if not nombre or not username or not email:
            error = "Todos los campos son obligatorios."

        elif not password or not confirmar_password:
            error = "Debes ingresar y confirmar la contraseña."

        elif password != confirmar_password:
            error = "Las contraseñas no coinciden."

        elif User.objects.filter(username=username).exists():
            error = "El nombre de usuario ya está registrado."

        elif User.objects.filter(email=email).exists():
            error = "El correo electrónico ya está registrado."

        else:
            usuario = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )

            usuario.first_name = nombre
            usuario.save()

            return redirect("login")

    return render(
        request,
        "inspecciones/registro.html",
        {
            "error": error,
        },
    )

@api_view(["GET"])
@permission_classes([AllowAny])
def verificar_acceso_streamlit(request):

    token = request.GET.get("token", "").strip()

    if not token:

        return Response(
            {
                "autenticado": False,
                "mensaje": "No se recibió el token de acceso.",
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    try:

        datos = signing.loads(
            token,
            salt="visionqa-streamlit",
            max_age=60 * 60 * 8,
        )

        usuario_id = datos.get("usuario_id")
        username = datos.get("username")
        session_key = datos.get("session_key")

        if not usuario_id or not username or not session_key:

            raise signing.BadSignature(
                "El token no contiene los datos necesarios."
            )

        # Comprobar que la sesión de Django siga activa.
        sesion_activa = Session.objects.filter(
            session_key=session_key,
             expire_date__gt=timezone.now(),
        ).exists()

        if not sesion_activa:

            return Response(
                {
                    "autenticado": False,
                    "mensaje": "La sesión ya no está activa.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        usuario = User.objects.filter(
            id=usuario_id,
            username=username,
            is_active=True,
        ).first()

        if usuario is None:

            return Response(
                {
                    "autenticado": False,
                    "mensaje": "El usuario no es válido.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(
            {
                "autenticado": True,
                "username": usuario.username,
                "first_name": usuario.first_name,
                "is_staff": usuario.is_staff,
            },
            status=status.HTTP_200_OK,
        )

    except signing.SignatureExpired:

        return Response(
            {
                "autenticado": False,
                "mensaje": "El acceso ha expirado.",
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    except signing.BadSignature:

        return Response(
            {
                "autenticado": False,
                "mensaje": "El acceso no es válido.",
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )
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
    correo = request.data.get("username", "").strip().lower()
    password = request.data.get("password", "")

    if not correo or not password:
        return Response(
            {
                "success": False,
                "message": "Debes ingresar correo electrónico y contraseña.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        usuario_encontrado = User.objects.get(email__iexact=correo)
    except User.DoesNotExist:
        return Response(
            {
                "success": False,
                "message": "Correo electrónico o contraseña incorrectos.",
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    usuario = authenticate(
        request=request,
        username=usuario_encontrado.username,
        password=password,
    )

    if usuario is None:
        return Response(
            {
                "success": False,
                "message": "Correo electrónico o contraseña incorrectos.",
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