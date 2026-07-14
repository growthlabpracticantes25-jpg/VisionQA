from modelo_ia import clasificar_imagen


resultado = clasificar_imagen(
    "dataset_yolo_v2/imagenes_validacion_yolo/rota/rota_1.JPG"
)

print("Estado:", resultado["estado"])
print("Defecto:", resultado["defecto"])
print(f"Confianza: {resultado['confianza']:.2f}%")