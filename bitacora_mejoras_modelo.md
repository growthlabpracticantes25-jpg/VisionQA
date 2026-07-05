# Bitácora de Mejoras del Modelo YOLO - VisionQA

## Mejora 1
### Problema detectado
El modelo train-4 únicamente detectó correctamente 4 de las 10 imágenes malas utilizadas para validación.

### Acción realizada
Se analizaron los falsos negativos y se seleccionaron seis imágenes donde el modelo no detectó correctamente los defectos.

Las imágenes fueron etiquetadas nuevamente utilizando MakeSense.ai y posteriormente incorporadas al dataset de entrenamiento.

### Resultado
Se entrenó el modelo train-5.

Durante la validación:

- Detectó 7 de 10 imágenes malas.
- Detectó correctamente 9 de 10 imágenes buenas.
- Solo presentó un falso positivo.

---

## Mejora 2
### Problema detectado

El modelo continuó fallando en:

- Mala 5
- Mala 7
- Mala 9

Además presentó un falso positivo en:

- Buena 7

### Hipótesis

Los defectos no eran claramente visibles debido al ángulo de captura y a la poca visibilidad de la fractura.

### Acción realizada

Se corrigieron nuevamente las cajas delimitadoras de las imágenes Mala 5, Mala 7 y Mala 9 para que únicamente abarcaran el defecto real.

Se actualizaron los archivos de anotación (.txt) del dataset.

### Estado

Pendiente de entrenar el modelo train-6.