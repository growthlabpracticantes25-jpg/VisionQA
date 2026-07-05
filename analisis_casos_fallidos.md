# Análisis de Casos Fallidos - Modelo YOLOv8

## Proyecto

VisionQA: Sistema de inspección visual asistido por Inteligencia Artificial para detección de defectos en piezas manufacturadas.

---

## Objetivo

Analizar las imágenes que el modelo YOLOv8 no logró detectar durante la validación del entrenamiento **train-6**, con el fin de identificar posibles causas y definir acciones de mejora antes de la integración del modelo en VisionQA.

---

# Caso 1 - Mala 5

## Resultado

No detección.

## Posibles causas

- Defecto con poca superficie visible.
- Bajo contraste entre el defecto y la pieza.
- Cantidad limitada de ejemplos similares en el entrenamiento.
- El defecto puede confundirse con una pieza en buen estado.

## Acción propuesta

Incorporar más imágenes con este tipo de defecto y diferentes ángulos de captura.

---

# Caso 2 - Mala 7

## Resultado

No detección.

## Posibles causas

- Defecto parcialmente visible.
- Ángulo de captura diferente al utilizado en el entrenamiento.
- Tamaño reducido del área defectuosa.

## Acción propuesta

Ampliar el dataset con imágenes similares y revisar la diversidad de posiciones durante el entrenamiento.

---

# Caso 3 - Mala 9

## Resultado

No detección.

## Posibles causas

- Defecto de baja visibilidad.
- Poco contraste respecto al material de la pieza.
- Escasa representación de este tipo de defecto en el dataset.

## Acción propuesta

Agregar nuevas imágenes con diferentes condiciones de iluminación y distintos niveles de severidad del defecto.

---

# Hallazgos generales

Durante la validación del modelo train-6 se observó que los errores de detección no corresponden a fallas del algoritmo, sino principalmente a limitaciones del conjunto de entrenamiento. Los tres casos fallidos presentan características visuales similares: defectos con poca superficie visible, bajo contraste o perspectivas diferentes a las utilizadas durante el entrenamiento.

---

# Conclusión

El modelo YOLOv8 demuestra un desempeño adecuado para el prototipo VisionQA; sin embargo, antes de su integración definitiva se recomienda fortalecer el dataset con nuevos ejemplos de los casos difíciles identificados durante esta validación. Se considera que la mejora del conjunto de datos tendrá un mayor impacto que realizar nuevos entrenamientos sin incorporar información adicional.