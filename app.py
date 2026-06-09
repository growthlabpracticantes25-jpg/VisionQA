import os
import csv
from datetime import datetime
import streamlit as st
import cv2

# ---------------- APP PRINCIPAL ----------------

st.title("VisionQA")

st.write("Sistema de Control de Calidad Asistido por IA")

st.subheader("Estado del Sistema")
st.success("Sistema listo para inspección")

st.subheader("Resumen")
st.write("Total inspecciones: 0")
st.write("Piezas buenas: 0")
st.write("Piezas malas: 0")

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
            "PENDIENTE",
            nombre_archivo
        ])

    st.success("Imagen capturada y guardada correctamente")

    st.write(f"Fecha y hora: {fecha_hora}")

    st.write(f"Archivo guardado: {nombre_archivo}")