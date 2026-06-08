import cv2

contador = 0

# Abrir cámara
camara = cv2.VideoCapture(1)

while True:

    resultado, frame = camara.read()

    if not resultado:
        print("Error al leer la cámara")
        break

    cv2.imshow("VisionQA - Camara", frame)

    tecla = cv2.waitKey(1) & 0xFF

    if tecla == ord('b'):
        cv2.imwrite(f"dataset/buenas/buena_{contador}.jpg", frame)
        print("Imagen buena guardada")
        contador += 1

    elif tecla == ord('m'):
        cv2.imwrite(f"dataset/malas/mala_{contador}.jpg", frame)
        print("Imagen mala guardada")
        contador += 1

    elif tecla == ord('q'):
        break

camara.release()
cv2.destroyAllWindows()

