import cv2

imagen = cv2.imread("pieza.jpg")

cv2.imshow("VisionQA", imagen)
cv2.waitKey(0)
cv2.destroyAllWindows()
