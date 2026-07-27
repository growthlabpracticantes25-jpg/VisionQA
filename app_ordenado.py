import os
import csv
from datetime import datetime

import streamlit as st
import cv2
import matplotlib.pyplot as plt
import pandas as pd
from openpyxl import Workbook

from modelo_ia import clasificar_imagen
from gemini_analisis import analizar_causas

# ---------------- APP PRINCIPAL ----------------

st.set_page_config(
    page_title="VisionQA",
    page_icon="🔍",
    layout="wide"
)


# -------- CARGAR ESTILOS CORPORATIVOS --------

with open("styles/styles.css", encoding="utf-8") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )


# -------- ESTADO DE LA INSPECCIÓN --------

if "inspeccion" not in st.session_state:
    st.session_state.inspeccion = False


# -------- ENCABEZADO --------

col_logo, col_texto = st.columns([1.2, 5.2])

with col_logo:
    st.image(
        "assets/logo_iot.png",
        width=230
    )

with col_texto:
    st.markdown(
        "<div style='padding-top:12px'></div>",
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="iot-title">VisionQA</div>'
        '<div class="iot-subtitle">'
        'Sistema Inteligente de Inspección Visual Asistido por Inteligencia Artificial'
        '</div>',
        unsafe_allow_html=True
    )

    st.divider()

def mostrar_estado_sistema():
    st.subheader("🟢 Estado del Sistema")

    st.success(
        """
        **Sistema listo para inspección**

        ✔ Modelo de IA cargado correctamente

        ✔ Gemini conectado

        ✔ Registro de inspecciones disponible
        """
    )

    st.divider()

mostrar_estado_sistema()
# -------- CARGAR DATOS DEL REGISTRO --------

total = 0
aptas = 0
no_aptas = 0

archivo_csv = "registro_inspecciones.csv"
os.makedirs("inspecciones", exist_ok=True)

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

                if fila[1] in ["APTO", "BUENA"]:
                    aptas += 1

                elif fila[1] in ["NO APTO", "MALA"]:
                    no_aptas += 1

def mostrar_modulo_inspeccion():
    archivo_csv = "registro_inspecciones.csv"
    st.subheader("🚀 Inspección")

    if st.button("Iniciar Inspección"):
        st.session_state.inspeccion = True
        st.rerun()

    # ---------------- MÓDULO DE INSPECCIÓN ----------------

    if st.session_state.inspeccion:

        # ---------------- CARGA DE ARCHIVO ----------------

        st.markdown("### 📂 Cargar imagen desde el equipo")
        st.caption("Sube una fotografía de la pieza para realizar la inspección.")

        archivo_subido = st.file_uploader(
            "Selecciona una imagen",
            type=["jpg", "jpeg", "png"]
        ) 
        # ---------------- CÁMARA ----------------
        st.divider()

        st.markdown("### 📷 Capturar imagen en tiempo real")
        st.caption("Toma una fotografía directamente desde la cámara conectada.")
        foto = st.camera_input("Toma una fotografía de la pieza")

        if archivo_subido is not None:

            nombre_original = archivo_subido.name 
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


            clasificacion = resultado["estado"]
            defecto = resultado["defecto"]
            confianza = resultado["confianza"]
            resultado_yolo = resultado["resultado_yolo"]

            st.subheader("Resultado de la Inspección")

            imagen_anotada = resultado_yolo.plot()

            imagen_anotada = cv2.cvtColor(
            imagen_anotada,
            cv2.COLOR_BGR2RGB
        )

            imagen_anotada = cv2.resize(
            imagen_anotada,
            (800, 600)
        )

            st.image(
            imagen_anotada,
            caption="Resultado de detección YOLO",
            use_container_width=False
        )
            if clasificacion == "APTO":
                st.markdown(
                    f"""
                    <div class="resultado-card">
                        <div class="resultado-titulo">Resultado de la Inspección</div>
                        <div class="resultado-estado-apto">✅ APTO</div>
                        <div class="resultado-info">
                            <b>Defecto detectado:</b> Ninguno<br>
                            <b>Confianza:</b> {confianza:.2f}%<br>
                            <b>Prioridad:</b> Baja<br>
                            <b>Acción recomendada:</b> Liberar pieza.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:
                st.markdown(
                    f"""
                    <div class="resultado-card">
                        <div class="resultado-titulo">Resultado de la Inspección</div>
                        <div class="resultado-estado-noapto">❌ NO APTO</div>
                        <div class="resultado-info">
                            <b>Defecto detectado:</b> {defecto}<br>
                            <b>Confianza:</b> {confianza:.2f}%<br>
                            <b>Prioridad:</b> Alta<br>
                            <b>Acción recomendada:</b> Retener pieza e inspeccionar manualmente.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

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
                    nombre_archivo,
                    nombre_original
                ])

            st.success("Imagen cargada y registrada correctamente")


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

            clasificacion = resultado["estado"]
            defecto = resultado["defecto"]
            confianza = resultado["confianza"]
            resultado_yolo = resultado["resultado_yolo"]

            st.subheader("Resultado de la Inspección")

            imagen_anotada = resultado_yolo.plot()

            imagen_anotada = cv2.cvtColor(
                imagen_anotada,
                cv2.COLOR_BGR2RGB
            )

            st.image(
                imagen_anotada,
                caption="Resultado de detección YOLO",
                use_container_width=True
            )

            if clasificacion == "APTO":

                st.markdown(
                    f"""
                    <div class="resultado-card">
                        <div class="resultado-titulo">Resultado de la Inspección</div>
                        <div class="resultado-estado-apto">✅ APTO</div>
                        <div class="resultado-info">
                            <b>Defecto detectado:</b> Ninguno<br>
                            <b>Confianza:</b> {confianza:.2f}%<br>
                            <b>Prioridad:</b> Baja<br>
                            <b>Acción recomendada:</b> Liberar pieza.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    f"""
                    <div class="resultado-card">
                        <div class="resultado-titulo">Resultado de la Inspección</div>
                        <div class="resultado-estado-noapto">❌ NO APTO</div>
                        <div class="resultado-info">
                            <b>Defecto detectado:</b> {defecto}<br>
                            <b>Confianza:</b> {confianza:.2f}%<br>
                            <b>Prioridad:</b> Alta<br>
                            <b>Acción recomendada:</b> Retener pieza e inspeccionar manualmente.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
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
                    nombre_archivo,
                    "Imagen capturada con cámara"
                ])

            st.success("Imagen capturada y guardada correctamente")

            st.write(f"Fecha y hora: {fecha_hora}")

            st.write(f"Archivo guardado: {nombre_archivo}") 

            

# -------- BOTÓN PRINCIPAL --------

st.divider()

# -------- DATOS DEL REGISTRO --------

def cargar_datos_registro():

    total = 0
    aptas = 0
    no_aptas = 0

    archivo_csv = "registro_inspecciones.csv"

    os.makedirs(
        "inspecciones",
        exist_ok=True
    )

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

                    if fila[1] in ["APTO", "BUENA"]:
                        aptas += 1

                    elif fila[1] in ["NO APTO", "MALA"]:
                        no_aptas += 1

    return total, aptas, no_aptas


# -------- RESUMEN --------

def mostrar_resumen(total, aptas, no_aptas):

    st.subheader("Resumen")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-icon">📦</div>
                <div class="kpi-value">{total}</div>
                <div class="kpi-label">Total de inspecciones</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-icon">✅</div>
                <div class="kpi-value">{aptas}</div>
                <div class="kpi-label">Piezas aptas</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-icon">❌</div>
                <div class="kpi-value">{no_aptas}</div>
                <div class="kpi-label">Piezas no aptas</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.caption(
        "Actualización automática con base en las inspecciones registradas."
    )


total, aptas, no_aptas = cargar_datos_registro()

mostrar_modulo_inspeccion()

mostrar_resumen(
    total,
    aptas,
    no_aptas
)

st.divider()
st.subheader("Estadísticas de Inspección")
col_graf1, col_graf2 = st.columns(2)

datos_grafica = {
    "Aptas": aptas,
    "No Aptas": no_aptas
}

with col_graf1:

    fig, ax = plt.subplots(figsize=(5,4))

    categorias = ["Aptas", "No Aptas"]
    valores = [aptas, no_aptas]

    ax.bar(
        categorias,
        valores,
        color=["#1D7EAE", "#DC3545"],
        width=0.55
    )

    ax.set_title(
        "Resultados de Inspección",
        fontsize=14,
        fontweight="bold",
        color="#231F20"
    )

    ax.set_ylabel("Cantidad")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()

    st.pyplot(fig)

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
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">📈</div>
            <div class="kpi-value">{porcentaje_apto:.1f}%</div>
            <div class="kpi-label">Tasa de aprobación</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col5:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">📉</div>
            <div class="kpi-value">{porcentaje_no_apto:.1f}%</div>
            <div class="kpi-label">Tasa de rechazo</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.divider() 

st.markdown(
    """
    <div class="inspection-card">
        <div class="inspection-title">🔎 Módulo de Inspección</div>
        <div class="inspection-subtitle">
            Selecciona el método de captura para evaluar la pieza.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# -------- GRÁFICA DE PASTEL --------

if inspecciones_validas > 0:

    st.subheader("Distribución de Resultados")

    fig, ax = plt.subplots()

    ax.pie(
    [aptas, no_aptas],
    labels=["Aptas", "No Aptas"],
    colors=["#1D7EAE", "#DC3545"],
    autopct="%1.1f%%",
    startangle=90,
    textprops={"fontsize":12}
)

ax.set_title(
    "Distribución de Resultados",
    fontsize=14,
    fontweight="bold",
    color="#231F20"
)

ax.axis("equal")

with col_graf2:
     st.pyplot(fig)


st.markdown(
    """
    <div class="inspection-card">
        <div class="inspection-title">📋 Registro de Inspecciones</div>
        <div class="inspection-subtitle">
            Historial de resultados generados durante las inspecciones.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

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

        st.markdown("### Última inspección registrada")

estado = ultima[1].strip()

if estado == "APTO" or estado == "BUENA":
    icono = "✅"
    texto_estado = "APTO"
    clase_estado = "resultado-estado-apto"

elif estado == "NO APTO" or estado == "MALA":
    icono = "❌"
    texto_estado = "NO APTO"
    clase_estado = "resultado-estado-noapto"

else:
    icono = "⚠️"
    texto_estado = "REVISIÓN MANUAL"
    clase_estado = "resultado-estado-revision"

st.markdown(
    f"""
    <div class="resultado-card">
        <div class="resultado-titulo">Última inspección</div>
       <div class="{clase_estado}">{icono} PIEZA NO APTA</div>
        <div class="resultado-info">
            <b>Fecha:</b> {ultima[0]}<br>
            <b>Archivo guardado:</b> {ultima[3]}<br>
            <b>Imagen original:</b> {ultima[4]}
        </div>
    </div>
    """,
    unsafe_allow_html=True
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

     df = pd.DataFrame(
    datos,
    columns=[
        "Fecha",
        "Resultado",
        "Confianza (%)",
        "Archivo Guardado",
        "Imagen Original"
    ]
)

    df = df.rename(columns={
    "Fecha": "📅 Fecha",
    "Resultado": "Estado",
    "Confianza (%)": "🎯 Confianza",
    "Archivo Guardado": "📁 Archivo",
    "Imagen Original": "🖼 Imagen"
})

    st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)
st.markdown("### 📥 Exportar Registro")

if st.button("Generar archivo Excel"):

    wb = Workbook()
    ws = wb.active
    ws.title = "Registro de Inspecciones"

    ws.append(df.columns.tolist())

    for fila in df.values.tolist():
        ws.append(fila)

    nombre_excel = "Registro_Inspecciones.xlsx"
    wb.save(nombre_excel)

    with open(nombre_excel, "rb") as archivo_excel:
        st.download_button(
            label="⬇ Descargar Excel",
            data=archivo_excel,
            file_name=nombre_excel,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

st.divider()

# -------- ANALIZAR CAUSAS --------

st.subheader("Análisis de Causas (IA)")

# -------- ÚLTIMA INSPECCIÓN --------

if st.button("Analizar Última Inspección"):

    if os.path.exists(archivo_csv):

        with open(archivo_csv, mode="r", encoding="utf-8") as archivo:
            lineas = archivo.readlines()

        if len(lineas) > 0:

            ultima_inspeccion = lineas[-1]

            with st.spinner("Gemini está analizando la última inspección..."):

                try:
                    resultado_gemini = analizar_causas(ultima_inspeccion)

                    st.subheader("🧠 Análisis IA de Última Inspección")
                    st.markdown(resultado_gemini)

                except Exception as e:
                    st.error("Ocurrió un error al conectar con Gemini.")
                    st.write(e)

        else:
            st.warning("No hay inspecciones registradas.")

    else:
        st.warning("No existe el archivo de inspecciones.")


# -------- ÚLTIMAS 10 INSPECCIONES --------

if st.button("Analizar Últimas 10 Inspecciones"):

    if os.path.exists(archivo_csv):

        with open(archivo_csv, mode="r", encoding="utf-8") as archivo:
            datos = archivo.readlines()

        datos_csv = "".join(datos[-10:])

        if datos_csv.strip() != "":

            with st.spinner("Gemini está analizando las causas..."):

                try:
                    resultado_gemini = analizar_causas(datos_csv)

                    st.subheader("🧠 Análisis IA - Gemini")
                    st.write(resultado_gemini)

                except Exception as e:
                    st.error("Ocurrió un error al conectar con Gemini.")
                    st.write(e)

        else:
            st.warning("El archivo de inspecciones está vacío.")

    else:
        st.warning("No existe el archivo de registro de inspecciones.")
st.divider()

st.markdown(
"""
<div class="footer">
<b>VisionQA v1.0</b><br>
Sistema Inteligente de Inspección Visual Asistido por Inteligencia Artificial
<hr>
Instituto Superior de Ciencias de Ciudad Juárez<br>
Proyecto desarrollado para IOT Technologies
<hr>
© 2026 VisionQA
</div>
""",
unsafe_allow_html=True
)