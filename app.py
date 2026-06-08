import os
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

st.subheader("Camara en tiempo real")

run_camera = st.checkbox("Activar cámara")

frame_window = st.image([])

if run_camera:
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    import time
    time.sleep(1)  # deja que la cámara encienda

    ret, frame = cap.read()

    if not ret or frame is None:
        st.error("No se pudo leer la cámara (frame vacío)")
    else:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_window.image(frame)

    cap.release()