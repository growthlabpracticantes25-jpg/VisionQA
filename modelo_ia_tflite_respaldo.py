import tensorflow as tf
import numpy as np
from PIL import Image

# Cargar modelo una sola vez
interpreter = tf.lite.Interpreter(
    model_path="modelo IA/model_unquant.tflite"
)

interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()


def clasificar_imagen(ruta_imagen):

    imagen = Image.open(ruta_imagen)

    imagen = imagen.resize((224, 224))

    imagen = imagen.convert("RGB")

    imagen = np.array(imagen, dtype=np.float32)

    imagen = (imagen / 127.5) - 1

    imagen = np.expand_dims(imagen, axis=0)

    interpreter.set_tensor(
        input_details[0]["index"],
        imagen
    )

    interpreter.invoke()

    resultado = interpreter.get_tensor(
        output_details[0]["index"]
    )

    return resultado