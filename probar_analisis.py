from gemini_analisis import analizar_causas

datos = """
22/06/2026 10:49:24,NO APTO,99.98,archivo_20260622_104924.jpg,Mala 65.JPG
"""

respuesta = analizar_causas(datos)

print(respuesta) 