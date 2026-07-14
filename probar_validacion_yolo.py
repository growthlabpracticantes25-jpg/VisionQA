from pathlib import Path
from ultralytics import YOLO

# Rutas del proyecto
RUTA_MODELO = Path("modelo IA/yolo/visionqa_yolo_v3_best.pt")
RUTA_VALIDACION = Path("dataset_yolo_v2/imagenes_validacion_yolo")

# Clases esperadas según cada carpeta
CLASES_ESPERADAS = {
    "buenas": None,
    "rota": "Rota",
    "manchada": "Manchada",
    "sin_backplate": "Sin_backplate",
}

EXTENSIONES_VALIDAS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def obtener_deteccion_principal(resultado):
    """Devuelve la clase con mayor confianza o None si no hubo detecciones."""
    if resultado.boxes is None or len(resultado.boxes) == 0:
        return None, 0.0

    confianzas = resultado.boxes.conf.cpu().tolist()
    clases = resultado.boxes.cls.cpu().tolist()

    indice_mejor = max(range(len(confianzas)), key=confianzas.__getitem__)
    clase_id = int(clases[indice_mejor])
    confianza = float(confianzas[indice_mejor])
    nombre_clase = resultado.names[clase_id]

    return nombre_clase, confianza


def main():
    if not RUTA_MODELO.exists():
        raise FileNotFoundError(
            f"No se encontró el modelo en:\n{RUTA_MODELO.resolve()}"
        )

    if not RUTA_VALIDACION.exists():
        raise FileNotFoundError(
            f"No se encontró la carpeta de validación en:\n"
            f"{RUTA_VALIDACION.resolve()}"
        )

    modelo = YOLO(str(RUTA_MODELO))

    total = 0
    aciertos = 0

    print("\nVALIDACIÓN DEL MODELO YOLO\n")

    for carpeta, clase_esperada in CLASES_ESPERADAS.items():
        ruta_carpeta = RUTA_VALIDACION / carpeta

        if not ruta_carpeta.exists():
            print(f"AVISO: No existe la carpeta {ruta_carpeta}")
            continue

        imagenes = [
            archivo
            for archivo in ruta_carpeta.iterdir()
            if archivo.is_file()
            and archivo.suffix.lower() in EXTENSIONES_VALIDAS
        ]

        print(f"\nClase esperada: {carpeta.upper()}")

        for imagen in sorted(imagenes):
            resultados = modelo.predict(
                source=str(imagen),
                conf=0.25,
                save=False,
                verbose=False,
            )

            clase_detectada, confianza = obtener_deteccion_principal(
                resultados[0]
            )

            if clase_esperada is None:
                correcto = clase_detectada is None
                esperado_texto = "Sin defecto"
            else:
                correcto = clase_detectada == clase_esperada
                esperado_texto = clase_esperada

            total += 1
            aciertos += int(correcto)

            detectado_texto = (
                clase_detectada if clase_detectada is not None else "Sin defecto"
            )

            print(
                f"{imagen.name} | "
                f"Esperado: {esperado_texto} | "
                f"Detectado: {detectado_texto} | "
                f"Confianza: {confianza * 100:.2f}% | "
                f"{'CORRECTO' if correcto else 'INCORRECTO'}"
            )

    porcentaje = (aciertos / total * 100) if total else 0

    print("\nRESUMEN")
    print(f"Imágenes evaluadas: {total}")
    print(f"Aciertos: {aciertos}")
    print(f"Errores: {total - aciertos}")
    print(f"Exactitud en imágenes nuevas: {porcentaje:.2f}%")


if __name__ == "__main__":
    main()