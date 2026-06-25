import os
import google.generativeai as genai

api_key = os.getenv("GEMINI_API_KEY")

genai.configure(
    api_key=api_key
)

modelo = genai.GenerativeModel("gemini-2.5-flash")

respuesta = modelo.generate_content(
    "Di hola, soy Gemini."
)

print(respuesta.text) 