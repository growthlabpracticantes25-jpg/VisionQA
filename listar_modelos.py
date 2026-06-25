import os
import google.generativeai as genai

api_key = os.getenv("GEMINI_API_KEY")

genai.configure(
    api_key=api_key
)