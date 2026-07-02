import os
from modelo_yolo import detectar_defectos

carpetas = [
    ("Buenas", "Imagenes validacion/Buenas"),
    ("Malas", "Imagenes validacion/Malas")
]

for tipo, carpeta in carpetas:

    print("\n==============================")
    print(f"VALIDANDO IMÁGENES {tipo.upper()}")
    print("==============================")

    for archivo in os.listdir(carpeta):

        if archivo.lower().endswith((".jpg", ".jpeg", ".png")):

            ruta = os.path.join(carpeta, archivo)

            estado, detecciones = detectar_defectos(
                ruta,
                confianza_minima=0.10
            )

            print(f"\nImagen: {archivo}")
            print(f"Estado: {estado}")

            if detecciones:
                for d in detecciones:
                    print(f"- {d['defecto']} ({d['confianza']}%)")
            else:
                print("- Sin defectos detectados")