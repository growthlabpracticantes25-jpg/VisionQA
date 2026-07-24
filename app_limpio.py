import os
import csv
from datetime import datetime
from datetime import datetime
import requests
import streamlit as st
import cv2
from textwrap import dedent
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
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

st.markdown(
    """
    <style>

    /* Fondo general */
    .stApp {
        background-color: #f4f7fb;
    }

    /* Ocultar elementos predeterminados de Streamlit */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    /* Espacio del contenido principal */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }

    /* Barra superior del Dashboard */
    .visionqa-header {
    background: linear-gradient(90deg, #168db5, #24a0c1);
    border-radius: 10px;
    padding: 18px 24px;
    margin-bottom: 22px;
    color: white;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.12);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.visionqa-header-left {
    display: flex;
    flex-direction: column;
}

.visionqa-header-right {
    text-align: right;
    color: white;
}

.visionqa-saludo {
    color: white;
    font-size: 20px;
    font-weight: 700;
}

.visionqa-subtitulo {
    color: white;
    font-size: 13px;
    margin-top: 5px;
    opacity: 0.92;
}

.visionqa-fecha {
    color: white;
    font-size: 13px;
}

.visionqa-hora {
    color: white;
    font-size: 18px;
    font-weight: 700;
    margin-top: 2px;
}
    </style>
    """,
    unsafe_allow_html=True
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
def guardar_inspeccion_api(
    resultado,
    defecto,
    confianza,
    archivo,
    origen
):
    url_api = "http://127.0.0.1:8000/api/inspecciones/"

    datos = {
        "resultado": resultado,
        "defecto": defecto,
        "confianza": float(confianza),
        "archivo": archivo,
        "origen": origen
    }

    try:
        respuesta = requests.post(
            url_api,
            json=datos,
            timeout=10
        )

        if respuesta.status_code == 201:
            return True, "Inspección guardada en Django."

        return False, f"Error de API {respuesta.status_code}: {respuesta.text}"

    except requests.exceptions.ConnectionError:
        return False, "No se pudo conectar con Django."

    except requests.exceptions.RequestException as error:
        return False, f"Error al enviar la inspección: {error}"

def obtener_inspecciones_api():

    url_api = "http://127.0.0.1:8000/api/inspecciones/"

    try:

        respuesta = requests.get(
            url_api,
            timeout=10
        )

        if respuesta.status_code == 200:

            return respuesta.json()

    except requests.exceptions.RequestException:

        pass

    return []

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

    url_api = "http://127.0.0.1:8000/api/inspecciones/"

    try:

        respuesta = requests.get(
            url_api,
            timeout=10
        )

        if respuesta.status_code != 200:

            return 0, 0, 0

        registros = respuesta.json()

        total = len(registros)
        aptas = 0
        no_aptas = 0

        for registro in registros:

            resultado = str(
                registro.get(
                    "resultado",
                    ""
                )
            ).strip().upper()

            if resultado in [
                "APTO",
                "BUENA"
            ]:

                aptas += 1

            elif resultado in [
                "NO APTO",
                "MALA"
            ]:

                no_aptas += 1

        return total, aptas, no_aptas

    except requests.exceptions.RequestException:

        return 0, 0, 0

def mostrar_modulo_inspeccion():

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
        else:

            st.info(
        "👆 Selecciona un método de inspección para comenzar."
    )

    if "metodo_inspeccion" not in st.session_state:
        st.session_state["metodo_inspeccion"] = None

    opcion = st.session_state["metodo_inspeccion"]

    # -------- PROCESAR Y REGISTRAR INSPECCIÓN --------

    def procesar_inspeccion(
        imagen,
        nombre_archivo,
        origen
    ):

        os.makedirs(
            "inspecciones",
            exist_ok=True
        )

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

        mostrar_encabezado_seccion(
        "Resultado de la inspección",
        "Clasificación y nivel de confianza obtenido por el modelo."
)

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

        # -------- GUARDAR EN DJANGO --------

        guardado_api, mensaje_api = guardar_inspeccion_api(
            resultado=resultado_registro,
            defecto=defecto or "",
            confianza=confianza_porcentaje,
            archivo=ruta_imagen,
            origen=origen
        )

        if guardado_api:
            st.caption(f"✅ {mensaje_api}")
        else:
            st.warning(mensaje_api)

        col_confianza, col_origen = st.columns(2)

        with col_confianza:
         st.metric(
                "Confianza del modelo",
                f"{confianza_porcentaje:.2f}%"
            )

        with col_origen:
            st.metric(
                "Origen de la imagen",
                origen
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
            defecto or "",
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

        st.caption(
            "Registro local CSV actualizado."
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

    porcentaje_aptas = (
        (aptas / total) * 100
        if total > 0
        else 0
    )

    porcentaje_no_aptas = (
        (no_aptas / total) * 100
        if total > 0
        else 0
    )

    col1, col2, col3 = st.columns(3)

    tarjetas = [
        {
            "icono": "bi bi-clipboard-data",
            "valor": total,
            "titulo": "Total de inspecciones",
            "descripcion": "Registros almacenados",
            "detalle": "Base de datos actualizada",
            "clase": "kpi-total"
        },
        {
            "icono": "bi bi-check-circle",
            "valor": aptas,
            "titulo": "Piezas aptas",
            "descripcion": "Cumplen con calidad",
            "detalle": f"{porcentaje_aptas:.1f}% del total",
            "clase": "kpi-success"
        },
        {
            "icono": "bi bi-exclamation-triangle",
            "valor": no_aptas,
            "titulo": "Piezas no aptas",
            "descripcion": "Requieren revisión",
            "detalle": f"{porcentaje_no_aptas:.1f}% del total",
            "clase": "kpi-danger"
        }
    ]

    for columna, tarjeta in zip(
    [col1, col2, col3],
    tarjetas
):

     with columna:

        html = (
            f'<div class="kpi-card {tarjeta["clase"]}">'
                '<div class="kpi-card-top">'
                    '<div class="kpi-icon">'
                        f'<i class="{tarjeta["icono"]}"></i>'
                    '</div>'
                    '<div class="kpi-detail">'
                        f'{tarjeta["detalle"]}'
                    '</div>'
                '</div>'
                '<div class="kpi-value">'
                    f'{tarjeta["valor"]}'
                '</div>'
                '<div class="kpi-title">'
                    f'{tarjeta["titulo"]}'
                '</div>'
                '<div class="kpi-description">'
                    f'{tarjeta["descripcion"]}'
                '</div>'
            '</div>'
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

    col1, col2 = st.columns(2)

    etiquetas = ["Aptas", "No aptas"]
    valores = [aptas, no_aptas]

    with col1:

        st.markdown("### Resultados de inspección")

        fig_barras, ax_barras = plt.subplots()

        barras = ax_barras.bar(
            etiquetas,
            valores
        )

        ax_barras.set_ylabel("Cantidad")
        ax_barras.set_title("Piezas inspeccionadas")

        for barra, valor in zip(barras, valores):

            ax_barras.text(
                barra.get_x() + barra.get_width() / 2,
                barra.get_height(),
                str(valor),
                ha="center",
                va="bottom"
            )

        st.pyplot(fig_barras)

    with col2:

        st.markdown("### Distribución de resultados")

        total = aptas + no_aptas

        if total > 0:

            fig_dona, ax_dona = plt.subplots()

            ax_dona.pie(
                valores,
                labels=etiquetas,
                autopct="%1.1f%%",
                startangle=90,
                wedgeprops={
                    "width": 0.40
                }
            )

            ax_dona.axis("equal")

            st.pyplot(fig_dona)

        else:

            st.info(
                "Todavía no hay inspecciones para mostrar la distribución."
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

    url_api = "http://127.0.0.1:8000/api/inspecciones/"

    try:

        respuesta = requests.get(
            url_api,
            timeout=10
        )

        if respuesta.status_code != 200:

            st.error(
                "No fue posible consultar el registro en Django."
            )

            st.caption(
                f"Error de API: {respuesta.status_code}"
            )

            st.divider()
            return

        registros = respuesta.json()

        if not registros:

            st.info(
                "Todavía no hay inspecciones registradas."
            )

            st.divider()
            return

        datos = pd.DataFrame(registros)

        # Cambiar nombres de las columnas de Django
        # por nombres visibles en Streamlit
        datos = datos.rename(
            columns={
                "fecha": "Fecha",
                "resultado": "Resultado",
                "defecto": "Defecto",
                "confianza": "Confianza (%)",
                "archivo": "Archivo Guardado",
                "origen": "Origen"
            }
        )

        # Convertir y ordenar las fechas
        datos["Fecha"] = pd.to_datetime(
            datos["Fecha"],
            errors="coerce"
        )

        datos = datos.sort_values(
            by="Fecha",
            ascending=True
        ).reset_index(
            drop=True
        )

        datos["Fecha"] = datos["Fecha"].dt.strftime(
            "%d/%m/%Y %H:%M:%S"
        )

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

            confianza = float(
                ultima_inspeccion["Confianza (%)"]
            )

            st.metric(
                "Confianza",
                f"{confianza:.2f}%"
            )

        defecto = ultima_inspeccion.get(
            "Defecto",
            ""
        )

        if pd.notna(defecto) and str(defecto).strip():

            st.caption(
                "Defecto detectado: "
                f"{str(defecto).replace('_', ' ').title()}"
            )

        st.caption(
            f"Origen de la imagen: "
            f"{ultima_inspeccion['Origen']}"
        )

        # -------- HISTORIAL COMPLETO --------

        st.markdown("### Historial de inspecciones")

        columnas_mostradas = [
            "Fecha",
            "Resultado",
            "Defecto",
            "Confianza (%)",
            "Archivo Guardado",
            "Origen"
        ]

        datos_mostrados = datos[
            columnas_mostradas
        ].iloc[::-1].reset_index(
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

    except requests.exceptions.ConnectionError:

        st.error(
            "No se pudo conectar con Django."
        )

        st.info(
            "Verifica que esté ejecutándose: "
            "python manage.py runserver"
        )

    except requests.exceptions.RequestException as error:

        st.error(
            "Ocurrió un error al consultar la API."
        )

        st.caption(
            f"Detalle técnico: {error}"
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

    registros = obtener_inspecciones_api()

    if not registros:

        st.info(
            "No existen inspecciones para exportar."
        )

        st.divider()
        return

    try:

        datos = pd.DataFrame(registros)

        datos = datos.rename(
            columns={
                "fecha": "Fecha",
                "resultado": "Resultado",
                "defecto": "Defecto",
                "confianza": "Confianza (%)",
                "archivo": "Archivo Guardado",
                "origen": "Origen"
            }
        )

        columnas = [
            "Fecha",
            "Resultado",
            "Defecto",
            "Confianza (%)",
            "Archivo Guardado",
            "Origen"
        ]

        datos = datos[columnas]

        wb = Workbook()

        ws = wb.active

        ws.title = "Registro VisionQA"

        ws.append(columnas)

        for fila in datos.itertuples(index=False):

            ws.append(list(fila))

        archivo_excel = BytesIO()

        wb.save(archivo_excel)

        archivo_excel.seek(0)

        st.download_button(
            label="📥 Descargar Excel",
            data=archivo_excel,
            file_name="Registro_VisionQA.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
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

        registros = obtener_inspecciones_api()

        if not registros:

            st.warning(
                "No hay inspecciones registradas."
            )

        else:

            ultima = registros[-1]

            datos = f"""
Fecha: {ultima['fecha']}
Resultado: {ultima['resultado']}
Defecto: {ultima['defecto']}
Confianza: {ultima['confianza']}%
Origen: {ultima['origen']}
"""

            with st.spinner(
                "Gemini está analizando..."
            ):

                resultado = analizar_causas(
                    datos
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

            registros = obtener_inspecciones_api()

            if not registros:

                st.warning(
                    "No hay inspecciones registradas."
                )

            else:

                ultimas = registros[:10]

                texto = ""

                for registro in ultimas:

                    texto += f"""
Fecha: {registro['fecha']}
Resultado: {registro['resultado']}
Defecto: {registro['defecto']}
Confianza: {registro['confianza']}%
Origen: {registro['origen']}

"""

                with st.spinner(
                    "Gemini está analizando..."
                ):

                    resultado = analizar_causas(
                        texto
                    )

                st.success(
                    "Análisis completado."
                )

                st.markdown(resultado)
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
        "padding": "12px 10px",
        "margin": "0px",
        "background-color": "#1998B7",
        "border": "none",
        "border-radius": "0px",
        "box-shadow": "none"
    },
    "icon": {
        "color": "#FFFFFF",
        "font-size": "18px"
    },
    "nav-link": {
        "font-size": "15px",
        "font-weight": "500",
        "color": "#FFFFFF",
        "text-align": "left",
        "margin": "6px 0",
        "padding": "14px 16px",
        "border-radius": "10px",
        "background-color": "#1998B7",
        "border": "none"
    },
    "nav-link-hover": {
        "background-color": "rgba(255,255,255,0.16)",
        "color": "#FFFFFF"
    },
    "nav-link-selected": {
        "background-color": "#0A4E95",
        "color": "#FFFFFF",
        "font-weight": "700",
        "border-radius": "10px",
        "box-shadow": "0 4px 10px rgba(0,0,0,0.18)"
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

        ahora = datetime.now()

        fecha_actual = ahora.strftime("%d/%m/%Y")
        hora_actual = ahora.strftime("%I:%M:%S %p")

        html_header = (
            '<div class="visionqa-header">'
                '<div class="header-left">'
                    '<div class="header-greeting">Buenos días, Dorcas</div>'
                    '<div class="header-description">'
                        'Sistema Inteligente de Inspección Visual'
                    '</div>'
                    '<div class="header-status">'
                        '<span class="status-dot"></span>'
                        'Sistema conectado'
                    '</div>'
                '</div>'
                '<div class="header-right">'
                    '<div class="header-label">Última actualización</div>'
                    f'<div class="header-date">{fecha_actual}</div>'
                    f'<div class="header-time">{hora_actual}</div>'
                '</div>'
            '</div>'
        )

        st.markdown(
            html_header,
            unsafe_allow_html=True
        )

        st.markdown("## 🏠 Dashboard Operativo")

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

    elif pagina == "Acerca de":

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