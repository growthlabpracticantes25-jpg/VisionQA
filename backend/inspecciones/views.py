from rest_framework import generics

from .models import Inspeccion
from .serializers import InspeccionSerializer


class InspeccionListCreateView(generics.ListCreateAPIView):

    queryset = Inspeccion.objects.all().order_by("-fecha")
    serializer_class = InspeccionSerializer