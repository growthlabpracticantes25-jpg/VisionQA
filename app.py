import os
import csv
from datetime import datetime
import streamlit as st
import cv2

from modelo_ia import clasificar_imagen

# ---------------- APP PRINCIPAL ----------------

st.title("VisionQA")

st.write("Sistema de Control de Calidad Asistido por IA")

st.subheader("Estado del Sistema")
st.success("Sistema listo para inspección")

st.subheader("Resumen")

total = 0
aptas = 0
no_aptas = 0

archivo_csv = "registro_inspecciones.csv"

if os.path.exists(archivo_csv):

    with open(
        archivo_csv,
        mode="r",
        encoding="utf-8"
    ) as archivo:

        lector = csv.reader(archivo)

        for fila in lector:

            total += 1

            if len(fila) > 1:

                if fila[1] == "APTO" or fila[1] == "BUENA":
                    aptas += 1

                elif fila[1] == "NO APTO" or fila[1] == "MALA":
                    no_aptas += 1

st.write(f"Total inspecciones: {total}")
st.write(f"Piezas aptas: {aptas}")
st.write(f"Piezas no aptas: {no_aptas}")
st.button("Iniciar Inspección")

st.subheader("Registro de Inspecciones")
st.write("No hay inspecciones registradas")

st.subheader("Información del Proyecto")
st.write("Versión: 1.0")
st.write("Proyecto VisionQA - ISSCJ")

# ---------------- CÁMARA ----------------

st.subheader("Captura de Imagen")

foto = st.camera_input("Toma una fotografía de la pieza")

if foto is not None:

    st.image(foto)

    fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    nombre_archivo = datetime.now().strftime(
        "inspeccion_%Y%m%d_%H%M%S.jpg"
    )

    ruta = os.path.join(
        "inspecciones",
        nombre_archivo
    )

    with open(ruta, "wb") as f:
        f.write(foto.getbuffer())

    # -------- IA --------

    resultado = clasificar_imagen(ruta)

    prob_buena = resultado[0][0]
    prob_mala = resultado[0][1]

    if prob_buena > prob_mala:
        clasificacion = "APTO"
        confianza = prob_buena * 100
    else:
        clasificacion = "NO APTO"
        confianza = prob_mala * 100

    st.subheader("Resultado de la Inspección")

    if clasificacion == "APTO":
        st.success(f"✅ APTO ({confianza:.2f}%)")
    else:
        st.error(f"❌ NO APTO ({confianza:.2f}%)")

    # -------- CSV --------

    archivo_csv = "registro_inspecciones.csv"

    with open(
        archivo_csv,
        mode="a",
        newline="",
        encoding="utf-8"
    ) as archivo:

        escritor = csv.writer(archivo)

        escritor.writerow([
            fecha_hora,
            clasificacion,
            nombre_archivo
        ])

    st.success("Imagen capturada y guardada correctamente")

    st.write(f"Fecha y hora: {fecha_hora}")

    st.write(f"Archivo guardado: {nombre_archivo}")
