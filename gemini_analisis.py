import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("No se encontró la variable de entorno GEMINI_API_KEY.")

genai.configure(api_key=api_key)

modelo = genai.GenerativeModel("gemini-2.5-flash")


def analizar_causas(datos_csv):

    prompt = f"""
Eres un Ingeniero Senior en Control de Calidad, Manufactura Esbelta y Six Sigma.

Analiza los siguientes registros del sistema VisionQA:

{datos_csv}

El sistema clasifica las piezas como:
- APTO
- NO APTO
- REVISION MANUAL

IMPORTANTE:
- Si solo existe un registro de inspección, evita realizar análisis de tendencias.
- Basa tus conclusiones únicamente en la información disponible.
- Elabora un reporte ejecutivo y profesional.
- No inventes información que no exista en los registros.
- Si los datos son insuficientes, indícalo claramente.
- NO menciones nombres de archivos, imágenes o rutas.
- NO repitas información innecesaria.
- Sé breve, claro y orientado a la toma de decisiones.
- NO generes un apartado llamado "Resumen Ejecutivo", ya que esa información se muestra en el dashboard mediante tarjetas.

El reporte debe tener exactamente este formato:

# Resumen del análisis

Redacta un resumen ejecutivo en máximo 3 líneas.

No repitas:

- Estado
- Confianza
- Prioridad
- Defecto
- Acción

porque esa información ya aparece en las tarjetas superiores.
---

# Posibles causas (6M)

### Mano de obra
Máximo 2 causas.

### Máquina
Máximo 2 causas.

### Método
Máximo 2 causas.

### Material
Máximo 2 causas.

### Medición
Máximo 2 causas.

### Medio ambiente
Máximo 2 causas.

---

# Acciones correctivas

Genera únicamente 5 acciones concretas y priorizadas.

---

# Recomendaciones de mejora

Genera únicamente 5 recomendaciones ejecutivas para fortalecer VisionQA.

---

# Conclusión

Redacta una conclusión en máximo 3 líneas.

El reporte debe verse como un informe ejecutivo para un supervisor de calidad.
"""

    try:

        respuesta = modelo.generate_content(prompt)

        return respuesta.text

    except Exception as error:

        mensaje_error = str(error).lower()

        if (
            "429" in mensaje_error
            or "quota" in mensaje_error
            or "resourceexhausted" in mensaje_error
        ):

            return """
# ⚠️ Servicio temporalmente no disponible

Se alcanzó temporalmente el límite de solicitudes de Gemini.

Espera aproximadamente un minuto y vuelve a ejecutar el análisis.
"""

        return """
# ⚠️ No fue posible generar el análisis

Ocurrió un problema al comunicarse con Gemini.

Verifica la conexión a internet y vuelve a intentarlo.
"""