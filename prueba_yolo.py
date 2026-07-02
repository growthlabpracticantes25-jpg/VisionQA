from modelo_yolo import detectar_defectos

estado, detecciones = detectar_defectos(
    "Imagenes validacion/Malas/Mala  2.JPG"
)

print("Estado:", estado)
print("Detecciones:")

for d in detecciones:
    print(d)