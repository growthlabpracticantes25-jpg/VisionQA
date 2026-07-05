# Validación del Modelo YOLOv8 - VisionQA

## Objetivo

Evaluar el desempeño del modelo YOLOv8 Nano entrenado para la detección de defectos en piezas del proyecto VisionQA, antes de integrarlo a la aplicación principal.

---

## Modelo evaluado

- Modelo: YOLOv8 Nano
- Entrenamiento: train-6
- Dataset: dataset_yolo
- Imágenes de entrenamiento: 206
- Umbral de confianza evaluado: 0.50

---

## Resultados de validación

### Imágenes buenas

- Total evaluadas: 10
- Correctamente clasificadas como APTO: 10
- Falsos positivos: 0

### Imágenes malas

- Total evaluadas: 10
- Defectos detectados: 7
- Falsos negativos: 3

### Imágenes no detectadas

- Mala 5
- Mala 7
- Mala 9

---

## Interpretación

El modelo YOLOv8 logró clasificar correctamente todas las piezas buenas, evitando falsos positivos durante la validación.

En las piezas defectuosas, el modelo detectó correctamente 7 de 10 imágenes. Sin embargo, aún presenta dificultades con algunos defectos visibles desde ángulos laterales o con baja exposición visual del daño.

---

## Conclusión

El modelo train-6 se considera un modelo experimental funcional para el prototipo VisionQA, pero aún no se considera definitivo para integrarse como detector principal.

Antes de su integración final, se recomienda ampliar el dataset con más imágenes similares a los casos Mala 5, Mala 7 y Mala 9, especialmente con defectos tomados desde ángulos laterales.

---

## Próximos pasos

1. Capturar o recopilar más imágenes de defectos laterales.
2. Etiquetar correctamente los nuevos casos difíciles.
3. Reentrenar el modelo con mayor variedad visual.
4. Validar nuevamente con imágenes externas.
5. Integrar YOLO a VisionQA cuando el desempeño sea más confiable.