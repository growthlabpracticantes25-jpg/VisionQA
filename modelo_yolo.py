from ultralytics import YOLO

modelo = YOLO("runs/detect/train-4/weights/best.pt")


def detectar_defectos(ruta_imagen, confianza_minima=0.10):

    resultados = modelo.predict(
        source=ruta_imagen,
        conf=confianza_minima,
        save=False,
        verbose=False
    )

    detecciones = []

    for resultado in resultados:

        if resultado.boxes is None:
            continue

        for caja in resultado.boxes:

            clase = int(caja.cls[0])

            confianza = float(caja.conf[0])

            nombre = modelo.names[clase]

            detecciones.append({
                "defecto": nombre,
                "confianza": round(confianza * 100, 2)
            })

    if detecciones:
        estado = "NO APTO"
    else:
        estado = "APTO"

    return estado, detecciones