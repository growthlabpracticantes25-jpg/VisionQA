from rest_framework import serializers
from .models import Inspeccion


class InspeccionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Inspeccion
        fields = "__all__"
        read_only_fields = ["id", "fecha"]