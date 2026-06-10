import tensorflow as tf
import numpy as np
from PIL import Image

# Cargar modelo
interpreter = tf.lite.Interpreter(
    model_path="modelo IA/model_unquant.tflite"
)

interpreter.allocate_tensors()

# Obtener detalles
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Abrir imagen
imagen = Image.open(
    "dataset/malas/Mala 01.JPG"
)

# Redimensionar
imagen = imagen.resize((224, 224))

# Convertir a RGB
imagen = imagen.convert("RGB")

# Convertir a numpy
imagen = np.array(imagen, dtype=np.float32)

# Normalización Teachable Machine
imagen = (imagen / 127.5) - 1

imagen = np.expand_dims(imagen, axis=0)

# Ejecutar modelo
interpreter.set_tensor(
    input_details[0]["index"],
    imagen
)

interpreter.invoke()

resultado = interpreter.get_tensor(
    output_details[0]["index"]
)

print(resultado)