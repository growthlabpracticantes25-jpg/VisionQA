import tensorflow as tf

interpreter = tf.lite.Interpreter(
    model_path="modelo ia/model_unquant.tflite"
)

interpreter.allocate_tensors()

print("MODELO CARGADO CORRECTAMENTE")

from modelo_ia import clasificar_imagen

resultado = clasificar_imagen("dataset/malas/Mala 22.JPG")

print(resultado)