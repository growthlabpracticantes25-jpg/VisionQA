import tensorflow as tf

interpreter = tf.lite.Interpreter(
    model_path="modelo ia/model_unquant.tflite"
)

interpreter.allocate_tensors()

print("MODELO CARGADO CORRECTAMENTE")