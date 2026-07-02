# Comparación de Modelos YOLOv8 - VisionQA

## Objetivo
Evaluar el desempeño de diferentes entrenamientos del modelo YOLOv8 Nano para la detección de defectos en piezas del proyecto VisionQA.

---

## Modelo train-4

### Dataset utilizado
- 200 imágenes totales.
- 120 imágenes malas etiquetadas.
- 80 imágenes buenas sin defectos.

### Resultados del entrenamiento
- Precision: 0.975
- Recall: 0.929
- mAP50: 0.979
- mAP50-95: 0.725

### Resultados en validación
- Imágenes buenas: 10/10 clasificadas como APTO.
- Imágenes malas: 4/10 detectadas como NO APTO.

### Observación
Aunque las métricas del entrenamiento fueron altas, el modelo no logró detectar varios defectos en imágenes de validación.

---

## Modelo train-5

### Dataset utilizado
- 206 imágenes totales.
- Se agregaron imágenes donde el modelo anterior había fallado.
- Se corrigieron etiquetas de casos difíciles.

### Resultados del entrenamiento
- Precision: 0.951
- Recall: 0.933
- mAP50: 0.973
- mAP50-95: 0.706

### Resultados en validación con conf=0.40
- Imágenes malas detectadas: 7/10.
- Imágenes buenas correctas: 9/10.
- Falso positivo observado: Buena 7 detectada como rota.

### Observación
El modelo train-5 mejoró la detección de imágenes malas, pasando de 4/10 a 7/10. Sin embargo, apareció un falso positivo en una imagen buena.

---

## Análisis de mejora

El refuerzo del dataset con imágenes donde el modelo falló permitió mejorar la detección de defectos. Esto demuestra que la estrategia de análisis de errores y reentrenamiento puede mejorar el desempeño del modelo.

---

## Próximos pasos

1. Corregir etiquetas de las imágenes Mala 5, Mala 7 y Mala 9.
2. Reentrenar un nuevo modelo train-6 cuando sea posible.
3. Validar nuevamente con imágenes buenas y malas.
4. Integrar YOLO a VisionQA solo cuando el modelo tenga un desempeño aceptable.