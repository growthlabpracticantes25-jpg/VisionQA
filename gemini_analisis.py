import os 
import google.generativeai as genai
api_key = os.getenv("GEMINI_API_KEY")

genai.configure(
    api_key=api_key
)

modelo = genai.GenerativeModel(
    "gemini-2.5-flash"
)

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

El reporte debe tener exactamente este formato:

# 🧠 Resumen Ejecutivo

**Estado general:**
(APTO / NO APTO / REVISION MANUAL)

**Nivel de confianza:**
(Indicar el porcentaje disponible.)

**Nivel de prioridad:**
🟢 Baja
🟡 Media
🔴 Alta

**Acción inmediata recomendada:**
(Una sola acción concreta.)

---

# 📌 Resumen del análisis

Explica en un máximo de 3 líneas lo que indican los registros.

---

# 🔎 Posibles causas (6M)

### 👷 Mano de obra
Máximo 2 causas.

### ⚙️ Máquina
Máximo 2 causas.

### 📏 Método
Máximo 2 causas.

### 🧱 Material
Máximo 2 causas.

### 📐 Medición
Máximo 2 causas.

### 🌎 Medio ambiente
Máximo 2 causas.

---

# ✅ Acciones correctivas

Genera únicamente 5 acciones concretas y priorizadas.

---

# 📈 Recomendaciones de mejora

Genera únicamente 5 recomendaciones ejecutivas para fortalecer VisionQA.

---

# 📝 Conclusión

Redacta una conclusión en máximo 3 líneas.

El reporte debe verse como un informe ejecutivo para un supervisor de calidad.
""" 
    respuesta = modelo.generate_content(prompt)

    return respuesta.text