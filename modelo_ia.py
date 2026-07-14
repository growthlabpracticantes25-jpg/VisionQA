from pathlib import Path

from ultralytics import YOLO


RUTA_MODELO = Path("modelo IA/yolo/visionqa_yolo_v3_best.pt")

if not RUTA_MODELO.exists():
    raise FileNotFoundError(
        f"No se encontró el modelo YOLO en:\n{RUTA_MODELO.resolve()}"
    )

# Cargar el modelo una sola vez
modelo = YOLO(str(RUTA_MODELO))


def clasificar_imagen(ruta_imagen):
    """
    Analiza una imagen con YOLO.

    Devuelve un diccionario con:
    - estado: APTO o NO APTO
    - defecto: Rota, Manchada, Sin_backplate o None
    - confianza: porcentaje de confianza
    - resultado_yolo: objeto original de YOLO
    """

    resultados = modelo.predict(
        source=str(ruta_imagen),
        conf=0.25,
        save=False,
        verbose=False,
    )

    resultado = resultados[0]

    # Si no se detectó ningún defecto, la pieza se considera buena
    if resultado.boxes is None or len(resultado.boxes) == 0:
        return {
            "estado": "APTO",
            "defecto": None,
            "confianza": 100.0,
            "resultado_yolo": resultado,
        }

    confianzas = resultado.boxes.conf.cpu().tolist()
    clases = resultado.boxes.cls.cpu().tolist()

    indice_mejor = max(
        range(len(confianzas)),
        key=confianzas.__getitem__,
    )

    clase_id = int(clases[indice_mejor])
    confianza = float(confianzas[indice_mejor]) * 100
    defecto = resultado.names[clase_id]

    return {
        "estado": "NO APTO",
        "defecto": defecto,
        "confianza": confianza,
        "resultado_yolo": resultado,
    }