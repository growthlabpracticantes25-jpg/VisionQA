import tensorflow as tf

interpreter = tf.lite.Interpreter(
    model_path="modelo IA/model_unquant.tflite"
)

interpreter.allocate_tensors()

entrada = interpreter.get_input_details()
salida = interpreter.get_output_details()

print("ENTRADA:")
print(entrada)

print("\nSALIDA:")
print(salida)