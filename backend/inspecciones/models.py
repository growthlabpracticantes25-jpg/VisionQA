from django.db import models


class Inspeccion(models.Model):

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    resultado = models.CharField(
        max_length=20
    )

    defecto = models.CharField(
        max_length=100,
        blank=True
    )

    confianza = models.FloatField()

    archivo = models.CharField(
        max_length=255
    )

    origen = models.CharField(
        max_length=50
    )

    def __str__(self):
        return (
            f"{self.fecha} - "
            f"{self.resultado}"
        )