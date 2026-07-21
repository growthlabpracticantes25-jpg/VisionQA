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
from streamlit_option_menu import option_menu

# ---------------- APP PRINCIPAL ----------------

st.set_page_config(
    page_title="VisionQA",
    page_icon="🔍",
    layout="wide"
)
# ---------------- ESTILOS ----------------

with open("styles/styles.css", encoding="utf-8") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )
    st.markdown(
    """
    <link rel="stylesheet"
    href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    """,
    unsafe_allow_html=True
)
# ---------------- VARIABLES GLOBALES ----------------

archivo_csv = "registro_inspecciones.csv"

os.makedirs(
    "inspecciones",
    exist_ok=True
)

if "inspeccion" not in st.session_state:
    st.session_state.inspeccion = False
# ---------------- FUNCIONES ----------------


def mostrar_titulo(titulo, subtitulo):

    html = (
        f'<div class="page-header">'
        f'<div class="page-title">{titulo}</div>'
        f'<div class="page-subtitle">{subtitulo}</div>'
        f'</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True
    )

    st.divider()
def mostrar_encabezado_seccion(titulo, descripcion=""):

    html = (
        '<div class="section-header">'
        f'<div class="section-title">{titulo}</div>'
        f'<div class="section-description">{descripcion}</div>'
        '</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True
    )
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

def cargar_datos_registro():

    total = 0
    aptas = 0
    no_aptas = 0

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

def mostrar_modulo_inspeccion():

    mostrar_titulo(
        "Inspección Visual",
        "Analiza una pieza mediante una imagen local o una fotografía."
    )

    mostrar_encabezado_seccion(
        "Método de inspección",
        "Selecciona cómo deseas capturar la pieza para iniciar el análisis."
    )

    col_metodo_1, col_metodo_2 = st.columns(2)

    with col_metodo_1:

        if st.button(
            "Cargar imagen",
            key="seleccionar_carga",
            use_container_width=True
        ):
            st.session_state["metodo_inspeccion"] = "Cargar imagen"

    with col_metodo_2:

        if st.button(
            "Tomar fotografía",
            key="seleccionar_camara",
            use_container_width=True
        ):
            st.session_state["metodo_inspeccion"] = "Tomar fotografía"

    if "metodo_inspeccion" not in st.session_state:
        st.session_state["metodo_inspeccion"] = "Cargar imagen"

    opcion = st.session_state["metodo_inspeccion"]

    # -------- PROCESAR Y REGISTRAR INSPECCIÓN --------

    def procesar_inspeccion(
        imagen,
        nombre_archivo,
        origen
    ):

        ruta_imagen = os.path.join(
            "inspecciones",
            nombre_archivo
        )

        with open(
            ruta_imagen,
            "wb"
        ) as archivo:

            archivo.write(
                imagen.getbuffer()
            )

        with st.spinner(
            "La inteligencia artificial está analizando la pieza..."
        ):

            respuesta_modelo = clasificar_imagen(
                ruta_imagen
            )
        
        # -------- INTERPRETAR RESPUESTA DEL MODELO --------

        if isinstance(respuesta_modelo, dict):

            resultado = respuesta_modelo.get(
                "estado",
                "DESCONOCIDO"
            )

            confianza = respuesta_modelo.get(
                "confianza",
                0.0
            )

            defecto = respuesta_modelo.get(
                "defecto",
                None
            )

            resultado_yolo = respuesta_modelo.get(
                "resultado_yolo"
            )

            if resultado_yolo is not None:
                imagen_resultado = resultado_yolo.plot()
            else:
                imagen_resultado = None

        else:

            st.error(
                "No fue posible interpretar la respuesta del modelo."
            )
            return

        # -------- MOSTRAR RESULTADO --------

        st.subheader("Resultado de la Inspección")

        resultado_normalizado = str(
            resultado
        ).strip().upper()

        if resultado_normalizado in [
            "APTO",
            "BUENA"
        ]:

            resultado_registro = "APTO"
            st.success("✅ PIEZA APTA")

        elif resultado_normalizado in [
            "NO APTO",
            "MALA"
        ]:

            resultado_registro = "NO APTO"
            st.error("❌ PIEZA NO APTA")

            if defecto:
                st.markdown(
                    f"**Defecto detectado:** "
                    f"{str(defecto).replace('_', ' ').title()}"
                )

        else:

            resultado_registro = resultado_normalizado
            st.warning(
                f"⚠ Resultado: {resultado_normalizado}"
            )

        try:
            confianza_numero = float(confianza)
        except (TypeError, ValueError):
            confianza_numero = 0.0

        # Si la confianza viene entre 0 y 1,
        # se convierte a porcentaje
        if confianza_numero <= 1:
            confianza_porcentaje = confianza_numero * 100
        else:
            confianza_porcentaje = confianza_numero

        st.metric(
            "Confianza del modelo",
            f"{confianza_porcentaje:.2f}%"
        )

        # -------- MOSTRAR IMAGEN PROCESADA --------

        if imagen_resultado is not None:

            try:
                imagen_rgb = cv2.cvtColor(
                    imagen_resultado,
                    cv2.COLOR_BGR2RGB
                )

                st.image(
                    imagen_rgb,
                    caption="Resultado procesado por VisionQA",
                    use_container_width=True
                )

            except Exception:

                st.image(
                    imagen_resultado,
                    caption="Resultado procesado por VisionQA",
                    use_container_width=True
                )

        # -------- GUARDAR EN CSV --------

        fecha_hora = datetime.now().strftime(
            "%d/%m/%Y %H:%M:%S"
        )

        nueva_fila = [
            fecha_hora,
            resultado_registro,
            f"{confianza_porcentaje:.2f}",
            nombre_archivo,
            origen
        ]

        with open(
            archivo_csv,
            mode="a",
            newline="",
            encoding="utf-8"
        ) as archivo:

            escritor = csv.writer(archivo)
            escritor.writerow(nueva_fila)

        st.success(
            "La inspección fue registrada correctamente."
        )

    # -------- CARGAR IMAGEN --------

    if opcion == "Cargar imagen":

        archivo_subido = st.file_uploader(
            "Selecciona una imagen de la pieza",
            type=[
                "jpg",
                "jpeg",
                "png"
            ],
            key="imagen_cargada"
        )

        if archivo_subido is not None:

            st.image(
                archivo_subido,
                caption="Imagen seleccionada",
                use_container_width=True
            )

            if st.button(
                "🔍 Analizar imagen",
                key="boton_analizar_archivo",
                use_container_width=True
            ):

                nombre_archivo = datetime.now().strftime(
                    "archivo_%Y%m%d_%H%M%S.jpg"
                )

                procesar_inspeccion(
                    archivo_subido,
                    nombre_archivo,
                    "Archivo local"
                )

    # -------- TOMAR FOTOGRAFÍA --------

    elif opcion == "Tomar fotografía":

        fotografia = st.camera_input(
            "Coloca la pieza frente a la cámara",
            key="fotografia_camara"
        )

        if fotografia is not None:

            if st.button(
                "📷 Analizar fotografía",
                key="boton_analizar_camara",
                use_container_width=True
            ):

                nombre_archivo = datetime.now().strftime(
                    "inspeccion_%Y%m%d_%H%M%S.jpg"
                )

                procesar_inspeccion(
                    fotografia,
                    nombre_archivo,
                    "Cámara"
                )

    st.divider()

def mostrar_resumen(total, aptas, no_aptas):

    mostrar_encabezado_seccion(
        "Resumen general",
        "Indicadores principales de las inspecciones registradas."
    )

    col1, col2, col3 = st.columns(3)

    tarjetas = [
        (
            "bi bi-clipboard-data",
            total,
            "Total de inspecciones",
            "Registros almacenados"
        ),
        (
            "bi bi-check-circle",
            aptas,
            "Piezas aptas",
            "Cumplen con calidad"
        ),
        (
            "bi bi-exclamation-triangle",
            no_aptas,
            "Piezas no aptas",
            "Requieren revisión"
        ),
    ]

    for columna, (icono, valor, titulo, descripcion) in zip(
        [col1, col2, col3],
        tarjetas
    ):

        with columna:

            html = (
                f'<div class="kpi-card">'
                f'<div class="kpi-icon">'
                f'<i class="{icono}"></i>'
                f'</div>'
                f'<div class="kpi-title">{titulo}</div>'
                f'<div class="kpi-value">{valor}</div>'
                f'<div class="kpi-description">{descripcion}</div>'
                f'</div>'
            )

            st.markdown(
                html,
                unsafe_allow_html=True
            )

    st.caption(
        "Actualización automática basada en las inspecciones registradas."
    )

    st.divider()

def mostrar_graficas(aptas, no_aptas):

    mostrar_encabezado_seccion(
        "Análisis de inspección",
        "Comparación visual entre piezas aptas y no aptas."
    )

    col_graf1, col_graf2 = st.columns(2)

    # -------- GRÁFICA DE BARRAS --------

    with col_graf1:

        with st.container(border=True):

            st.markdown(
                '<div class="chart-title">Resultados de Inspección</div>',
                unsafe_allow_html=True
            )

            fig, ax = plt.subplots(figsize=(5, 3.2))

            categorias = [
                "Aptas",
                "No Aptas"
            ]

            valores = [
                aptas,
                no_aptas
            ]

            barras = ax.bar(
                categorias,
                valores,
                color=["#1D7EAE", "#DC3545"],
                width=0.55
            )

            ax.set_ylabel(
                "Cantidad",
                fontsize=10,
                color="#5F6368"
            )

            ax.tick_params(
                axis="both",
                labelsize=10
            )

            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_color("#D9D9D9")
            ax.spines["bottom"].set_color("#D9D9D9")

            ax.grid(
                axis="y",
                linestyle="--",
                alpha=0.25
            )

            for barra in barras:

                altura = barra.get_height()

                ax.text(
                    barra.get_x() + barra.get_width() / 2,
                    altura,
                    f"{int(altura)}",
                    ha="center",
                    va="bottom",
                    fontsize=10,
                    fontweight="bold"
                )

            plt.tight_layout()

            st.pyplot(
                fig,
                use_container_width=True
            )

            plt.close(fig)

    # -------- GRÁFICA DE PASTEL --------

    inspecciones = aptas + no_aptas

    with col_graf2:

        with st.container(border=True):

            st.markdown(
                '<div class="chart-title">Distribución de Resultados</div>',
                unsafe_allow_html=True
            )

            if inspecciones > 0:

                fig, ax = plt.subplots(figsize=(5, 3.2))

                ax.pie(
                    [aptas, no_aptas],
                    labels=[
                        "Aptas",
                        "No Aptas"
                    ],
                    colors=[
                        "#1D7EAE",
                        "#DC3545"
                    ],
                    autopct="%1.1f%%",
                    startangle=90,
                    wedgeprops={
                        "width": 0.55,
                        "edgecolor": "white"
                    },
                    textprops={
                        "fontsize": 10
                    }
                )

                ax.axis("equal")

                plt.tight_layout()

                st.pyplot(
                    fig,
                    use_container_width=True
                )

                plt.close(fig)

            else:

                st.info(
                    "Todavía no hay inspecciones registradas."
                )

    st.divider()

def mostrar_indicadores(aptas, no_aptas):

    inspecciones_validas = aptas + no_aptas

    if inspecciones_validas == 0:
        st.info("Todavía no hay inspecciones suficientes para calcular indicadores.")
        st.divider()
        return

    porcentaje_apto = (
        aptas / inspecciones_validas
    ) * 100

    porcentaje_no_apto = (
        no_aptas / inspecciones_validas
    ) * 100

    mostrar_encabezado_seccion(
    "Indicadores de calidad",
    "Métricas porcentuales del desempeño del proceso."
)

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

def mostrar_registro():

    st.subheader("📋 Registro de Inspecciones")

    if not os.path.exists(archivo_csv):

        st.info(
            "Todavía no hay inspecciones registradas."
        )

        st.divider()
        return

    try:

        columnas = [
            "Fecha",
            "Resultado",
            "Confianza (%)",
            "Archivo Guardado",
            "Origen"
        ]

        datos = pd.read_csv(
            archivo_csv,
            header=None,
            names=columnas,
            encoding="utf-8"
        )

        datos = datos.dropna(
            how="all"
        )

        if datos.empty:

            st.info(
                "Todavía no hay inspecciones registradas."
            )

            st.divider()
            return

        # -------- ÚLTIMA INSPECCIÓN --------

        ultima_inspeccion = datos.iloc[-1]

        st.markdown("### Última inspección")

        col1, col2, col3 = st.columns(3)

        resultado = str(
            ultima_inspeccion["Resultado"]
        ).strip().upper()

        with col1:

            st.metric(
                "Fecha",
                str(
                    ultima_inspeccion["Fecha"]
                )
            )

        with col2:

            if resultado in [
                "APTO",
                "BUENA"
            ]:

                st.success(
                    "✅ PIEZA APTA"
                )

            elif resultado in [
                "NO APTO",
                "MALA"
            ]:

                st.error(
                    "❌ PIEZA NO APTA"
                )

            else:

                st.warning(
                    f"⚠ {resultado}"
                )

        with col3:

            confianza = ultima_inspeccion[
                "Confianza (%)"
            ]

            st.metric(
                "Confianza",
                f"{confianza}%"
            )

        st.caption(
            f"Origen de la imagen: "
            f"{ultima_inspeccion['Origen']}"
        )

        # -------- HISTORIAL COMPLETO --------

        st.markdown("### Historial de inspecciones")

        datos_mostrados = datos.iloc[
            ::-1
        ].reset_index(
            drop=True
        )

        st.dataframe(
            datos_mostrados,
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            f"Total de registros mostrados: {len(datos)}"
        )

    except pd.errors.EmptyDataError:

        st.info(
            "El archivo de registro está vacío."
        )

    except Exception as error:

        st.error(
            "No fue posible cargar el registro de inspecciones."
        )

        st.caption(
            f"Detalle técnico: {error}"
        )

    st.divider()

def mostrar_exportar():

    st.subheader("📤 Exportar Registro")

    if not os.path.exists(archivo_csv):

        st.info(
            "No existen inspecciones para exportar."
        )

        st.divider()
        return

    if st.button(
        "📥 Exportar a Excel",
        use_container_width=True
    ):

        try:

            columnas = [
                "Fecha",
                "Resultado",
                "Confianza (%)",
                "Archivo Guardado",
                "Origen"
            ]

            datos = pd.read_csv(
                archivo_csv,
                header=None,
                names=columnas,
                encoding="utf-8"
            )

            wb = Workbook()

            ws = wb.active

            ws.title = "Registro VisionQA"

            ws.append(columnas)

            for fila in datos.itertuples(index=False):

                ws.append(list(fila))

            nombre_excel = (
                "Registro_VisionQA.xlsx"
            )

            wb.save(nombre_excel)

            st.success(
                f"Archivo exportado correctamente: {nombre_excel}"
            )

        except Exception as error:

            st.error(
                "No fue posible exportar el archivo."
            )

            st.caption(error)

    st.divider()

def mostrar_gemini():

    st.subheader("🧠 Análisis de Causas con IA")

    st.write(
        """
        Utiliza Gemini para analizar los resultados de las inspecciones
        aplicando principios de Manufactura Esbelta y metodología Six Sigma.
        """
    )

    col1, col2 = st.columns(2)

    # -------- ÚLTIMA INSPECCIÓN --------

    with col1:

        if st.button(
            "Analizar última inspección",
            use_container_width=True
        ):

            if not os.path.exists(archivo_csv):

                st.warning(
                    "No existe el registro de inspecciones."
                )

            else:

                with open(
                    archivo_csv,
                    "r",
                    encoding="utf-8"
                ) as archivo:

                    lineas = archivo.readlines()

                if len(lineas) == 0:

                    st.warning(
                        "No hay inspecciones registradas."
                    )

                else:

                    ultima = lineas[-1]

                    with st.spinner(
                        "Gemini está analizando..."
                    ):

                        resultado = analizar_causas(
                            ultima
                        )

                    st.success(
                        "Análisis completado."
                    )

                    st.markdown(resultado)

    # -------- ÚLTIMAS 10 INSPECCIONES --------

    with col2:

        if st.button(
            "Analizar últimas 10 inspecciones",
            use_container_width=True
        ):

            if not os.path.exists(archivo_csv):

                st.warning(
                    "No existe el registro de inspecciones."
                )

            else:

                with open(
                    archivo_csv,
                    "r",
                    encoding="utf-8"
                ) as archivo:

                    lineas = archivo.readlines()

                if len(lineas) == 0:

                    st.warning(
                        "No hay inspecciones registradas."
                    )

                else:

                    ultimas = "".join(
                        lineas[-10:]
                    )

                    with st.spinner(
                        "Gemini está analizando..."
                    ):

                        resultado = analizar_causas(
                            ultimas
                        )

                    st.success(
                        "Análisis completado."
                    )

                    st.markdown(resultado)

    st.divider()

def mostrar_footer():

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

def main():

    # -------- MENÚ LATERAL --------

    with st.sidebar:

        st.image(
            "assets/logo_iot.png",
            use_container_width=True
        )

        st.markdown(
            '<div class="sidebar-brand">'
            '<div class="sidebar-title">VisionQA</div>'
            '<div class="sidebar-subtitle">'
            'Sistema Inteligente de Inspección Visual'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="sidebar-separator"></div>',
            unsafe_allow_html=True
        )

        pagina = option_menu(
    menu_title=None,
    options=[
        "Dashboard",
        "Inspección",
        "Registro",
        "IA Generativa",
        "Reportes",
        "Acerca de"
    ],
    icons=[
        "speedometer2",
        "search",
        "clipboard-data",
        "cpu",
        "file-earmark-bar-graph",
        "info-circle"
    ],
    menu_icon=None,
    default_index=0,
    orientation="vertical",
    styles={
        "container": {
            "padding": "10px",
            "background-color": "#FFFFFF",
            "border": "1px solid #D9E2E8",
            "border-radius": "16px",
            "box-shadow": "0 6px 18px rgba(35, 31, 32, 0.06)"
        },
        "icon": {
            "color": "#1D7EAE",
            "font-size": "22px"
        },
        "nav-link": {
            "font-size": "15px",
            "font-weight": "500",
            "color": "#231F20",
            "text-align": "left",
            "margin": "5px 0",
            "padding": "15px 16px",
            "border-radius": "11px"
        },
        "nav-link-hover": {
            "background-color": "#F2F8FC",
            "color": "#0032A0"
        },
        "nav-link-selected": {
            "background-color": "#EAF5FB",
            "color": "#0032A0",
            "font-weight": "700",
            "border-left": "4px solid #1D7EAE"
        }
    }
)

        st.markdown(
                """
                <div class="sidebar-footer">
                    <strong>VisionQA</strong><br>
                    Versión 1.0<br>
                    IOT Technologies
                </div>
                """,
                unsafe_allow_html=True
            )

    # -------- DATOS DEL REGISTRO --------

    total, aptas, no_aptas = cargar_datos_registro()

    # -------- DASHBOARD --------

    if pagina == "Dashboard":

        mostrar_titulo(
            "📊 Dashboard Ejecutivo",
            "Indicadores generales del sistema de inspección visual."
        )

        mostrar_resumen(
            total,
            aptas,
            no_aptas
        )

        mostrar_graficas(
            aptas,
            no_aptas
        )

        mostrar_indicadores(
            aptas,
            no_aptas
        )

    # -------- INSPECCIÓN --------

    elif pagina == "Inspección":

        mostrar_titulo(
            "🔍 Inspección Visual",
            "Captura y analiza piezas mediante inteligencia artificial."
        )

        mostrar_estado_sistema()
        mostrar_modulo_inspeccion()

    # -------- REGISTRO --------

    elif pagina == "Registro":

        mostrar_titulo(
            "📋 Registro de Inspecciones",
            "Consulta los resultados y el historial de inspecciones."
        )

        mostrar_registro()

    # -------- IA GENERATIVA --------

    elif pagina == "IA Generativa":

        mostrar_titulo(
            "🧠 Análisis Inteligente",
            "Analiza posibles causas y acciones de mejora mediante Gemini."
        )

        mostrar_gemini()

    # -------- REPORTES --------

    elif pagina == "Reportes":

        mostrar_titulo(
            "📤 Exportación de Reportes",
            "Genera archivos para el seguimiento del proceso de calidad."
        )

        mostrar_exportar()

    # -------- ACERCA DE --------

    elif pagina == " Acerca de":

        mostrar_titulo(
            "ℹ️ Acerca de VisionQA",
            "Información general del sistema y las tecnologías utilizadas."
        )

        st.markdown(
            """
            **VisionQA** es un sistema inteligente de inspección visual
            desarrollado para apoyar el control de calidad de piezas
            manufacturadas.

            El sistema integra:

            - Visión por computadora.
            - Modelo de detección YOLOv8.
            - Procesamiento de imágenes con OpenCV.
            - Dashboard desarrollado con Streamlit.
            - Análisis de causas mediante Gemini.
            - Principios de Manufactura Esbelta y Six Sigma.
            """
        )

        st.markdown("### Información del proyecto")

        col1, col2 = st.columns(2)

        with col1:

            st.markdown(
                """
                **Proyecto:** VisionQA

                **Empresa:** IOT Technologies

                **Área:** Control de Calidad
                """
            )

        with col2:

            st.markdown(
                """
                **Desarrolladora:** Dorcas Tabita Perez Martinez

                **Tecnologías:** Python, YOLOv8, OpenCV, Streamlit y Gemini

                **Versión:** 1.0
                """
            )

        st.divider()

    mostrar_footer()


if __name__ == "__main__":
    main()