import os
import csv
from datetime import datetime
import streamlit as st
import cv2
import matplotlib.pyplot as plt

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

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total", total)

with col2:
    st.metric("Aptas", aptas)

with col3:
    st.metric("No Aptas", no_aptas)
st.subheader("Estadísticas de Inspección")

datos_grafica = {
    "Aptas": aptas,
    "No Aptas": no_aptas
}

st.bar_chart(datos_grafica)
# -------- KPIs --------

inspecciones_validas = aptas + no_aptas

if inspecciones_validas > 0:

    porcentaje_apto = (
        aptas / inspecciones_validas
    ) * 100

    porcentaje_no_apto = (
        no_aptas / inspecciones_validas
    ) * 100

    st.subheader("Indicadores de Calidad")

    col4, col5 = st.columns(2)

    with col4:
        st.metric(
            "Tasa de Aprobación",
            f"{porcentaje_apto:.1f}%"
        )

    with col5:
        st.metric(
            "Tasa de Rechazo",
            f"{porcentaje_no_apto:.1f}%"
        )

# -------- GRÁFICA DE PASTEL --------

if inspecciones_validas > 0:

    st.subheader("Distribución de Resultados")

    fig, ax = plt.subplots()

    ax.pie(
        [aptas, no_aptas],
        labels=["Aptas", "No Aptas"],
        autopct="%1.1f%%"
    )

    ax.axis("equal")

    st.pyplot(fig)
# -------- ANALIZAR CAUSAS --------

st.subheader("Análisis de Causas")

if st.button("Analizar Causas"):

    if inspecciones_validas > 0:

        porcentaje_rechazo = (
            no_aptas / inspecciones_validas
        ) * 100

        if porcentaje_rechazo < 20:

            st.success(
                f"""
                Nivel de rechazo: {porcentaje_rechazo:.1f}%

                El proceso presenta una
                condición estable.

                Recomendación:

                Mantener monitoreo continuo
                y control del proceso.
                """
            )

        elif porcentaje_rechazo < 40:

            st.warning(
                f"""
                Nivel de rechazo: {porcentaje_rechazo:.1f}%

                Se observa una tendencia
                moderada de defectos.

                Posibles causas:

                • Variación de material.
                • Ajustes de proceso.
                • Desgaste parcial de herramienta.

                Recomendación:

                Revisar parámetros críticos.
                """
            )

        else:

            st.error(
                f"""
                Nivel de rechazo: {porcentaje_rechazo:.1f}%

                Condición crítica detectada.

                Posibles causas:

                • Herramienta desgastada.
                • Problemas de calibración.
                • Variación significativa del proceso.

                Recomendación:

                Realizar análisis de causa raíz
                utilizando metodología 6M.
                """
            )
    else:

        st.success(
            """
            El proceso presenta una
            tendencia estable.

            La mayoría de las piezas
            cumplen con los criterios
            de calidad establecidos.

            Recomendación:

            Mantener monitoreo continuo
            del proceso.
            """
        )
st.button("Iniciar Inspección")

st.subheader("Registro de Inspecciones")

# -------- ÚLTIMA INSPECCIÓN --------

if os.path.exists(archivo_csv):

    with open(
        archivo_csv,
        mode="r",
        encoding="utf-8"
    ) as archivo:

        lector = csv.reader(archivo)

        datos = list(lector)

    if len(datos) > 0:

        ultima = datos[-1]

        st.subheader("Última Inspección")

        if ultima[1] == "APTO":

            st.success(
                f"""
                ✅ Última Inspección

                Fecha: {ultima[0]}

                Archivo: {ultima[2]}
                """
            )

        else:

            st.error(
                f"""
                ❌ Última Inspección

                Fecha: {ultima[0]}

                Archivo: {ultima[2]}
                """
            )

if os.path.exists(archivo_csv):

    with open(
        archivo_csv,
        mode="r",
        encoding="utf-8"
    ) as archivo:

        lector = csv.reader(archivo)

        datos = list(lector)

    if len(datos) > 0:
        st.table(datos)

    else:
        st.write("No hay inspecciones registradas")

st.subheader("Información del Proyecto")
st.write("Versión: 1.0")
st.write("Proyecto VisionQA - ISSCJ")

# ---------------- CARGA DE ARCHIVO ----------------

st.subheader("Cargar Imagen")

archivo_subido = st.file_uploader(
    "Selecciona una imagen",
    type=["jpg", "jpeg", "png"]
)
# ---------------- CÁMARA ----------------

st.subheader("Captura de Imagen")

foto = st.camera_input("Toma una fotografía de la pieza")

if archivo_subido is not None:

    st.image(archivo_subido)

    fecha_hora = datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )

    nombre_archivo = datetime.now().strftime(
        "archivo_%Y%m%d_%H%M%S.jpg"
    )

    ruta = os.path.join(
        "inspecciones",
        nombre_archivo
    )

    with open(ruta, "wb") as f:
        f.write(archivo_subido.getbuffer())

    resultado = clasificar_imagen(ruta)

    st.write("Resultado IA:")
    st.write(resultado)

    prob_buena = resultado[0][0]
    prob_mala = resultado[0][1]

    st.write("Prob Buena:", prob_buena)
    st.write("Prob Mala:", prob_mala)

    if prob_buena > prob_mala:
        clasificacion = "APTO"
        confianza = prob_buena * 100
    else:
        clasificacion = "NO APTO"
        confianza = prob_mala * 100

    st.subheader("Resultado de la Inspección")

    if clasificacion == "APTO":
        st.success(
            f"✅ APTO ({confianza:.2f}%)"
        )
    else:
        st.error(
            f"❌ NO APTO ({confianza:.2f}%)"
        )

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
            f"{confianza:.2f}",
            nombre_archivo
        ])

    st.success(
        "Imagen cargada y registrada correctamente"
    )
if foto is not None:

    st.image(foto)

    fecha_hora = datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )

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

    st.write("Resultado IA:")
    st.write(resultado)

    prob_buena = resultado[0][0]
    prob_mala = resultado[0][1]

    if prob_buena > prob_mala:
        clasificacion = "APTO"
        confianza = prob_buena * 100
    else:
        clasificacion = "NO APTO"
        confianza = prob_mala * 100

    st.subheader("Resultado de la Inspección")

    st.write("Prob Buena:", prob_buena)
    st.write("Prob Mala:", prob_mala)
    
    if clasificacion == "APTO":
        st.success(
            f"✅ APTO ({confianza:.2f}%)"
        )
    else:
        st.error(
            f"❌ NO APTO ({confianza:.2f}%)"
        )

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
            f"{confianza:.2f}",
            nombre_archivo
        ])

    st.success("Imagen capturada y guardada correctamente")

    st.write(f"Fecha y hora: {fecha_hora}")

    st.write(f"Archivo guardado: {nombre_archivo}")